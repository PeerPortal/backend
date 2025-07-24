from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MentorBase(BaseModel):
    """指导者基础模型"""
    university: str = Field(..., description="就读/毕业学校")
    major: str = Field(..., description="专业")
    degree_level: str = Field(..., description="学位层次", pattern="^(bachelor|master|phd)$")
    graduation_year: int = Field(..., description="毕业年份")
    current_status: str = Field(..., description="当前状态", pattern="^(student|graduated|working)$")
    bio: Optional[str] = Field(None, max_length=1000, description="个人简介")
    specialties: List[str] = Field(default=[], description="指导专长领域")
    languages: List[str] = Field(default=["中文"], description="支持语言")
    
class MentorProfile(MentorBase):
    """完整的指导者资料"""
    id: int
    user_id: int
    verification_status: str = Field(default="pending", description="认证状态")
    rating: Optional[float] = Field(None, description="评分")
    total_sessions: int = Field(default=0, description="总指导次数")
    success_rate: Optional[float] = Field(None, description="成功率")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MentorUpdate(BaseModel):
    """更新指导者资料"""
    university: Optional[str] = None
    major: Optional[str] = None
    degree_level: Optional[str] = None
    graduation_year: Optional[int] = None
    current_status: Optional[str] = None
    bio: Optional[str] = None
    specialties: Optional[List[str]] = None
    languages: Optional[List[str]] = None

class MentorCreate(MentorBase):
    """创建指导者资料"""
    pass

class MentorPublic(BaseModel):
    """公开的指导者信息（用于搜索和展示）"""
    id: int
    user_id: int
    university: str
    major: str
    degree_level: str
    graduation_year: int
    current_status: str
    bio: Optional[str]
    specialties: List[str]
    languages: List[str]
    rating: Optional[float]
    total_sessions: int
    verification_status: str
    
    class Config:
        from_attributes = True

class MentorFilter(BaseModel):
    """指导者筛选条件"""
    university: Optional[str] = None
    major: Optional[str] = None
    degree_level: Optional[str] = None
    graduation_year_min: Optional[int] = None
    graduation_year_max: Optional[int] = None
    rating_min: Optional[float] = Field(None, ge=0, le=5)
    specialties: Optional[List[str]] = None
    languages: Optional[List[str]] = None 