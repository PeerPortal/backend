from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import PlainTextResponse
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from app.api.deps import get_current_user, get_db_or_supabase, require_admin_role
from app.schemas.user_schema import UserRead
from app.schemas.payment_schema import (
    OrderCreate, OrderRead, OrderUpdate, OrderQuery, OrderListResponse,
    PaymentCreate, PaymentRead, PaymentResponse, PaymentQuery, PaymentListResponse,
    RefundCreate, RefundRead, RefundQuery, RefundListResponse,
    PaymentStatsRead, APIResponse, ErrorResponse
)
from app.crud import crud_payment
from app.services.payment.factory import PaymentFactory
from app.core.payment_exceptions import (
    PaymentException, OrderNotFoundException, PaymentNotFoundException,
    OrderAlreadyPaidException, PaymentAmountMismatchException
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ================== 订单相关路由 ==================

@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    current_user: UserRead = Depends(get_current_user),
    order_in: OrderCreate
):
    """
    创建订单
    
    - **service_id**: 服务ID
    - **notes**: 订单备注（可选）
    - **payment_method**: 首选支付方式（可选）
    """
    try:
        order = await crud_payment.create_order(db, order_in, current_user.id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单创建失败"
            )
        return order
    except PaymentException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"创建订单失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单失败: {str(e)}"
        )


@router.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    current_user: UserRead = Depends(get_current_user),
    order_id: int
):
    """获取订单详情"""
    try:
        order = await crud_payment.get_order_by_id(db, order_id, current_user.id)
        if not order:
            raise OrderNotFoundException(order_id)
        return order
    except PaymentException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"获取订单失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单失败: {str(e)}"
        )


@router.get("/orders", response_model=OrderListResponse)
async def get_orders(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    current_user: UserRead = Depends(get_current_user),
    query_params: OrderQuery = Depends()
):
    """获取用户订单列表"""
    try:
        orders, total = await crud_payment.get_orders_by_user(db, current_user.id, query_params)
        
        total_pages = (total + query_params.page_size - 1) // query_params.page_size
        
        return OrderListResponse(
            orders=orders,
            total=total,
            page=query_params.page,
            page_size=query_params.page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"获取订单列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )


# ================== 支付相关路由 ==================

@router.post("/orders/{order_id}/pay", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    current_user: UserRead = Depends(get_current_user),
    order_id: int,
    payment_in: PaymentCreate,
    request: Request
):
    """
    创建支付
    
    - **payment_method**: 支付方式 (alipay/wechat)
    - **payment_type**: 支付类型 (web/wap/app/native/jsapi)
    - **return_url**: 支付成功返回URL（可选）
    - **notify_url**: 异步通知URL（可选，系统会自动设置）
    """
    try:
        # 获取订单信息
        order = await crud_payment.get_order_by_id(db, order_id, current_user.id)
        if not order:
            raise OrderNotFoundException(order_id)
        
        # 检查订单状态
        if order['status'] == 'paid':
            raise OrderAlreadyPaidException(order_id)
        
        # 验证支付金额
        if payment_in.amount != order['total_price']:
            raise PaymentAmountMismatchException(
                expected=float(order['total_price']),
                actual=float(payment_in.amount)
            )
        
        # 检查支付方式是否可用
        if not PaymentFactory.is_method_available(payment_in.payment_method.value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"支付方式 {payment_in.payment_method.value} 不可用"
            )
        
        # 创建支付记录
        payment = await crud_payment.create_payment(db, order_id, payment_in, current_user.id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="支付记录创建失败"
            )
        
        # 获取支付提供商
        provider = PaymentFactory.get_provider(payment_in.payment_method.value)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="支付提供商不可用"
            )
        
        # 设置通知URL
        notify_url = payment_in.notify_url or f"{request.base_url}api/v2/payments/callback/{payment_in.payment_method.value}/{payment['id']}"
        
        # 获取客户端IP
        client_ip = payment_in.client_ip or request.client.host
        
        # 调用支付提供商创建支付
        payment_result = await provider.create_payment(
            out_trade_no=payment['out_trade_no'],
            total_amount=payment_in.amount,
            subject=order['service_title'],
            payment_type=payment_in.payment_type.value,
            return_url=payment_in.return_url,
            notify_url=notify_url,
            client_ip=client_ip
        )
        
        if not payment_result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"支付创建失败: {payment_result.message}"
            )
        
        # 更新支付记录
        update_data = {}
        if payment_result.payment_url:
            update_data['payment_url'] = payment_result.payment_url
        if payment_result.qr_code_url:
            update_data['qr_code_url'] = payment_result.qr_code_url
        if payment_result.code_url:
            update_data['code_url'] = payment_result.code_url
        if payment_result.prepay_id:
            update_data['prepay_id'] = payment_result.prepay_id
        
        if update_data:
            await crud_payment.update_payment_status(
                db, payment['id'], payment['status'], **update_data
            )
        
        # 构建响应
        response = PaymentResponse(
            payment_id=payment['id'],
            out_trade_no=payment['out_trade_no'],
            payment_method=payment_in.payment_method,
            payment_type=payment_in.payment_type,
            amount=payment_in.amount,
            status=payment['status'],
            payment_url=payment_result.payment_url,
            qr_code_url=payment_result.qr_code_url,
            code_url=payment_result.code_url,
            prepay_id=payment_result.prepay_id,
            expired_at=payment.get('expired_at')
        )
        
        return response
        
    except PaymentException as e:
        raise e.to_http_exception()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建支付失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建支付失败: {str(e)}"
        )


