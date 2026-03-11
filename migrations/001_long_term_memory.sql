-- 创建长期记忆相关的表结构
-- 版本: 001
-- 日期: 2025-01-14

-- 创建长期记忆表
CREATE TABLE IF NOT EXISTS memory.long_term_conversations (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    key_info JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    compressed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retention_days INT DEFAULT 90
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_long_term_conversations_thread_id
    ON memory.long_term_conversations(thread_id);

CREATE INDEX IF NOT EXISTS idx_long_term_conversations_created_at
    ON memory.long_term_conversations(created_at);

CREATE INDEX IF NOT EXISTS idx_long_term_conversations_compressed_at
    ON memory.long_term_conversations(compressed_at);

-- 创建关键信息索引表
CREATE TABLE IF NOT EXISTS memory.conversation_key_info (
    id SERIAL PRIMARY KEY,
    conversation_id INT NOT NULL REFERENCES memory.long_term_conversations(id) ON DELETE CASCADE,
    key_type VARCHAR(50) NOT NULL,  -- topic, intent, decision, conclusion, technical_detail
    key_value TEXT NOT NULL,
    importance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_conversation_key_info_conversation_id
    ON memory.conversation_key_info(conversation_id);

CREATE INDEX IF NOT EXISTS idx_conversation_key_info_key_type
    ON memory.conversation_key_info(key_type);

CREATE INDEX IF NOT EXISTS idx_conversation_key_info_key_value
    ON memory.conversation_key_info(key_value);

-- 修改短期记忆表，添加压缩标记
ALTER TABLE memory.checkpoints
    ADD COLUMN IF NOT EXISTS retention_days INT DEFAULT 7;

ALTER TABLE memory.checkpoints
    ADD COLUMN IF NOT EXISTS is_compressed BOOLEAN DEFAULT FALSE;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_checkpoints_is_compressed
    ON memory.checkpoints(is_compressed);

CREATE INDEX IF NOT EXISTS idx_checkpoints_updated_at
    ON memory.checkpoints(updated_at);

COMMENT ON TABLE memory.long_term_conversations IS '长期记忆表，存储压缩后的对话摘要';
COMMENT ON TABLE memory.conversation_key_info IS '对话关键信息索引表';
COMMENT ON COLUMN memory.long_term_conversations.key_info IS 'JSONB 格式，包含 topics, intents, decisions, conclusions, technical_details';
COMMENT ON COLUMN memory.long_term_conversations.metadata IS 'JSONB 格式，包含 thread_id, created_at, compressed_at, original_message_count 等';
