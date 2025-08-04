-- 启航引路人项目数据库架构
-- 版本: 2.2
-- 更新时间: 2024-07-27
-- 描述: 合并了所有表结构到一个文件，并为消息系统增加了 'conversations' 和 'conversation_participants' 表。

-- 用户表（核心用户账户信息）
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',  -- user, navigator, admin
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    avatar_url TEXT -- 补充在 user_schema 中使用的字段
);

-- 用户资料表（扩展用户信息）
CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(100),
    bio TEXT,
    phone VARCHAR(20),
    location VARCHAR(100),
    website VARCHAR(255),
    birth_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 好友关系表
CREATE TABLE IF NOT EXISTS friends (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    friend_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, accepted, blocked
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, friend_id),
    CHECK (user_id != friend_id)
);

-- 服务表（引路人提供的服务）
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    navigator_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),  -- study, life, career, etc.
    price DECIMAL(10,2),
    duration_hours INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    navigator_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, completed, cancelled
    scheduled_at TIMESTAMP,
    total_price DECIMAL(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 评价表
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 论坛帖子表
CREATE TABLE IF NOT EXISTS forum_posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    tags TEXT[] DEFAULT '{}', -- PostgreSQL 数组类型
    is_anonymous BOOLEAN DEFAULT FALSE, -- 新增匿名发帖字段
    replies_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_hot BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 论坛回复表
CREATE TABLE IF NOT EXISTS forum_replies (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES forum_posts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_reply_id INTEGER REFERENCES forum_replies(id) ON DELETE SET NULL, -- 更新外键约束
    likes_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 论坛点赞记录表 (帖子)
CREATE TABLE IF NOT EXISTS forum_likes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES forum_posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, post_id)
);

-- 论坛回复点赞记录表 (新增)
CREATE TABLE IF NOT EXISTS forum_reply_likes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reply_id INTEGER NOT NULL REFERENCES forum_replies(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, reply_id)
);

-- 文件上传记录表
CREATE TABLE IF NOT EXISTS uploaded_files (
    id SERIAL PRIMARY KEY,
    file_id UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    file_type VARCHAR(20) NOT NULL CHECK (file_type IN ('avatar', 'document', 'other')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER, -- 外键后添加，避免循环依赖
    sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'system', 'multi_modal')),
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'read')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE NULL,
    CONSTRAINT messages_sender_recipient_check CHECK (sender_id != recipient_id)
);

-- 对话表
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_id INT -- 外键后添加，避免循环依赖
);

-- 对话参与者表
CREATE TABLE IF NOT EXISTS conversation_participants (
    id SERIAL PRIMARY KEY,
    conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (conversation_id, user_id)
);


