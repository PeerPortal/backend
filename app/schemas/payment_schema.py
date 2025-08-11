from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from decimal import Decimal
from datetime import datetime
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIAL_REFUNDED = "partial_refunded"


class PaymentMethod(str, Enum):
    ALIPAY = "alipay"
    WECHAT = "wechat"


class PaymentType(str, Enum):
    WEB = "web"
    WAP = "wap"
    APP = "app"
    NATIVE = "native"
    JSAPI = "jsapi"


class RefundStatus(str, Enum):
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REFUNDED = "refunded"


# ================== 订单相关Schema ==================

class OrderBase(BaseModel):
    service_id: int = Field(..., description="服务ID")
    notes: Optional[str] = Field(None, max_length=500, description="订单备注")
    
    class Config:
        from_attributes = True


class OrderCreate(OrderBase):
    payment_method: Optional[PaymentMethod] = Field(None, description="首选支付方式")


class OrderUpdate(BaseModel):
    notes: Optional[str] = Field(None, max_length=500, description="订单备注")
    status: Optional[OrderStatus] = Field(None, description="订单状态")


class OrderRead(OrderBase):
    id: int
    user_id: int
    service_title: str
    service_description: Optional[str]
    unit_price: Decimal
    quantity: int
    total_price: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    service: Optional[Dict[str, Any]] = None
    payments: Optional[List[Dict[str, Any]]] = None


# ================== 支付相关Schema ==================

class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="支付金额")
    payment_method: PaymentMethod = Field(..., description="支付方式")
    payment_type: PaymentType = Field(PaymentType.WEB, description="支付类型")
    
    class Config:
        from_attributes = True


