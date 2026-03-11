# 对话上下文与数据存储优化方案

## 分析日期
2025-01-14

---

## 一、当前数据存储方案分析

### 1.1 对话记忆存储

#### 当前方案
| 存储类型 | 方案 | 说明 | 问题 |
|---------|------|------|------|
| 优先方案 | PostgreSQL (AsyncPostgresSaver) | 通过环境变量 PGDATABASE_URL 配置 | - |
| 兜底方案 | MemorySaver | 内存存储，不持久化 | 重启后数据丢失 |

#### 配置位置
- 文件：`src/storage/memory/memory_saver.py`
- 配置：环境变量 `PGDATABASE_URL`
- 连接池：AsyncConnectionPool（min_size=1, max_idle=300）

#### 当前问题
1. ❌ 没有长期记忆机制
2. ❌ 超过滑动窗口（20 轮）的对话会被丢弃
3. ❌ 没有对话压缩和检索能力
4. ❌ 无法根据历史对话优化回答

### 1.2 其他数据存储

| 数据类型 | 存储方案 | 位置 | 问题 |
|---------|---------|------|------|
| SQL 示例 | 本地文件系统 | `assets/sql_examples/*.jsonl` | ❌ 不支持分布式部署 |
| 语言风格配置 | 本地文件系统 | `assets/language_styles.json` | ❌ 不支持分布式部署 |
| 知识库 | 云端服务 | coze-coding-dev-sdk | ✅ 无问题 |
| 生成的文档 | S3 对象存储 | 自动上传 | ✅ 无问题 |

---

## 二、对话上下文优化方案

### 2.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                     用户对话                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              短期记忆（当前活跃对话）                        │
│  - 滑动窗口：最近 20 轮对话（40 条消息）                    │
│  - 存储：PostgreSQL（内存缓存）                             │
│  - 保留时间：7 天（可配置）                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    超过阈值时触发
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              对话压缩引擎（LLM 驱动）                         │
│  1. 提取关键信息（用户意图、重要决策、关键结论）            │
│  2. 生成对话摘要（使用 LLM）                                 │
│  3. 保留元数据（时间戳、会话 ID、压缩时间）                   │
│  4. 建立上下文关联关系                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              长期记忆（压缩后的对话）                         │
│  - 存储：PostgreSQL + 知识库                                │
│  - 结构：会话摘要 + 关键信息索引                            │
│  - 保留时间：90 天（可配置）                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              上下文感知引擎（检索）                           │
│  1. 语义相似性匹配                                           │
│  2. 时间范围过滤                                             │
│  3. 会话关联查找                                             │
│  4. 重要性排序                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              优化后的回答                                     │
│  - 基于短期记忆的即时上下文                                 │
│  - 基于长期记忆的历史上下文                                 │
│  - 上下文关联的智能回答                                     │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 短期记忆（优化）

#### 设计方案
```python
class ShortTermMemory:
    """短期记忆管理"""
    
    def __init__(self, max_messages: int = 40, retention_days: int = 7):
        self.max_messages = max_messages  # 最大消息数
        self.retention_days = retention_days  # 保留天数
        self.checkpointer = get_memory_saver()  # PostgreSQL checkpointer
    
    def add_message(self, message: AnyMessage):
        """添加消息到短期记忆"""
        # 实现滑动窗口逻辑
        pass
    
    def get_recent_messages(self, limit: int = 10) -> List[AnyMessage]:
        """获取最近的消息"""
        pass
    
    def should_compress(self) -> bool:
        """判断是否需要压缩"""
        # 判断条件：
        # 1. 消息数超过阈值
        # 2. 会话时长超过阈值
        # 3. 距离上次压缩超过阈值
        pass
```

#### 存储结构（PostgreSQL）
```sql
-- 短期记忆表（已存在，优化字段）
CREATE TABLE IF NOT EXISTS memory.checkpoints (
    thread_id VARCHAR(255) PRIMARY KEY,
    checkpoint NAMESPACE,
    checkpoint_id VARCHAR(255),
    parent_checkpoint_id VARCHAR(255),
    type VARCHAR(255),
    checkpoint JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retention_days INT DEFAULT 7,  -- 新增：保留天数
    is_compressed BOOLEAN DEFAULT FALSE  -- 新增：是否已压缩
);
```

