"""
论坛系统的API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.api.deps import get_current_user, get_db_or_supabase, get_current_user_optional
from app.schemas.token_schema import AuthenticatedUser
from app.schemas.forum_schema import (
    PostCreate, PostUpdate, ReplyCreate, ReplyUpdate,
    ForumPost, ForumReply, ForumCategory, PopularTag,
    PostListResponse, ReplyListResponse, LikeResponse
)
from app.crud.crud_forum import forum_crud

router = APIRouter()

@router.get("/categories", response_model=List[ForumCategory], summary="获取论坛分类")
async def get_categories():
    try:
        return await forum_crud.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类失败: {e}")

@router.get("/posts", response_model=PostListResponse, summary="获取帖子列表")
async def get_posts(
    category: Optional[str] = Query(None), author_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None), sort_by: str = Query("latest"),
    sort_order: str = Query("desc"), limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0), db_conn=Depends(get_db_or_supabase),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        user_id = int(current_user.id) if current_user else None
        result = await forum_crud.get_posts(
            db_conn=db_conn, category=category, author_id=author_id, search=search,
            sort_by=sort_by, sort_order=sort_order, limit=limit, offset=offset, user_id=user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取帖子列表失败: {e}")

@router.get("/posts/{post_id}", response_model=ForumPost, summary="获取帖子详情")
async def get_post(
    post_id: int, db_conn=Depends(get_db_or_supabase),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    """
    获取单个帖子的详细信息。
    - 如果帖子不存在，返回 404。
    - 每次成功获取后，帖子的浏览量会增加。
    """
    user_id = int(current_user.id) if current_user else None
    
    # 首先，安全地获取帖子
    post = await forum_crud.get_post_by_id(db_conn, post_id, user_id)
    
    # 如果找不到帖子，立即返回 404
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子不存在")

    # 确认帖子存在后，再增加其浏览量
    await forum_crud.increment_post_views(db_conn, post_id)
    
    # 手动更新返回对象中的浏览量，以反映此次查看操作
    post.views_count += 1
    
    return post

@router.post("/posts", response_model=ForumPost, status_code=201, summary="创建帖子")
async def create_post(
    post_data: PostCreate, db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    try:
        post = await forum_crud.create_post(db_conn, int(current_user.id), post_data)
        if not post:
            raise HTTPException(status_code=400, detail="创建帖子失败")
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建帖子失败: {e}")

@router.put("/posts/{post_id}", response_model=ForumPost, summary="更新帖子")
async def update_post(
    post_id: int, post_data: PostUpdate, db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    try:
        post = await forum_crud.update_post(db_conn, post_id, int(current_user.id), post_data)
        if not post:
            raise HTTPException(status_code=404, detail="帖子不存在或无权限修改")
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新帖子失败: {e}")

@router.delete("/posts/{post_id}", status_code=status.HTTP_200_OK, summary="删除帖子")
async def delete_post(
    post_id: int, 
    db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除一个帖子。
    - 需要用户认证。
    - 只有帖子的作者才能删除。
    - 删除成功返回 200 OK 和成功消息。
    - 如果帖子不存在或用户无权限删除，返回 404 Not Found。
    """
    success = await forum_crud.delete_post(db_conn, post_id, int(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在或您没有权限删除"
        )
    return {"message": "删除成功"}

@router.post("/posts/{post_id}/like", response_model=LikeResponse, summary="点赞/取消点赞帖子")
async def toggle_post_like(
    post_id: int, db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    try:
        return await forum_crud.toggle_post_like(db_conn, post_id, int(current_user.id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"点赞操作失败: {e}")

@router.get("/posts/{post_id}/replies", response_model=ReplyListResponse, summary="获取帖子回复")
async def get_post_replies(
    post_id: int, limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0), db_conn=Depends(get_db_or_supabase),
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    try:
        user_id = int(current_user.id) if current_user else None
        result = await forum_crud.get_post_replies(db_conn, post_id, user_id, limit, offset)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取回复列表失败: {e}")

@router.post("/posts/{post_id}/replies", response_model=ForumReply, status_code=201, summary="创建回复")
async def create_reply(
    post_id: int, reply_data: ReplyCreate, db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    try:
        reply = await forum_crud.create_reply(db_conn, post_id, int(current_user.id), reply_data)
        if not reply:
            raise HTTPException(status_code=400, detail="创建回复失败")
        return reply
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建回复失败: {e}")

@router.put("/replies/{reply_id}", response_model=ForumReply, summary="更新回复")
async def update_reply(
    reply_id: int, reply_data: ReplyUpdate, db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    try:
        reply = await forum_crud.update_reply(db_conn, reply_id, int(current_user.id), reply_data)
        if not reply:
            raise HTTPException(status_code=404, detail="回复不存在或无权限修改")
        return reply
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新回复失败: {e}")

@router.delete("/replies/{reply_id}", summary="删除回复")
async def delete_reply(
    reply_id: int, db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    try:
        success = await forum_crud.delete_reply(db_conn, reply_id, int(current_user.id))
        if not success:
            raise HTTPException(status_code=404, detail="回复不存在或无权限删除")
        return {"message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除回复失败: {e}")

@router.post("/replies/{reply_id}/like", response_model=LikeResponse, summary="点赞/取消点赞回复")
async def toggle_reply_like(
    reply_id: int, db_conn=Depends(get_db_or_supabase),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    try:
        return await forum_crud.toggle_reply_like(db_conn, reply_id, int(current_user.id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"点赞操作失败: {e}")
