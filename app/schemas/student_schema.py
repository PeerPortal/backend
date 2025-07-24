from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class StudentBase(BaseModel):
    """申请者基础模型"""
    current_education: str = Field(..., description="当前教育背景")
    gpa: Optional[float] = Field(None, ge=0, le=4.0, description="GPA")
    target_degree: str = Field(..., description="目标学位", pattern="^(bachelor|master|phd)$")
    target_universities: List[str] = Field(..., description="目标大学列表")
    target_majors: List[str] = Field(..., description="目标专业列表")
    application_timeline: str = Field(..., description="申请时间线")
    budget_range: Optional[str] = Field(None, description="预算范围")
    preferred_countries: List[str] = Field(default=[], description="偏好国家")
    language_scores: Optional[dict] = Field(None, description="语言成绩")
    
class StudentProfile(StudentBase):
    """完整的申请者资料"""
    id: int
    user_id: int
    application_status: str = Field(default="preparing", description="申请状态")
    interests: List[str] = Field(default=[], description="兴趣爱好")
    extracurricular: List[str] = Field(default=[], description="课外活动")
    work_experience: Optional[str] = Field(None, description="工作经验")
    research_experience: Optional[str] = Field(None, description="研究经验")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    """更新申请者资料"""
    current_education: Optional[str] = None
    gpa: Optional[float] = None
    target_degree: Optional[str] = None
    target_universities: Optional[List[str]] = None
    target_majors: Optional[List[str]] = None
    application_timeline: Optional[str] = None
    budget_range: Optional[str] = None
    preferred_countries: Optional[List[str]] = None
    language_scores: Optional[dict] = None
    application_status: Optional[str] = None
    interests: Optional[List[str]] = None
    extracurricular: Optional[List[str]] = None
    work_experience: Optional[str] = None
    research_experience: Optional[str] = None

class StudentCreate(StudentBase):
    """创建申请者资料"""
    pass

class LearningNeeds(BaseModel):
    """学习需求模型"""
    user_id: int
    need_type: str = Field(..., description="需求类型", pattern="^(essay|recommendation|interview|planning|other)$")
    subject_area: str = Field(..., description="学科领域")
    urgency_level: str = Field(..., description="紧急程度", pattern="^(low|medium|high|urgent)$")
    budget: Optional[float] = Field(None, ge=0, description="预算")
    description: str = Field(..., max_length=1000, description="详细需求描述")
    preferred_mentor_criteria: Optional[dict] = Field(None, description="偏好指导者条件")
    
class LearningNeedsUpdate(BaseModel):
    """更新学习需求"""
    need_type: Optional[str] = None
    subject_area: Optional[str] = None
    urgency_level: Optional[str] = None
    budget: Optional[float] = None
    description: Optional[str] = None
    preferred_mentor_criteria: Optional[dict] = None 