### 2.3 长期记忆（新增）

#### 压缩策略
```python
class ConversationCompressor:
    """对话压缩引擎"""
    
    async def compress_conversation(
        self,
        thread_id: str,
        messages: List[AnyMessage]
    ) -> CompressedConversation:
        """
        压缩对话为长期记忆
        
        Args:
            thread_id: 会话 ID
            messages: 消息列表
        
        Returns:
            压缩后的对话对象
        """
        # 1. 提取关键信息
        key_info = await self._extract_key_info(messages)
        
        # 2. 生成摘要
        summary = await self._generate_summary(messages)
        
        # 3. 保留元数据
        metadata = {
            "thread_id": thread_id,
            "created_at": datetime.now().isoformat(),
            "compressed_at": datetime.now().isoformat(),
            "original_message_count": len(messages),
            "key_topics": key_info["topics"],
            "user_intents": key_info["intents"]
        }
        
        # 4. 创建压缩对象
        compressed = CompressedConversation(
            summary=summary,
            key_info=key_info,
            metadata=metadata
        )
        
        return compressed
    
    async def _extract_key_info(
        self,
        messages: List[AnyMessage]
    ) -> Dict[str, Any]:
        """
        提取关键信息
        
        Returns:
            {
                "topics": List[str],  # 主题列表
                "intents": List[str],  # 用户意图列表
                "decisions": List[str],  # 重要决策
                "conclusions": List[str],  # 关键结论
                "technical_details": List[str]  # 技术细节
            }
        """
        prompt = f"""
        分析以下对话，提取关键信息：
        
        {self._format_messages(messages)}
        
        请提取：
        1. 对话主题（3-5 个关键词）
        2. 用户意图（1-3 个）
        3. 重要决策（如有）
        4. 关键结论（如有）
        5. 技术细节（如有）
        
        以 JSON 格式返回。
        """
        
        response = await self.llm.ainvoke(prompt)
        return json.loads(response.content)
    
    async def _generate_summary(
        self,
        messages: List[AnyMessage]
    ) -> str:
        """
        生成对话摘要
        
        Returns:
            摘要文本
        """
        prompt = f"""
        为以下对话生成简洁的摘要（200-300 字）：
        
        {self._format_messages(messages)}
        
        摘要应包含：
        1. 对话主题
        2. 主要讨论内容
        3. 关键结论或决策
        4. 未解决的问题（如有）
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
```

#### 存储结构（PostgreSQL）
```sql
-- 长期记忆表（新增）
CREATE TABLE IF NOT EXISTS memory.long_term_conversations (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    key_info JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    compressed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retention_days INT DEFAULT 90,
    INDEX idx_thread_id (thread_id),
    INDEX idx_created_at (created_at)
);

-- 关键信息索引表（新增）
CREATE TABLE IF NOT EXISTS memory.conversation_key_info (
    id SERIAL PRIMARY KEY,
    conversation_id INT REFERENCES memory.long_term_conversations(id),
    key_type VARCHAR(50) NOT NULL,  -- topic, intent, decision, conclusion, technical_detail
    key_value TEXT NOT NULL,
    importance_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_key_type (key_type),
    INDEX idx_key_value (key_value)
);
```

#### 知识库集成
```python
class LongTermMemoryStorage:
    """长期记忆存储"""
    
    async def store_to_knowledge_base(
        self,
        compressed: CompressedConversation
    ) -> str:
        """
        将压缩的对话存储到知识库
        
        Returns:
            文档 ID
        """
        # 构建知识库文档
        content = f"""
# 对话摘要

{compressed.summary}

## 关键信息

### 主题
{', '.join(compressed.key_info['topics'])}

### 用户意图
{', '.join(compressed.key_info['intents'])}

### 重要决策
{', '.join(compressed.key_info['decisions']) if compressed.key_info['decisions'] else '无'}

### 关键结论
{', '.join(compressed.key_info['conclusions']) if compressed.key_info['conclusions'] else '无'}

### 技术细节
{', '.join(compressed.key_info['technical_details']) if compressed.key_info['technical_details'] else '无'}

## 元数据

- 会话 ID: {compressed.metadata['thread_id']}
- 创建时间: {compressed.metadata['created_at']}
- 原始消息数: {compressed.metadata['original_message_count']}
"""
        
        # 导入到知识库
        client = KnowledgeClient()
        doc = KnowledgeDocument(
            source=DataSourceType.TEXT,
            raw_data=content,
            metadata=compressed.metadata
        )
        
        response = client.add_documents(
            documents=[doc],
            table_name="long_term_conversations"
        )
        
        return response.doc_ids[0]
```