@router.get("/payments/{payment_id}", response_model=PaymentRead)
async def get_payment(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    current_user: UserRead = Depends(get_current_user),
    payment_id: int
):
    """获取支付详情"""
    try:
        payment = await crud_payment.get_payment_by_id(db, payment_id, current_user.id)
        if not payment:
            raise PaymentNotFoundException(payment_id)
        return payment
    except PaymentException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"获取支付记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取支付记录失败: {str(e)}"
        )


@router.get("/payments", response_model=PaymentListResponse)
async def get_payments(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    current_user: UserRead = Depends(get_current_user),
    query_params: PaymentQuery = Depends()
):
    """获取用户支付记录列表"""
    try:
        payments, total = await crud_payment.get_payments_by_user(db, current_user.id, query_params)
        
        total_pages = (total + query_params.page_size - 1) // query_params.page_size
        
        return PaymentListResponse(
            payments=payments,
            total=total,
            page=query_params.page,
            page_size=query_params.page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"获取支付列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取支付列表失败: {str(e)}"
        )


@router.post("/payments/{payment_id}/cancel", response_model=APIResponse)
async def cancel_payment(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    current_user: UserRead = Depends(get_current_user),
    payment_id: int
):
    """取消支付"""
    try:
        payment = await crud_payment.get_payment_by_id(db, payment_id, current_user.id)
        if not payment:
            raise PaymentNotFoundException(payment_id)
        
        if payment['status'] != 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能取消待支付的订单"
            )
        
        # 更新支付状态
        success = await crud_payment.update_payment_status(
            db, payment_id, 'cancelled'
        )
        
        if success:
            # 可以调用支付提供商关闭支付
            provider = PaymentFactory.get_provider(payment['payment_method'])
            if provider:
                await provider.close_payment(payment['out_trade_no'])
            
            return APIResponse(message="支付已取消")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="取消支付失败"
            )
            
    except PaymentException as e:
        raise e.to_http_exception()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消支付失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消支付失败: {str(e)}"
        )


# ================== 支付回调路由 ==================

@router.post("/callback/alipay/{payment_id}", response_class=PlainTextResponse)
async def alipay_callback(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    payment_id: int,
    request: Request
):
    """支付宝支付回调"""
    try:
        # 获取回调数据
        form_data = await request.form()
        callback_data = dict(form_data)
        
        # 获取支付记录
        payment = await crud_payment.get_payment_by_id(db, payment_id)
        if not payment:
            logger.warning(f"支付记录 {payment_id} 不存在")
            return "fail"
        
        # 获取支付提供商
        provider = PaymentFactory.get_provider("alipay")
        if not provider:
            logger.error("支付宝提供商不可用")
            return "fail"
        
        # 验证签名
        signature = callback_data.get('sign', '')
        is_valid = await provider.verify_callback(callback_data, signature)
        if not is_valid:
            logger.warning(f"支付宝回调签名验证失败: {payment_id}")
            return "fail"
        
        # 解析回调数据
        parsed_data = provider.parse_callback_data(callback_data)
        
        # 验证订单号
        if parsed_data['out_trade_no'] != payment['out_trade_no']:
            logger.warning(f"订单号不匹配: {parsed_data['out_trade_no']} != {payment['out_trade_no']}")
            return "fail"
        
        # 更新支付状态
        if parsed_data['status'] == 'paid':
            success = await crud_payment.update_payment_status(
                db,
                payment_id,
                'paid',
                trade_no=parsed_data['trade_no'],
                paid_at=parsed_data['paid_at'] or datetime.utcnow()
            )
            
            if success:
                # 更新订单状态
                await crud_payment.update_order_status(db, payment['order_id'], 'paid')
                logger.info(f"支付宝支付成功: {payment_id}")
            else:
                logger.error(f"更新支付状态失败: {payment_id}")
                return "fail"
        
        return "success"
        
    except Exception as e:
        logger.error(f"支付宝回调处理失败: {str(e)}")
        return "fail"