class PaymentCreate(PaymentBase):
    return_url: Optional[str] = Field(None, max_length=500, description="支付成功返回URL")
    notify_url: Optional[str] = Field(None, max_length=500, description="异步通知URL")
    client_ip: Optional[str] = Field(None, description="客户端IP")
    
    @validator('return_url', 'notify_url')
    def validate_urls(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL必须以http://或https://开头')
        return v


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = Field(None, description="支付状态")
    trade_no: Optional[str] = Field(None, description="第三方交易号")
    paid_at: Optional[datetime] = Field(None, description="支付完成时间")


class PaymentRead(PaymentBase):
    id: int
    order_id: int
    user_id: int
    out_trade_no: str
    trade_no: Optional[str]
    status: PaymentStatus
    payment_url: Optional[str]
    qr_code_url: Optional[str]
    code_url: Optional[str]  # 微信扫码URL
    prepay_id: Optional[str]  # 微信预支付ID
    paid_at: Optional[datetime]
    expired_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # 扩展信息
    order: Optional[Dict[str, Any]] = None
    refunds: Optional[List[Dict[str, Any]]] = None


class PaymentResponse(BaseModel):
    """支付创建响应"""
    payment_id: int
    out_trade_no: str
    payment_method: PaymentMethod
    payment_type: PaymentType
    amount: Decimal
    status: PaymentStatus
    payment_url: Optional[str] = None
    qr_code_url: Optional[str] = None
    code_url: Optional[str] = None
    prepay_id: Optional[str] = None
    expired_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


# ================== 退款相关Schema ==================

class RefundBase(BaseModel):
    refund_amount: Decimal = Field(..., gt=0, description="退款金额")
    refund_reason: str = Field(..., max_length=200, description="退款原因")
    refund_type: Literal["full", "partial"] = Field("partial", description="退款类型")
    
    class Config:
        from_attributes = True


class RefundCreate(RefundBase):
    operator_notes: Optional[str] = Field(None, max_length=500, description="操作员备注")


class RefundUpdate(BaseModel):
    status: Optional[RefundStatus] = Field(None, description="退款状态")
    refund_id: Optional[str] = Field(None, description="第三方退款单号")
    processed_at: Optional[datetime] = Field(None, description="退款处理完成时间")
    operator_notes: Optional[str] = Field(None, max_length=500, description="操作员备注")


class RefundRead(RefundBase):
    id: int
    payment_id: int
    user_id: int
    out_refund_no: str
    refund_id: Optional[str]
    status: RefundStatus
    processed_at: Optional[datetime]
    operator_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # 关联信息
    payment: Optional[Dict[str, Any]] = None


# ================== 支付统计Schema ==================

class PaymentStatsRead(BaseModel):
    """支付统计信息"""
    total_payments: int = Field(..., description="总支付笔数")
    total_amount: Decimal = Field(..., description="总支付金额")
    success_rate: float = Field(..., description="支付成功率")
    avg_amount: Decimal = Field(..., description="平均支付金额")
    
    # 按支付方式统计
    alipay_count: int = Field(0, description="支付宝支付笔数")
    alipay_amount: Decimal = Field(Decimal('0'), description="支付宝支付金额")
    wechat_count: int = Field(0, description="微信支付笔数")
    wechat_amount: Decimal = Field(Decimal('0'), description="微信支付金额")
    
    # 按状态统计
    pending_count: int = Field(0, description="待支付笔数")
    paid_count: int = Field(0, description="已支付笔数")
    failed_count: int = Field(0, description="失败笔数")
    cancelled_count: int = Field(0, description="已取消笔数")
    
    # 时间范围
    start_date: Optional[datetime] = Field(None, description="统计开始时间")
    end_date: Optional[datetime] = Field(None, description="统计结束时间")
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


# ================== 回调相关Schema ==================

class PaymentCallbackData(BaseModel):
    """支付回调数据基类"""
    platform: PaymentMethod = Field(..., description="支付平台")
    callback_data: Dict[str, Any] = Field(..., description="原始回调数据")
    signature: Optional[str] = Field(None, description="签名")
    client_ip: str = Field(..., description="客户端IP")
    
    class Config:
        extra = "allow"


class AlipayCallbackData(PaymentCallbackData):
    """支付宝回调数据"""
    trade_no: str = Field(..., description="支付宝交易号")
    out_trade_no: str = Field(..., description="商户订单号")
    trade_status: str = Field(..., description="交易状态")
    total_amount: str = Field(..., description="交易金额")
    buyer_id: Optional[str] = Field(None, description="买家支付宝用户ID")
    gmt_payment: Optional[str] = Field(None, description="交易付款时间")


class WechatCallbackData(PaymentCallbackData):
    """微信支付回调数据"""
    transaction_id: str = Field(..., description="微信支付订单号")
    out_trade_no: str = Field(..., description="商户订单号")
    trade_state: str = Field(..., description="交易状态")
    total_fee: str = Field(..., description="订单总金额，单位为分")
    openid: Optional[str] = Field(None, description="用户在商户appid下的唯一标识")
    time_end: Optional[str] = Field(None, description="支付完成时间")


# ================== 分页和查询Schema ==================

class PaymentQuery(BaseModel):
    """支付查询参数"""
    user_id: Optional[int] = Field(None, description="用户ID")
    order_id: Optional[int] = Field(None, description="订单ID")
    payment_method: Optional[PaymentMethod] = Field(None, description="支付方式")
    status: Optional[PaymentStatus] = Field(None, description="支付状态")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    
    # 分页参数
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class PaymentListResponse(BaseModel):
    """支付列表响应"""
    payments: List[PaymentRead]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class OrderQuery(BaseModel):
    """订单查询参数"""
    user_id: Optional[int] = Field(None, description="用户ID")
    service_id: Optional[int] = Field(None, description="服务ID")
    status: Optional[OrderStatus] = Field(None, description="订单状态")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    
    # 分页参数
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class OrderListResponse(BaseModel):
    """订单列表响应"""
    orders: List[OrderRead]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class RefundQuery(BaseModel):
    """退款查询参数"""
    payment_id: Optional[int] = Field(None, description="支付ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    status: Optional[RefundStatus] = Field(None, description="退款状态")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    
    # 分页参数
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class RefundListResponse(BaseModel):
    """退款列表响应"""
    refunds: List[RefundRead]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


# ================== 异步任务Schema ==================

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AsyncTaskResponse(BaseModel):
    """异步任务响应"""
    task_id: str
    task_name: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class QueueStatsResponse(BaseModel):
    """队列统计响应"""
    queues: Dict[str, int]
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    workers: int
    is_running: bool
    uptime: Optional[float] = None
    
    class Config:
        extra = "allow"


# ================== 监控和健康检查Schema ==================

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    services: Dict[str, Dict[str, Any]]
    metrics: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaymentMetrics(BaseModel):
    """支付指标"""
    success_count: int = Field(0, description="成功支付数")
    failure_count: int = Field(0, description="失败支付数")
    total_amount: Decimal = Field(Decimal('0'), description="总金额")
    avg_response_time: float = Field(0.0, description="平均响应时间(ms)")
    error_rate: float = Field(0.0, description="错误率")
    
    class Config:
        json_encoders = {
            Decimal: str
        }


# ================== API响应基类 ==================

class APIResponse(BaseModel):
    """API响应基类"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    code: int = Field(200, description="业务状态码")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(False, description="操作失败")
    message: str = Field(..., description="错误消息")
    code: int = Field(..., description="错误状态码")
    error_type: Optional[str] = Field(None, description="错误类型")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
