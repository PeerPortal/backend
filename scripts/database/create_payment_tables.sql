-- 支付系统数据库表结构
-- 创建时间: 2024-01-01
-- 说明: 支持支付宝、微信支付的完整支付系统

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_id BIGINT NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    order_no VARCHAR(64) NOT NULL UNIQUE,
    service_title VARCHAR(200) NOT NULL,
    service_description TEXT,
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    total_price DECIMAL(10,2) NOT NULL CHECK (total_price > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'cancelled', 'completed', 'refunded')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_orders_user_id (user_id),
    INDEX idx_orders_service_id (service_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_order_no (order_no),
    INDEX idx_orders_created_at (created_at)
);

-- 支付记录表
CREATE TABLE IF NOT EXISTS payments (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    out_trade_no VARCHAR(64) NOT NULL UNIQUE,
    trade_no VARCHAR(64),
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('alipay', 'wechat')),
    payment_type VARCHAR(20) NOT NULL DEFAULT 'web' CHECK (payment_type IN ('web', 'wap', 'app', 'native', 'jsapi')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed', 'cancelled', 'refunded', 'partial_refunded')),
    payment_url TEXT,
    qr_code_url TEXT,
    code_url TEXT,
    prepay_id VARCHAR(64),
    paid_at TIMESTAMP WITH TIME ZONE,
    expired_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_payments_order_id (order_id),
    INDEX idx_payments_user_id (user_id),
    INDEX idx_payments_out_trade_no (out_trade_no),
    INDEX idx_payments_trade_no (trade_no),
    INDEX idx_payments_status (status),
    INDEX idx_payments_payment_method (payment_method),
    INDEX idx_payments_created_at (created_at),
    INDEX idx_payments_paid_at (paid_at)
);

-- 退款记录表
CREATE TABLE IF NOT EXISTS refunds (
    id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    out_refund_no VARCHAR(64) NOT NULL UNIQUE,
    refund_id VARCHAR(64),
    refund_amount DECIMAL(10,2) NOT NULL CHECK (refund_amount > 0),
    refund_reason VARCHAR(200) NOT NULL,
    refund_type VARCHAR(20) NOT NULL DEFAULT 'partial' CHECK (refund_type IN ('full', 'partial')),
    status VARCHAR(20) NOT NULL DEFAULT 'processing' CHECK (status IN ('processing', 'success', 'failed')),
    processed_at TIMESTAMP WITH TIME ZONE,
    operator_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_refunds_payment_id (payment_id),
    INDEX idx_refunds_user_id (user_id),
    INDEX idx_refunds_out_refund_no (out_refund_no),
    INDEX idx_refunds_refund_id (refund_id),
    INDEX idx_refunds_status (status),
    INDEX idx_refunds_created_at (created_at)
);

-- 支付回调日志表（用于记录和调试回调）
CREATE TABLE IF NOT EXISTS payment_callbacks (
    id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT REFERENCES payments(id) ON DELETE SET NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('alipay', 'wechat')),
    callback_type VARCHAR(20) NOT NULL DEFAULT 'payment' CHECK (callback_type IN ('payment', 'refund')),
    callback_data JSONB NOT NULL,
    signature VARCHAR(500),
    client_ip INET,
    is_valid BOOLEAN DEFAULT NULL,
    processed BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_callbacks_payment_id (payment_id),
    INDEX idx_callbacks_platform (platform),
    INDEX idx_callbacks_processed (processed),
    INDEX idx_callbacks_created_at (created_at)
);

-- 支付统计表（用于快速统计查询）
CREATE TABLE IF NOT EXISTS payment_stats (
    id BIGSERIAL PRIMARY KEY,
    date_key DATE NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    total_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    success_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    refund_count INTEGER NOT NULL DEFAULT 0,
    refund_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束
    UNIQUE(date_key, payment_method),
    
    -- 索引
    INDEX idx_payment_stats_date (date_key),
    INDEX idx_payment_stats_method (payment_method)
);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为各表添加更新时间触发器
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_refunds_updated_at BEFORE UPDATE ON refunds
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_stats_updated_at BEFORE UPDATE ON payment_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建支付统计更新函数
CREATE OR REPLACE FUNCTION update_payment_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- 当支付状态更新时，更新统计表
    IF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
        -- 插入或更新当天的统计数据
        INSERT INTO payment_stats (date_key, payment_method, total_count, success_count, total_amount, success_amount)
        VALUES (
            CURRENT_DATE,
            NEW.payment_method,
            CASE WHEN NEW.status = 'paid' THEN 1 ELSE 0 END,
            CASE WHEN NEW.status = 'paid' THEN 1 ELSE 0 END,
            CASE WHEN NEW.status = 'paid' THEN NEW.amount ELSE 0 END,
            CASE WHEN NEW.status = 'paid' THEN NEW.amount ELSE 0 END
        )
        ON CONFLICT (date_key, payment_method)
        DO UPDATE SET
            success_count = payment_stats.success_count + CASE WHEN NEW.status = 'paid' AND OLD.status != 'paid' THEN 1 ELSE 0 END,
            success_amount = payment_stats.success_amount + CASE WHEN NEW.status = 'paid' AND OLD.status != 'paid' THEN NEW.amount ELSE 0 END,
            updated_at = CURRENT_TIMESTAMP;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 添加支付统计触发器
CREATE TRIGGER trigger_update_payment_stats
    AFTER UPDATE ON payments
    FOR EACH ROW
    EXECUTE FUNCTION update_payment_stats();

