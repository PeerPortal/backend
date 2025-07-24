from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ServiceBase(BaseModel):
    """指导服务基础模型"""
    title: str = Field(..., max_length=200, description="服务标题")
    description: str = Field(..., max_length=2000, description="服务描述")
    category: str = Field(..., description="服务分类", pattern="^(essay|recommendation|interview|planning|consultation|other)$")
    subcategory: Optional[str] = Field(None, description="子分类")
    price: Decimal = Field(..., ge=0, description="服务价格")
    duration: int = Field(..., ge=30, description="服务时长（分钟）")
    delivery_days: int = Field(..., ge=1, description="交付天数")
    is_active: bool = Field(default=True, description="是否可用")
    
class ServiceCreate(ServiceBase):
    """创建服务"""
    pass

class ServiceUpdate(BaseModel):
    """更新服务"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price: Optional[Decimal] = None
    duration: Optional[int] = None
    delivery_days: Optional[int] = None
    is_active: Optional[bool] = None

class ServiceRead(ServiceBase):
    """服务详情"""
    id: int
    mentor_id: int
    mentor_name: Optional[str] = None
    mentor_university: Optional[str] = None
    mentor_rating: Optional[float] = None
    total_orders: int = Field(default=0, description="总订单数")
    rating: Optional[float] = Field(None, description="服务评分")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ServicePublic(BaseModel):
    """公开的服务信息（用于搜索和展示）"""
    id: int
    title: str
    description: str
    category: str
    subcategory: Optional[str]
    price: Decimal
    duration: int
    delivery_days: int
    mentor_id: int
    mentor_name: str
    mentor_university: str
    mentor_rating: Optional[float]
    total_orders: int
    rating: Optional[float]
    
    class Config:
        from_attributes = True

class ServiceFilter(BaseModel):
    """服务筛选条件"""
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    duration_min: Optional[int] = None
    duration_max: Optional[int] = None
    delivery_days_max: Optional[int] = None
    mentor_university: Optional[str] = None
    rating_min: Optional[float] = Field(None, ge=0, le=5)

class OrderCreate(BaseModel):
    """创建订单"""
    service_id: int
    notes: Optional[str] = Field(None, max_length=1000, description="特殊需求说明")
    
class OrderRead(BaseModel):
    """订单详情"""
    id: int
    service_id: int
    student_id: int
    mentor_id: int
    status: str
    total_amount: Decimal
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    service_title: str
    mentor_name: str
    student_name: str
    
    class Config:
        from_attributes = True

class OrderUpdate(BaseModel):
    """更新订单状态"""
    status: str = Field(..., pattern="^(pending|confirmed|in_progress|completed|cancelled|refunded)$")
    notes: Optional[str] = None 