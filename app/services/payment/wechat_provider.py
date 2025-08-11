from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import logging
import json
import httpx
import hashlib
import hmac
import base64
from urllib.parse import urlencode

from app.services.payment.base_provider import BasePaymentProvider, PaymentResult, RefundResult
from app.core.payment_exceptions import WechatAPIException

logger = logging.getLogger(__name__)


class WechatProvider(BasePaymentProvider):
    """微信支付提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mchid = config['mchid']
        self.appid = config['appid']
        self.private_key = config['private_key']
        self.cert_serial_no = config['cert_serial_no']
        self.api_v3_key = config['api_v3_key']
        self.debug = config.get('debug', False)
        
        # API地址
        self.base_url = "https://api.mch.weixin.qq.com"
        if self.debug:
            self.base_url = "https://api.mch.weixin.qq.com"  # 微信支付没有沙箱环境
        
        # 初始化HTTP客户端
        self._client = httpx.AsyncClient(timeout=30.0)
        
        if self.debug:
            logger.info("微信支付提供商初始化完成（调试模式）")
    
    @property
    def provider_name(self) -> str:
        return "wechat"
    
    async def create_payment(
        self,
        out_trade_no: str,
        total_amount: Decimal,
        subject: str,
        payment_type: str = "native",
        return_url: Optional[str] = None,
        notify_url: Optional[str] = None,
        **kwargs
    ) -> PaymentResult:
        """创建微信支付"""
        try:
            # 验证参数
            if not self._validate_trade_no(out_trade_no):
                return PaymentResult(
                    success=False,
                    message="无效的交易号",
                    error_code="INVALID_TRADE_NO"
                )
            
            if not self._validate_amount(total_amount):
                return PaymentResult(
                    success=False,
                    message="无效的支付金额",
                    error_code="INVALID_AMOUNT"
                )
            
            # 构建请求数据
            amount_in_cents = int(total_amount * 100)  # 微信支付金额以分为单位
            
            request_data = {
                "appid": self.appid,
                "mchid": self.mchid,
                "description": subject,
                "out_trade_no": out_trade_no,
                "amount": {
                    "total": amount_in_cents,
                    "currency": "CNY"
                },
                "notify_url": notify_url or ""
            }
            
            # 根据支付类型选择API端点和参数
            if payment_type == "native":
                # 扫码支付
                url = f"{self.base_url}/v3/pay/transactions/native"
                
            elif payment_type == "jsapi":
                # JSAPI支付
                url = f"{self.base_url}/v3/pay/transactions/jsapi"
                openid = kwargs.get('openid')
                if not openid:
                    return PaymentResult(
                        success=False,
                        message="JSAPI支付需要提供openid",
                        error_code="MISSING_OPENID"
                    )
                request_data["payer"] = {"openid": openid}
                
            elif payment_type == "app":
                # APP支付
                url = f"{self.base_url}/v3/pay/transactions/app"
                
            elif payment_type == "h5":
                # H5支付
                url = f"{self.base_url}/v3/pay/transactions/h5"
                scene_info = kwargs.get('scene_info', {})
                if not scene_info:
                    scene_info = {
                        "payer_client_ip": kwargs.get('client_ip', '127.0.0.1'),
                        "h5_info": {
                            "type": "Wap"
                        }
                    }
                request_data["scene_info"] = scene_info
                
            else:
                return PaymentResult(
                    success=False,
                    message=f"不支持的支付类型: {payment_type}",
                    error_code="UNSUPPORTED_PAYMENT_TYPE"
                )
            
            # 添加可选参数
            if kwargs.get('attach'):
                request_data['attach'] = kwargs['attach']
            
            if kwargs.get('time_expire'):
                request_data['time_expire'] = kwargs['time_expire']
            else:
                # 默认30分钟过期
                from datetime import datetime, timedelta
                expire_time = datetime.now() + timedelta(minutes=30)
                request_data['time_expire'] = expire_time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
            
            # 发送请求
            response = await self._make_api_request("POST", url, request_data)
            
            if response.get('code'):
                # 有错误码表示失败
                return PaymentResult(
                    success=False,
                    message=response.get('message', '支付创建失败'),
                    error_code=response.get('code'),
                    error_message=response.get('detail'),
                    raw_data=response
                )
            
            # 成功响应
            result = PaymentResult(
                success=True,
                message="支付创建成功",
                out_trade_no=out_trade_no,
                raw_data=response
            )
            
            # 根据支付类型设置返回数据
            if payment_type == "native":
                result.code_url = response.get('code_url')
            elif payment_type == "jsapi":
                result.prepay_id = response.get('prepay_id')
                # JSAPI需要前端调起支付，返回调起支付所需参数
                if result.prepay_id:
                    js_api_params = self._build_jsapi_params(result.prepay_id)
                    result.raw_data['jsapi_params'] = js_api_params
            elif payment_type == "app":
                result.prepay_id = response.get('prepay_id')
                # APP支付需要返回调起支付所需参数
                if result.prepay_id:
                    app_params = self._build_app_params(result.prepay_id)
                    result.raw_data['app_params'] = app_params
            elif payment_type == "h5":
                result.payment_url = response.get('h5_url')
            
            return result
            
        except Exception as e:
            logger.error(f"微信支付创建失败: {str(e)}")
            return self._handle_network_error(e)
    
    async def query_payment(
        self,
        out_trade_no: Optional[str] = None,
        trade_no: Optional[str] = None
    ) -> PaymentResult:
        """查询微信支付状态"""
        try:
            if not out_trade_no and not trade_no:
                return PaymentResult(
                    success=False,
                    message="必须提供商户订单号或微信支付订单号",
                    error_code="MISSING_PARAMETER"
                )
            
            # 构建查询URL
            if out_trade_no:
                url = f"{self.base_url}/v3/pay/transactions/out-trade-no/{out_trade_no}"
            else:
                url = f"{self.base_url}/v3/pay/transactions/id/{trade_no}"
            
            # 添加查询参数
            params = {"mchid": self.mchid}
            url += f"?{urlencode(params)}"
            
            response = await self._make_api_request("GET", url)
            
            if response.get('code'):
                return PaymentResult(
                    success=False,
                    message=response.get('message', '查询失败'),
                    error_code=response.get('code'),
                    error_message=response.get('detail'),
                    raw_data=response
                )
            
            # 解析响应
            trade_state = response.get('trade_state')
            status = self._convert_trade_state(trade_state)
            
            amount_info = response.get('amount', {})
            total_amount = amount_info.get('total', 0) / 100  # 转换为元
            
            return PaymentResult(
                success=True,
                message="查询成功",
                status=status,
                trade_no=response.get('transaction_id'),
                out_trade_no=response.get('out_trade_no'),
                amount=Decimal(str(total_amount)),
                paid_at=self._parse_datetime(response.get('success_time')),
                raw_data=response
            )
            
        except Exception as e:
            logger.error(f"微信支付查询失败: {str(e)}")
            return self._handle_network_error(e)
    
    async def create_refund(
        self,
        out_trade_no: Optional[str] = None,
        trade_no: Optional[str] = None,
        refund_amount: Decimal = None,
        refund_reason: str = "",
        out_refund_no: Optional[str] = None,
        **kwargs
    ) -> RefundResult:
        """创建微信支付退款"""
        try:
            if not out_trade_no and not trade_no:
                return RefundResult(
                    success=False,
                    message="必须提供商户订单号或微信支付订单号"
                )
            
            if not refund_amount or refund_amount <= 0:
                return RefundResult(
                    success=False,
                    message="退款金额必须大于0"
                )
            
            if not out_refund_no:
                # 生成退款单号
                import uuid
                out_refund_no = f"RF{int(datetime.now().timestamp())}{uuid.uuid4().hex[:8]}"
            
            # 构建请求数据
            refund_amount_cents = int(refund_amount * 100)
            total_amount_cents = kwargs.get('total_amount_cents')
            if not total_amount_cents:
                # 如果没有提供原订单金额，需要先查询
                query_result = await self.query_payment(out_trade_no, trade_no)
                if not query_result.success:
                    return RefundResult(
                        success=False,
                        message="无法获取原订单信息"
                    )
                total_amount_cents = int(query_result.amount * 100)
            
            request_data = {
                "out_refund_no": out_refund_no,
                "reason": refund_reason or "用户申请退款",
                "amount": {
                    "refund": refund_amount_cents,
                    "total": total_amount_cents,
                    "currency": "CNY"
                },
                "notify_url": kwargs.get('notify_url', '')
            }
            
            if out_trade_no:
                request_data['out_trade_no'] = out_trade_no
            if trade_no:
                request_data['transaction_id'] = trade_no
            
            url = f"{self.base_url}/v3/refund/domestic/refunds"
            response = await self._make_api_request("POST", url, request_data)
            
            if response.get('code'):
                return RefundResult(
                    success=False,
                    message=response.get('message', '退款申请失败'),
                    error_code=response.get('code'),
                    error_message=response.get('detail'),
                    raw_data=response
                )
            
            # 解析响应
            amount_info = response.get('amount', {})
            refund_amount_result = amount_info.get('refund', 0) / 100
            
            return RefundResult(
                success=True,
                message="退款申请成功",
                refund_id=response.get('refund_id'),
                out_refund_no=response.get('out_refund_no'),
                refund_amount=Decimal(str(refund_amount_result)),
                refund_status=response.get('status'),
                raw_data=response
            )
            
        except Exception as e:
            logger.error(f"微信支付退款申请失败: {str(e)}")
            return RefundResult(
                success=False,
                message=f"退款申请失败: {str(e)}"
            )
    
    async def query_refund(
        self,
        out_refund_no: Optional[str] = None,
        refund_id: Optional[str] = None
    ) -> RefundResult:
        """查询微信支付退款状态"""
        try:
            if not out_refund_no and not refund_id:
                return RefundResult(
                    success=False,
                    message="必须提供商户退款单号或微信退款单号"
                )
            
            # 构建查询URL
            if out_refund_no:
                url = f"{self.base_url}/v3/refund/domestic/refunds/{out_refund_no}"
            else:
                # 微信退款单号查询需要不同的接口
                url = f"{self.base_url}/v3/refund/domestic/refunds/{refund_id}"
            
            response = await self._make_api_request("GET", url)
            
            if response.get('code'):
                return RefundResult(
                    success=False,
                    message=response.get('message', '退款查询失败'),
                    error_code=response.get('code'),
                    error_message=response.get('detail'),
                    raw_data=response
                )
            
            # 解析响应
            amount_info = response.get('amount', {})
            refund_amount_result = amount_info.get('refund', 0) / 100
            
            return RefundResult(
                success=True,
                message="退款查询成功",
                refund_id=response.get('refund_id'),
                out_refund_no=response.get('out_refund_no'),
                refund_amount=Decimal(str(refund_amount_result)),
                refund_status=response.get('status'),
                refund_time=self._parse_datetime(response.get('success_time')),
                raw_data=response
            )
            
        except Exception as e:
            logger.error(f"微信支付退款查询失败: {str(e)}")
            return RefundResult(
                success=False,
                message=f"退款查询失败: {str(e)}"
            )
    
    async def verify_callback(
        self,
        callback_data: Dict[str, Any],
        signature: str
    ) -> bool:
        """验证微信支付回调签名"""
        try:
            # 微信支付V3使用AEAD_AES_256_GCM加密
            # 这里简化处理，实际应该解密并验证
            return True  # 简化实现
            
        except Exception as e:
            logger.error(f"微信支付签名验证失败: {str(e)}")
            return False
    
    def parse_callback_data(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析微信支付回调数据"""
        # 微信支付V3的回调数据是加密的，需要解密
        # 这里简化处理，实际需要解密resource字段
        resource = callback_data.get('resource', {})
        
        return {
            "trade_no": resource.get("transaction_id"),
            "out_trade_no": resource.get("out_trade_no"),
            "status": self._convert_trade_state(resource.get("trade_state")),
            "amount": Decimal(str(resource.get("amount", {}).get("total", 0) / 100)),
            "paid_at": self._parse_datetime(resource.get("success_time")),
            "openid": resource.get("payer", {}).get("openid"),
            "raw_data": callback_data
        }
    
    def _convert_trade_state(self, trade_state: str) -> str:
        """转换交易状态"""
        status_map = {
            "SUCCESS": "paid",
            "REFUND": "refunded",
            "NOTPAY": "pending",
            "CLOSED": "failed",
            "REVOKED": "cancelled",
            "USERPAYING": "pending",
            "PAYERROR": "failed"
        }
        return status_map.get(trade_state, "unknown")
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not date_str:
            return None
        
        try:
            # 微信支付时间格式: 2018-06-08T10:34:56+08:00
            if '+' in date_str:
                date_str = date_str.split('+')[0]
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None
    
    def _build_jsapi_params(self, prepay_id: str) -> Dict[str, str]:
        """构建JSAPI调起支付参数"""
        import time
        import random
        import string
        
        timestamp = str(int(time.time()))
        nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        params = {
            "appId": self.appid,
            "timeStamp": timestamp,
            "nonceStr": nonce_str,
            "package": f"prepay_id={prepay_id}",
            "signType": "RSA"
        }
        
        # 生成签名
        sign_string = f"{self.appid}\n{timestamp}\n{nonce_str}\nprepay_id={prepay_id}\n"
        params["paySign"] = self._generate_sign(sign_string)
        
        return params
    
    def _build_app_params(self, prepay_id: str) -> Dict[str, str]:
        """构建APP调起支付参数"""
        import time
        import random
        import string
        
        timestamp = str(int(time.time()))
        nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        params = {
            "appid": self.appid,
            "partnerid": self.mchid,
            "prepayid": prepay_id,
            "package": "Sign=WXPay",
            "noncestr": nonce_str,
            "timestamp": timestamp
        }
        
        # 生成签名
        sign_string = f"{self.appid}\n{timestamp}\n{nonce_str}\n{prepay_id}\n"
        params["sign"] = self._generate_sign(sign_string)
        
        return params
    
    async def _make_api_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送API请求"""
        try:
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "WechatPay-Python-SDK"
            }
            
            # 添加认证头（简化处理）
            headers["Authorization"] = f"WECHATPAY2-SHA256-RSA2048 mchid=\"{self.mchid}\""
            
            # 发送请求
            if method.upper() == "POST":
                response = await self._client.post(
                    url,
                    json=data,
                    headers=headers
                )
            else:
                response = await self._client.get(
                    url,
                    headers=headers
                )
            
            # 解析响应
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                # 错误响应
                try:
                    error_data = response.json()
                    return error_data
                except:
                    return {
                        "code": str(response.status_code),
                        "message": "API调用失败",
                        "detail": response.text
                    }
                    
        except httpx.RequestError as e:
            raise WechatAPIException(f"网络请求失败: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise WechatAPIException(f"HTTP错误: {e.response.status_code}")
        except Exception as e:
            raise WechatAPIException(f"API调用失败: {str(e)}")
    
    def _generate_sign(self, sign_string: str) -> str:
        """生成签名"""
        # 这里简化处理，实际应使用RSA私钥签名
        # 在真实环境中，应该使用 cryptography 库进行RSA签名
        import hashlib
        return hashlib.sha256(sign_string.encode('utf-8')).hexdigest()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
