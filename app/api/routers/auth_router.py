"""
认证相关的 API 路由
包括用户注册、登录、OAuth等功能
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import BaseModel
from typing import Dict, Any
import httpx

from app.core.config import settings
from app.api.deps import get_db_or_supabase, get_current_user
from app.schemas.user_schema import UserCreate, UserRead
from app.schemas.token_schema import Token
from app.crud.crud_user import create_user, authenticate_user, get_user_by_email, get_user_by_email

router = APIRouter()

# OAuth回调请求模型
class OAuthCallbackRequest(BaseModel):
    provider: str
    code: str
    state: str


def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post(
    "/register", 
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建新用户账户"
)
async def register(
    user_in: UserCreate,
    db_conn = Depends(get_db_or_supabase)
):
    """
    用户注册端点
    
    - **username**: 用户名（3-50字符，唯一）
    - **email**: 邮箱地址（可选，但推荐）  
    - **password**: 密码（最少8字符）
    """
    try:
        # 创建用户
        user = await create_user(db_conn, user_in)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户创建失败"
            )
        
        # 返回用户信息（不包含密码）
        return UserRead(
            id=user["id"],
            username=user["username"],
            email=user.get("email"),
            role=user.get("role", "user"),
            is_active=user.get("is_active", True),
            created_at=user["created_at"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用用户名和密码登录获取访问令牌"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_conn = Depends(get_db_or_supabase)
):
    """
    用户登录端点
    
    - **username**: 用户名
    - **password**: 密码
    
    返回JWT访问令牌
    """
    # 验证用户
    user = await authenticate_user(db_conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="刷新令牌",
    description="使用有效令牌刷新获取新的访问令牌"
)
async def refresh_token(
    current_user = Depends(get_current_user)
):
    """
    令牌刷新端点
    
    使用当前有效的令牌获取新的访问令牌
    """
    try:
        # 验证用户是否还有效
        if not current_user or not current_user.username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户信息",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.username}, 
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 捕获其他异常并转换为HTTP异常
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}"
        )


@router.post(
    "/oauth/callback",
    response_model=Token,
    summary="OAuth回调处理",
    description="处理Google和GitHub的OAuth认证回调"
)
async def oauth_callback(
    callback_data: OAuthCallbackRequest,
    db_conn = Depends(get_db_or_supabase)
):
    """
    处理OAuth认证回调
    """
    try:
        # 验证OAuth提供商
        if callback_data.provider not in ['google', 'github']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的OAuth提供商"
            )
        
        # 根据提供商获取用户信息
        if callback_data.provider == 'google':
            user_info = await get_google_user_info(callback_data.code)
        elif callback_data.provider == 'github':
            user_info = await get_github_user_info(callback_data.code)
        
        # 检查用户是否已存在
        existing_user = await get_user_by_email(db_conn, user_info['email'])
        
        if existing_user:
            # 用户已存在，直接登录
            user = existing_user
        else:
            # 创建新用户
            user_create = UserCreate(
                username=user_info['login'],
                email=user_info['email'],
                password="oauth_" + user_info['id']  # OAuth用户使用特殊密码
            )
            user = await create_user(db_conn, user_create)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="创建用户失败"
                )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, 
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth认证失败: {str(e)}"
        )


async def get_google_user_info(code: str) -> Dict[str, Any]:
    """获取Google用户信息"""
    try:
        # 获取访问令牌
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{settings.FRONTEND_URL}/auth/google/callback"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="获取Google访问令牌失败"
                )
            
            token_info = token_response.json()
            access_token = token_info["access_token"]
            
            # 获取用户信息
            user_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
            user_response = await client.get(user_url)
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="获取Google用户信息失败"
                )
            
            user_data = user_response.json()
            return {
                "id": user_data["id"],
                "email": user_data["email"],
                "login": user_data.get("name", user_data["email"].split("@")[0]),
                "name": user_data.get("name", "")
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google OAuth处理失败: {str(e)}"
        )


async def get_github_user_info(code: str) -> Dict[str, Any]:
    """获取GitHub用户信息"""
    try:
        # 获取访问令牌
        token_url = "https://github.com/login/oauth/access_token"
        token_data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url, 
                data=token_data,
                headers={"Accept": "application/json"}
            )
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="获取GitHub访问令牌失败"
                )
            
            token_info = token_response.json()
            access_token = token_info["access_token"]
            
            # 获取用户信息
            user_url = "https://api.github.com/user"
            headers = {"Authorization": f"token {access_token}"}
            user_response = await client.get(user_url, headers=headers)
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="获取GitHub用户信息失败"
                )
            
            user_data = user_response.json()
            
            # 获取用户邮箱（可能需要额外请求）
            email = user_data.get("email")
            if not email:
                emails_response = await client.get(
                    "https://api.github.com/user/emails", 
                    headers=headers
                )
                if emails_response.status_code == 200:
                    emails = emails_response.json()
                    primary_email = next((e for e in emails if e.get("primary")), None)
                    if primary_email:
                        email = primary_email["email"]
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无法获取GitHub用户邮箱"
                )
            
            return {
                "id": str(user_data["id"]),
                "email": email,
                "login": user_data["login"],
                "name": user_data.get("name", user_data["login"])
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub OAuth处理失败: {str(e)}"
        )