### 2.4 上下文感知（新增）

#### 检索引擎
```python
class ContextRetriever:
    """上下文感知检索引擎"""
    
    async def retrieve_context(
        self,
        thread_id: str,
        current_query: str,
        limit: int = 5
    ) -> List[ContextItem]:
        """
        检索相关上下文
        
        Args:
            thread_id: 会话 ID
            current_query: 当前查询
            limit: 返回数量
        
        Returns:
            相关上下文列表
        """
        # 1. 从短期记忆检索（最近 20 轮）
        short_term = await self._retrieve_short_term(thread_id, limit=3)
        
        # 2. 从长期记忆检索（知识库）
        long_term = await self._retrieve_long_term(thread_id, current_query, limit=2)
        
        # 3. 合并和排序
        contexts = short_term + long_term
        contexts = self._rank_contexts(contexts, current_query)
        
        return contexts[:limit]
    
    async def _retrieve_long_term(
        self,
        thread_id: str,
        query: str,
        limit: int
    ) -> List[ContextItem]:
        """
        从长期记忆检索
        
        Returns:
            相关上下文列表
        """
        client = KnowledgeClient()
        
        # 构建检索查询
        search_query = f"""
        会话 ID: {thread_id}
        查询: {query}
        
        请检索相关的历史对话摘要和关键信息。
        """
        
        response = client.search(
            query=search_query,
            top_k=limit,
            min_score=0.6
        )
        
        contexts = []
        for chunk in response.chunks:
            contexts.append(ContextItem(
                content=chunk.content,
                score=chunk.score,
                source="long_term",
                metadata=chunk.metadata
            ))
        
        return contexts
    
    def _rank_contexts(
        self,
        contexts: List[ContextItem],
        query: str
    ) -> List[ContextItem]:
        """
        对上下文进行排序
        
        排序规则：
        1. 语义相似度（score）
        2. 时间权重（越新越重要）
        3. 重要性权重（元数据中的 importance）
        """
        now = datetime.now()
        
        for context in contexts:
            # 计算时间权重（7 天内权重 1.0，之后线性递减）
            if context.metadata.get('created_at'):
                created_at = datetime.fromisoformat(context.metadata['created_at'])
                days_ago = (now - created_at).days
                time_weight = max(0.1, 1.0 - days_ago / 90)
            else:
                time_weight = 0.5
            
            # 计算重要性权重
            importance = context.metadata.get('importance', 1.0)
            
            # 综合评分
            context.final_score = context.score * 0.7 + time_weight * 0.2 + importance * 0.1
        
        # 按综合评分降序排序
        contexts.sort(key=lambda x: x.final_score, reverse=True)
        
        return contexts
```

#### 上下文注入
```python
class ContextInjector:
    """上下文注入器"""
    
    async def inject_context(
        self,
        messages: List[AnyMessage],
        contexts: List[ContextItem]
    ) -> List[AnyMessage]:
        """
        将检索到的上下文注入到消息中
        
        Args:
            messages: 原始消息列表
            contexts: 检索到的上下文
        
        Returns:
            注入上下文后的消息列表
        """
        if not contexts:
            return messages
        
        # 构建上下文消息
        context_message = self._build_context_message(contexts)
        
        # 在用户消息之前插入上下文消息
        # 找到最后一条用户消息的位置
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].type == "human":
                messages.insert(i, context_message)
                break
        
        return messages
    
    def _build_context_message(
        self,
        contexts: List[ContextItem]
    ) -> SystemMessage:
        """
        构建上下文消息
        
        Returns:
            系统消息
        """
        context_text = "## 相关历史上下文\n\n"
        
        for i, context in enumerate(contexts, 1):
            source = "短期记忆" if context.source == "short_term" else "长期记忆"
            context_text += f"### {source} (相关度: {context.score:.2%})\n\n"
            context_text += f"{context.content}\n\n"
        
        return SystemMessage(content=context_text)
```

