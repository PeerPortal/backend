from fastapi import HTTPException
from typing import Optional, Dict, Any
from enum import Enum


class PaymentErrorCode(str, Enum):
    """支付错误码枚举"""
    # 通用错误 (1000-1099)
    UNKNOWN_ERROR = "1000"
    INVALID_PARAMETER = "1001"
    MISSING_PARAMETER = "1002"
    INVALID_SIGNATURE = "1003"
    PERMISSION_DENIED = "1004"
    RATE_LIMIT_EXCEEDED = "1005"
    
    # 订单相关错误 (1100-1199)
    ORDER_NOT_FOUND = "1100"
    ORDER_ALREADY_PAID = "1101"
    ORDER_EXPIRED = "1102"
    ORDER_CANCELLED = "1103"
    ORDER_AMOUNT_MISMATCH = "1104"
    ORDER_STATUS_INVALID = "1105"
    
    # 支付相关错误 (1200-1299)
    PAYMENT_NOT_FOUND = "1200"
    PAYMENT_ALREADY_PROCESSED = "1201"
    PAYMENT_EXPIRED = "1202"
    PAYMENT_CANCELLED = "1203"
    PAYMENT_AMOUNT_INVALID = "1204"
    PAYMENT_METHOD_NOT_SUPPORTED = "1205"
    PAYMENT_CREATION_FAILED = "1206"
    PAYMENT_VERIFICATION_FAILED = "1207"
    PAYMENT_CALLBACK_INVALID = "1208"
    PAYMENT_STATUS_INVALID = "1209"
    
    # 退款相关错误 (1300-1399)
    REFUND_NOT_FOUND = "1300"
    REFUND_ALREADY_PROCESSED = "1301"
    REFUND_AMOUNT_INVALID = "1302"
    REFUND_NOT_ALLOWED = "1303"
    REFUND_CREATION_FAILED = "1304"
    REFUND_PROCESSING_FAILED = "1305"
    REFUND_AMOUNT_EXCEEDS_PAYMENT = "1306"
    
    # 第三方支付平台错误 (1400-1499)
    ALIPAY_API_ERROR = "1400"
    ALIPAY_SIGNATURE_ERROR = "1401"
    ALIPAY_NETWORK_ERROR = "1402"
    WECHAT_API_ERROR = "1410"
    WECHAT_SIGNATURE_ERROR = "1411"
    WECHAT_NETWORK_ERROR = "1412"
    
    # 数据库相关错误 (1500-1599)
    DATABASE_ERROR = "1500"
    DATABASE_CONNECTION_ERROR = "1501"
    DATABASE_CONSTRAINT_ERROR = "1502"
    DATABASE_TIMEOUT_ERROR = "1503"
    
    # 业务逻辑错误 (1600-1699)
    INSUFFICIENT_BALANCE = "1600"
    USER_NOT_FOUND = "1601"
    SERVICE_NOT_FOUND = "1602"
    SERVICE_UNAVAILABLE = "1603"
    DUPLICATE_PAYMENT = "1604"
    CONCURRENT_OPERATION = "1605"
    
    # 系统错误 (1700-1799)
    SYSTEM_MAINTENANCE = "1700"
    SERVICE_UNAVAILABLE = "1701"
    INTERNAL_SERVER_ERROR = "1702"
    NETWORK_ERROR = "1703"
    TIMEOUT_ERROR = "1704"
    QUEUE_FULL_ERROR = "1705"
    
    # 安全相关错误 (1800-1899)
    INVALID_IP_ADDRESS = "1800"
    SUSPICIOUS_ACTIVITY = "1801"
    REPLAY_ATTACK_DETECTED = "1802"
    CALLBACK_IP_NOT_ALLOWED = "1803"
    SIGNATURE_VERIFICATION_FAILED = "1804"


