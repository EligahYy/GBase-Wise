-- 创建 SQL 示例和语言风格相关的表结构
-- 版本: 002
-- 日期: 2025-01-14

-- 创建 SQL 示例表
CREATE TABLE IF NOT EXISTS memory.sql_examples (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255),
    business_requirement TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    feedback_type VARCHAR(20) NOT NULL CHECK (feedback_type IN ('positive', 'negative')),
    feedback_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_sql_examples_thread_id
    ON memory.sql_examples(thread_id);

CREATE INDEX IF NOT EXISTS idx_sql_examples_feedback_type
    ON memory.sql_examples(feedback_type);

CREATE INDEX IF NOT EXISTS idx_sql_examples_created_at
    ON memory.sql_examples(created_at);

-- 创建语言风格表
CREATE TABLE IF NOT EXISTS memory.language_styles (
    id SERIAL PRIMARY KEY,
    style_id VARCHAR(50) UNIQUE NOT NULL,
    style_name VARCHAR(100) NOT NULL,
    description TEXT,
    称呼 VARCHAR(50),
    tone VARCHAR(100),
    greeting VARCHAR(100),
    closing VARCHAR(100),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_language_styles_style_id
    ON memory.language_styles(style_id);

CREATE INDEX IF NOT EXISTS idx_language_styles_is_default
    ON memory.language_styles(is_default);

COMMENT ON TABLE memory.sql_examples IS 'SQL 示例表，存储业务需求和生成的 SQL 及反馈';
COMMENT ON TABLE memory.language_styles IS '语言风格配置表';
