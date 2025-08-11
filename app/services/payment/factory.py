from typing import Dict, Any, Optional, List
from app.services.payment.base_provider import BasePaymentProvider
from app.services.payment.alipay_provider import AlipayProvider
from app.services.payment.wechat_provider import WechatProvider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class PaymentFactory:
    """支付提供商工厂类"""
    
    _providers: Dict[str, BasePaymentProvider] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """初始化所有支付提供商"""
        if cls._initialized:
            return
        
        try:
            # 初始化支付宝
            if hasattr(settings, 'ALIPAY_APP_ID') and settings.ALIPAY_APP_ID:
                alipay_config = {
                    'app_id': settings.ALIPAY_APP_ID,
                    'private_key': settings.ALIPAY_PRIVATE_KEY,
                    'public_key': settings.ALIPAY_PUBLIC_KEY,
                    'gateway': getattr(settings, 'ALIPAY_GATEWAY', 'https://openapi.alipay.com/gateway.do'),
                    'sign_type': getattr(settings, 'ALIPAY_SIGN_TYPE', 'RSA2'),
                    'debug': getattr(settings, 'ALIPAY_DEBUG', False)
                }
                cls._providers['alipay'] = AlipayProvider(alipay_config)
                logger.info("支付宝支付提供商初始化成功")
            else:
                logger.warning("支付宝配置不完整，跳过初始化")
            
            # 初始化微信支付
            if hasattr(settings, 'WECHAT_MCHID') and settings.WECHAT_MCHID:
                wechat_config = {
                    'mchid': settings.WECHAT_MCHID,
                    'appid': settings.WECHAT_APPID,
                    'private_key': settings.WECHAT_PRIVATE_KEY,
                    'cert_serial_no': settings.WECHAT_CERT_SERIAL_NO,
                    'api_v3_key': settings.WECHAT_API_V3_KEY,
                    'debug': getattr(settings, 'WECHAT_DEBUG', False)
                }
                cls._providers['wechat'] = WechatProvider(wechat_config)
                logger.info("微信支付提供商初始化成功")
            else:
                logger.warning("微信支付配置不完整，跳过初始化")
            
            cls._initialized = True
            logger.info(f"支付工厂初始化完成，可用提供商: {list(cls._providers.keys())}")
            
        except Exception as e:
            logger.error(f"支付工厂初始化失败: {str(e)}")
            raise
    
    @classmethod
    def get_provider(cls, provider_name: str) -> Optional[BasePaymentProvider]:
        """获取支付提供商实例"""
        if not cls._initialized:
            cls.initialize()
        
        provider = cls._providers.get(provider_name.lower())
        if not provider:
            logger.warning(f"未找到支付提供商: {provider_name}")
            return None
        
        return provider
    
    @classmethod
    def get_available_methods(cls) -> List[str]:
        """获取所有可用的支付方式"""
        if not cls._initialized:
            cls.initialize()
        
        return list(cls._providers.keys())
    
    @classmethod
    def is_method_available(cls, method: str) -> bool:
        """检查支付方式是否可用"""
        if not cls._initialized:
            cls.initialize()
        
        return method.lower() in cls._providers
    
    @classmethod
    async def health_check_all(cls) -> Dict[str, Any]:
        """检查所有支付提供商的健康状态"""
        if not cls._initialized:
            cls.initialize()
        
        health_status = {
            "overall_status": "healthy",
            "providers": {},
            "available_methods": list(cls._providers.keys()),
            "total_providers": len(cls._providers)
        }
        
        unhealthy_count = 0
        
        for name, provider in cls._providers.items():
            try:
                provider_health = await provider.health_check()
                health_status["providers"][name] = provider_health
                
                if provider_health.get("status") != "healthy":
                    unhealthy_count += 1
                    
            except Exception as e:
                health_status["providers"][name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "provider": name
                }
                unhealthy_count += 1
        
        # 判断整体健康状态
        if unhealthy_count == 0:
            health_status["overall_status"] = "healthy"
        elif unhealthy_count < len(cls._providers):
            health_status["overall_status"] = "degraded"
        else:
            health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    @classmethod
    def get_provider_config(cls, provider_name: str) -> Optional[Dict[str, Any]]:
        """获取支付提供商配置信息（敏感信息已脱敏）"""
        provider = cls.get_provider(provider_name)
        if not provider:
            return None
        
        config = provider.config.copy()
        
        # 脱敏处理
        sensitive_keys = ['private_key', 'public_key', 'api_v3_key', 'cert_serial_no']
        for key in sensitive_keys:
            if key in config:
                value = config[key]
                if isinstance(value, str) and len(value) > 8:
                    config[key] = value[:4] + '*' * (len(value) - 8) + value[-4:]
                else:
                    config[key] = '***'
        
        return {
            "provider": provider_name,
            "provider_class": provider.__class__.__name__,
            "config": config
        }
    
    @classmethod
    def reload_providers(cls):
        """重新加载所有支付提供商"""
        logger.info("开始重新加载支付提供商...")
        
        # 清空现有提供商
        cls._providers.clear()
        cls._initialized = False
        
        # 重新初始化
        cls.initialize()
        
        logger.info("支付提供商重新加载完成")
    
    @classmethod
    def register_provider(cls, name: str, provider: BasePaymentProvider):
        """注册自定义支付提供商"""
        if not isinstance(provider, BasePaymentProvider):
            raise ValueError("提供商必须继承自 BasePaymentProvider")
        
        cls._providers[name.lower()] = provider
        logger.info(f"自定义支付提供商 {name} 注册成功")
    
    @classmethod
    def unregister_provider(cls, name: str):
        """注销支付提供商"""
        if name.lower() in cls._providers:
            del cls._providers[name.lower()]
            logger.info(f"支付提供商 {name} 已注销")
        else:
            logger.warning(f"支付提供商 {name} 不存在，无法注销")


# 全局工厂实例
payment_factory = PaymentFactory()


# 便捷函数
def get_payment_provider(method: str) -> Optional[BasePaymentProvider]:
    """获取支付提供商的便捷函数"""
    return PaymentFactory.get_provider(method)


def get_available_payment_methods() -> List[str]:
    """获取可用支付方式的便捷函数"""
    return PaymentFactory.get_available_methods()


async def check_payment_health() -> Dict[str, Any]:
    """检查支付系统健康状态的便捷函数"""
    return await PaymentFactory.health_check_all()
