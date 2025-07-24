# 🎓 导师-学员匹配系统设计方案

## 📋 核心设计理念

1. **双重身份支持**: 同一用户可以同时是导师和学员
2. **智能匹配算法**: 基于技能、经验、需求进行匹配
3. **灵活的交易模式**: 支持付费、免费、积分兑换等多种形式
4. **完整的生命周期管理**: 从匹配到完成的全流程追踪

## 🏗️ 数据库架构设计

### 1. 用户技能和兴趣表
```sql
-- 技能分类表
CREATE TABLE skill_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    name_en VARCHAR(100),
    description TEXT,
    icon_url VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 具体技能表
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES skill_categories(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    description TEXT,
    difficulty_level INTEGER DEFAULT 1, -- 1-5难度等级
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户技能关系表（作为导师的技能）
CREATE TABLE user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level INTEGER DEFAULT 1, -- 1-5熟练度等级
    years_experience INTEGER DEFAULT 0,
    can_mentor BOOLEAN DEFAULT false, -- 是否愿意作为导师
    hourly_rate DECIMAL(10,2), -- 每小时费率（可为null表示免费）
    description TEXT, -- 技能描述
    verified BOOLEAN DEFAULT false, -- 是否经过验证
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_id)
);

-- 用户学习需求表（作为学员的需求）
CREATE TABLE user_learning_needs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    urgency_level INTEGER DEFAULT 1, -- 1-5紧急程度
    budget_min DECIMAL(10,2), -- 预算下限
    budget_max DECIMAL(10,2), -- 预算上限
    preferred_format VARCHAR(50) DEFAULT 'online', -- online, offline, hybrid
    description TEXT, -- 学习需求描述
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_id)
);
```

