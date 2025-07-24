-- 导师-学员匹配系统数据库架构
-- 版本: 3.0 - 导师学员匹配系统
-- 基于现有 users 表扩展

-- ================================
-- 1. 技能和兴趣管理
-- ================================

-- 技能分类表
CREATE TABLE skill_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    name_en VARCHAR(100),
    description TEXT,
    icon_url VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 具体技能表
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES skill_categories(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description TEXT,
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户技能关系表（作为导师的技能）
CREATE TABLE user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level INTEGER DEFAULT 1 CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    years_experience INTEGER DEFAULT 0 CHECK (years_experience >= 0),
    can_mentor BOOLEAN DEFAULT false,
    hourly_rate DECIMAL(10,2) CHECK (hourly_rate >= 0),
    currency VARCHAR(3) DEFAULT 'CNY',
    description TEXT,
    verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMP,
    verified_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_id)
);

-- 用户学习需求表（作为学员的需求）
CREATE TABLE user_learning_needs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    urgency_level INTEGER DEFAULT 1 CHECK (urgency_level >= 1 AND urgency_level <= 5),
    budget_min DECIMAL(10,2) CHECK (budget_min >= 0),
    budget_max DECIMAL(10,2) CHECK (budget_max >= budget_min),
    currency VARCHAR(3) DEFAULT 'CNY',
    preferred_format VARCHAR(50) DEFAULT 'online', -- online, offline, hybrid
    preferred_duration VARCHAR(50), -- 1-3 months, 3-6 months, 6+ months
    description TEXT,
    learning_goals TEXT,
    current_level INTEGER DEFAULT 1 CHECK (current_level >= 1 AND current_level <= 5),
    target_level INTEGER DEFAULT 2 CHECK (target_level >= 1 AND target_level <= 5),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '3 months'),
    UNIQUE(user_id, skill_id)
);

-- ================================
-- 2. 匹配系统
-- ================================

-- 匹配记录表
CREATE TABLE mentor_matches (
    id SERIAL PRIMARY KEY,
    mentor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    mentee_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    learning_need_id INTEGER REFERENCES user_learning_needs(id) ON DELETE CASCADE,
    mentor_skill_id INTEGER REFERENCES user_skills(id) ON DELETE CASCADE,
    
    -- 匹配算法信息
    match_score DECIMAL(5,2) CHECK (match_score >= 0 AND match_score <= 100),
    match_algorithm VARCHAR(50) DEFAULT 'v1.0',
    match_factors JSONB, -- 存储匹配因素详情
    
    -- 匹配状态
    status VARCHAR(20) DEFAULT 'suggested', -- suggested, mentor_interested, mentee_interested, mutual_interest, declined_by_mentor, declined_by_mentee, expired
    mentor_viewed_at TIMESTAMP,
    mentee_viewed_at TIMESTAMP,
    mentor_responded_at TIMESTAMP,
    mentee_responded_at TIMESTAMP,
    
    -- 时间管理
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    
    CHECK (mentor_id != mentee_id)
);

-- ================================
-- 3. 指导关系系统
-- ================================

-- 指导关系表
CREATE TABLE mentorship_relationships (
    id SERIAL PRIMARY KEY,
    mentor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    mentee_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    match_id INTEGER REFERENCES mentor_matches(id),
    
    -- 关系基本信息
    title VARCHAR(200) NOT NULL,
    description TEXT,
    learning_goals TEXT,
    success_criteria TEXT,
    
    -- 时间安排
    start_date DATE DEFAULT CURRENT_DATE,
    estimated_end_date DATE,
    total_sessions_planned INTEGER,
    session_duration_minutes INTEGER DEFAULT 60,
    
    -- 费用信息
    hourly_rate DECIMAL(10,2) CHECK (hourly_rate >= 0),
    currency VARCHAR(3) DEFAULT 'CNY',
    total_amount DECIMAL(10,2),
    payment_schedule VARCHAR(20) DEFAULT 'per_session', -- per_session, weekly, monthly, upfront
    
    -- 关系配置
    relationship_type VARCHAR(20) DEFAULT 'paid', -- paid, free, exchange, volunteer, credits
    preferred_communication VARCHAR(100), -- zoom, wechat, email, phone, in_person
    meeting_frequency VARCHAR(50), -- weekly, biweekly, monthly, flexible
    timezone VARCHAR(50),
    
    -- 状态管理
    status VARCHAR(20) DEFAULT 'pending', -- pending, active, paused, completed, cancelled, dispute
    cancellation_reason TEXT,
    
    -- 统计信息
    sessions_completed INTEGER DEFAULT 0,
    total_hours_spent DECIMAL(5,2) DEFAULT 0,
    last_session_at TIMESTAMP,
    next_session_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    CHECK (mentor_id != mentee_id)
);