---

## 三、数据存储优化方案

### 3.1 存储策略

| 数据类型 | 当前方案 | 优化方案 | 说明 |
|---------|---------|---------|------|
| 对话记忆 | PostgreSQL | PostgreSQL（短期）+ PostgreSQL（长期） | 分层存储 |
| SQL 示例 | 本地文件系统 | PostgreSQL + S3 对象存储 | 持久化 + 备份 |
| 语言风格配置 | 本地文件系统 | PostgreSQL | 支持分布式部署 |
| 生成的文档 | S3 对象存储 | S3 对象存储 | 无需优化 |
| 知识库 | 云端服务 | 云端服务 | 无需优化 |

### 3.2 PostgreSQL 表结构优化

#### SQL 示例表（新增）
```sql
-- SQL 示例表（替代本地 JSONL 文件）
CREATE TABLE IF NOT EXISTS memory.sql_examples (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR(255),
    business_requirement TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    feedback_type VARCHAR(20) NOT NULL,  -- positive/negative
    feedback_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_thread_id (thread_id),
    INDEX idx_feedback_type (feedback_type),
    INDEX idx_created_at (created_at)
);
```

#### 语言风格表（新增）
```sql
-- 语言风格表（替代本地 JSON 文件）
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
```

#### 数据清理策略
```sql
-- 清理过期的长期记忆
DELETE FROM memory.long_term_conversations
WHERE compressed_at < NOW() - INTERVAL '90 days';

-- 清理过期的短期记忆
DELETE FROM memory.checkpoints
WHERE updated_at < NOW() - INTERVAL '7 days'
  AND is_compressed = TRUE;

-- 清理旧的 SQL 示例（可选）
DELETE FROM memory.sql_examples
WHERE created_at < NOW() - INTERVAL '180 days';
```

### 3.3 S3 对象存储集成

#### 备份策略
```python
class S3BackupManager:
    """S3 备份管理器"""
    
    def __init__(self):
        self.storage_client = StorageClient()
        self.bucket_name = "gbase8a-assistant-backups"
    
    async def backup_sql_examples(self):
        """备份 SQL 示例到 S3"""
        # 1. 从 PostgreSQL 导出数据
        examples = await self._export_sql_examples()
        
        # 2. 上传到 S3
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"sql_examples/backup_{timestamp}.jsonl"
        
        content = "\n".join([json.dumps(e, ensure_ascii=False) for e in examples])
        url = self.storage_client.upload_object(
            bucket=self.bucket_name,
            key=key,
            content=content.encode('utf-8')
        )
        
        return url
    
    async def backup_language_styles(self):
        """备份语言风格配置到 S3"""
        # 1. 从 PostgreSQL 导出数据
        styles = await self._export_language_styles()
        
        # 2. 上传到 S3
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"language_styles/backup_{timestamp}.json"
        
        content = json.dumps(styles, ensure_ascii=False, indent=2)
        url = self.storage_client.upload_object(
            bucket=self.bucket_name,
            key=key,
            content=content.encode('utf-8')
        )
        
        return url
```

---

## 四、实施计划

### 阶段一：对话压缩机制（1-2 周）

#### 任务清单
1. ✅ 设计对话压缩引擎
2. ✅ 创建长期记忆表结构
3. ✅ 实现对话压缩功能
4. ✅ 集成知识库存储
5. ⏳ 测试压缩功能
6. ⏳ 优化压缩算法

#### 文件清单
- `src/storage/memory/conversation_compressor.py` - 对话压缩引擎
- `src/storage/memory/long_term_storage.py` - 长期记忆存储
- `migrations/001_add_long_term_conversations.sql` - 数据库迁移

