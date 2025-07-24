-- 留学生互助平台完整数据库架构
-- 整合导师-学员匹配系统 + AI咨询 + 筛选 + 认证 + 支付

-- ================================
-- 核心用户系统
-- ================================

-- 扩展用户表
ALTER TABLE users ADD COLUMN IF NOT EXISTS user_type VARCHAR(20) DEFAULT 'mentee'; -- mentor/mentee/both
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_status VARCHAR(20) DEFAULT 'unverified'; -- unverified/identity_verified/university_verified/fully_verified
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS cover_image_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS tagline VARCHAR(200);
ALTER TABLE users ADD COLUMN IF NOT EXISTS introduction TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS languages_spoken JSONB DEFAULT '[]'::jsonb;
ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMP;

-- 用户教育背景表
CREATE TABLE IF NOT EXISTS user_education (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    degree_type VARCHAR(50) NOT NULL, -- bachelor/master/phd/other
    school_name VARCHAR(200) NOT NULL,
    school_location VARCHAR(200),
    major VARCHAR(200),
    minor VARCHAR(200),
    gpa DECIMAL(3,2),
    graduation_year INTEGER,
    is_current BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,
    verification_documents JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 地区/国家表
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    country_code VARCHAR(3),
    region_type VARCHAR(20) DEFAULT 'country', -- country/state/province
    parent_id INTEGER REFERENCES regions(id),
    is_popular BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 院校表
CREATE TABLE IF NOT EXISTS universities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    region_id INTEGER REFERENCES regions(id),
    university_type VARCHAR(50), -- public/private/community
    ranking_qs INTEGER,
    ranking_us_news INTEGER,
    ranking_times INTEGER,
    website VARCHAR(500),
    logo_url VARCHAR(500),
    description TEXT,
    is_verified BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 专业表
CREATE TABLE IF NOT EXISTS majors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    category VARCHAR(100), -- STEM/Business/Arts/Social Sciences
    description TEXT,
    is_popular BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 大学专业关联表
CREATE TABLE IF NOT EXISTS university_majors (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    major_id INTEGER REFERENCES majors(id) ON DELETE CASCADE,
    degree_types JSONB DEFAULT '["bachelor","master","phd"]'::jsonb,
    tuition_domestic INTEGER,
    tuition_international INTEGER,
    admission_requirements JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(university_id, major_id)
);

-- ================================
-- 认证系统
-- ================================

-- 用户认证记录表
CREATE TABLE IF NOT EXISTS user_verifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    verification_type VARCHAR(50) NOT NULL, -- identity/university/phone/email
    status VARCHAR(20) DEFAULT 'pending', -- pending/approved/rejected/expired
    verification_data JSONB DEFAULT '{}'::jsonb, -- 存储认证相关数据
    documents JSONB DEFAULT '[]'::jsonb, -- 上传的文档列表
    reviewer_id INTEGER REFERENCES users(id),
    review_notes TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- 发帖系统
-- ================================

-- 帖子表
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    post_type VARCHAR(20) NOT NULL, -- mentor_offer/help_request
    title VARCHAR(300) NOT NULL,
    content TEXT NOT NULL,
    tags JSONB DEFAULT '[]'::jsonb,
    
    -- 筛选相关字段
    target_degree VARCHAR(50), -- bachelor/master/phd
    target_region_id INTEGER REFERENCES regions(id),
    target_university_id INTEGER REFERENCES universities(id),
    target_major_id INTEGER REFERENCES majors(id),
    
    -- 服务相关字段
    services_offered JSONB DEFAULT '[]'::jsonb, -- 提供的服务列表
    pricing_info JSONB DEFAULT '{}'::jsonb, -- 价格信息
    availability JSONB DEFAULT '{}'::jsonb, -- 时间安排
    
    -- 状态字段
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 帖子评论表
CREATE TABLE IF NOT EXISTS post_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES post_comments(id), -- 支持回复
    content TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 帖子点赞表
CREATE TABLE IF NOT EXISTS post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);

-- ================================
-- 聊天系统
-- ================================

-- 好友关系表
CREATE TABLE IF NOT EXISTS friendships (
    id SERIAL PRIMARY KEY,
    requester_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    addressee_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending', -- pending/accepted/blocked
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP,
    UNIQUE(requester_id, addressee_id)
);

