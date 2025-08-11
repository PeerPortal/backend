from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import logging
import hashlib
import base64
import json
import httpx
from urllib.parse import urlencode, parse_qs

from app.services.payment.base_provider import BasePaymentProvider, PaymentResult, RefundResult
from app.core.payment_exceptions import AlipayAPIException

logger = logging.getLogger(__name__)


class AlipayProvider(BasePaymentProvider):
    """支付宝支付提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config['app_id']
        self.private_key = config['private_key']
        self.public_key = config['public_key']
        self.gateway = config.get('gateway', 'https://openapi.alipay.com/gateway.do')
        self.sign_type = config.get('sign_type', 'RSA2')
        self.debug = config.get('debug', False)
        
        # 初始化HTTP客户端
        self._client = httpx.AsyncClient(timeout=30.0)
        
        if self.debug:
            logger.info("支付宝提供商初始化完成（调试模式）")
    
    @property
    def provider_name(self) -> str:
        return "alipay"
    
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
        """创建支付宝支付"""
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
            
            # 构建请求参数
            biz_content = {
                "out_trade_no": out_trade_no,
                "total_amount": str(total_amount),
                "subject": subject,
                "product_code": self._get_product_code(payment_type),
                "timeout_express": kwargs.get('timeout_express', '30m')
            }
            
            # 添加可选参数
            if kwargs.get('body'):
                biz_content['body'] = kwargs['body']
            
            # 根据支付类型选择API方法
            if payment_type == "web":
                method = "alipay.trade.page.pay"
                if return_url:
                    biz_content['return_url'] = return_url
            elif payment_type == "wap":
                method = "alipay.trade.wap.pay"
                if return_url:
                    biz_content['return_url'] = return_url
            elif payment_type == "app":
                method = "alipay.trade.app.pay"
            elif payment_type == "native":
                method = "alipay.trade.precreate"
            else:
                return PaymentResult(
                    success=False,
                    message=f"不支持的支付类型: {payment_type}",
                    error_code="UNSUPPORTED_PAYMENT_TYPE"
                )
            
            # 构建公共参数
            params = {
                "app_id": self.app_id,
                "method": method,
                "charset": "utf-8",
                "sign_type": self.sign_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "biz_content": json.dumps(biz_content, ensure_ascii=False)
            }
            
            if notify_url:
                params['notify_url'] = notify_url
            
            # 生成签名
            sign = self._generate_sign(params)
            params['sign'] = sign
            
            # 发送请求
            if payment_type in ["web", "wap"]:
                # 网页支付返回重定向URL
                payment_url = f"{self.gateway}?{urlencode(params)}"
                return PaymentResult(
                    success=True,
                    message="支付创建成功",
                    payment_url=payment_url,
                    out_trade_no=out_trade_no
                )
            elif payment_type == "app":
                # APP支付返回支付字符串
                payment_string = urlencode(params)
                return PaymentResult(
                    success=True,
                    message="支付创建成功",
                    payment_url=payment_string,  # APP支付字符串
                    out_trade_no=out_trade_no
                )
            else:
                # 扫码支付调用API获取二维码
                response = await self._make_api_request(params)
                
                if response.get('code') == '10000':
                    qr_code = response.get('qr_code')
                    return PaymentResult(
                        success=True,
                        message="支付创建成功",
                        qr_code_url=qr_code,
                        out_trade_no=out_trade_no,
                        raw_data=response
                    )
                else:
                    return PaymentResult(
                        success=False,
                        message=response.get('msg', '支付创建失败'),
                        error_code=response.get('code'),
                        error_message=response.get('sub_msg'),
                        raw_data=response
                    )
                    
        except Exception as e:
            logger.error(f"支付宝支付创建失败: {str(e)}")
            return self._handle_network_error(e)
    
    async def query_payment(
        self,
        out_trade_no: Optional[str] = None,
        trade_no: Optional[str] = None
    ) -> PaymentResult:
        """查询支付宝支付状态"""
        try:
            if not out_trade_no and not trade_no:
                return PaymentResult(
                    success=False,
                    message="必须提供商户订单号或支付宝交易号",
                    error_code="MISSING_PARAMETER"
                )
            
            biz_content = {}
            if out_trade_no:
                biz_content['out_trade_no'] = out_trade_no
            if trade_no:
                biz_content['trade_no'] = trade_no
            
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.query",
                "charset": "utf-8",
                "sign_type": self.sign_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "biz_content": json.dumps(biz_content)
            }
            
            sign = self._generate_sign(params)
            params['sign'] = sign
            
            response = await self._make_api_request(params)
            
            if response.get('code') == '10000':
                trade_status = response.get('trade_status')
                status = self._convert_trade_status(trade_status)
                
                return PaymentResult(
                    success=True,
                    message="查询成功",
                    status=status,
                    trade_no=response.get('trade_no'),
                    out_trade_no=response.get('out_trade_no'),
                    amount=Decimal(response.get('total_amount', '0')),
                    paid_at=self._parse_datetime(response.get('send_pay_date')),
                    raw_data=response
                )
            else:
                return PaymentResult(
                    success=False,
                    message=response.get('msg', '查询失败'),
                    error_code=response.get('code'),
                    error_message=response.get('sub_msg'),
                    raw_data=response
                )
                
        except Exception as e:
            logger.error(f"支付宝支付查询失败: {str(e)}")
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
        """创建支付宝退款"""
        try:
            if not out_trade_no and not trade_no:
                return RefundResult(
                    success=False,
                    message="必须提供商户订单号或支付宝交易号"
                )
            
            if not refund_amount or refund_amount <= 0:
                return RefundResult(
                    success=False,
                    message="退款金额必须大于0"
                )
            
            biz_content = {
                "refund_amount": str(refund_amount),
                "refund_reason": refund_reason or "用户申请退款"
            }
            
            if out_trade_no:
                biz_content['out_trade_no'] = out_trade_no
            if trade_no:
                biz_content['trade_no'] = trade_no
            if out_refund_no:
                biz_content['out_request_no'] = out_refund_no
            
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.refund",
                "charset": "utf-8",
                "sign_type": self.sign_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "biz_content": json.dumps(biz_content, ensure_ascii=False)
            }
            
            sign = self._generate_sign(params)
            params['sign'] = sign
            
            response = await self._make_api_request(params)
            
            if response.get('code') == '10000':
                return RefundResult(
                    success=True,
                    message="退款申请成功",
                    refund_id=response.get('trade_no'),
                    out_refund_no=response.get('out_request_no'),
                    refund_amount=Decimal(response.get('refund_fee', '0')),
                    refund_time=self._parse_datetime(response.get('gmt_refund_pay')),
                    raw_data=response
                )
            else:
                return RefundResult(
                    success=False,
                    message=response.get('msg', '退款申请失败'),
                    error_code=response.get('code'),
                    error_message=response.get('sub_msg'),
                    raw_data=response
                )
                
        except Exception as e:
            logger.error(f"支付宝退款申请失败: {str(e)}")
            return RefundResult(
                success=False,
                message=f"退款申请失败: {str(e)}"
            )
    
    async def query_refund(
        self,
        out_refund_no: Optional[str] = None,
        refund_id: Optional[str] = None
    ) -> RefundResult:
        """查询支付宝退款状态"""
        try:
            if not out_refund_no:
                return RefundResult(
                    success=False,
                    message="必须提供退款请求号"
                )
            
            biz_content = {
                "out_request_no": out_refund_no
            }
            
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.fastpay.refund.query",
                "charset": "utf-8",
                "sign_type": self.sign_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "biz_content": json.dumps(biz_content)
            }
            
            sign = self._generate_sign(params)
            params['sign'] = sign
            
            response = await self._make_api_request(params)
            
            if response.get('code') == '10000':
                return RefundResult(
                    success=True,
                    message="退款查询成功",
                    refund_id=response.get('trade_no'),
                    out_refund_no=response.get('out_request_no'),
                    refund_amount=Decimal(response.get('refund_amount', '0')),
                    refund_status=response.get('refund_status'),
                    refund_time=self._parse_datetime(response.get('gmt_refund_pay')),
                    raw_data=response
                )
            else:
                return RefundResult(
                    success=False,
                    message=response.get('msg', '退款查询失败'),
                    error_code=response.get('code'),
                    error_message=response.get('sub_msg'),
                    raw_data=response
                )
                
        except Exception as e:
            logger.error(f"支付宝退款查询失败: {str(e)}")
            return RefundResult(
                success=False,
                message=f"退款查询失败: {str(e)}"
            )
    
    async def verify_callback(
        self,
        callback_data: Dict[str, Any],
        signature: str
    ) -> bool:
        """验证支付宝回调签名"""
        try:
            # 移除签名和签名类型参数
            params = callback_data.copy()
            params.pop('sign', None)
            params.pop('sign_type', None)
            
            # 生成待签名字符串
            sign_string = self._build_sign_string(params)
            
            # 验证签名
            return self._verify_sign(sign_string, signature)
            
        except Exception as e:
            logger.error(f"支付宝签名验证失败: {str(e)}")
            return False
    
    def parse_callback_data(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析支付宝回调数据"""
        return {
            "trade_no": callback_data.get("trade_no"),
            "out_trade_no": callback_data.get("out_trade_no"),
            "status": self._convert_trade_status(callback_data.get("trade_status")),
            "amount": Decimal(callback_data.get("total_amount", "0")),
            "paid_at": self._parse_datetime(callback_data.get("gmt_payment")),
            "buyer_id": callback_data.get("buyer_id"),
            "raw_data": callback_data
        }
    
    async def close_payment(self, out_trade_no: str) -> PaymentResult:
        """关闭支付宝支付"""
        try:
            biz_content = {
                "out_trade_no": out_trade_no
            }
            
            params = {
                "app_id": self.app_id,
                "method": "alipay.trade.close",
                "charset": "utf-8",
                "sign_type": self.sign_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0",
                "biz_content": json.dumps(biz_content)
            }
            
            sign = self._generate_sign(params)
            params['sign'] = sign
            
            response = await self._make_api_request(params)
            
            if response.get('code') == '10000':
                return PaymentResult(
                    success=True,
                    message="支付关闭成功",
                    out_trade_no=out_trade_no,
                    raw_data=response
                )
            else:
                return PaymentResult(
                    success=False,
                    message=response.get('msg', '支付关闭失败'),
                    error_code=response.get('code'),
                    error_message=response.get('sub_msg'),
                    raw_data=response
                )
                
        except Exception as e:
            logger.error(f"支付宝支付关闭失败: {str(e)}")
            return self._handle_network_error(e)
    
    def _get_product_code(self, payment_type: str) -> str:
        """获取产品码"""
        product_codes = {
            "web": "FAST_INSTANT_TRADE_PAY",
            "wap": "QUICK_WAP_WAY",
            "app": "QUICK_MSECURITY_PAY",
            "native": "FACE_TO_FACE_PAYMENT"
        }
        return product_codes.get(payment_type, "FAST_INSTANT_TRADE_PAY")
    
    def _convert_trade_status(self, trade_status: str) -> str:
        """转换交易状态"""
        status_map = {
            "WAIT_BUYER_PAY": "pending",
            "TRADE_SUCCESS": "paid",
            "TRADE_FINISHED": "paid",
            "TRADE_CLOSED": "failed",
            "TRADE_CANCELLED": "cancelled"
        }
        return status_map.get(trade_status, "unknown")
    
    def _parse_datetime(self, date_str: str) -> Optional[datetime]:
        """解析日期时间字符串"""
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
    
    async def _make_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送API请求"""
        try:
            response = await self._client.post(
                self.gateway,
                data=params,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            
            # 解析响应
            response_text = response.text
            
            # 提取JSON响应（支付宝返回格式特殊）
            import re
            pattern = r'"alipay_[^"]*_response":\s*({.*?})(?=,\s*"sign"|\s*}$)'
            match = re.search(pattern, response_text)
            
            if match:
                return json.loads(match.group(1))
            else:
                # 如果无法解析，返回原始响应
                return {"code": "PARSE_ERROR", "msg": "响应解析失败", "raw": response_text}
                
        except httpx.RequestError as e:
            raise AlipayAPIException(f"网络请求失败: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise AlipayAPIException(f"HTTP错误: {e.response.status_code}")
        except Exception as e:
            raise AlipayAPIException(f"API调用失败: {str(e)}")
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 构建待签名字符串
        sign_string = self._build_sign_string(params)
        
        # 使用RSA私钥签名（这里简化处理，实际应使用RSA库）
        # 在真实环境中，应该使用 cryptography 库进行RSA签名
        import hashlib
        return hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    
    def _build_sign_string(self, params: Dict[str, Any]) -> str:
        """构建待签名字符串"""
        # 过滤空值并排序
        filtered_params = {k: v for k, v in params.items() if v is not None and v != ''}
        sorted_params = sorted(filtered_params.items())
        
        # 构建签名字符串
        sign_list = []
        for key, value in sorted_params:
            if key not in ['sign', 'sign_type']:
                sign_list.append(f"{key}={value}")
        
        return "&".join(sign_list)
    
    def _verify_sign(self, sign_string: str, signature: str) -> bool:
        """验证签名"""
        # 这里简化处理，实际应使用RSA公钥验证
        # 在真实环境中，应该使用 cryptography 库进行RSA签名验证
        import hashlib
        expected_sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
        return expected_sign == signature
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
