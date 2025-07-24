-- AI留学申请咨询系统数据库表结构

-- 用户背景档案表
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 基本信息
    name VARCHAR(100) NOT NULL,
    target_degree VARCHAR(50) NOT NULL, -- bachelor/master/phd/mba
    target_major VARCHAR(100) NOT NULL,
    target_year VARCHAR(10) NOT NULL, -- 2025Fall
    
    -- 学术背景
    undergraduate_school VARCHAR(200),
    undergraduate_major VARCHAR(100),
    gpa DECIMAL(3,2),
    school_ranking INTEGER,
    core_courses JSONB DEFAULT '[]'::jsonb, -- 核心课程列表
    
    -- 标准化考试成绩
    gre_total INTEGER,
    gre_verbal INTEGER,
    gre_quantitative INTEGER,
    gre_writing DECIMAL(2,1),
    toefl_total INTEGER,
    ielts_total DECIMAL(2,1),
    
    -- 研究经历 (JSON数组格式)
    research_experiences JSONB DEFAULT '[]'::jsonb,
    
    -- 工作/实习经历 (JSON数组格式)
    work_experiences JSONB DEFAULT '[]'::jsonb,
    
    -- 其他背景
    awards JSONB DEFAULT '[]'::jsonb, -- 获奖情况
    extracurriculars JSONB DEFAULT '[]'::jsonb, -- 课外活动
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 大学和项目数据表
CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(50) NOT NULL,
    
    -- 排名信息
    ranking_us_news INTEGER,
    ranking_qs INTEGER,
    ranking_times INTEGER,
    ranking_arwu INTEGER,
    
    -- 基本信息
    location VARCHAR(200),
    website VARCHAR(500),
    logo_url VARCHAR(500),
    
    -- 录取统计数据
    acceptance_rate DECIMAL(4,2), -- 录取率
    avg_gpa DECIMAL(3,2), -- 平均GPA
    avg_gre JSONB, -- 平均GRE成绩 {"total": 320, "verbal": 160, "quant": 160, "writing": 4.0}
    avg_toefl INTEGER, -- 平均TOEFL
    avg_ielts DECIMAL(2,1), -- 平均IELTS
    
    -- 费用信息
    tuition_domestic INTEGER, -- 本国学生学费
    tuition_international INTEGER, -- 国际学生学费
    living_cost INTEGER, -- 生活费估算
    
    -- 其他信息
    campus_size VARCHAR(50), -- 校园规模
    student_population INTEGER, -- 学生人数
    international_ratio DECIMAL(3,2), -- 国际学生比例
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 专业项目表
CREATE TABLE academic_programs (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    
    -- 项目基本信息
    name VARCHAR(200) NOT NULL, -- 项目名称
    degree_type VARCHAR(50) NOT NULL, -- bachelor/master/phd/mba
    department VARCHAR(100), -- 所属院系
    
    -- 项目详情
    duration_years DECIMAL(2,1), -- 学制年数
    credit_hours INTEGER, -- 学分要求
    description TEXT, -- 项目描述
    
    -- 录取要求
    min_gpa DECIMAL(3,2),
    min_gre JSONB, -- GRE要求
    min_toefl INTEGER, -- TOEFL要求
    min_ielts DECIMAL(2,1), -- IELTS要求
    
    -- 申请信息
    application_deadline DATE, -- 申请截止日期
    application_fee INTEGER, -- 申请费
    required_documents JSONB DEFAULT '[]'::jsonb, -- 所需材料
    
    -- 项目特色
    specializations JSONB DEFAULT '[]'::jsonb, -- 专业方向
    research_areas JSONB DEFAULT '[]'::jsonb, -- 研究领域
    career_prospects JSONB DEFAULT '[]'::jsonb, -- 就业前景
    
    -- 统计数据
    enrollment_size INTEGER, -- 招生规模
    acceptance_rate DECIMAL(4,2), -- 项目录取率
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI咨询会话表
CREATE TABLE consultation_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- 会话元数据
    title VARCHAR(200),
    status VARCHAR(50) DEFAULT 'active', -- active/completed/archived
    session_type VARCHAR(50) DEFAULT 'general', -- general/profile_analysis/school_recommendation
    
    -- AI分析结果 (JSON格式存储)
    profile_analysis JSONB, -- 背景分析结果
    school_recommendations JSONB DEFAULT '[]'::jsonb, -- 学校推荐结果
    application_strategy JSONB, -- 申请策略
    
    -- 会话统计
    message_count INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 聊天消息表
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES consultation_sessions(session_id) ON DELETE CASCADE,
    
    -- 消息内容
    role VARCHAR(20) NOT NULL, -- user/assistant/system
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text', -- text/analysis/recommendation/strategy
    
    -- AI相关元数据
    model_used VARCHAR(50), -- 使用的AI模型
    tokens_used INTEGER, -- 消耗的token数量
    confidence_score DECIMAL(3,2), -- 置信度评分
    processing_time_ms INTEGER, -- 处理时间(毫秒)
    
    -- 消息元数据
    metadata JSONB DEFAULT '{}'::jsonb, -- 额外的元数据
    
    -- 状态
    is_deleted BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学校收藏表
CREATE TABLE user_school_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    program_id INTEGER REFERENCES academic_programs(id) ON DELETE CASCADE,
    
    -- 收藏信息
    notes TEXT, -- 用户备注
    priority_level INTEGER DEFAULT 5, -- 优先级 1-10
    application_status VARCHAR(50) DEFAULT 'considering', -- considering/applied/admitted/rejected
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, university_id, program_id)
);