@router.post("/callback/wechat/{payment_id}", response_class=PlainTextResponse)
async def wechat_callback(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    payment_id: int,
    request: Request
):
    """微信支付回调"""
    try:
        # 获取回调数据
        callback_data = await request.json()
        
        # 获取支付记录
        payment = await crud_payment.get_payment_by_id(db, payment_id)
        if not payment:
            logger.warning(f"支付记录 {payment_id} 不存在")
            return '{"code":"FAIL","message":"支付记录不存在"}'
        
        # 获取支付提供商
        provider = PaymentFactory.get_provider("wechat")
        if not provider:
            logger.error("微信支付提供商不可用")
            return '{"code":"FAIL","message":"支付提供商不可用"}'
        
        # 验证签名
        signature = request.headers.get('Wechatpay-Signature', '')
        is_valid = await provider.verify_callback(callback_data, signature)
        if not is_valid:
            logger.warning(f"微信支付回调签名验证失败: {payment_id}")
            return '{"code":"FAIL","message":"签名验证失败"}'
        
        # 解析回调数据
        parsed_data = provider.parse_callback_data(callback_data)
        
        # 验证订单号
        if parsed_data['out_trade_no'] != payment['out_trade_no']:
            logger.warning(f"订单号不匹配: {parsed_data['out_trade_no']} != {payment['out_trade_no']}")
            return '{"code":"FAIL","message":"订单号不匹配"}'
        
        # 更新支付状态
        if parsed_data['status'] == 'paid':
            success = await crud_payment.update_payment_status(
                db,
                payment_id,
                'paid',
                trade_no=parsed_data['trade_no'],
                paid_at=parsed_data['paid_at'] or datetime.utcnow()
            )
            
            if success:
                # 更新订单状态
                await crud_payment.update_order_status(db, payment['order_id'], 'paid')
                logger.info(f"微信支付成功: {payment_id}")
            else:
                logger.error(f"更新支付状态失败: {payment_id}")
                return '{"code":"FAIL","message":"状态更新失败"}'
        
        return '{"code":"SUCCESS","message":"成功"}'
        
    except Exception as e:
        logger.error(f"微信支付回调处理失败: {str(e)}")
        return '{"code":"FAIL","message":"处理失败"}'


# ================== 退款相关路由 ==================

@router.post("/payments/{payment_id}/refund", response_model=RefundRead, status_code=status.HTTP_201_CREATED)
async def create_refund(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    current_user: UserRead = Depends(get_current_user),
    payment_id: int,
    refund_in: RefundCreate
):
    """创建退款"""
    try:
        # 获取支付记录
        payment = await crud_payment.get_payment_by_id(db, payment_id, current_user.id)
        if not payment:
            raise PaymentNotFoundException(payment_id)
        
        if payment['status'] != 'paid':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能对已支付的订单申请退款"
            )
        
        # 验证退款金额
        if refund_in.refund_amount > payment['amount']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="退款金额不能超过支付金额"
            )
        
        # 创建退款记录
        refund = await crud_payment.create_refund(db, payment_id, refund_in, current_user.id)
        if not refund:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="退款记录创建失败"
            )
        
        # 调用支付提供商创建退款
        provider = PaymentFactory.get_provider(payment['payment_method'])
        if provider:
            refund_result = await provider.create_refund(
                out_trade_no=payment['out_trade_no'],
                trade_no=payment.get('trade_no'),
                refund_amount=refund_in.refund_amount,
                refund_reason=refund_in.refund_reason,
                out_refund_no=refund['out_refund_no']
            )
            
            if refund_result.success:
                # 更新退款记录
                await crud_payment.update_payment_status(
                    db, refund['id'], 'success',
                    refund_id=refund_result.refund_id,
                    processed_at=datetime.utcnow()
                )
                refund['status'] = 'success'
                refund['refund_id'] = refund_result.refund_id
                refund['processed_at'] = datetime.utcnow()
        
        return refund
        
    except PaymentException as e:
        raise e.to_http_exception()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建退款失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建退款失败: {str(e)}"
        )


# ================== 统计相关路由 ==================

@router.get("/stats", response_model=PaymentStatsRead)
async def get_payment_stats(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    current_user: UserRead = Depends(get_current_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """获取支付统计信息"""
    try:
        stats = await crud_payment.get_payment_statistics(
            db, current_user.id, start_date, end_date
        )
        
        return PaymentStatsRead(
            total_payments=stats['total_payments'],
            total_amount=stats['total_amount'],
            success_rate=stats['success_rate'],
            avg_amount=stats['avg_amount'],
            start_date=start_date,
            end_date=end_date
        )
        
    except Exception as e:
        logger.error(f"获取支付统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取支付统计失败: {str(e)}"
        )


# ================== 管理员路由 ==================

@router.get("/admin/stats", response_model=PaymentStatsRead, dependencies=[Depends(require_admin_role)])
async def get_admin_payment_stats(
    *,
    db: Dict[str, Any] = Depends(get_db_or_supabase),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """获取管理员支付统计信息"""
    try:
        stats = await crud_payment.get_payment_statistics(
            db, user_id=None, start_date=start_date, end_date=end_date
        )
        
        return PaymentStatsRead(
            total_payments=stats['total_payments'],
            total_amount=stats['total_amount'],
            success_rate=stats['success_rate'],
            avg_amount=stats['avg_amount'],
            start_date=start_date,
            end_date=end_date
        )
        
    except Exception as e:
        logger.error(f"获取管理员支付统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取管理员支付统计失败: {str(e)}"
        )


# ================== 健康检查路由 ==================

@router.get("/health")
async def payment_health_check():
    """支付系统健康检查"""
    try:
        health_status = await PaymentFactory.health_check_all()
        return health_status
    except Exception as e:
        logger.error(f"支付系统健康检查失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"支付系统健康检查失败: {str(e)}"
        )