### 2. 匹配和交易系统
```sql
-- 匹配记录表
CREATE TABLE mentor_matches (
    id SERIAL PRIMARY KEY,
    mentor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    mentee_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    match_score DECIMAL(5,2), -- 匹配度评分 0-100
    match_algorithm VARCHAR(50) DEFAULT 'default', -- 匹配算法版本
    status VARCHAR(20) DEFAULT 'suggested', -- suggested, interested, declined, expired
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- 匹配过期时间
    CHECK (mentor_id != mentee_id)
);

-- 指导关系表（正式建立的指导关系）
CREATE TABLE mentorship_relationships (
    id SERIAL PRIMARY KEY,
    mentor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    mentee_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    match_id INTEGER REFERENCES mentor_matches(id),
    
    -- 关系基本信息
    title VARCHAR(200), -- 指导项目名称
    description TEXT,
    goals TEXT, -- 学习目标
    
    -- 时间和费用
    start_date DATE,
    estimated_end_date DATE,
    total_hours INTEGER,
    hourly_rate DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    
    -- 状态管理
    status VARCHAR(20) DEFAULT 'pending', -- pending, active, paused, completed, cancelled
    relationship_type VARCHAR(20) DEFAULT 'paid', -- paid, free, exchange, volunteer
    
    -- 沟通偏好
    preferred_communication VARCHAR(100), -- zoom, wechat, email, etc.
    meeting_frequency VARCHAR(50), -- weekly, biweekly, monthly, flexible
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    CHECK (mentor_id != mentee_id)
);

-- 指导会话记录表
CREATE TABLE mentorship_sessions (
    id SERIAL PRIMARY KEY,
    relationship_id INTEGER REFERENCES mentorship_relationships(id) ON DELETE CASCADE,
    session_number INTEGER,
    
    -- 会话时间
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_minutes INTEGER,
    
    -- 会话内容
    agenda TEXT,
    notes TEXT, -- 导师笔记
    student_feedback TEXT, -- 学员反馈
    homework TEXT, -- 作业或任务
    
    -- 会话状态
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled, no_show
    rating_by_mentee INTEGER CHECK (rating_by_mentee >= 1 AND rating_by_mentee <= 5),
    rating_by_mentor INTEGER CHECK (rating_by_mentor >= 1 AND rating_by_mentor <= 5),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 交易和支付系统
```sql
-- 交易记录表
CREATE TABLE mentorship_transactions (
    id SERIAL PRIMARY KEY,
    relationship_id INTEGER REFERENCES mentorship_relationships(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES mentorship_sessions(id), -- 可为null表示预付款
    
    -- 交易基本信息
    transaction_type VARCHAR(20) NOT NULL, -- payment, refund, bonus, penalty
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    
    -- 支付方式
    payment_method VARCHAR(50), -- wechat, alipay, credit_card, platform_credit
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed, refunded
    
    -- 第三方支付信息
    external_transaction_id VARCHAR(255),
    payment_gateway VARCHAR(50),
    
    -- 平台费用
    platform_fee DECIMAL(10,2) DEFAULT 0,
    mentor_amount DECIMAL(10,2), -- 导师实际收到金额
    
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- 用户积分/信用系统
CREATE TABLE user_credits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    credit_type VARCHAR(20) NOT NULL, -- mentor_points, learning_points, platform_credits
    amount INTEGER NOT NULL,
    reason VARCHAR(100),
    reference_id INTEGER, -- 关联的记录ID（可能是relationship_id, session_id等）
    reference_type VARCHAR(50), -- 关联记录类型
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. 评价和反馈系统
```sql
-- 扩展的评价表
CREATE TABLE mentorship_reviews (
    id SERIAL PRIMARY KEY,
    relationship_id INTEGER REFERENCES mentorship_relationships(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    reviewee_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 评价维度
    overall_rating INTEGER CHECK (overall_rating >= 1 AND overall_rating <= 5),
    communication_rating INTEGER CHECK (communication_rating >= 1 AND communication_rating <= 5),
    expertise_rating INTEGER CHECK (expertise_rating >= 1 AND expertise_rating <= 5),
    timeliness_rating INTEGER CHECK (timeliness_rating >= 1 AND timeliness_rating <= 5),
    value_rating INTEGER CHECK (value_rating >= 1 AND value_rating <= 5),
    
    -- 详细反馈
    comment TEXT,
    pros TEXT, -- 优点
    cons TEXT, -- 改进建议
    would_recommend BOOLEAN,
    
    -- 标签评价
    tags TEXT[], -- 如：['patient', 'knowledgeable', 'responsive']
    
    is_public BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户信誉统计表
CREATE TABLE user_reputation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 作为导师的统计
    mentor_rating_avg DECIMAL(3,2) DEFAULT 0,
    mentor_rating_count INTEGER DEFAULT 0,
    mentor_sessions_completed INTEGER DEFAULT 0,
    mentor_hours_taught INTEGER DEFAULT 0,
    mentor_success_rate DECIMAL(5,2) DEFAULT 0, -- 成功完成率
    
    -- 作为学员的统计
    mentee_rating_avg DECIMAL(3,2) DEFAULT 0,
    mentee_rating_count INTEGER DEFAULT 0,
    mentee_sessions_attended INTEGER DEFAULT 0,
    mentee_hours_learned INTEGER DEFAULT 0,
    mentee_completion_rate DECIMAL(5,2) DEFAULT 0, -- 课程完成率
    
    -- 综合信誉
    reputation_score INTEGER DEFAULT 0, -- 综合信誉分数
    trust_level VARCHAR(20) DEFAULT 'newcomer', -- newcomer, bronze, silver, gold, platinum
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 关键功能特性

### 1. 智能匹配算法
```python
class MatchingAlgorithm:
    def calculate_match_score(self, mentor_skill, mentee_need):
        """计算匹配度评分"""
        score = 0
        
        # 技能匹配度 (40%)
        skill_match = self.skill_compatibility(mentor_skill, mentee_need)
        score += skill_match * 0.4
        
        # 预算匹配度 (25%)
        budget_match = self.budget_compatibility(mentor_skill.hourly_rate, mentee_need.budget_range)
        score += budget_match * 0.25
        
        # 时间可用性 (20%)
        time_match = self.time_compatibility(mentor_skill.availability, mentee_need.availability)
        score += time_match * 0.2
        
        # 历史评价 (15%)
        reputation_boost = self.reputation_boost(mentor_skill.user.reputation)
        score += reputation_boost * 0.15
        
        return min(score, 100)  # 确保不超过100分
```

### 2. 双重身份管理
```python
class UserRoleManager:
    def get_user_roles(self, user_id: int):
        """获取用户的所有角色"""
        roles = {}
        
        # 检查是否为导师
        mentor_skills = self.get_mentor_skills(user_id)
        if mentor_skills:
            roles['mentor'] = {
                'skills': mentor_skills,
                'active_mentorships': self.get_active_mentorships_as_mentor(user_id),
                'reputation': self.get_mentor_reputation(user_id)
            }
        
        # 检查是否为学员
        learning_needs = self.get_learning_needs(user_id)
        if learning_needs:
            roles['mentee'] = {
                'needs': learning_needs,
                'active_learning': self.get_active_mentorships_as_mentee(user_id),
                'progress': self.get_learning_progress(user_id)
            }
        
        return roles
```

### 3. 多样化交易模式
```python
class TransactionModes:
    PAID = "paid"           # 付费指导
    FREE = "free"           # 免费指导  
    EXCHANGE = "exchange"   # 技能交换
    VOLUNTEER = "volunteer" # 志愿服务
    CREDITS = "credits"     # 积分兑换
```

## 📊 API 端点设计

### 匹配相关 API
```python
# 获取推荐匹配
GET /api/v1/matching/suggestions?skill_id=1&role=mentor&limit=10

# 创建指导关系
POST /api/v1/mentorship/relationships

# 获取我的指导关系
GET /api/v1/mentorship/my-relationships?role=mentor&status=active

# 会话管理
POST /api/v1/mentorship/sessions
PUT /api/v1/mentorship/sessions/{session_id}
GET /api/v1/mentorship/sessions/{session_id}/notes
```

### 用户能力管理 API
```python
# 技能管理
POST /api/v1/users/me/skills
PUT /api/v1/users/me/skills/{skill_id}
DELETE /api/v1/users/me/skills/{skill_id}

# 学习需求管理
POST /api/v1/users/me/learning-needs
PUT /api/v1/users/me/learning-needs/{need_id}
```

## 🔄 业务流程设计

### 1. 导师注册流程
```
1. 用户添加技能 → 2. 设置可指导状态 → 3. 平台审核/验证 → 4. 开始接收匹配推荐
```

### 2. 学员匹配流程
```
1. 用户发布学习需求 → 2. 系统智能匹配 → 3. 双方确认意向 → 4. 建立指导关系 → 5. 开始学习
```

### 3. 指导关系生命周期
```
建立关系 → 制定计划 → 进行会话 → 跟踪进度 → 完成评价 → 关系结束/续约
```

这个设计支持：
- ✅ **双重身份**: 用户可以同时是多个领域的导师和其他领域的学员
- ✅ **智能匹配**: 基于技能、预算、时间等多维度匹配
- ✅ **灵活交易**: 支持付费、免费、技能交换等多种模式
- ✅ **完整追踪**: 从匹配到完成的全流程管理
- ✅ **信誉系统**: 基于历史表现的信誉评级

你觉得这个设计如何？需要我详细解释某个部分或者调整哪些方面吗？
