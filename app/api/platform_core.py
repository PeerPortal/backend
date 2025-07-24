"""
留学生互助平台核心API
整合筛选、发帖、聊天、认证、支付、AI咨询功能
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Form, File, UploadFile
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

from app.models.user import User
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1", tags=["留学平台核心"])

# ================================
# 筛选系统API
# ================================

@router.get("/filters/regions", summary="获取地区列表")
async def get_regions(popular_only: bool = False):
    """获取地区/国家列表"""
    # 模拟数据，实际应从数据库获取
    regions = [
        {"id": 1, "name": "美国", "name_en": "United States", "country_code": "US", "is_popular": True},
        {"id": 2, "name": "英国", "name_en": "United Kingdom", "country_code": "UK", "is_popular": True},
        {"id": 3, "name": "加拿大", "name_en": "Canada", "country_code": "CA", "is_popular": True},
        {"id": 4, "name": "澳大利亚", "name_en": "Australia", "country_code": "AU", "is_popular": True},
        {"id": 5, "name": "新加坡", "name_en": "Singapore", "country_code": "SG", "is_popular": True},
        {"id": 6, "name": "中国香港", "name_en": "Hong Kong", "country_code": "HK", "is_popular": True},
        {"id": 7, "name": "德国", "name_en": "Germany", "country_code": "DE", "is_popular": True},
        {"id": 8, "name": "法国", "name_en": "France", "country_code": "FR", "is_popular": True},
        {"id": 9, "name": "日本", "name_en": "Japan", "country_code": "JP", "is_popular": True},
        {"id": 10, "name": "韩国", "name_en": "South Korea", "country_code": "KR", "is_popular": True}
    ]
    
    if popular_only:
        regions = [r for r in regions if r["is_popular"]]
    
    return {"regions": regions}

@router.get("/filters/universities", summary="获取院校列表")
async def get_universities(region_id: Optional[int] = None, search: Optional[str] = None):
    """获取院校列表，支持按地区筛选和搜索"""
    universities = [
        {"id": 1, "name": "哈佛大学", "name_en": "Harvard University", "region_id": 1, "ranking_qs": 4, "ranking_us_news": 3},
        {"id": 2, "name": "斯坦福大学", "name_en": "Stanford University", "region_id": 1, "ranking_qs": 5, "ranking_us_news": 6},
        {"id": 3, "name": "麻省理工学院", "name_en": "MIT", "region_id": 1, "ranking_qs": 1, "ranking_us_news": 2},
        {"id": 4, "name": "加州大学伯克利分校", "name_en": "UC Berkeley", "region_id": 1, "ranking_qs": 10, "ranking_us_news": 22},
        {"id": 5, "name": "牛津大学", "name_en": "University of Oxford", "region_id": 2, "ranking_qs": 2, "ranking_us_news": 5},
        {"id": 6, "name": "剑桥大学", "name_en": "University of Cambridge", "region_id": 2, "ranking_qs": 3, "ranking_us_news": 8},
        {"id": 7, "name": "多伦多大学", "name_en": "University of Toronto", "region_id": 3, "ranking_qs": 21, "ranking_us_news": 18},
        {"id": 8, "name": "悉尼大学", "name_en": "University of Sydney", "region_id": 4, "ranking_qs": 19, "ranking_us_news": 28},
        {"id": 9, "name": "新加坡国立大学", "name_en": "NUS", "region_id": 5, "ranking_qs": 8, "ranking_us_news": 25},
        {"id": 10, "name": "香港大学", "name_en": "University of Hong Kong", "region_id": 6, "ranking_qs": 22, "ranking_us_news": 35}
    ]
    
    # 按地区筛选
    if region_id:
        universities = [u for u in universities if u["region_id"] == region_id]
    
    # 搜索功能
    if search:
        search_lower = search.lower()
        universities = [
            u for u in universities 
            if search_lower in u["name"].lower() or search_lower in u["name_en"].lower()
        ]
    
    return {"universities": universities}

@router.get("/filters/majors", summary="获取专业列表")
async def get_majors(category: Optional[str] = None, search: Optional[str] = None):
    """获取专业列表，支持按类别筛选和搜索"""
    majors = [
        {"id": 1, "name": "计算机科学", "name_en": "Computer Science", "category": "STEM", "is_popular": True},
        {"id": 2, "name": "商业管理", "name_en": "Business Administration", "category": "Business", "is_popular": True},
        {"id": 3, "name": "金融学", "name_en": "Finance", "category": "Business", "is_popular": True},
        {"id": 4, "name": "电子工程", "name_en": "Electrical Engineering", "category": "STEM", "is_popular": True},
        {"id": 5, "name": "机械工程", "name_en": "Mechanical Engineering", "category": "STEM", "is_popular": True},
        {"id": 6, "name": "心理学", "name_en": "Psychology", "category": "Social Sciences", "is_popular": True},
        {"id": 7, "name": "经济学", "name_en": "Economics", "category": "Social Sciences", "is_popular": True},
        {"id": 8, "name": "生物学", "name_en": "Biology", "category": "STEM", "is_popular": True},
        {"id": 9, "name": "数据科学", "name_en": "Data Science", "category": "STEM", "is_popular": True},
        {"id": 10, "name": "人工智能", "name_en": "Artificial Intelligence", "category": "STEM", "is_popular": True}
    ]
    
    # 按类别筛选
    if category:
        majors = [m for m in majors if m["category"] == category]
    
    # 搜索功能
    if search:
        search_lower = search.lower()
        majors = [
            m for m in majors 
            if search_lower in m["name"].lower() or search_lower in m["name_en"].lower()
        ]
    
    return {"majors": majors}

@router.get("/search/mentors", summary="导师搜索")
async def search_mentors(
    degree: Optional[str] = None,
    region_id: Optional[int] = None,
    university_id: Optional[int] = None,
    major_id: Optional[int] = None,
    service_types: Optional[List[str]] = Query(None),
    min_rating: Optional[float] = 0,
    max_price: Optional[float] = None,
    page: int = 1,
    limit: int = 20
):
    """导师搜索 - 四步筛选：学历→地区→院校→专业"""
    # 模拟导师数据
    mentors = [
        {
            "id": 1,
            "username": "alice_cs",
            "full_name": "Alice Wang",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice",
            "university": "斯坦福大学",
            "major": "计算机科学",
            "degree": "master",
            "graduation_year": 2023,
            "region": "美国",
            "rating": 4.9,
            "review_count": 28,
            "services": ["申请咨询", "文书写作", "简历修改"],
            "hourly_rate": 200,
            "currency": "CNY",
            "tagline": "斯坦福CS硕士，专业申请指导",
            "verified": True,
            "response_rate": "95%",
            "response_time": "2小时内"
        },
        {
            "id": 2,
            "username": "bob_finance",
            "full_name": "Bob Chen",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob",
            "university": "哈佛大学",
            "major": "金融学",
            "degree": "master",
            "graduation_year": 2022,
            "region": "美国",
            "rating": 4.8,
            "review_count": 35,
            "services": ["申请咨询", "面试辅导", "选校定位"],
            "hourly_rate": 250,
            "currency": "CNY",
            "tagline": "哈佛商学院MBA，金融背景",
            "verified": True,
            "response_rate": "90%",
            "response_time": "1小时内"
        },
        {
            "id": 3,
            "username": "carol_ai",
            "full_name": "Carol Liu",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Carol",
            "university": "麻省理工学院",
            "major": "人工智能",
            "degree": "phd",
            "graduation_year": 2024,
            "region": "美国",
            "rating": 5.0,
            "review_count": 15,
            "services": ["申请咨询", "文书写作", "背景提升"],
            "hourly_rate": 300,
            "currency": "CNY",
            "tagline": "MIT AI博士，顶尖学术背景",
            "verified": True,
            "response_rate": "98%",
            "response_time": "30分钟内"
        }
    ]
    
    # 应用筛选条件
    filtered_mentors = mentors
    
    if degree:
        filtered_mentors = [m for m in filtered_mentors if m["degree"] == degree]
    
    if region_id:
        # 这里应该根据region_id匹配，简化处理
        pass
    
    if university_id:
        # 这里应该根据university_id匹配，简化处理
        pass
    
    if major_id:
        # 这里应该根据major_id匹配，简化处理
        pass
    
    if service_types:
        filtered_mentors = [
            m for m in filtered_mentors 
            if any(service in m["services"] for service in service_types)
        ]
    
    if min_rating:
        filtered_mentors = [m for m in filtered_mentors if m["rating"] >= min_rating]
    
    if max_price:
        filtered_mentors = [m for m in filtered_mentors if m["hourly_rate"] <= max_price]
    
    # 分页
    total = len(filtered_mentors)
    start = (page - 1) * limit
    end = start + limit
    mentors_page = filtered_mentors[start:end]
    
    return {
        "mentors": mentors_page,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }

# ================================
# 发帖系统API
# ================================

@router.get("/posts", summary="获取帖子列表")
async def get_posts(
    post_type: Optional[str] = None,  # mentor_offer/help_request
    category: Optional[str] = None,
    region_id: Optional[int] = None,
    university_id: Optional[int] = None,
    major_id: Optional[int] = None,
    page: int = 1,
    limit: int = 20
):
    """获取帖子列表，支持筛选"""
    # 模拟帖子数据
    posts = [
        {
            "id": 1,
            "user_id": 1,
            "post_type": "mentor_offer",
            "title": "斯坦福CS硕士，提供专业申请指导",
            "content": "大家好！我是2023年毕业的斯坦福计算机科学硕士，在申请过程中积累了丰富经验。现在提供以下服务：\n\n• 申请策略制定\n• 文书写作指导\n• 简历优化\n• 面试准备\n\n我的背景：本科985，GPA 3.8，托福110，GRE 330。成功申请到斯坦福、CMU、伯克利等顶尖学校。\n\n服务特色：\n✅ 一对一个性化指导\n✅ 提供实际案例参考\n✅ 24小时内回复\n✅ 满意度保证",
            "tags": ["CS", "斯坦福", "硕士申请", "文书指导"],
            "target_degree": "master",
            "target_region": "美国",
            "target_university": "斯坦福大学",
            "target_major": "计算机科学",
            "services_offered": ["申请咨询", "文书写作", "简历修改"],
            "pricing_info": {
                "申请咨询": "200/小时",
                "文书写作": "1500/篇",
                "简历修改": "300/次"
            },
            "author": {
                "id": 1,
                "username": "alice_cs",
                "full_name": "Alice Wang",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice",
                "verified": True,
                "rating": 4.9
            },
            "view_count": 156,
            "like_count": 23,
            "comment_count": 8,
            "created_at": "2024-07-20T10:30:00Z",
            "is_featured": True
        },
        {
            "id": 2,
            "user_id": 2,
            "post_type": "help_request",
            "title": "求助！25Fall CS硕士申请，求学长学姐指导",
            "content": "大家好，我是985本科CS专业的大三学生，准备申请25Fall的CS硕士项目。\n\n我的背景：\n• 本科：某985大学计算机科学\n• GPA：3.6/4.0\n• 托福：还没考（预计目标105+）\n• GRE：还没考（预计目标320+）\n• 研究经历：一篇二作论文在投\n• 实习：字节跳动算法实习3个月\n\n申请目标：\n• 冲刺：CMU、Stanford、MIT\n• 匹配：UCSD、UIUC、UW\n• 保底：还没定\n\n希望得到帮助：\n1. 选校建议（特别是保底学校）\n2. 文书写作指导\n3. 背景提升建议\n4. 时间规划\n\n预算：2000-5000元，希望找到合适的学长学姐！",
            "tags": ["25Fall", "CS硕士", "求指导", "985背景"],
            "target_degree": "master",
            "target_region": "美国",
            "target_major": "计算机科学",
            "author": {
                "id": 2,
                "username": "student_cs",
                "full_name": "Tom Li",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom",
                "verified": False,
                "rating": None
            },
            "view_count": 89,
            "like_count": 12,
            "comment_count": 15,
            "created_at": "2024-07-22T14:20:00Z",
            "is_featured": False
        }
    ]
    
    # 应用筛选
    filtered_posts = posts
    if post_type:
        filtered_posts = [p for p in filtered_posts if p["post_type"] == post_type]
    
    # 分页
    total = len(filtered_posts)
    start = (page - 1) * limit
    end = start + limit
    posts_page = filtered_posts[start:end]
    
    return {
        "posts": posts_page,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }

@router.post("/posts", summary="创建新帖子")
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    post_type: str = Form(...),  # mentor_offer/help_request
    tags: str = Form(""),  # 逗号分隔的标签
    target_degree: Optional[str] = Form(None),
    target_region_id: Optional[int] = Form(None),
    target_university_id: Optional[int] = Form(None),
    target_major_id: Optional[int] = Form(None),
    services_offered: Optional[str] = Form(None),  # JSON字符串
    pricing_info: Optional[str] = Form(None),  # JSON字符串
    current_user: User = Depends(get_current_user)
):
    """创建新帖子"""
    import json
    
    # 解析标签
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # 解析服务和价格信息
    services_list = []
    pricing_dict = {}
    
    if services_offered:
        try:
            services_list = json.loads(services_offered)
        except:
            services_list = [s.strip() for s in services_offered.split(",") if s.strip()]
    
    if pricing_info:
        try:
            pricing_dict = json.loads(pricing_info)
        except:
            pass
    
    # 创建帖子
    new_post = {
        "id": len(posts) + 1,  # 简化的ID生成
        "user_id": current_user.id,
        "post_type": post_type,
        "title": title,
        "content": content,
        "tags": tag_list,
        "target_degree": target_degree,
        "target_region_id": target_region_id,
        "target_university_id": target_university_id,
        "target_major_id": target_major_id,
        "services_offered": services_list,
        "pricing_info": pricing_dict,
        "view_count": 0,
        "like_count": 0,
        "comment_count": 0,
        "created_at": datetime.now().isoformat(),
        "is_active": True,
        "is_featured": False
    }
    
    return {
        "message": "帖子创建成功",
        "post": new_post
    }

@router.get("/posts/{post_id}", summary="获取帖子详情")
async def get_post_detail(post_id: int):
    """获取帖子详情"""
    # 模拟获取帖子详情
    post = {
        "id": post_id,
        "user_id": 1,
        "post_type": "mentor_offer",
        "title": "斯坦福CS硕士，提供专业申请指导",
        "content": "详细的帖子内容...",
        "tags": ["CS", "斯坦福", "硕士申请"],
        "author": {
            "id": 1,
            "username": "alice_cs",
            "full_name": "Alice Wang",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice",
            "verified": True,
            "rating": 4.9,
            "university": "斯坦福大学",
            "major": "计算机科学"
        },
        "view_count": 156,
        "like_count": 23,
        "comment_count": 8,
        "created_at": "2024-07-20T10:30:00Z"
    }
    
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    return {"post": post}

# ================================
# 认证系统API
# ================================

@router.get("/verification/status", summary="获取认证状态")
async def get_verification_status(current_user: User = Depends(get_current_user)):
    """获取用户认证状态"""
    return {
        "user_id": current_user.id,
        "identity_verified": True,  # 实名认证
        "university_verified": False,  # 院校认证
        "phone_verified": True,  # 手机认证
        "email_verified": True,  # 邮箱认证
        "verification_badges": ["实名认证"],
        "pending_verifications": ["院校认证"]
    }

@router.post("/verification/university", summary="提交院校认证")
async def submit_university_verification(
    university_id: int = Form(...),
    degree_type: str = Form(...),
    graduation_year: int = Form(...),
    student_id: str = Form(...),
    offer_image: UploadFile = File(...),
    student_card: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """提交院校认证材料"""
    # 这里应该保存上传的文件并创建认证记录
    verification_id = str(uuid.uuid4())
    
    return {
        "message": "院校认证材料已提交，请等待审核",
        "verification_id": verification_id,
        "estimated_review_time": "3-5个工作日"
    }

# ================================
# 聊天系统API
# ================================

@router.get("/friends", summary="获取好友列表")
async def get_friends(current_user: User = Depends(get_current_user)):
    """获取好友列表"""
    friends = [
        {
            "id": 1,
            "username": "alice_cs",
            "full_name": "Alice Wang",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice",
            "online_status": "online",
            "last_message": "好的，我来帮你看看文书",
            "last_message_time": "2024-07-24T15:30:00Z",
            "unread_count": 2
        },
        {
            "id": 2,
            "username": "bob_finance",
            "full_name": "Bob Chen",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Bob",
            "online_status": "offline",
            "last_message": "面试准备的资料我发给你了",
            "last_message_time": "2024-07-24T10:15:00Z",
            "unread_count": 0
        }
    ]
    
    return {"friends": friends}

@router.post("/friends/add", summary="添加好友")
async def add_friend(
    user_id: int,
    message: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """发送好友申请"""
    return {
        "message": "好友申请已发送",
        "request_id": str(uuid.uuid4())
    }

@router.get("/chat/rooms", summary="获取聊天房间列表")
async def get_chat_rooms(current_user: User = Depends(get_current_user)):
    """获取用户的聊天房间列表"""
    rooms = [
        {
            "id": 1,
            "room_type": "private",
            "other_user": {
                "id": 1,
                "username": "alice_cs",
                "full_name": "Alice Wang",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice"
            },
            "last_message": {
                "content": "好的，我来帮你看看文书",
                "sender_id": 1,
                "created_at": "2024-07-24T15:30:00Z"
            },
            "unread_count": 2,
            "updated_at": "2024-07-24T15:30:00Z"
        }
    ]
    
    return {"rooms": rooms}

@router.get("/chat/rooms/{room_id}/messages", summary="获取聊天消息")
async def get_chat_messages(
    room_id: int,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """获取聊天房间的消息列表"""
    messages = [
        {
            "id": 1,
            "sender_id": 1,
            "content": "你好！看到你的申请需求了，我可以帮你看看文书",
            "message_type": "text",
            "created_at": "2024-07-24T15:25:00Z"
        },
        {
            "id": 2,
            "sender_id": current_user.id,
            "content": "太好了！我现在还在准备PS，想请你帮忙看看思路对不对",
            "message_type": "text",
            "created_at": "2024-07-24T15:28:00Z"
        },
        {
            "id": 3,
            "sender_id": 1,
            "content": "好的，我来帮你看看文书",
            "message_type": "text",
            "created_at": "2024-07-24T15:30:00Z"
        }
    ]
    
    return {
        "messages": messages,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(messages)
        }
    }

@router.post("/chat/rooms/{room_id}/messages", summary="发送消息")
async def send_message(
    room_id: int,
    content: str,
    message_type: str = "text",
    current_user: User = Depends(get_current_user)
):
    """发送聊天消息"""
    message = {
        "id": 999,  # 应该由数据库生成
        "room_id": room_id,
        "sender_id": current_user.id,
        "content": content,
        "message_type": message_type,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "message": "消息发送成功",
        "data": message
    }

# ================================
# 服务类型API
# ================================

@router.get("/services/types", summary="获取服务类型列表")
async def get_service_types():
    """获取所有服务类型"""
    service_types = [
        {"id": 1, "name": "申请咨询", "name_en": "Application Consulting", "category": "consulting", "is_popular": True},
        {"id": 2, "name": "文书写作", "name_en": "Essay Writing", "category": "writing", "is_popular": True},
        {"id": 3, "name": "文书润色", "name_en": "Essay Editing", "category": "writing", "is_popular": True},
        {"id": 4, "name": "简历修改", "name_en": "Resume Editing", "category": "writing", "is_popular": True},
        {"id": 5, "name": "网申指导", "name_en": "Application Guidance", "category": "application", "is_popular": True},
        {"id": 6, "name": "面试辅导", "name_en": "Interview Coaching", "category": "consulting", "is_popular": True},
        {"id": 7, "name": "选校定位", "name_en": "School Selection", "category": "consulting", "is_popular": True},
        {"id": 8, "name": "背景提升", "name_en": "Background Enhancement", "category": "background", "is_popular": True}
    ]
    
    return {"service_types": service_types}

# ================================
# 用户资料API
# ================================

@router.get("/profile/me", summary="获取我的资料")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户的详细资料"""
    profile = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": "Alice Wang",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice",
        "cover_image_url": None,
        "tagline": "斯坦福CS硕士，专业申请指导",
        "introduction": "大家好！我是2023年毕业的斯坦福计算机科学硕士...",
        "user_type": "mentor",
        "verification_status": "university_verified",
        "languages_spoken": ["中文", "English"],
        "timezone": "America/Los_Angeles",
        
        # 教育背景
        "education": [
            {
                "degree_type": "master",
                "school_name": "斯坦福大学",
                "major": "计算机科学",
                "graduation_year": 2023,
                "gpa": 3.9,
                "is_verified": True
            },
            {
                "degree_type": "bachelor",
                "school_name": "清华大学",
                "major": "计算机科学与技术",
                "graduation_year": 2021,
                "gpa": 3.8,
                "is_verified": True
            }
        ],
        
        # 服务能力
        "services": [
            {
                "service_type": "申请咨询",
                "proficiency_level": 5,
                "experience_years": 2,
                "hourly_rate": 200,
                "description": "提供专业的申请策略制定和指导"
            },
            {
                "service_type": "文书写作",
                "proficiency_level": 5,
                "experience_years": 2,
                "hourly_rate": 300,
                "description": "帮助完善个人陈述和推荐信"
            }
        ],
        
        # 统计信息
        "stats": {
            "total_students_helped": 28,
            "average_rating": 4.9,
            "response_rate": "95%",
            "response_time": "2小时内",
            "completion_rate": "100%"
        }
    }
    
    return {"profile": profile}