-- 创建查询视图
CREATE OR REPLACE VIEW v_order_payments AS
SELECT 
    o.id as order_id,
    o.order_no,
    o.user_id,
    o.service_id,
    o.service_title,
    o.total_price as order_amount,
    o.status as order_status,
    o.created_at as order_created_at,
    p.id as payment_id,
    p.out_trade_no,
    p.trade_no,
    p.amount as payment_amount,
    p.payment_method,
    p.payment_type,
    p.status as payment_status,
    p.paid_at,
    p.created_at as payment_created_at,
    u.username,
    u.email
FROM orders o
LEFT JOIN payments p ON o.id = p.order_id
LEFT JOIN users u ON o.user_id = u.id;

-- 创建支付统计视图
CREATE OR REPLACE VIEW v_payment_summary AS
SELECT 
    payment_method,
    COUNT(*) as total_payments,
    COUNT(CASE WHEN status = 'paid' THEN 1 END) as successful_payments,
    SUM(amount) as total_amount,
    SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) as successful_amount,
    ROUND(
        COUNT(CASE WHEN status = 'paid' THEN 1 END) * 100.0 / COUNT(*), 2
    ) as success_rate,
    AVG(CASE WHEN status = 'paid' THEN amount END) as avg_payment_amount
FROM payments
GROUP BY payment_method;

-- 插入一些示例数据（可选，用于测试）
-- 注意：这些数据仅用于开发测试，生产环境请删除

-- 示例：插入测试订单（需要先有用户和服务数据）
/*
INSERT INTO orders (user_id, service_id, order_no, service_title, unit_price, total_price, status) VALUES
(1, 1, 'ORD202401010001', '留学申请指导服务', 299.00, 299.00, 'pending'),
(1, 2, 'ORD202401010002', '文书修改服务', 199.00, 199.00, 'pending');

-- 示例：插入测试支付记录
INSERT INTO payments (order_id, user_id, out_trade_no, amount, payment_method, status) VALUES
(1, 1, 'PP202401010001', 299.00, 'alipay', 'pending'),
(2, 1, 'PP202401010002', 199.00, 'wechat', 'pending');
*/

-- 创建支付系统相关的存储过程

-- 获取用户支付统计
CREATE OR REPLACE FUNCTION get_user_payment_stats(user_id_param BIGINT)
RETURNS TABLE(
    total_orders BIGINT,
    total_payments BIGINT,
    total_amount DECIMAL,
    successful_payments BIGINT,
    successful_amount DECIMAL,
    success_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT o.id) as total_orders,
        COUNT(p.id) as total_payments,
        COALESCE(SUM(p.amount), 0) as total_amount,
        COUNT(CASE WHEN p.status = 'paid' THEN 1 END) as successful_payments,
        COALESCE(SUM(CASE WHEN p.status = 'paid' THEN p.amount ELSE 0 END), 0) as successful_amount,
        CASE 
            WHEN COUNT(p.id) > 0 THEN 
                ROUND(COUNT(CASE WHEN p.status = 'paid' THEN 1 END) * 100.0 / COUNT(p.id), 2)
            ELSE 0
        END as success_rate
    FROM orders o
    LEFT JOIN payments p ON o.id = p.order_id
    WHERE o.user_id = user_id_param;
END;
$$ LANGUAGE plpgsql;

-- 获取支付方式统计
CREATE OR REPLACE FUNCTION get_payment_method_stats(
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL
)
RETURNS TABLE(
    payment_method VARCHAR,
    total_count BIGINT,
    success_count BIGINT,
    total_amount DECIMAL,
    success_amount DECIMAL,
    success_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.payment_method,
        COUNT(*) as total_count,
        COUNT(CASE WHEN p.status = 'paid' THEN 1 END) as success_count,
        COALESCE(SUM(p.amount), 0) as total_amount,
        COALESCE(SUM(CASE WHEN p.status = 'paid' THEN p.amount ELSE 0 END), 0) as success_amount,
        CASE 
            WHEN COUNT(*) > 0 THEN 
                ROUND(COUNT(CASE WHEN p.status = 'paid' THEN 1 END) * 100.0 / COUNT(*), 2)
            ELSE 0
        END as success_rate
    FROM payments p
    WHERE 
        (start_date IS NULL OR DATE(p.created_at) >= start_date)
        AND (end_date IS NULL OR DATE(p.created_at) <= end_date)
    GROUP BY p.payment_method
    ORDER BY total_amount DESC;
END;
$$ LANGUAGE plpgsql;

-- 添加表注释
COMMENT ON TABLE orders IS '订单表 - 存储用户购买服务的订单信息';
COMMENT ON TABLE payments IS '支付记录表 - 存储支付交易的详细信息';
COMMENT ON TABLE refunds IS '退款记录表 - 存储退款申请和处理记录';
COMMENT ON TABLE payment_callbacks IS '支付回调日志表 - 记录第三方支付平台的回调信息';
COMMENT ON TABLE payment_stats IS '支付统计表 - 存储每日支付统计数据，用于快速查询';

-- 添加列注释
COMMENT ON COLUMN orders.order_no IS '订单编号，全局唯一';
COMMENT ON COLUMN orders.total_price IS '订单总金额，单位：元';
COMMENT ON COLUMN payments.out_trade_no IS '商户订单号，发送给第三方支付平台';
COMMENT ON COLUMN payments.trade_no IS '第三方支付平台交易号';
COMMENT ON COLUMN payments.payment_method IS '支付方式：alipay-支付宝，wechat-微信支付';
COMMENT ON COLUMN payments.payment_type IS '支付类型：web-网页支付，app-APP支付，native-扫码支付等';
COMMENT ON COLUMN refunds.out_refund_no IS '商户退款单号';
COMMENT ON COLUMN refunds.refund_id IS '第三方支付平台退款单号';

COMMIT;
