"""
导师-学员匹配系统的数据模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum


# ================================
# 枚举类型定义
# ================================

class UserRole(str, Enum):
    MENTOR = "mentor"
    MENTEE = "mentee"
    BOTH = "both"


class MatchStatus(str, Enum):
    SUGGESTED = "suggested"
    MENTOR_INTERESTED = "mentor_interested"
    MENTEE_INTERESTED = "mentee_interested"
    MUTUAL_INTEREST = "mutual_interest"
    DECLINED_BY_MENTOR = "declined_by_mentor"
    DECLINED_BY_MENTEE = "declined_by_mentee"
    EXPIRED = "expired"


class RelationshipStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTE = "dispute"


class RelationshipType(str, Enum):
    PAID = "paid"
    FREE = "free"
    EXCHANGE = "exchange"
    VOLUNTEER = "volunteer"
    CREDITS = "credits"


class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW_MENTOR = "no_show_mentor"
    NO_SHOW_MENTEE = "no_show_mentee"
    RESCHEDULED = "rescheduled"


class TransactionType(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    BONUS = "bonus"
    PENALTY = "penalty"
    CREDIT_DEDUCTION = "credit_deduction"
    CREDIT_ADDITION = "credit_addition"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


# ================================
# 技能管理模型
# ================================

class SkillCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon_url: Optional[str] = None
    sort_order: int = Field(default=0)


class SkillCategoryCreate(SkillCategoryBase):
    pass


class SkillCategoryRead(SkillCategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillBase(BaseModel):
    category_id: int
    name: str = Field(..., max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    difficulty_level: int = Field(default=1, ge=1, le=5)
    sort_order: int = Field(default=0)


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[SkillCategoryRead] = None

    model_config = {"from_attributes": True}


# ================================
# 用户技能模型
# ================================

class UserSkillBase(BaseModel):
    skill_id: int
    proficiency_level: int = Field(default=1, ge=1, le=5)
    years_experience: int = Field(default=0, ge=0)
    can_mentor: bool = Field(default=False)
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field(default="CNY", max_length=3)
    description: Optional[str] = None


class UserSkillCreate(UserSkillBase):
    pass


class UserSkillUpdate(BaseModel):
    proficiency_level: Optional[int] = Field(None, ge=1, le=5)
    years_experience: Optional[int] = Field(None, ge=0)
    can_mentor: Optional[bool] = None
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    description: Optional[str] = None


class UserSkillRead(UserSkillBase):
    id: int
    user_id: int
    verified: bool
    verified_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    skill: Optional[SkillRead] = None

    model_config = {"from_attributes": True}


# ================================
# 学习需求模型
# ================================

class UserLearningNeedBase(BaseModel):
    skill_id: int
    urgency_level: int = Field(default=1, ge=1, le=5)
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field(default="CNY", max_length=3)
    preferred_format: str = Field(default="online", max_length=50)
    preferred_duration: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    current_level: int = Field(default=1, ge=1, le=5)
    target_level: int = Field(default=2, ge=1, le=5)

    @validator('budget_max')
    def validate_budget_max(cls, v, values):
        if v is not None and 'budget_min' in values and values['budget_min'] is not None:
            if v < values['budget_min']:
                raise ValueError('budget_max must be greater than or equal to budget_min')
        return v

    @validator('target_level')
    def validate_target_level(cls, v, values):
        if 'current_level' in values and v <= values['current_level']:
            raise ValueError('target_level must be higher than current_level')
        return v


class UserLearningNeedCreate(UserLearningNeedBase):
    pass


class UserLearningNeedUpdate(BaseModel):
    urgency_level: Optional[int] = Field(None, ge=1, le=5)
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    preferred_format: Optional[str] = Field(None, max_length=50)
    preferred_duration: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    current_level: Optional[int] = Field(None, ge=1, le=5)
    target_level: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None


class UserLearningNeedRead(UserLearningNeedBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    skill: Optional[SkillRead] = None

    model_config = {"from_attributes": True}


# ================================
# 匹配系统模型
# ================================

class MentorMatchBase(BaseModel):
    mentor_id: int
    mentee_id: int
    skill_id: int
    learning_need_id: int
    mentor_skill_id: int
    match_score: Decimal = Field(..., ge=0, le=100)
    match_algorithm: str = Field(default="v1.0", max_length=50)
    match_factors: Optional[Dict[str, Any]] = None


class MentorMatchCreate(MentorMatchBase):
    pass


class MentorMatchRead(MentorMatchBase):
    id: int
    status: MatchStatus
    mentor_viewed_at: Optional[datetime]
    mentee_viewed_at: Optional[datetime]
    mentor_responded_at: Optional[datetime]
    mentee_responded_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    
    # 关联数据
    skill: Optional[SkillRead] = None
    mentor_skill: Optional[UserSkillRead] = None
    learning_need: Optional[UserLearningNeedRead] = None

    model_config = {"from_attributes": True}


class MentorMatchUpdate(BaseModel):
    status: Optional[MatchStatus] = None


# ================================
# 指导关系模型
# ================================

class MentorshipRelationshipBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    success_criteria: Optional[str] = None
    start_date: date = Field(default_factory=date.today)
    estimated_end_date: Optional[date] = None
    total_sessions_planned: Optional[int] = None
    session_duration_minutes: int = Field(default=60)
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field(default="CNY", max_length=3)
    total_amount: Optional[Decimal] = None
    payment_schedule: str = Field(default="per_session", max_length=20)
    relationship_type: RelationshipType = Field(default=RelationshipType.PAID)
    preferred_communication: Optional[str] = Field(None, max_length=100)
    meeting_frequency: Optional[str] = Field(None, max_length=50)
    timezone: Optional[str] = Field(None, max_length=50)


class MentorshipRelationshipCreate(MentorshipRelationshipBase):
    mentor_id: int
    mentee_id: int
    skill_id: int
    match_id: Optional[int] = None


class MentorshipRelationshipUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    success_criteria: Optional[str] = None
    estimated_end_date: Optional[date] = None
    total_sessions_planned: Optional[int] = None
    session_duration_minutes: Optional[int] = None
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    total_amount: Optional[Decimal] = None
    payment_schedule: Optional[str] = Field(None, max_length=20)
    relationship_type: Optional[RelationshipType] = None
    preferred_communication: Optional[str] = Field(None, max_length=100)
    meeting_frequency: Optional[str] = Field(None, max_length=50)
    timezone: Optional[str] = Field(None, max_length=50)
    status: Optional[RelationshipStatus] = None
    cancellation_reason: Optional[str] = None


class MentorshipRelationshipRead(MentorshipRelationshipBase):
    id: int
    mentor_id: int
    mentee_id: int
    skill_id: int
    match_id: Optional[int]
    status: RelationshipStatus
    sessions_completed: int
    total_hours_spent: Decimal
    last_session_at: Optional[datetime]
    next_session_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    # 关联数据
    skill: Optional[SkillRead] = None

    model_config = {"from_attributes": True}


# ================================
# 指导会话模型
# ================================

class MentorshipSessionBase(BaseModel):
    session_number: int
    scheduled_at: datetime
    agenda: Optional[str] = None


class MentorshipSessionCreate(MentorshipSessionBase):
    relationship_id: int


class MentorshipSessionUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None
    agenda: Optional[str] = None
    mentor_notes: Optional[str] = None
    mentee_notes: Optional[str] = None
    key_topics: Optional[List[str]] = None
    homework_assigned: Optional[str] = None
    resources_shared: Optional[List[str]] = None
    next_session_plan: Optional[str] = None
    status: Optional[SessionStatus] = None
    cancellation_reason: Optional[str] = None
    mentor_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    mentee_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    mentor_feedback: Optional[str] = None
    mentee_feedback: Optional[str] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    milestones_achieved: Optional[List[str]] = None


class MentorshipSessionRead(MentorshipSessionBase):
    id: int
    relationship_id: int
    actual_start_at: Optional[datetime]
    actual_end_at: Optional[datetime]
    duration_minutes: Optional[int]
    mentor_notes: Optional[str]
    mentee_notes: Optional[str]
    key_topics: Optional[List[str]]
    homework_assigned: Optional[str]
    resources_shared: Optional[List[str]]
    next_session_plan: Optional[str]
    status: SessionStatus
    cancellation_reason: Optional[str]
    rescheduled_from: Optional[datetime]
    mentor_satisfaction: Optional[int]
    mentee_satisfaction: Optional[int]
    mentor_feedback: Optional[str]
    mentee_feedback: Optional[str]
    progress_percentage: int
    milestones_achieved: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ================================
# 评价系统模型
# ================================

class MentorshipReviewBase(BaseModel):
    overall_rating: int = Field(..., ge=1, le=5)
    communication_rating: Optional[int] = Field(None, ge=1, le=5)
    expertise_rating: Optional[int] = Field(None, ge=1, le=5)
    timeliness_rating: Optional[int] = Field(None, ge=1, le=5)
    value_rating: Optional[int] = Field(None, ge=1, le=5)
    professionalism_rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    pros: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    would_recommend: bool = Field(default=True)
    would_work_again: bool = Field(default=True)
    positive_tags: Optional[List[str]] = None
    negative_tags: Optional[List[str]] = None
    learning_objectives_met: Optional[int] = Field(None, ge=1, le=5)
    skill_improvement: Optional[int] = Field(None, ge=1, le=5)
    is_public: bool = Field(default=True)


class MentorshipReviewCreate(MentorshipReviewBase):
    relationship_id: int
    reviewee_id: int


class MentorshipReviewRead(MentorshipReviewBase):
    id: int
    relationship_id: int
    reviewer_id: int
    reviewee_id: int
    reviewer_role: UserRole
    is_verified: bool
    verification_notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ================================
# 统计和概览模型
# ================================

class UserRoleStats(BaseModel):
    """用户角色统计"""
    role: UserRole
    active_relationships: int
    completed_relationships: int
    total_sessions: int
    total_hours: Decimal
    average_rating: Optional[Decimal]
    rating_count: int
    success_rate: Decimal


class UserProfileOverview(BaseModel):
    """用户档案概览"""
    user_id: int
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    
    # 角色信息
    available_roles: List[UserRole]
    mentor_skills: List[UserSkillRead]
    learning_needs: List[UserLearningNeedRead]
    
    # 统计信息
    mentor_stats: Optional[UserRoleStats]
    mentee_stats: Optional[UserRoleStats]
    
    # 信誉信息
    reputation_score: int
    trust_level: str
    badges: List[str]


class MatchingSuggestion(BaseModel):
    """匹配建议"""
    match: MentorMatchRead
    compatibility_score: Decimal
    compatibility_factors: Dict[str, Any]
    estimated_cost: Optional[Decimal]
    mentor_profile: UserProfileOverview


class DashboardStats(BaseModel):
    """仪表板统计"""
    active_relationships: int
    pending_matches: int
    upcoming_sessions: int
    completed_sessions_this_month: int
    total_hours_this_month: Decimal
    earnings_this_month: Optional[Decimal]
    spending_this_month: Optional[Decimal]
    recent_reviews: List[MentorshipReviewRead]


# ================================
# API 请求/响应模型
# ================================

class MatchingFilters(BaseModel):
    """匹配过滤器"""
    skill_ids: Optional[List[int]] = None
    min_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    max_hourly_rate: Optional[Decimal] = Field(None, ge=0)
    min_hourly_rate: Optional[Decimal] = Field(None, ge=0)
    experience_years_min: Optional[int] = Field(None, ge=0)
    preferred_format: Optional[str] = None
    availability_timezone: Optional[str] = None
    relationship_type: Optional[RelationshipType] = None


class MatchingRequest(BaseModel):
    """匹配请求"""
    learning_need_id: int
    filters: Optional[MatchingFilters] = None
    limit: int = Field(default=10, ge=1, le=50)


class MatchingResponse(BaseModel):
    """匹配响应"""
    suggestions: List[MatchingSuggestion]
    total_count: int
    filters_applied: MatchingFilters


class RelationshipCreationRequest(BaseModel):
    """创建指导关系请求"""
    match_id: Optional[int] = None
    mentor_id: int
    skill_id: int
    title: str
    description: Optional[str] = None
    learning_goals: Optional[str] = None
    estimated_duration_weeks: Optional[int] = None
    session_frequency: Optional[str] = None
    preferred_session_duration: Optional[int] = None
    budget_total: Optional[Decimal] = None
    relationship_type: RelationshipType = RelationshipType.PAID
    message_to_mentor: Optional[str] = None