@router.put("/profile/me", summary="更新我的资料")
async def update_my_profile(
    full_name: Optional[str] = None,
    tagline: Optional[str] = None,
    introduction: Optional[str] = None,
    languages_spoken: Optional[List[str]] = None,
    timezone: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """更新用户资料"""
    # 这里应该更新数据库
    return {
        "message": "资料更新成功",
        "updated_fields": {
            "full_name": full_name,
            "tagline": tagline,
            "introduction": introduction,
            "languages_spoken": languages_spoken,
            "timezone": timezone
        }
    }

# ================================
# 仪表板API
# ================================

@router.get("/dashboard/stats", summary="获取仪表板统计")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """获取用户仪表板统计数据"""
    stats = {
        "overview": {
            "total_orders": 15,
            "active_orders": 3,
            "completed_orders": 12,
            "total_earnings": 8500.00,
            "this_month_earnings": 2100.00,
            "average_rating": 4.9,
            "total_reviews": 28
        },
        "recent_activities": [
            {
                "type": "order_completed",
                "title": "文书写作服务已完成",
                "description": "为Tom Li完成了PS写作",
                "amount": 1500.00,
                "created_at": "2024-07-24T10:30:00Z"
            },
            {
                "type": "new_order",
                "title": "收到新订单",
                "description": "Lucy Zhang预订了申请咨询服务",
                "amount": 800.00,
                "created_at": "2024-07-23T15:20:00Z"
            }
        ],
        "upcoming_sessions": [
            {
                "id": 1,
                "student_name": "Tom Li",
                "service": "申请咨询",
                "scheduled_at": "2024-07-25T14:00:00Z",
                "duration": 60
            }
        ]
    }
    
    return {"stats": stats}
