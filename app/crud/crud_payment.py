from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from app.core.db import get_db_or_supabase
from app.schemas.payment_schema import (
    OrderCreate, OrderUpdate, OrderQuery,
    PaymentCreate, PaymentUpdate, PaymentQuery,
    RefundCreate, RefundUpdate, RefundQuery,
    PaymentStatus, OrderStatus, RefundStatus
)
from app.core.payment_exceptions import (
    OrderNotFoundException, PaymentNotFoundException, 
    DatabaseException, PaymentErrorCode
)

logger = logging.getLogger(__name__)


# ================== 订单CRUD操作 ==================

async def create_order(
    db: Dict[str, Any],
    order_data: OrderCreate,
    user_id: int
) -> Dict[str, Any]:
    """创建订单"""
    try:
        # 获取服务信息
        service = await get_service_by_id(db, order_data.service_id)
        if not service:
            raise Exception(f"服务 {order_data.service_id} 不存在")
        
        # 计算订单金额
        unit_price = Decimal(str(service['price']))
        quantity = 1  # 默认数量为1
        total_price = unit_price * quantity
        
        # 生成订单号
        import uuid
        order_no = f"ORD{int(datetime.now().timestamp())}{uuid.uuid4().hex[:8]}"
        
        order_record = {
            "user_id": user_id,
            "service_id": order_data.service_id,
            "order_no": order_no,
            "service_title": service['title'],
            "service_description": service.get('description', ''),
            "unit_price": float(unit_price),
            "quantity": quantity,
            "total_price": float(total_price),
            "status": OrderStatus.PENDING.value,
            "notes": order_data.notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if 'supabase' in db:
            # Supabase实现
            result = db['supabase'].table('orders').insert(order_record).execute()
            if result.data:
                return result.data[0]
        else:
            # PostgreSQL实现
            query = """
                INSERT INTO orders (
                    user_id, service_id, order_no, service_title, service_description,
                    unit_price, quantity, total_price, status, notes, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING *
            """
            result = await db['connection'].fetchrow(
                query,
                user_id, order_data.service_id, order_no, service['title'],
                service.get('description', ''), float(unit_price), quantity,
                float(total_price), OrderStatus.PENDING.value, order_data.notes,
                datetime.utcnow(), datetime.utcnow()
            )
            return dict(result) if result else None
            
    except Exception as e:
        logger.error(f"创建订单失败: {str(e)}")
        raise DatabaseException(
            f"创建订单失败: {str(e)}",
            PaymentErrorCode.DATABASE_ERROR
        )


async def get_order_by_id(db: Dict[str, Any], order_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """根据ID获取订单"""
    try:
        if 'supabase' in db:
            # Supabase实现
            query = db['supabase'].table('orders').select('*').eq('id', order_id)
            if user_id:
                query = query.eq('user_id', user_id)
            result = query.execute()
            return result.data[0] if result.data else None
        else:
            # PostgreSQL实现
            query = "SELECT * FROM orders WHERE id = $1"
            params = [order_id]
            if user_id:
                query += " AND user_id = $2"
                params.append(user_id)
            
            result = await db['connection'].fetchrow(query, *params)
            return dict(result) if result else None
            
    except Exception as e:
        logger.error(f"获取订单失败: {str(e)}")
        return None


async def update_order_status(
    db: Dict[str, Any],
    order_id: int,
    status: OrderStatus,
    user_id: Optional[int] = None
) -> bool:
    """更新订单状态"""
    try:
        if 'supabase' in db:
            # Supabase实现
            query = db['supabase'].table('orders').update({
                'status': status.value,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', order_id)
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.execute()
            return len(result.data) > 0
        else:
            # PostgreSQL实现
            query = "UPDATE orders SET status = $1, updated_at = $2 WHERE id = $3"
            params = [status.value, datetime.utcnow(), order_id]
            
            if user_id:
                query += " AND user_id = $4"
                params.append(user_id)
            
            result = await db['connection'].execute(query, *params)
            return result == "UPDATE 1"
            
    except Exception as e:
        logger.error(f"更新订单状态失败: {str(e)}")
        return False


async def get_orders_by_user(
    db: Dict[str, Any],
    user_id: int,
    query_params: OrderQuery
) -> Tuple[List[Dict[str, Any]], int]:
    """获取用户订单列表"""
    try:
        # 构建查询条件
        conditions = ["user_id = $1"]
        params = [user_id]
        param_count = 1
        
        if query_params.service_id:
            param_count += 1
            conditions.append(f"service_id = ${param_count}")
            params.append(query_params.service_id)
        
        if query_params.status:
            param_count += 1
            conditions.append(f"status = ${param_count}")
            params.append(query_params.status.value)
        
        if query_params.start_date:
            param_count += 1
            conditions.append(f"created_at >= ${param_count}")
            params.append(query_params.start_date)
        
        if query_params.end_date:
            param_count += 1
            conditions.append(f"created_at <= ${param_count}")
            params.append(query_params.end_date)
        
        where_clause = " AND ".join(conditions)
        
        if 'supabase' in db:
            # Supabase实现
            query_builder = db['supabase'].table('orders').select('*')
            
            # 添加过滤条件
            query_builder = query_builder.eq('user_id', user_id)
            if query_params.service_id:
                query_builder = query_builder.eq('service_id', query_params.service_id)
            if query_params.status:
                query_builder = query_builder.eq('status', query_params.status.value)
            if query_params.start_date:
                query_builder = query_builder.gte('created_at', query_params.start_date.isoformat())
            if query_params.end_date:
                query_builder = query_builder.lte('created_at', query_params.end_date.isoformat())
            
            # 分页
            offset = (query_params.page - 1) * query_params.page_size
            query_builder = query_builder.range(offset, offset + query_params.page_size - 1)
            query_builder = query_builder.order('created_at', desc=True)
            
            result = query_builder.execute()
            orders = result.data or []
            
            # 获取总数
            count_result = db['supabase'].table('orders').select('id', count='exact').eq('user_id', user_id).execute()
            total = count_result.count or 0
            
            return orders, total
        else:
            # PostgreSQL实现
            # 获取订单列表
            offset = (query_params.page - 1) * query_params.page_size
            orders_query = f"""
                SELECT * FROM orders 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_count + 1} OFFSET ${param_count + 2}
            """
            params.extend([query_params.page_size, offset])
            
            orders = await db['connection'].fetch(orders_query, *params)
            
            # 获取总数
            count_query = f"SELECT COUNT(*) FROM orders WHERE {where_clause}"
            count_params = params[:-2]  # 移除LIMIT和OFFSET参数
            total = await db['connection'].fetchval(count_query, *count_params)
            
            return [dict(order) for order in orders], total
            
    except Exception as e:
        logger.error(f"获取订单列表失败: {str(e)}")
        return [], 0


# ================== 支付CRUD操作 ==================

async def create_payment(
    db: Dict[str, Any],
    order_id: int,
    payment_data: PaymentCreate,
    user_id: int
) -> Dict[str, Any]:
    """创建支付记录"""
    try:
        # 生成支付单号
        import uuid
        out_trade_no = f"PP{int(datetime.now().timestamp())}{uuid.uuid4().hex[:8]}"
        
        # 计算过期时间
        expired_at = datetime.utcnow() + timedelta(minutes=30)
        
        payment_record = {
            "order_id": order_id,
            "user_id": user_id,
            "out_trade_no": out_trade_no,
            "amount": float(payment_data.amount),
            "payment_method": payment_data.payment_method.value,
            "payment_type": payment_data.payment_type.value,
            "status": PaymentStatus.PENDING.value,
            "expired_at": expired_at,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if 'supabase' in db:
            # Supabase实现
            result = db['supabase'].table('payments').insert(payment_record).execute()
            if result.data:
                return result.data[0]
        else:
            # PostgreSQL实现
            query = """
                INSERT INTO payments (
                    order_id, user_id, out_trade_no, amount, payment_method,
                    payment_type, status, expired_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
            """
            result = await db['connection'].fetchrow(
                query,
                order_id, user_id, out_trade_no, float(payment_data.amount),
                payment_data.payment_method.value, payment_data.payment_type.value,
                PaymentStatus.PENDING.value, expired_at, datetime.utcnow(), datetime.utcnow()
            )
            return dict(result) if result else None
            
    except Exception as e:
        logger.error(f"创建支付记录失败: {str(e)}")
        raise DatabaseException(
            f"创建支付记录失败: {str(e)}",
            PaymentErrorCode.DATABASE_ERROR
        )


async def get_payment_by_id(db: Dict[str, Any], payment_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """根据ID获取支付记录"""
    try:
        if 'supabase' in db:
            # Supabase实现
            query = db['supabase'].table('payments').select('*').eq('id', payment_id)
            if user_id:
                query = query.eq('user_id', user_id)
            result = query.execute()
            return result.data[0] if result.data else None
        else:
            # PostgreSQL实现
            query = "SELECT * FROM payments WHERE id = $1"
            params = [payment_id]
            if user_id:
                query += " AND user_id = $2"
                params.append(user_id)
            
            result = await db['connection'].fetchrow(query, *params)
            return dict(result) if result else None
            
    except Exception as e:
        logger.error(f"获取支付记录失败: {str(e)}")
        return None


async def get_payment_by_out_trade_no(db: Dict[str, Any], out_trade_no: str) -> Optional[Dict[str, Any]]:
    """根据商户订单号获取支付记录"""
    try:
        if 'supabase' in db:
            # Supabase实现
            result = db['supabase'].table('payments').select('*').eq('out_trade_no', out_trade_no).execute()
            return result.data[0] if result.data else None
        else:
            # PostgreSQL实现
            query = "SELECT * FROM payments WHERE out_trade_no = $1"
            result = await db['connection'].fetchrow(query, out_trade_no)
            return dict(result) if result else None
            
    except Exception as e:
        logger.error(f"获取支付记录失败: {str(e)}")
        return None


async def update_payment_status(
    db: Dict[str, Any],
    payment_id: int,
    status: PaymentStatus,
    trade_no: Optional[str] = None,
    paid_at: Optional[datetime] = None,
    **kwargs
) -> bool:
    """更新支付状态"""
    try:
        update_data = {
            'status': status.value,
            'updated_at': datetime.utcnow()
        }
        
        if trade_no:
            update_data['trade_no'] = trade_no
        
        if paid_at:
            update_data['paid_at'] = paid_at
        
        # 添加其他字段
        for key, value in kwargs.items():
            if value is not None:
                update_data[key] = value
        
        if 'supabase' in db:
            # Supabase实现
            result = db['supabase'].table('payments').update(update_data).eq('id', payment_id).execute()
            return len(result.data) > 0
        else:
            # PostgreSQL实现
            set_clauses = []
            params = []
            param_count = 0
            
            for key, value in update_data.items():
                param_count += 1
                set_clauses.append(f"{key} = ${param_count}")
                params.append(value if not isinstance(value, datetime) else value else value)
            
            param_count += 1
            params.append(payment_id)
            
            query = f"UPDATE payments SET {', '.join(set_clauses)} WHERE id = ${param_count}"
            result = await db['connection'].execute(query, *params)
            return result == "UPDATE 1"
            
    except Exception as e:
        logger.error(f"更新支付状态失败: {str(e)}")
        return False


async def get_payments_by_user(
    db: Dict[str, Any],
    user_id: int,
    query_params: PaymentQuery
) -> Tuple[List[Dict[str, Any]], int]:
    """获取用户支付记录列表"""
    try:
        # 构建查询条件
        conditions = ["user_id = $1"]
        params = [user_id]
        param_count = 1
        
        if query_params.order_id:
            param_count += 1
            conditions.append(f"order_id = ${param_count}")
            params.append(query_params.order_id)
        
        if query_params.payment_method:
            param_count += 1
            conditions.append(f"payment_method = ${param_count}")
            params.append(query_params.payment_method.value)
        
        if query_params.status:
            param_count += 1
            conditions.append(f"status = ${param_count}")
            params.append(query_params.status.value)
        
        if query_params.start_date:
            param_count += 1
            conditions.append(f"created_at >= ${param_count}")
            params.append(query_params.start_date)
        
        if query_params.end_date:
            param_count += 1
            conditions.append(f"created_at <= ${param_count}")
            params.append(query_params.end_date)
        
        where_clause = " AND ".join(conditions)
        
        if 'supabase' in db:
            # Supabase实现
            query_builder = db['supabase'].table('payments').select('*')
            
            # 添加过滤条件
            query_builder = query_builder.eq('user_id', user_id)
            if query_params.order_id:
                query_builder = query_builder.eq('order_id', query_params.order_id)
            if query_params.payment_method:
                query_builder = query_builder.eq('payment_method', query_params.payment_method.value)
            if query_params.status:
                query_builder = query_builder.eq('status', query_params.status.value)
            if query_params.start_date:
                query_builder = query_builder.gte('created_at', query_params.start_date.isoformat())
            if query_params.end_date:
                query_builder = query_builder.lte('created_at', query_params.end_date.isoformat())
            
            # 分页
            offset = (query_params.page - 1) * query_params.page_size
            query_builder = query_builder.range(offset, offset + query_params.page_size - 1)
            query_builder = query_builder.order('created_at', desc=True)
            
            result = query_builder.execute()
            payments = result.data or []
            
            # 获取总数
            count_result = db['supabase'].table('payments').select('id', count='exact').eq('user_id', user_id).execute()
            total = count_result.count or 0
            
            return payments, total
        else:
            # PostgreSQL实现
            # 获取支付列表
            offset = (query_params.page - 1) * query_params.page_size
            payments_query = f"""
                SELECT * FROM payments 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_count + 1} OFFSET ${param_count + 2}
            """
            params.extend([query_params.page_size, offset])
            
            payments = await db['connection'].fetch(payments_query, *params)
            
            # 获取总数
            count_query = f"SELECT COUNT(*) FROM payments WHERE {where_clause}"
            count_params = params[:-2]  # 移除LIMIT和OFFSET参数
            total = await db['connection'].fetchval(count_query, *count_params)
            
            return [dict(payment) for payment in payments], total
            
    except Exception as e:
        logger.error(f"获取支付列表失败: {str(e)}")
        return [], 0


async def get_pending_payments(db: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
    """获取待处理的支付记录（用于状态同步）"""
    try:
        # 获取创建时间超过5分钟且仍为pending状态的支付记录
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        if 'supabase' in db:
            # Supabase实现
            result = db['supabase'].table('payments').select('*').eq('status', PaymentStatus.PENDING.value).lt('created_at', cutoff_time.isoformat()).limit(limit).execute()
            return result.data or []
        else:
            # PostgreSQL实现
            query = """
                SELECT * FROM payments 
                WHERE status = $1 AND created_at < $2
                ORDER BY created_at ASC
                LIMIT $3
            """
            payments = await db['connection'].fetch(query, PaymentStatus.PENDING.value, cutoff_time, limit)
            return [dict(payment) for payment in payments]
            
    except Exception as e:
        logger.error(f"获取待处理支付记录失败: {str(e)}")
        return []


# ================== 退款CRUD操作 ==================

async def create_refund(
    db: Dict[str, Any],
    payment_id: int,
    refund_data: RefundCreate,
    user_id: int
) -> Dict[str, Any]:
    """创建退款记录"""
    try:
        # 生成退款单号
        import uuid
        out_refund_no = f"RF{int(datetime.now().timestamp())}{uuid.uuid4().hex[:8]}"
        
        refund_record = {
            "payment_id": payment_id,
            "user_id": user_id,
            "out_refund_no": out_refund_no,
            "refund_amount": float(refund_data.refund_amount),
            "refund_reason": refund_data.refund_reason,
            "refund_type": refund_data.refund_type,
            "status": RefundStatus.PROCESSING.value,
            "operator_notes": refund_data.operator_notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if 'supabase' in db:
            # Supabase实现
            result = db['supabase'].table('refunds').insert(refund_record).execute()
            if result.data:
                return result.data[0]
        else:
            # PostgreSQL实现
            query = """
                INSERT INTO refunds (
                    payment_id, user_id, out_refund_no, refund_amount, refund_reason,
                    refund_type, status, operator_notes, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
            """
            result = await db['connection'].fetchrow(
                query,
                payment_id, user_id, out_refund_no, float(refund_data.refund_amount),
                refund_data.refund_reason, refund_data.refund_type,
                RefundStatus.PROCESSING.value, refund_data.operator_notes,
                datetime.utcnow(), datetime.utcnow()
            )
            return dict(result) if result else None
            
    except Exception as e:
        logger.error(f"创建退款记录失败: {str(e)}")
        raise DatabaseException(
            f"创建退款记录失败: {str(e)}",
            PaymentErrorCode.DATABASE_ERROR
        )


# ================== 辅助函数 ==================

async def get_service_by_id(db: Dict[str, Any], service_id: int) -> Optional[Dict[str, Any]]:
    """获取服务信息"""
    try:
        if 'supabase' in db:
            # Supabase实现
            result = db['supabase'].table('services').select('*').eq('id', service_id).execute()
            return result.data[0] if result.data else None
        else:
            # PostgreSQL实现
            query = "SELECT * FROM services WHERE id = $1"
            result = await db['connection'].fetchrow(query, service_id)
            return dict(result) if result else None
            
    except Exception as e:
        logger.error(f"获取服务信息失败: {str(e)}")
        return None


async def get_payment_statistics(
    db: Dict[str, Any],
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """获取支付统计信息"""
    try:
        conditions = []
        params = []
        param_count = 0
        
        if user_id:
            param_count += 1
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)
        
        if start_date:
            param_count += 1
            conditions.append(f"created_at >= ${param_count}")
            params.append(start_date)
        
        if end_date:
            param_count += 1
            conditions.append(f"created_at <= ${param_count}")
            params.append(end_date)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        if 'supabase' in db:
            # Supabase实现 - 简化统计
            query_builder = db['supabase'].table('payments').select('*')
            if user_id:
                query_builder = query_builder.eq('user_id', user_id)
            if start_date:
                query_builder = query_builder.gte('created_at', start_date.isoformat())
            if end_date:
                query_builder = query_builder.lte('created_at', end_date.isoformat())
            
            result = query_builder.execute()
            payments = result.data or []
            
            # 手动统计
            total_payments = len(payments)
            total_amount = sum(Decimal(str(p.get('amount', 0))) for p in payments)
            success_count = len([p for p in payments if p.get('status') == 'paid'])
            success_rate = (success_count / total_payments * 100) if total_payments > 0 else 0
            
            return {
                "total_payments": total_payments,
                "total_amount": total_amount,
                "success_rate": success_rate,
                "avg_amount": total_amount / total_payments if total_payments > 0 else Decimal('0'),
                "success_count": success_count
            }
        else:
            # PostgreSQL实现
            query = f"""
                SELECT 
                    COUNT(*) as total_payments,
                    COALESCE(SUM(amount), 0) as total_amount,
                    COUNT(CASE WHEN status = 'paid' THEN 1 END) as success_count,
                    COALESCE(AVG(amount), 0) as avg_amount
                FROM payments 
                WHERE {where_clause}
            """
            
            result = await db['connection'].fetchrow(query, *params)
            
            if result:
                total_payments = result['total_payments']
                success_rate = (result['success_count'] / total_payments * 100) if total_payments > 0 else 0
                
                return {
                    "total_payments": total_payments,
                    "total_amount": Decimal(str(result['total_amount'])),
                    "success_rate": success_rate,
                    "avg_amount": Decimal(str(result['avg_amount'])),
                    "success_count": result['success_count']
                }
            
            return {
                "total_payments": 0,
                "total_amount": Decimal('0'),
                "success_rate": 0.0,
                "avg_amount": Decimal('0'),
                "success_count": 0
            }
            
    except Exception as e:
        logger.error(f"获取支付统计失败: {str(e)}")
        return {
            "total_payments": 0,
            "total_amount": Decimal('0'),
            "success_rate": 0.0,
            "avg_amount": Decimal('0'),
            "success_count": 0
        }