### 阶段二：上下文感知（1-2 周）

#### 任务清单
1. ✅ 设计上下文检索引擎
2. ✅ 实现短期记忆检索
3. ✅ 实现长期记忆检索
4. ✅ 实现上下文排序
5. ✅ 实现上下文注入
6. ⏳ 测试上下文感知功能

#### 文件清单
- `src/storage/memory/context_retriever.py` - 上下文检索引擎
- `src/storage/memory/context_injector.py` - 上下文注入器
- `migrations/002_add_conversation_key_info.sql` - 数据库迁移

### 阶段三：数据存储优化（1 周）

#### 任务清单
1. ✅ 设计 SQL 示例表
2. ✅ 设计语言风格表
3. ✅ 实现数据迁移工具
4. ✅ 实现 S3 备份功能
5. ⏳ 测试数据迁移
6. ⏳ 测试备份功能

#### 文件清单
- `migrations/003_add_sql_examples.sql` - 数据库迁移
- `migrations/004_add_language_styles.sql` - 数据库迁移
- `src/storage/backup/s3_backup_manager.py` - S3 备份管理器
- `src/storage/migration/migrator.py` - 数据迁移工具

---

## 五、优势与风险

### 5.1 优势

| 优势 | 说明 |
|------|------|
| 长期记忆 | 保留历史对话，支持上下文感知 |
| 智能回答 | 基于历史上下文优化回答质量 |
| 数据持久化 | 所有数据存储在 PostgreSQL，支持分布式部署 |
| 自动备份 | S3 对象存储提供灾难恢复能力 |
| 可扩展性 | 支持水平扩展，适应业务增长 |
| 成本优化 | 定期清理过期数据，降低存储成本 |

### 5.2 风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 压缩质量 | LLM 压缩可能丢失重要信息 | 多轮验证，人工审核 |
| 检索精度 | 上下文检索可能不准确 | 优化算法，调整阈值 |
| 存储成本 | 长期记忆可能占用大量存储 | 定期清理，压缩数据 |
| 性能影响 | 压缩和检索可能影响性能 | 异步处理，缓存优化 |
| 数据迁移 | 迁移可能导致数据丢失 | 充分测试，备份原始数据 |

---

## 六、监控与维护

### 6.1 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| 对话压缩成功率 | 压缩成功的对话数 / 总对话数 | < 95% |
| 上下文检索耗时 | 检索上下文的平均耗时 | > 1s |
| 长期记忆存储量 | 长期记忆占用的存储空间 | > 10GB |
| 数据库连接池使用率 | 连接池的使用率 | > 80% |
| S3 备份成功率 | S3 备份成功的次数 / 总备份次数 | < 95% |

### 6.2 维护计划

| 任务 | 频率 | 说明 |
|------|------|------|
| 数据清理 | 每周 | 清理过期的长期记忆 |
| 数据备份 | 每天 | 备份 SQL 示例和语言风格配置 |
| 性能优化 | 每月 | 分析性能瓶颈，优化算法 |
| 存储审计 | 每季度 | 审计存储使用情况，优化成本 |

---

## 七、总结

### 7.1 当前存储方案
- ✅ 对话记忆：PostgreSQL（短期）
- ❌ 没有长期记忆
- ❌ SQL 示例：本地文件系统（不支持分布式）
- ❌ 语言风格：本地文件系统（不支持分布式）

### 7.2 优化后存储方案
- ✅ 对话记忆：PostgreSQL（短期）+ PostgreSQL（长期）+ 知识库
- ✅ SQL 示例：PostgreSQL + S3 对象存储（备份）
- ✅ 语言风格：PostgreSQL
- ✅ 支持分布式部署
- ✅ 支持长期记忆
- ✅ 支持上下文感知

### 7.3 实施时间线
- **阶段一**：1-2 周（对话压缩机制）
- **阶段二**：1-2 周（上下文感知）
- **阶段三**：1 周（数据存储优化）
- **总计**：3-5 周

---

**优化完成后，系统将具备长期记忆能力，能够基于历史对话上下文优化回答质量，并且数据存储更加可靠和可扩展。** 🚀