-- 聊天房间表
CREATE TABLE IF NOT EXISTS chat_rooms (
    id SERIAL PRIMARY KEY,
    room_type VARCHAR(20) DEFAULT 'private', -- private/group
    name VARCHAR(200),
    description TEXT,
    avatar_url VARCHAR(500),
    created_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 聊天房间成员表
CREATE TABLE IF NOT EXISTS chat_room_members (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES chat_rooms(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member', -- member/admin
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_muted BOOLEAN DEFAULT false,
    UNIQUE(room_id, user_id)
);

-- 聊天消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES chat_rooms(id) ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message_type VARCHAR(20) DEFAULT 'text', -- text/image/file/system
    content TEXT,
    file_url VARCHAR(500),
    file_name VARCHAR(200),
    file_size INTEGER,
    reply_to_id INTEGER REFERENCES chat_messages(id),
    is_edited BOOLEAN DEFAULT false,
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- 支付系统
-- ================================

-- 服务订单表
CREATE TABLE IF NOT EXISTS service_orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    mentor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    mentee_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES posts(id),
    
    -- 订单基本信息
    title VARCHAR(300) NOT NULL,
    description TEXT,
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    
    -- 订单状态
    status VARCHAR(20) DEFAULT 'pending', -- pending/confirmed/in_progress/completed/cancelled/disputed
    payment_status VARCHAR(20) DEFAULT 'unpaid', -- unpaid/paid/partial_refund/full_refund
    
    -- 时间信息
    start_date DATE,
    estimated_completion_date DATE,
    actual_completion_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 服务里程碑表
CREATE TABLE IF NOT EXISTS service_milestones (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES service_orders(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    amount DECIMAL(10,2) NOT NULL,
    sequence_order INTEGER NOT NULL,
    
    -- 里程碑状态
    status VARCHAR(20) DEFAULT 'pending', -- pending/in_progress/completed/confirmed
    due_date DATE,
    completed_at TIMESTAMP,
    confirmed_at TIMESTAMP,
    
    -- 交付物
    deliverables JSONB DEFAULT '[]'::jsonb,
    mentor_notes TEXT,
    mentee_feedback TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 支付交易表
CREATE TABLE IF NOT EXISTS payment_transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    order_id INTEGER REFERENCES service_orders(id) ON DELETE CASCADE,
    milestone_id INTEGER REFERENCES service_milestones(id),
    
    -- 交易信息
    transaction_type VARCHAR(20) NOT NULL, -- payment/refund/release/hold
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    
    -- 支付信息
    payment_method VARCHAR(50), -- wechat/alipay/bank_transfer
    payment_gateway VARCHAR(50),
    gateway_transaction_id VARCHAR(200),
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending', -- pending/processing/completed/failed/cancelled
    
    -- 时间
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- AI咨询系统表（之前已创建，这里引用）
-- ================================
-- consultation_sessions, chat_messages, user_profiles 等表已存在

-- ================================
-- 系统配置和内容
-- ================================

-- 服务类型表
CREATE TABLE IF NOT EXISTS service_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description TEXT,
    category VARCHAR(50), -- consulting/writing/application/background
    icon_url VARCHAR(500),
    is_popular BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户服务能力表
CREATE TABLE IF NOT EXISTS user_service_capabilities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    service_type_id INTEGER REFERENCES service_types(id) ON DELETE CASCADE,
    proficiency_level INTEGER DEFAULT 1 CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    experience_years INTEGER DEFAULT 0,
    pricing JSONB DEFAULT '{}'::jsonb, -- 价格信息
    description TEXT,
    portfolio_items JSONB DEFAULT '[]'::jsonb, -- 作品集
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, service_type_id)
);

-- ================================
-- 索引创建
-- ================================

-- 用户相关索引
CREATE INDEX IF NOT EXISTS idx_users_type_status ON users(user_type, verification_status);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active, last_active_at);

-- 教育背景索引
CREATE INDEX IF NOT EXISTS idx_user_education_user ON user_education(user_id);
CREATE INDEX IF NOT EXISTS idx_user_education_school ON user_education(school_name, major);

-- 筛选相关索引
CREATE INDEX IF NOT EXISTS idx_posts_filters ON posts(target_degree, target_region_id, target_university_id, target_major_id);
CREATE INDEX IF NOT EXISTS idx_posts_type_active ON posts(post_type, is_active, created_at);
CREATE INDEX IF NOT EXISTS idx_posts_featured ON posts(is_featured, created_at);

-- 聊天相关索引
CREATE INDEX IF NOT EXISTS idx_chat_messages_room_time ON chat_messages(room_id, created_at);
CREATE INDEX IF NOT EXISTS idx_friendships_users ON friendships(requester_id, addressee_id, status);

-- 支付相关索引
CREATE INDEX IF NOT EXISTS idx_service_orders_users ON service_orders(mentor_id, mentee_id, status);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_order ON payment_transactions(order_id, status);

-- ================================
-- 初始数据插入
-- ================================

-- 插入热门地区
INSERT INTO regions (name, name_en, country_code, is_popular, sort_order) VALUES
('美国', 'United States', 'US', true, 1),
('英国', 'United Kingdom', 'UK', true, 2),
('加拿大', 'Canada', 'CA', true, 3),
('澳大利亚', 'Australia', 'AU', true, 4),
('新加坡', 'Singapore', 'SG', true, 5),
('中国香港', 'Hong Kong', 'HK', true, 6),
('德国', 'Germany', 'DE', true, 7),
('法国', 'France', 'FR', true, 8),
('日本', 'Japan', 'JP', true, 9),
('韩国', 'South Korea', 'KR', true, 10)
ON CONFLICT DO NOTHING;

-- 插入热门院校
INSERT INTO universities (name, name_en, region_id, ranking_qs, ranking_us_news) VALUES
('哈佛大学', 'Harvard University', 1, 4, 3),
('斯坦福大学', 'Stanford University', 1, 5, 6),
('麻省理工学院', 'Massachusetts Institute of Technology', 1, 1, 2),
('加州大学伯克利分校', 'University of California, Berkeley', 1, 10, 22),
('牛津大学', 'University of Oxford', 2, 2, 5),
('剑桥大学', 'University of Cambridge', 2, 3, 8),
('多伦多大学', 'University of Toronto', 3, 21, 18),
('悉尼大学', 'University of Sydney', 4, 19, 28),
('新加坡国立大学', 'National University of Singapore', 5, 8, 25),
('香港大学', 'University of Hong Kong', 6, 22, 35)
ON CONFLICT DO NOTHING;

-- 插入热门专业
INSERT INTO majors (name, name_en, category, is_popular, sort_order) VALUES
('计算机科学', 'Computer Science', 'STEM', true, 1),
('商业管理', 'Business Administration', 'Business', true, 2),
('金融学', 'Finance', 'Business', true, 3),
('电子工程', 'Electrical Engineering', 'STEM', true, 4),
('机械工程', 'Mechanical Engineering', 'STEM', true, 5),
('心理学', 'Psychology', 'Social Sciences', true, 6),
('经济学', 'Economics', 'Social Sciences', true, 7),
('生物学', 'Biology', 'STEM', true, 8),
('化学', 'Chemistry', 'STEM', true, 9),
('英语文学', 'English Literature', 'Arts', true, 10),
('传播学', 'Communications', 'Social Sciences', true, 11),
('市场营销', 'Marketing', 'Business', true, 12),
('数据科学', 'Data Science', 'STEM', true, 13),
('人工智能', 'Artificial Intelligence', 'STEM', true, 14),
('国际关系', 'International Relations', 'Social Sciences', true, 15)
ON CONFLICT DO NOTHING;

-- 插入服务类型
INSERT INTO service_types (name, name_en, category, is_popular, sort_order) VALUES
('申请咨询', 'Application Consulting', 'consulting', true, 1),
('文书写作', 'Essay Writing', 'writing', true, 2),
('文书润色', 'Essay Editing', 'writing', true, 3),
('简历修改', 'Resume Editing', 'writing', true, 4),
('网申指导', 'Application Guidance', 'application', true, 5),
('面试辅导', 'Interview Coaching', 'consulting', true, 6),
('选校定位', 'School Selection', 'consulting', true, 7),
('背景提升', 'Background Enhancement', 'background', true, 8),
('推荐信指导', 'Recommendation Letter Guidance', 'application', true, 9),
('奖学金申请', 'Scholarship Application', 'application', true, 10),
('签证指导', 'Visa Guidance', 'application', false, 11),
('住宿安排', 'Housing Assistance', 'application', false, 12)
ON CONFLICT DO NOTHING;

-- 创建更新时间戳触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加触发器
DO $$
DECLARE
    table_name text;
BEGIN
    FOR table_name IN 
        SELECT t.table_name 
        FROM information_schema.columns t 
        WHERE t.column_name = 'updated_at' 
        AND t.table_schema = 'public'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS update_%s_updated_at ON %s', table_name, table_name);
        EXECUTE format('CREATE TRIGGER update_%s_updated_at 
                       BEFORE UPDATE ON %s 
                       FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', 
                       table_name, table_name);
    END LOOP;
END $$;