class PaymentException(Exception):
    """支付系统基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: PaymentErrorCode = PaymentErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        http_status_code: int = 400
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.http_status_code = http_status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }
    
    def to_http_exception(self) -> HTTPException:
        """转换为FastAPI HTTP异常"""
        return HTTPException(
            status_code=self.http_status_code,
            detail={
                "success": False,
                "error_code": self.error_code.value,
                "message": self.message,
                "details": self.details
            }
        )


class OrderException(PaymentException):
    """订单相关异常"""
    
    def __init__(self, message: str, error_code: PaymentErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details, http_status_code=400)


class PaymentProcessingException(PaymentException):
    """支付处理异常"""
    
    def __init__(self, message: str, error_code: PaymentErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details, http_status_code=402)


class RefundException(PaymentException):
    """退款相关异常"""
    
    def __init__(self, message: str, error_code: PaymentErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details, http_status_code=400)


class ThirdPartyException(PaymentException):
    """第三方支付平台异常"""
    
    def __init__(self, message: str, error_code: PaymentErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details, http_status_code=502)


class SecurityException(PaymentException):
    """安全相关异常"""
    
    def __init__(self, message: str, error_code: PaymentErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details, http_status_code=403)


class DatabaseException(PaymentException):
    """数据库相关异常"""
    
    def __init__(self, message: str, error_code: PaymentErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details, http_status_code=500)


class SystemException(PaymentException):
    """系统相关异常"""
    
    def __init__(self, message: str, error_code: PaymentErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details, http_status_code=500)


# ================== 具体异常类 ==================

class OrderNotFoundException(OrderException):
    """订单未找到异常"""
    
    def __init__(self, order_id: int):
        super().__init__(
            f"订单 {order_id} 不存在",
            PaymentErrorCode.ORDER_NOT_FOUND,
            {"order_id": order_id}
        )


class OrderAlreadyPaidException(OrderException):
    """订单已支付异常"""
    
    def __init__(self, order_id: int):
        super().__init__(
            f"订单 {order_id} 已支付",
            PaymentErrorCode.ORDER_ALREADY_PAID,
            {"order_id": order_id}
        )


class PaymentNotFoundException(PaymentProcessingException):
    """支付记录未找到异常"""
    
    def __init__(self, payment_id: int):
        super().__init__(
            f"支付记录 {payment_id} 不存在",
            PaymentErrorCode.PAYMENT_NOT_FOUND,
            {"payment_id": payment_id}
        )


class PaymentAlreadyProcessedException(PaymentProcessingException):
    """支付已处理异常"""
    
    def __init__(self, payment_id: int, current_status: str):
        super().__init__(
            f"支付记录 {payment_id} 已处理，当前状态：{current_status}",
            PaymentErrorCode.PAYMENT_ALREADY_PROCESSED,
            {"payment_id": payment_id, "current_status": current_status}
        )


class PaymentAmountMismatchException(PaymentProcessingException):
    """支付金额不匹配异常"""
    
    def __init__(self, expected: float, actual: float):
        super().__init__(
            f"支付金额不匹配，期望：{expected}，实际：{actual}",
            PaymentErrorCode.PAYMENT_AMOUNT_INVALID,
            {"expected_amount": expected, "actual_amount": actual}
        )


class PaymentMethodNotSupportedException(PaymentProcessingException):
    """支付方式不支持异常"""
    
    def __init__(self, payment_method: str):
        super().__init__(
            f"不支持的支付方式：{payment_method}",
            PaymentErrorCode.PAYMENT_METHOD_NOT_SUPPORTED,
            {"payment_method": payment_method}
        )


class RefundAmountExceedsPaymentException(RefundException):
    """退款金额超过支付金额异常"""
    
    def __init__(self, refund_amount: float, payment_amount: float):
        super().__init__(
            f"退款金额 {refund_amount} 超过支付金额 {payment_amount}",
            PaymentErrorCode.REFUND_AMOUNT_EXCEEDS_PAYMENT,
            {"refund_amount": refund_amount, "payment_amount": payment_amount}
        )


class InvalidSignatureException(SecurityException):
    """签名验证失败异常"""
    
    def __init__(self, platform: str):
        super().__init__(
            f"{platform} 签名验证失败",
            PaymentErrorCode.SIGNATURE_VERIFICATION_FAILED,
            {"platform": platform}
        )


class CallbackIPNotAllowedException(SecurityException):
    """回调IP不在白名单异常"""
    
    def __init__(self, ip: str, platform: str):
        super().__init__(
            f"IP {ip} 不在 {platform} 回调白名单中",
            PaymentErrorCode.CALLBACK_IP_NOT_ALLOWED,
            {"ip": ip, "platform": platform}
        )


class ReplayAttackException(SecurityException):
    """重放攻击异常"""
    
    def __init__(self, nonce: str):
        super().__init__(
            f"检测到重放攻击，nonce: {nonce}",
            PaymentErrorCode.REPLAY_ATTACK_DETECTED,
            {"nonce": nonce}
        )


class AlipayAPIException(ThirdPartyException):
    """支付宝API异常"""
    
    def __init__(self, message: str, api_response: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"支付宝API错误：{message}",
            PaymentErrorCode.ALIPAY_API_ERROR,
            {"api_response": api_response}
        )


class WechatAPIException(ThirdPartyException):
    """微信支付API异常"""
    
    def __init__(self, message: str, api_response: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"微信支付API错误：{message}",
            PaymentErrorCode.WECHAT_API_ERROR,
            {"api_response": api_response}
        )


class ConcurrentOperationException(PaymentException):
    """并发操作异常"""
    
    def __init__(self, resource_type: str, resource_id: int):
        super().__init__(
            f"{resource_type} {resource_id} 正在被其他操作处理",
            PaymentErrorCode.CONCURRENT_OPERATION,
            {"resource_type": resource_type, "resource_id": resource_id},
            http_status_code=409
        )


class QueueFullException(SystemException):
    """队列已满异常"""
    
    def __init__(self, queue_name: str):
        super().__init__(
            f"队列 {queue_name} 已满，无法添加新任务",
            PaymentErrorCode.QUEUE_FULL_ERROR,
            {"queue_name": queue_name},
            http_status_code=503
        )


# ================== 异常处理器 ==================

def create_payment_error_response(
    error_code: PaymentErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    http_status_code: int = 400
) -> Dict[str, Any]:
    """创建标准的支付错误响应"""
    return {
        "success": False,
        "error_code": error_code.value,
        "message": message,
        "details": details or {},
        "timestamp": "2024-01-01T00:00:00Z"  # 实际使用时应该是当前时间
    }


def handle_payment_exception(exc: PaymentException) -> Dict[str, Any]:
    """处理支付异常并返回标准格式"""
    return {
        "success": False,
        "error_code": exc.error_code.value,
        "message": exc.message,
        "details": exc.details,
        "timestamp": "2024-01-01T00:00:00Z"  # 实际使用时应该是当前时间
    }