-- 指导会话记录表
CREATE TABLE mentorship_sessions (
    id SERIAL PRIMARY KEY,
    relationship_id INTEGER REFERENCES mentorship_relationships(id) ON DELETE CASCADE,
    session_number INTEGER NOT NULL,
    
    -- 会话时间
    scheduled_at TIMESTAMP NOT NULL,
    actual_start_at TIMESTAMP,
    actual_end_at TIMESTAMP,
    duration_minutes INTEGER,
    
    -- 会话内容
    agenda TEXT,
    mentor_notes TEXT,
    mentee_notes TEXT,
    key_topics TEXT[],
    homework_assigned TEXT,
    resources_shared TEXT[],
    next_session_plan TEXT,
    
    -- 会话状态和评价
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled, no_show_mentor, no_show_mentee, rescheduled
    cancellation_reason TEXT,
    rescheduled_from TIMESTAMP,
    
    -- 即时反馈
    mentor_satisfaction INTEGER CHECK (mentor_satisfaction >= 1 AND mentor_satisfaction <= 5),
    mentee_satisfaction INTEGER CHECK (mentee_satisfaction >= 1 AND mentee_satisfaction <= 5),
    mentor_feedback TEXT,
    mentee_feedback TEXT,
    
    -- 进度追踪
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    milestones_achieved TEXT[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- 4. 交易系统
-- ================================

-- 交易记录表
CREATE TABLE mentorship_transactions (
    id SERIAL PRIMARY KEY,
    relationship_id INTEGER REFERENCES mentorship_relationships(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES mentorship_sessions(id),
    
    -- 交易基本信息
    transaction_type VARCHAR(20) NOT NULL, -- payment, refund, bonus, penalty, credit_deduction, credit_addition
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    currency VARCHAR(3) DEFAULT 'CNY',
    
    -- 支付信息
    payment_method VARCHAR(50), -- wechat, alipay, credit_card, platform_credit, bank_transfer
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed, refunded, disputed
    
    -- 第三方支付
    external_transaction_id VARCHAR(255),
    payment_gateway VARCHAR(50),
    gateway_response JSONB,
    
    -- 费用分配
    platform_fee_rate DECIMAL(5,4) DEFAULT 0.05, -- 5% platform fee
    platform_fee_amount DECIMAL(10,2) DEFAULT 0,
    mentor_amount DECIMAL(10,2), -- 导师实际收到金额
    
    -- 附加信息
    description TEXT,
    reference_number VARCHAR(100) UNIQUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    confirmed_at TIMESTAMP
);

-- 用户钱包/信用系统
CREATE TABLE user_wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- 余额信息
    balance DECIMAL(10,2) DEFAULT 0 CHECK (balance >= 0),
    frozen_balance DECIMAL(10,2) DEFAULT 0 CHECK (frozen_balance >= 0),
    currency VARCHAR(3) DEFAULT 'CNY',
    
    -- 积分信息
    mentor_points INTEGER DEFAULT 0 CHECK (mentor_points >= 0),
    learning_points INTEGER DEFAULT 0 CHECK (learning_points >= 0),
    reputation_points INTEGER DEFAULT 0 CHECK (reputation_points >= 0),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 积分/信用记录
CREATE TABLE user_credit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    credit_type VARCHAR(20) NOT NULL, -- mentor_points, learning_points, reputation_points, balance
    amount INTEGER NOT NULL, -- 可以为负数表示扣除
    balance_after INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,
    reference_id INTEGER,
    reference_type VARCHAR(50),
    description TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- 5. 评价和反馈系统
-- ================================

-- 关系评价表（关系结束时的综合评价）
CREATE TABLE mentorship_reviews (
    id SERIAL PRIMARY KEY,
    relationship_id INTEGER REFERENCES mentorship_relationships(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    reviewee_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    reviewer_role VARCHAR(10) NOT NULL CHECK (reviewer_role IN ('mentor', 'mentee')),
    
    -- 评价维度（1-5分）
    overall_rating INTEGER NOT NULL CHECK (overall_rating >= 1 AND overall_rating <= 5),
    communication_rating INTEGER CHECK (communication_rating >= 1 AND communication_rating <= 5),
    expertise_rating INTEGER CHECK (expertise_rating >= 1 AND expertise_rating <= 5),
    timeliness_rating INTEGER CHECK (timeliness_rating >= 1 AND timeliness_rating <= 5),
    value_rating INTEGER CHECK (value_rating >= 1 AND value_rating <= 5),
    professionalism_rating INTEGER CHECK (professionalism_rating >= 1 AND professionalism_rating <= 5),
    
    -- 文字评价
    comment TEXT,
    pros TEXT,
    areas_for_improvement TEXT,
    would_recommend BOOLEAN DEFAULT true,
    would_work_again BOOLEAN DEFAULT true,
    
    -- 标签评价
    positive_tags TEXT[], -- ['patient', 'knowledgeable', 'responsive', 'well-prepared']
    negative_tags TEXT[], -- ['unpunctual', 'unprepared', 'difficult-to-understand']
    
    -- 学习成果（仅针对学员评价导师）
    learning_objectives_met INTEGER CHECK (learning_objectives_met >= 1 AND learning_objectives_met <= 5),
    skill_improvement INTEGER CHECK (skill_improvement >= 1 AND skill_improvement <= 5),
    
    -- 评价状态
    is_public BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    verification_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (reviewer_id != reviewee_id)
);

-- 用户信誉统计表
CREATE TABLE user_reputation_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- 作为导师的统计
    mentor_rating_avg DECIMAL(3,2) DEFAULT 0 CHECK (mentor_rating_avg >= 0 AND mentor_rating_avg <= 5),
    mentor_rating_count INTEGER DEFAULT 0 CHECK (mentor_rating_count >= 0),
    mentor_relationships_total INTEGER DEFAULT 0,
    mentor_relationships_completed INTEGER DEFAULT 0,
    mentor_sessions_completed INTEGER DEFAULT 0,
    mentor_hours_taught DECIMAL(8,2) DEFAULT 0,
    mentor_success_rate DECIMAL(5,2) DEFAULT 0 CHECK (mentor_success_rate >= 0 AND mentor_success_rate <= 100),
    mentor_response_rate DECIMAL(5,2) DEFAULT 0 CHECK (mentor_response_rate >= 0 AND mentor_response_rate <= 100),
    mentor_punctuality_rate DECIMAL(5,2) DEFAULT 0 CHECK (mentor_punctuality_rate >= 0 AND mentor_punctuality_rate <= 100),
    
    -- 作为学员的统计
    mentee_rating_avg DECIMAL(3,2) DEFAULT 0 CHECK (mentee_rating_avg >= 0 AND mentee_rating_avg <= 5),
    mentee_rating_count INTEGER DEFAULT 0 CHECK (mentee_rating_count >= 0),
    mentee_relationships_total INTEGER DEFAULT 0,
    mentee_relationships_completed INTEGER DEFAULT 0,
    mentee_sessions_attended INTEGER DEFAULT 0,
    mentee_hours_learned DECIMAL(8,2) DEFAULT 0,
    mentee_completion_rate DECIMAL(5,2) DEFAULT 0 CHECK (mentee_completion_rate >= 0 AND mentee_completion_rate <= 100),
    mentee_attendance_rate DECIMAL(5,2) DEFAULT 0 CHECK (mentee_attendance_rate >= 0 AND mentee_attendance_rate <= 100),
    
    -- 综合信誉
    reputation_score INTEGER DEFAULT 0 CHECK (reputation_score >= 0),
    trust_level VARCHAR(20) DEFAULT 'newcomer', -- newcomer, bronze, silver, gold, platinum, diamond
    badges TEXT[], -- 成就徽章
    
    -- 最近活动
    last_active_as_mentor TIMESTAMP,
    last_active_as_mentee TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- 6. 时间可用性管理
-- ================================

-- 用户可用时间表
CREATE TABLE user_availability (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 时间设置
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6), -- 0=Sunday, 6=Saturday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    
    -- 可用性类型
    availability_type VARCHAR(20) DEFAULT 'mentoring', -- mentoring, learning, both
    is_active BOOLEAN DEFAULT true,
    
    -- 时间段备注
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (end_time > start_time)
);

-- 临时不可用时间表（假期、忙碌期等）
CREATE TABLE user_unavailable_periods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    
    reason VARCHAR(100),
    description TEXT,
    affects_mentoring BOOLEAN DEFAULT true,
    affects_learning BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (end_date >= start_date)
);

-- ================================
-- 7. 索引优化
-- ================================

-- 技能相关索引
CREATE INDEX idx_skills_category ON skills(category_id);
CREATE INDEX idx_user_skills_user ON user_skills(user_id);
CREATE INDEX idx_user_skills_skill ON user_skills(skill_id);
CREATE INDEX idx_user_skills_mentor ON user_skills(user_id, can_mentor) WHERE can_mentor = true;
CREATE INDEX idx_learning_needs_user ON user_learning_needs(user_id);
CREATE INDEX idx_learning_needs_skill ON user_learning_needs(skill_id);
CREATE INDEX idx_learning_needs_active ON user_learning_needs(skill_id, is_active) WHERE is_active = true;

-- 匹配相关索引
CREATE INDEX idx_matches_mentor ON mentor_matches(mentor_id, status);
CREATE INDEX idx_matches_mentee ON mentor_matches(mentee_id, status);
CREATE INDEX idx_matches_skill ON mentor_matches(skill_id, status);
CREATE INDEX idx_matches_score ON mentor_matches(match_score DESC, created_at DESC);
CREATE INDEX idx_matches_expires ON mentor_matches(expires_at) WHERE status = 'suggested';

-- 关系相关索引
CREATE INDEX idx_relationships_mentor ON mentorship_relationships(mentor_id, status);
CREATE INDEX idx_relationships_mentee ON mentorship_relationships(mentee_id, status);
CREATE INDEX idx_relationships_active ON mentorship_relationships(status) WHERE status = 'active';
CREATE INDEX idx_sessions_relationship ON mentorship_sessions(relationship_id, session_number);
CREATE INDEX idx_sessions_scheduled ON mentorship_sessions(scheduled_at) WHERE status = 'scheduled';

-- 交易相关索引
CREATE INDEX idx_transactions_relationship ON mentorship_transactions(relationship_id);
CREATE INDEX idx_transactions_status ON mentorship_transactions(payment_status, created_at);
CREATE INDEX idx_credit_logs_user ON user_credit_logs(user_id, created_at DESC);

-- 评价相关索引
CREATE INDEX idx_reviews_reviewee ON mentorship_reviews(reviewee_id, is_public) WHERE is_public = true;
CREATE INDEX idx_reviews_relationship ON mentorship_reviews(relationship_id);

-- 可用性相关索引
CREATE INDEX idx_availability_user ON user_availability(user_id, day_of_week, is_active);
CREATE INDEX idx_unavailable_user ON user_unavailable_periods(user_id, start_date, end_date);

-- ================================
-- 8. 初始数据插入
-- ================================

-- 插入技能分类
INSERT INTO skill_categories (name, name_en, description, sort_order) VALUES
('编程开发', 'Programming', '软件开发相关技能', 1),
('设计创意', 'Design', '设计和创意相关技能', 2),
('商业管理', 'Business', '商业和管理相关技能', 3),
('语言学习', 'Languages', '外语学习相关技能', 4),
('学术研究', 'Academic', '学术和研究相关技能', 5),
('生活技能', 'Life Skills', '日常生活技能', 6);

-- 插入热门技能
INSERT INTO skills (category_id, name, name_en, difficulty_level, sort_order) VALUES
-- 编程开发
(1, 'Python编程', 'Python Programming', 2, 1),
(1, 'JavaScript开发', 'JavaScript Development', 2, 2),
(1, '前端开发', 'Frontend Development', 3, 3),
(1, '后端开发', 'Backend Development', 4, 4),
(1, '移动应用开发', 'Mobile Development', 4, 5),
(1, '数据分析', 'Data Analysis', 3, 6),
(1, '机器学习', 'Machine Learning', 5, 7),

-- 设计创意
(2, 'UI/UX设计', 'UI/UX Design', 3, 1),
(2, '平面设计', 'Graphic Design', 2, 2),
(2, '插画设计', 'Illustration', 3, 3),
(2, '视频制作', 'Video Production', 4, 4),
(2, '摄影', 'Photography', 2, 5),

-- 商业管理
(3, '项目管理', 'Project Management', 3, 1),
(3, '数字营销', 'Digital Marketing', 2, 2),
(3, '财务分析', 'Financial Analysis', 4, 3),
(3, '创业指导', 'Entrepreneurship', 4, 4),
(3, '团队管理', 'Team Management', 4, 5),

-- 语言学习
(4, '英语口语', 'English Speaking', 2, 1),
(4, '英语写作', 'English Writing', 3, 2),
(4, '日语学习', 'Japanese Learning', 3, 3),
(4, '韩语学习', 'Korean Learning', 3, 4),
(4, '德语学习', 'German Learning', 4, 5),

-- 学术研究
(5, '论文写作', 'Academic Writing', 3, 1),
(5, '研究方法', 'Research Methods', 4, 2),
(5, '统计分析', 'Statistical Analysis', 4, 3),
(5, '留学申请', 'Study Abroad Application', 3, 4),

-- 生活技能
(6, '烹饪', 'Cooking', 1, 1),
(6, '健身指导', 'Fitness Training', 2, 2),
(6, '理财规划', 'Financial Planning', 3, 3),
(6, '时间管理', 'Time Management', 2, 4),
(6, '面试技巧', 'Interview Skills', 2, 5);

-- ================================
-- 9. 触发器和函数
-- ================================

-- 自动更新 updated_at 字段的函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加触发器
CREATE TRIGGER update_skill_categories_updated_at BEFORE UPDATE ON skill_categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_skills_updated_at BEFORE UPDATE ON user_skills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_learning_needs_updated_at BEFORE UPDATE ON user_learning_needs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mentor_matches_updated_at BEFORE UPDATE ON mentor_matches FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mentorship_relationships_updated_at BEFORE UPDATE ON mentorship_relationships FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mentorship_sessions_updated_at BEFORE UPDATE ON mentorship_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mentorship_transactions_updated_at BEFORE UPDATE ON mentorship_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_wallets_updated_at BEFORE UPDATE ON user_wallets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_reputation_stats_updated_at BEFORE UPDATE ON user_reputation_stats FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_availability_updated_at BEFORE UPDATE ON user_availability FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE skill_categories IS '技能分类表';
COMMENT ON TABLE skills IS '具体技能表';
COMMENT ON TABLE user_skills IS '用户技能表（导师能力）';
COMMENT ON TABLE user_learning_needs IS '用户学习需求表';
COMMENT ON TABLE mentor_matches IS '导师学员匹配记录表';
COMMENT ON TABLE mentorship_relationships IS '指导关系表';
COMMENT ON TABLE mentorship_sessions IS '指导会话记录表';
COMMENT ON TABLE mentorship_transactions IS '交易记录表';
COMMENT ON TABLE user_wallets IS '用户钱包表';
COMMENT ON TABLE user_credit_logs IS '积分记录表';
COMMENT ON TABLE mentorship_reviews IS '指导关系评价表';
COMMENT ON TABLE user_reputation_stats IS '用户信誉统计表';
COMMENT ON TABLE user_availability IS '用户可用时间表';
COMMENT ON TABLE user_unavailable_periods IS '用户不可用时间段表';