-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_services_navigator ON services(navigator_id);
CREATE INDEX IF NOT EXISTS idx_services_category ON services(category);
CREATE INDEX IF NOT EXISTS idx_orders_client ON orders(client_id);
CREATE INDEX IF NOT EXISTS idx_orders_navigator ON orders(navigator_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- 消息表索引
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient_id ON messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_is_read ON messages(is_read) WHERE is_read = FALSE;

-- 论坛帖子表索引
CREATE INDEX IF NOT EXISTS idx_forum_posts_author_id ON forum_posts(author_id);
CREATE INDEX IF NOT EXISTS idx_forum_posts_category ON forum_posts(category);
CREATE INDEX IF NOT EXISTS idx_forum_posts_created_at ON forum_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forum_posts_last_activity ON forum_posts(last_activity DESC);
CREATE INDEX IF NOT EXISTS idx_forum_posts_is_pinned ON forum_posts(is_pinned) WHERE is_pinned = TRUE;
CREATE INDEX IF NOT EXISTS idx_forum_posts_is_hot ON forum_posts(is_hot) WHERE is_hot = TRUE;
CREATE INDEX IF NOT EXISTS idx_forum_posts_tags ON forum_posts USING GIN(tags);

-- 论坛回复表索引
CREATE INDEX IF NOT EXISTS idx_forum_replies_post_id ON forum_replies(post_id);
CREATE INDEX IF NOT EXISTS idx_forum_replies_author_id ON forum_replies(author_id);
CREATE INDEX IF NOT EXISTS idx_forum_replies_parent_id ON forum_replies(parent_reply_id);
CREATE INDEX IF NOT EXISTS idx_forum_replies_created_at ON forum_replies(created_at ASC);

-- 论坛点赞表索引
CREATE INDEX IF NOT EXISTS idx_forum_likes_user_id ON forum_likes(user_id);
CREATE INDEX IF NOT EXISTS idx_forum_likes_post_id ON forum_likes(post_id);

-- 论坛回复点赞表索引
CREATE INDEX IF NOT EXISTS idx_forum_reply_likes_user_id ON forum_reply_likes(user_id);
CREATE INDEX IF NOT EXISTS idx_forum_reply_likes_reply_id ON forum_reply_likes(reply_id);

-- 文件上传表索引
CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_id ON uploaded_files(user_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_file_type ON uploaded_files(file_type);
CREATE INDEX IF NOT EXISTS idx_uploaded_files_created_at ON uploaded_files(created_at DESC);

-- 对话参与者表索引
CREATE INDEX IF NOT EXISTS idx_conversation_participants_conversation_id ON conversation_participants(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_participants_user_id ON conversation_participants(user_id);


-- 消息系统外键约束 (为解决循环依赖后添加)
ALTER TABLE messages
    ADD CONSTRAINT fk_messages_conversation
    FOREIGN KEY (conversation_id)
    REFERENCES conversations(id)
    ON DELETE CASCADE;

ALTER TABLE conversations
    ADD CONSTRAINT fk_conversations_last_message
    FOREIGN KEY (last_message_id)
    REFERENCES messages(id)
    ON DELETE SET NULL;


-- 创建触发器函数和触发器
-- 创建更新时间戳的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表添加更新时间戳触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_friends_updated_at BEFORE UPDATE ON friends FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- 更新帖子回复数量的触发器函数
CREATE OR REPLACE FUNCTION update_post_replies_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE forum_posts 
        SET replies_count = replies_count + 1,
            last_activity = NOW()
        WHERE id = NEW.post_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE forum_posts 
        SET replies_count = replies_count - 1,
            last_activity = NOW()
        WHERE id = OLD.post_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 帖子回复数量触发器
DROP TRIGGER IF EXISTS trigger_update_post_replies_count ON forum_replies;
CREATE TRIGGER trigger_update_post_replies_count
    AFTER INSERT OR DELETE ON forum_replies
    FOR EACH ROW
    EXECUTE FUNCTION update_post_replies_count();

-- 更新点赞数量的触发器函数
CREATE OR REPLACE FUNCTION update_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF TG_TABLE_NAME = 'forum_likes' THEN
            UPDATE forum_posts 
            SET likes_count = likes_count + 1 
            WHERE id = NEW.post_id;
        ELSIF TG_TABLE_NAME = 'forum_reply_likes' THEN
            UPDATE forum_replies 
            SET likes_count = likes_count + 1 
            WHERE id = NEW.reply_id;
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        IF TG_TABLE_NAME = 'forum_likes' THEN
            UPDATE forum_posts 
            SET likes_count = likes_count - 1 
            WHERE id = OLD.post_id;
        ELSIF TG_TABLE_NAME = 'forum_reply_likes' THEN
            UPDATE forum_replies 
            SET likes_count = likes_count - 1 
            WHERE id = OLD.reply_id;
        END IF;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 帖子点赞触发器
DROP TRIGGER IF EXISTS trigger_update_post_likes_count ON forum_likes;
CREATE TRIGGER trigger_update_post_likes_count
    AFTER INSERT OR DELETE ON forum_likes
    FOR EACH ROW
    EXECUTE FUNCTION update_likes_count();

-- 回复点赞触发器
DROP TRIGGER IF EXISTS trigger_update_reply_likes_count ON forum_reply_likes;
CREATE TRIGGER trigger_update_reply_likes_count
    AFTER INSERT OR DELETE ON forum_reply_likes
    FOR EACH ROW
    EXECUTE FUNCTION update_likes_count();


-- 创建视图以简化复杂查询
-- 论坛帖子列表视图 (包含作者信息)
CREATE OR REPLACE VIEW forum_posts_with_author AS
SELECT 
    fp.*,
    u.username as author_username,
    p.avatar_url as author_avatar,
    u.role as author_role
FROM forum_posts fp
JOIN users u ON fp.author_id = u.id
LEFT JOIN profiles p ON u.id = p.user_id;

-- 论坛回复列表视图 (包含作者信息)
CREATE OR REPLACE VIEW forum_replies_with_author AS
SELECT 
    fr.*,
    u.username as author_username,
    p.avatar_url as author_avatar,
    u.role as author_role
FROM forum_replies fr
JOIN users u ON fr.author_id = u.id
LEFT JOIN profiles p ON u.id = p.user_id;


-- 私信功能的函数
CREATE OR REPLACE FUNCTION get_conversation_between_users(user1_id_in INT, user2_id_in INT)
RETURNS TABLE(id INT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT cp1.conversation_id
    FROM conversation_participants AS cp1
    JOIN conversation_participants AS cp2 ON cp1.conversation_id = cp2.conversation_id
    WHERE cp1.user_id = user1_id_in AND cp2.user_id = user2_id_in
    LIMIT 1;
END;
$$;

CREATE OR REPLACE FUNCTION get_user_conversations(p_user_id INT, p_limit INT, p_offset INT)
RETURNS TABLE(
    conversation_id INT,
    other_user_details JSON,
    last_message_content TEXT,
    last_message_time TIMESTAMPTZ,
    unread_count BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH user_convs AS (
        SELECT c.id as conv_id, c.updated_at
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE cp.user_id = p_user_id
    ),
    other_participants AS (
        SELECT 
            uc.conv_id,
            u.id as other_user_id,
            json_build_object('id', u.id, 'username', u.username, 'avatar_url', u.avatar_url, 'role', u.role) as other_user_info
        FROM user_convs uc
        JOIN conversation_participants cp ON uc.conv_id = cp.conversation_id
        JOIN users u ON cp.user_id = u.id
        WHERE cp.user_id != p_user_id
    ),
    last_messages AS (
        SELECT 
            c.id as conv_id,
            m.content,
            m.created_at
        FROM conversations c
        LEFT JOIN messages m ON c.last_message_id = m.id
    ),
    unread_counts AS (
        SELECT 
            m.conversation_id as conv_id,
            count(*) as unread
        FROM messages m
        WHERE m.recipient_id = p_user_id AND NOT m.is_read
        GROUP BY m.conversation_id
    )
    SELECT 
        uc.conv_id,
        op.other_user_info,
        lm.content,
        lm.created_at,
        COALESCE(ucnt.unread, 0) as unread
    FROM user_convs uc
    JOIN other_participants op ON uc.conv_id = op.conv_id
    LEFT JOIN last_messages lm ON uc.conv_id = lm.conv_id
    LEFT JOIN unread_counts ucnt ON uc.conv_id = ucnt.conv_id
    ORDER BY uc.updated_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;


-- 最终提醒信息
DO $$
BEGIN
    RAISE NOTICE '数据库统一脚本执行完成！';
    RAISE NOTICE '已创建的表: users, profiles, friends, services, orders, reviews, messages, conversations, conversation_participants, forum_posts, forum_replies, forum_likes, forum_reply_likes, uploaded_files';
    RAISE NOTICE '已创建的索引: 所有主要查询优化索引';
    RAISE NOTICE '已创建的触发器: 自动更新统计数据和时间戳';
    RAISE NOTICE '已创建的视图: forum_posts_with_author, forum_replies_with_author';
    RAISE NOTICE '请使用此文件作为数据库结构的唯一真实来源。';
END $$;