-- 申请反馈表
CREATE TABLE consultation_feedback (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES consultation_sessions(session_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 反馈内容
    feedback_type VARCHAR(50) NOT NULL, -- recommendation/strategy/chat/overall
    rating INTEGER CHECK (rating >= 1 AND rating <= 5), -- 1-5星评分
    comment TEXT,
    
    -- 具体评价维度
    accuracy_rating INTEGER CHECK (accuracy_rating >= 1 AND accuracy_rating <= 5),
    helpfulness_rating INTEGER CHECK (helpfulness_rating >= 1 AND helpfulness_rating <= 5),
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    
    -- 改进建议
    suggestions TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知识库文档表 (用于RAG增强)
CREATE TABLE knowledge_base_documents (
    id SERIAL PRIMARY KEY,
    
    -- 文档信息
    title VARCHAR(300) NOT NULL,
    content TEXT NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- university_guide/admission_tips/essay_examples/interview_prep
    category VARCHAR(100), -- 分类标签
    tags JSONB DEFAULT '[]'::jsonb, -- 标签数组
    
    -- 向量化相关
    embedding_vector VECTOR(1536), -- 文档向量 (OpenAI embedding维度)
    chunk_id VARCHAR(100), -- 分块ID
    source_url VARCHAR(500), -- 来源链接
    
    -- 元数据
    author VARCHAR(100),
    publication_date DATE,
    relevance_score DECIMAL(3,2) DEFAULT 1.0,
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI模型使用统计表
CREATE TABLE ai_usage_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),
    
    -- 使用统计
    model_name VARCHAR(50) NOT NULL,
    operation_type VARCHAR(50) NOT NULL, -- analysis/recommendation/chat/strategy
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_total INTEGER,
    
    -- 成本统计
    cost_usd DECIMAL(8,4), -- 美元成本
    
    -- 性能统计
    response_time_ms INTEGER, -- 响应时间
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_consultation_sessions_user_id ON consultation_sessions(user_id);
CREATE INDEX idx_consultation_sessions_session_id ON consultation_sessions(session_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX idx_universities_ranking ON universities(ranking_us_news, ranking_qs);
CREATE INDEX idx_academic_programs_university_id ON academic_programs(university_id);
CREATE INDEX idx_academic_programs_degree_type ON academic_programs(degree_type);
CREATE INDEX idx_user_school_favorites_user_id ON user_school_favorites(user_id);
CREATE INDEX idx_consultation_feedback_session_id ON consultation_feedback(session_id);
CREATE INDEX idx_knowledge_base_documents_type ON knowledge_base_documents(document_type);
CREATE INDEX idx_ai_usage_stats_user_id ON ai_usage_stats(user_id);
CREATE INDEX idx_ai_usage_stats_created_at ON ai_usage_stats(created_at);

-- 创建向量搜索索引 (如果使用pgvector扩展)
-- CREATE INDEX idx_knowledge_base_embedding ON knowledge_base_documents USING ivfflat (embedding_vector vector_cosine_ops);

-- 创建更新时间戳的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加更新时间戳触发器
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_universities_updated_at BEFORE UPDATE ON universities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_academic_programs_updated_at BEFORE UPDATE ON academic_programs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_consultation_sessions_updated_at BEFORE UPDATE ON consultation_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_base_documents_updated_at BEFORE UPDATE ON knowledge_base_documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入一些示例数据

-- 示例大学数据
INSERT INTO universities (name, country, ranking_us_news, ranking_qs, location, acceptance_rate, avg_gpa, avg_gre, avg_toefl, tuition_international) VALUES
('Massachusetts Institute of Technology', 'USA', 2, 1, 'Cambridge, MA', 0.07, 3.96, '{"total": 332, "verbal": 162, "quant": 170, "writing": 4.6}', 109, 53790),
('Stanford University', 'USA', 6, 5, 'Stanford, CA', 0.04, 3.95, '{"total": 330, "verbal": 161, "quant": 169, "writing": 4.5}', 108, 56169),
('Harvard University', 'USA', 3, 4, 'Cambridge, MA', 0.05, 3.97, '{"total": 331, "verbal": 162, "quant": 169, "writing": 4.6}', 109, 51904),
('University of California, Berkeley', 'USA', 22, 10, 'Berkeley, CA', 0.17, 3.89, '{"total": 325, "verbal": 158, "quant": 167, "writing": 4.3}', 105, 44007),
('Carnegie Mellon University', 'USA', 25, 53, 'Pittsburgh, PA', 0.15, 3.84, '{"total": 328, "verbal": 160, "quant": 168, "writing": 4.4}', 106, 58924),
('University of Toronto', 'Canada', 18, 21, 'Toronto, ON', 0.43, 3.7, '{"total": 320, "verbal": 155, "quant": 165, "writing": 4.0}', 100, 25000),
('ETH Zurich', 'Switzerland', NULL, 9, 'Zurich', 0.27, 3.8, '{"total": 315, "verbal": 150, "quant": 165, "writing": 3.8}', 95, 1460),
('University of Oxford', 'UK', 5, 2, 'Oxford', 0.21, 3.9, '{"total": 325, "verbal": 160, "quant": 165, "writing": 4.2}', 110, 39678);

-- 示例项目数据
INSERT INTO academic_programs (university_id, name, degree_type, department, duration_years, min_gpa, min_gre, min_toefl, application_deadline, specializations) VALUES
(1, 'Master of Engineering in Computer Science', 'master', 'Electrical Engineering and Computer Science', 1.5, 3.7, '{"total": 320, "verbal": 155, "quant": 165}', 100, '2024-12-15', '["Artificial Intelligence", "Machine Learning", "Systems"]'),
(2, 'Master of Science in Computer Science', 'master', 'Computer Science', 2.0, 3.5, '{"total": 315, "verbal": 153, "quant": 162}', 103, '2024-12-15', '["AI", "HCI", "Theory", "Systems"]'),
(3, 'Master in Data Science', 'master', 'Harvard School of Engineering', 1.5, 3.6, '{"total": 318, "verbal": 155, "quant": 163}', 105, '2025-01-15', '["Machine Learning", "Statistical Modeling", "Data Engineering"]'),
(4, 'Master of Engineering in EECS', 'master', 'Electrical Engineering and Computer Sciences', 1.0, 3.4, '{"total": 310, "verbal": 150, "quant": 160}', 100, '2024-12-15', '["Computer Systems", "AI/ML", "Signal Processing"]'),
(5, 'Master of Science in Machine Learning', 'master', 'Machine Learning Department', 2.0, 3.7, '{"total": 325, "verbal": 158, "quant": 167}', 105, '2024-12-15', '["Deep Learning", "Robotics", "NLP", "Computer Vision"]');

-- 示例知识库文档
INSERT INTO knowledge_base_documents (title, content, document_type, category, tags) VALUES
('CS硕士申请完整指南', '计算机科学硕士申请需要准备的材料包括：学术成绩单、推荐信、个人陈述、标准化考试成绩等。其中GPA是最重要的指标之一，建议维持在3.5以上...', 'university_guide', 'Computer Science', '["CS", "硕士申请", "GPA", "推荐信"]'),
('如何写出优秀的个人陈述', '个人陈述是申请材料中最能体现个人特色的部分。一篇优秀的个人陈述应该包含：明确的学术目标、相关的背景经历、未来的职业规划...', 'essay_examples', 'Writing Tips', '["个人陈述", "文书写作", "申请技巧"]'),
('GRE备考策略与技巧', 'GRE考试分为语文、数学和写作三个部分。对于中国学生来说，数学部分相对容易，建议重点提升语文部分的成绩。备考策略包括...', 'admission_tips', 'Test Preparation', '["GRE", "标准化考试", "备考策略"]'),
('名校面试常见问题及回答技巧', '研究生入学面试中常见的问题包括：为什么选择这个专业、你的研究兴趣是什么、未来的职业规划等。回答这些问题时要注意...', 'interview_prep', 'Interview', '["面试", "研究生", "问答技巧"]');

-- 创建视图以简化常用查询

-- 用户完整档案视图
CREATE VIEW user_complete_profiles AS
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    up.*,
    CASE 
        WHEN up.gpa >= 3.8 THEN 'Excellent'
        WHEN up.gpa >= 3.5 THEN 'Good' 
        WHEN up.gpa >= 3.0 THEN 'Average'
        ELSE 'Below Average'
    END as gpa_category,
    CASE 
        WHEN up.toefl_total >= 100 THEN 'Strong'
        WHEN up.toefl_total >= 90 THEN 'Good'
        WHEN up.toefl_total >= 80 THEN 'Average'
        ELSE 'Weak'
    END as english_proficiency
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id;

-- 大学项目综合信息视图
CREATE VIEW university_programs_view AS
SELECT 
    u.id as university_id,
    u.name as university_name,
    u.country,
    u.ranking_us_news,
    u.ranking_qs,
    u.location,
    ap.id as program_id,
    ap.name as program_name,
    ap.degree_type,
    ap.department,
    ap.min_gpa,
    ap.min_toefl,
    ap.application_deadline,
    ap.specializations,
    u.acceptance_rate as university_acceptance_rate,
    ap.acceptance_rate as program_acceptance_rate
FROM universities u
JOIN academic_programs ap ON u.id = ap.university_id
WHERE ap.application_deadline > CURRENT_DATE;

-- 会话活动统计视图
CREATE VIEW session_activity_stats AS
SELECT 
    cs.session_id,
    cs.user_id,
    cs.title,
    cs.status,
    cs.message_count,
    cs.total_tokens_used,
    cs.created_at,
    cs.last_activity,
    CASE 
        WHEN cs.profile_analysis IS NOT NULL THEN TRUE 
        ELSE FALSE 
    END as has_analysis,
    CASE 
        WHEN jsonb_array_length(cs.school_recommendations) > 0 THEN TRUE 
        ELSE FALSE 
    END as has_recommendations,
    CASE 
        WHEN cs.application_strategy IS NOT NULL THEN TRUE 
        ELSE FALSE 
    END as has_strategy
FROM consultation_sessions cs;

COMMENT ON TABLE user_profiles IS 'AI咨询系统用户背景档案表';
COMMENT ON TABLE universities IS '大学基础信息表';
COMMENT ON TABLE academic_programs IS '学术项目详细信息表';
COMMENT ON TABLE consultation_sessions IS 'AI咨询会话记录表';
COMMENT ON TABLE chat_messages IS '聊天消息记录表';
COMMENT ON TABLE user_school_favorites IS '用户收藏的学校和项目';
COMMENT ON TABLE consultation_feedback IS '用户对AI咨询服务的反馈';
COMMENT ON TABLE knowledge_base_documents IS 'RAG知识库文档表';
COMMENT ON TABLE ai_usage_stats IS 'AI服务使用统计表';
