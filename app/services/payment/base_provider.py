from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PaymentResult:
    """支付结果基类"""
    success: bool
    message: str = ""
    
    # 支付创建结果
    payment_url: Optional[str] = None
    qr_code_url: Optional[str] = None
    code_url: Optional[str] = None  # 微信扫码URL
    prepay_id: Optional[str] = None  # 微信预支付ID
    
    # 交易信息
    trade_no: Optional[str] = None
    out_trade_no: Optional[str] = None
    
    # 查询结果
    status: Optional[str] = None
    amount: Optional[Decimal] = None
    paid_at: Optional[datetime] = None
    
    # 原始响应数据
    raw_data: Optional[Dict[str, Any]] = None
    
    # 错误信息
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class RefundResult:
    """退款结果基类"""
    success: bool
    message: str = ""
    
    # 退款信息
    refund_id: Optional[str] = None
    out_refund_no: Optional[str] = None
    refund_amount: Optional[Decimal] = None
    refund_status: Optional[str] = None
    
    # 时间信息
    refund_time: Optional[datetime] = None
    
    # 原始响应数据
    raw_data: Optional[Dict[str, Any]] = None
    
    # 错误信息
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class BasePaymentProvider(ABC):
    """支付提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._client = None
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供商名称"""
        pass
    
    @abstractmethod
    async def create_payment(
        self,
        out_trade_no: str,
        total_amount: Decimal,
        subject: str,
        payment_type: str = "web",
        return_url: Optional[str] = None,
        notify_url: Optional[str] = None,
        **kwargs
    ) -> PaymentResult:
        """创建支付"""
        pass
    
    @abstractmethod
    async def query_payment(
        self,
        out_trade_no: Optional[str] = None,
        trade_no: Optional[str] = None
    ) -> PaymentResult:
        """查询支付状态"""
        pass
    
    @abstractmethod
    async def create_refund(
        self,
        out_trade_no: Optional[str] = None,
        trade_no: Optional[str] = None,
        refund_amount: Decimal = None,
        refund_reason: str = "",
        out_refund_no: Optional[str] = None,
        **kwargs
    ) -> RefundResult:
        """创建退款"""
        pass
    
    @abstractmethod
    async def query_refund(
        self,
        out_refund_no: Optional[str] = None,
        refund_id: Optional[str] = None
    ) -> RefundResult:
        """查询退款状态"""
        pass
    
    @abstractmethod
    async def verify_callback(
        self,
        callback_data: Dict[str, Any],
        signature: str
    ) -> bool:
        """验证回调签名"""
        pass
    
    @abstractmethod
    def parse_callback_data(
        self,
        callback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """解析回调数据"""
        pass
    
    async def close_payment(
        self,
        out_trade_no: str
    ) -> PaymentResult:
        """关闭支付（可选实现）"""
        return PaymentResult(
            success=False,
            message="该支付方式不支持关闭支付",
            error_code="NOT_SUPPORTED"
        )
    
    def _handle_network_error(self, error: Exception) -> PaymentResult:
        """处理网络错误"""
        return PaymentResult(
            success=False,
            message=f"网络错误: {str(error)}",
            error_code="NETWORK_ERROR",
            error_message=str(error)
        )
    
    def _handle_api_error(self, error_data: Dict[str, Any]) -> PaymentResult:
        """处理API错误"""
        return PaymentResult(
            success=False,
            message=error_data.get("message", "API调用失败"),
            error_code=error_data.get("code", "API_ERROR"),
            error_message=error_data.get("sub_msg", ""),
            raw_data=error_data
        )
    
    def _validate_amount(self, amount: Decimal) -> bool:
        """验证金额格式"""
        if not isinstance(amount, Decimal):
            return False
        
        # 金额必须大于0
        if amount <= 0:
            return False
        
        # 金额最多两位小数
        if amount.as_tuple().exponent < -2:
            return False
        
        return True
    
    def _validate_trade_no(self, trade_no: str) -> bool:
        """验证交易号格式"""
        if not trade_no or not isinstance(trade_no, str):
            return False
        
        # 交易号长度限制
        if len(trade_no) < 6 or len(trade_no) > 64:
            return False
        
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 可以实现一个简单的API调用来检查服务状态
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
