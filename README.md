# GBase-Wise 数据库产品经理助手

一个基于 LangChain 和 LangGraph 的智能助手，帮助 GBase8a 数据库产品经理完成竞品调研、市场分析、需求文档编写、技术支持和 SQL 生成等工作。

## 功能特性

### 核心功能
- ✅ **竞品数据库调研**：搜索和分析竞品数据库的产品特性、技术架构、市场表现
- ✅ **市场趋势分析**：了解数据库市场的最新趋势、技术发展方向
- ✅ **需求文档编写**：生成产品优化需求文档、竞品调研报告、市场分析文档
- ✅ **技术支持**：回答 GBase8a 数据库技术问题，生成 SQL 样例
- ✅ **SQL 生成与验证**：根据业务需求生成 GBase8a SQL 语句，并提供语法验证
- ✅ **持续学习**：通过记录正向/反向反馈，持续优化 SQL 生成效果
- ✅ **网页内容获取**：获取和分析网页内容
- ✅ **多语言风格**：支持 7 种对话风格（专业/亲和/简洁/幽默/技术/导师/温柔大姐姐）

### 高级功能（v2.0 新增）
- ✅ **对话压缩**：自动将过期对话压缩为摘要，保留关键信息
- ✅ **长期记忆**：将压缩后的对话存储到 PostgreSQL 和知识库，支持长期记忆检索
- ✅ **上下文感知**：基于历史对话上下文优化回答质量，提供更连贯的交互体验
- ✅ **数据持久化**：所有数据存储在 PostgreSQL，支持分布式部署
- ✅ **S3 备份**：支持将数据备份到 S3 对象存储，提供灾难恢复能力
- ✅ **数据迁移**：支持将本地文件数据迁移到 PostgreSQL

### 工具清单（22 个）
- 搜索工具（4 个）：web_search, search_competitor_info, search_market_trends, search_database_best_practices
- 知识库工具（3 个）：import_document_to_knowledge, search_knowledge_base, query_technical_detail
- 文档生成工具（4 个）：generate_requirement_doc, generate_competitor_report, generate_market_analysis_doc, generate_optimization_proposal
- 网页获取工具（4 个）：fetch_url, fetch_webpage_content, fetch_article_summary, fetch_document_content
- 语言风格工具（3 个）：list_available_styles, switch_language_style, get_current_style_info
- SQL 工具（4 个）：generate_sql, validate_sql, record_sql_feedback, manage_sql_examples

### 系统架构
```
用户对话 → 短期记忆（滑动窗口 20 轮）
         ↓
      超过阈值时触发压缩
         ↓
      对话压缩引擎（LLM 驱动）
         ├─ 提取关键信息（主题、意图、决策、结论、技术细节）
         ├─ 生成对话摘要（200-300 字）
         └─ 保留元数据（时间戳、会话 ID、原始消息数）
         ↓
      长期记忆存储
         ├─ PostgreSQL（结构化数据）
         └─ 知识库（全文检索）
         ↓
      上下文感知引擎
         ├─ 语义相似性匹配（70% 权重）
         ├─ 时间权重（越新越重要，20% 权重）
         └─ 重要性评分（10% 权重）
         ↓
      上下文注入器
         ├─ 作为独立消息注入
         └─ 注入到最后一条用户消息中
         ↓
      优化后的回答（基于短期 + 长期记忆）
```

## 技术栈

- **语言**：Python 3.x
- **框架**：
  - LangChain 1.0
  - LangGraph 1.0
  - LangChain OpenAI
- **模型**：Doubao (doubao-seed-1-6-251015)
- **SDK**：coze-coding-dev-sdk

## 项目结构

```
.
├── .scripts-local/               # 本地脚本（不会提交到仓库）
│   ├── setup_git.sh              # Git 一键配置脚本
│   └── git_push.sh               # 自动提交和推送脚本
├── .gitignore                    # Git 忽略文件
├── config/                       # 配置目录
│   └── agent_llm_config.json     # LLM 配置文件
├── docs/                         # 文档
│   ├── git_quickstart.md         # Git 快速开始指南
│   ├── git_config_guide.md       # Git 配置完整指南
│   └── security_audit_report.md  # 安全审计报告
├── scripts/                      # 脚本
│   └── init_migrate.py           # 初始化和迁移脚本
├── assets/                       # 资源目录
│   ├── sql_examples/             # SQL 示例库（本地）
│   │   ├── positive_examples.jsonl
│   │   └── negative_examples.jsonl
│   ├── language_styles.json      # 语言风格配置（本地）
│   ├── context_and_storage_optimization.md  # 优化方案文档
│   └── implementation_summary.md # 实施总结文档
├── src/                          # 项目源码
│   ├── agents/                   # Agent 代码
│   │   └── agent.py              # 主 Agent 实现
│   ├── tools/                    # 工具定义
│   │   ├── unified_search_tool.py
│   │   ├── unified_fetch_tool.py
│   │   ├── knowledge_tool.py
│   │   ├── document_generation_tool.py
│   │   ├── language_style_tool.py
│   │   ├── sql_generation_tool.py
│   │   ├── sql_validation_tool.py
│   │   └── sql_feedback_tool.py
│   ├── storage/                  # 存储实现
│   │   ├── database/             # 数据库
│   │   │   └── db.py             # PostgreSQL 连接
│   │   ├── memory/               # 短期记忆
│   │   │   └── memory_saver.py   # 内存/PostgreSQL 存储
│   │   ├── long_term/            # 长期记忆（v2.0 新增）
│   │   │   ├── models.py         # 数据模型
│   │   │   ├── conversation_compressor.py  # 对话压缩引擎
│   │   │   ├── long_term_storage.py        # 长期记忆存储
│   │   │   ├── compression_manager.py      # 对话压缩管理器
│   │   │   ├── context_retriever.py        # 上下文检索引擎
│   │   │   ├── context_injector.py         # 上下文注入器
│   │   │   └── agent_managers.py          # Agent 管理器单例
│   │   ├── migration/            # 数据迁移（v2.0 新增）
│   │   │   └── migrator.py       # 数据迁移工具
│   │   └── backup/               # 备份（v2.0 新增）
│   │       └── s3_backup_manager.py  # S3 备份管理器
│   └── utils/                    # 业务封装代码
├── migrations/                   # 数据库迁移脚本（v2.0 新增）
│   ├── 001_long_term_memory.sql  # 长期记忆表结构
│   └── 002_data_storage.sql      # SQL 示例和语言风格表结构
├── tests/                        # 单元测试
├── requirements.txt              # 依赖包列表
├── .coze                         # 配置文件
└── README.md                     # 项目说明
```

## 安全说明

### 敏感信息管理

项目采用分层安全策略，保护敏感信息不被泄露：

1. **环境变量**：
   - 所有敏感信息（API Key、数据库密码等）通过环境变量配置
   - 本地开发使用 `.env` 文件
   - 生产环境通过平台配置注入

2. **配置文件**：
   - `config/agent_llm_config.json` 已在 `.gitignore` 中
   - `assets/language_styles.json` 已在 `.gitignore` 中
   - 配置文件不会被提交到远程仓库

3. **本地脚本**：
   - Git 配置脚本位于 `.scripts-local/` 目录
   - `.scripts-local/` 目录已在 `.gitignore` 中
   - 本地脚本不会被提交到远程仓库

### SQL 安全

1. **参数化查询**：
   - 所有 SQL 查询使用参数化查询
   - 防止 SQL 注入攻击

2. **SQL 生成工具**：
   - SQL 生成工具只生成 SQL，不直接执行
   - 用户需手动复制并执行
   - 提供验证工具检查语法

### 安全审计

- 定期执行安全审计（见 `docs/security_audit_report.md`）
- 定期检查依赖项安全漏洞
- 更新有安全问题的依赖项

### 最佳实践

1. 不要将 `.env` 文件提交到仓库
2. 不要在代码中硬编码敏感信息
3. 定期更新依赖项
4. 定期执行安全审计
5. 使用强密码和密钥
6. 启用双因素认证（如适用）

## 快速开始

### 前置要求

- Python 3.8+
- pip
- Git
- SSH 密钥（用于 GitHub 访问）

### 配置 Git SSH 访问

#### 1. 生成 SSH 密钥（如果还没有）

```bash
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""
```

#### 2. 添加公钥到 GitHub

```bash
# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

访问 [GitHub SSH Keys](https://github.com/settings/keys)，将公钥添加进去。

#### 3. 测试连接

```bash
ssh -T git@github.com
```

如果看到 `Hi <username>! You've successfully authenticated...`，说明配置成功。

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件（可选）：

```bash
# LLM 配置
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
COZE_INTEGRATION_MODEL_BASE_URL=your_base_url

# 工作目录
COZE_WORKSPACE_PATH=/path/to/project
```

### 本地运行

#### 运行完整流程
```bash
bash scripts/local_run.sh -m flow
```

#### 运行单个节点
```bash
bash scripts/local_run.sh -m node -n node_name
```

#### 启动 HTTP 服务
```bash
bash scripts/http_run.sh -p 5000
```

## 部署指南

### 本地部署

1. 克隆项目
```bash
git clone git@github.com:EligahYy/GBase-Wise.git
cd GBase-Wise
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
export COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
export COZE_INTEGRATION_MODEL_BASE_URL=your_base_url
```

4. 运行
```bash
bash scripts/local_run.sh -m flow
```

### Docker 部署

1. 克隆项目
```bash
git clone git@github.com:EligahYy/GBase-Wise.git
cd GBase-Wise
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

3. 运行
```bash
docker-compose up -d
```

## 常用命令

### 本地开发

```json
{
    "styles": [
        {
            "id": "professional",
            "name": "专业严谨",
            "description": "正式、客观、专业，适合商务场景"
        },
        ...
    ]
}
```

## 使用示例

### 示例 1：竞品调研
```
用户：帮我调研 Oracle 数据库的最新特性
Agent：[调用 web_search 工具] → 返回 Oracle 数据库最新特性报告
```

### 示例 2：SQL 生成
```
用户：查询销售额超过 100 万的产品，按销售额降序排列
Agent：[调用 generate_sql 工具] → 返回 SQL 语句
用户：帮我验证这个 SQL 的语法
Agent：[调用 validate_sql 工具] → 返回验证结果
```

### 示例 3：切换语言风格
```
用户：切换到亲和友好的风格
Agent：[调用 switch_language_style 工具] → 风格已切换
```

## 开发指南

### 添加新工具

1. 在 `src/tools/` 下创建工具文件
2. 使用 `@tool` 装饰器定义工具函数
3. 在 `src/agents/agent.py` 中导入工具
4. 在 `config/agent_llm_config.json` 中添加工具名称

### 更新系统提示词

编辑 `config/agent_llm_config.json` 中的 `sp` 字段。

### 测试

```bash
# 运行测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_sql_generation.py
```

## v2.0 新特性

### 升级说明
v2.0 版本新增了对话压缩、长期记忆、上下文感知、数据持久化和 S3 备份功能。以下是升级步骤：

### 升级前准备
1. 备份现有数据（如果有）
2. 确保已配置 PostgreSQL 环境变量 `PGDATABASE_URL`
3. 确保已配置 S3 对象存储环境变量（如需备份功能）

### 升级步骤

#### 1. 拉取最新代码
```bash
git pull origin main
```

#### 2. 安装新依赖
```bash
pip install -r requirements.txt
```

#### 3. 执行数据库迁移
```bash
# 自动执行数据库迁移和数据迁移
python scripts/init_migrate.py

# 或分别执行
python scripts/init_migrate.py --skip-data-migration  # 只执行数据库迁移
python scripts/init_migrate.py --skip-db-migration    # 只执行数据迁移
```

#### 4. 重启服务
```bash
# 本地运行
bash scripts/local_run.sh -m flow

# Docker 部署
docker-compose down
docker-compose up -d
```

### 新增功能使用

#### 对话压缩
- 自动触发：消息数达到 100 时自动压缩
- 压缩间隔：每 24 小时最多压缩一次
- 保留策略：压缩后保留最近 20 条消息
- 长期记忆：压缩后的对话存储到 PostgreSQL 和知识库

#### 上下文感知
- 自动检索：每次对话自动检索相关历史上下文
- 智能排序：基于语义相似度、时间权重和重要性评分
- 上下文注入：将相关上下文注入到当前对话中
- 优化回答：基于历史对话上下文提供更连贯的回答

#### 数据持久化
- PostgreSQL 存储：所有数据存储在 PostgreSQL
- 分布式支持：支持多实例部署
- 数据迁移：支持将本地文件迁移到 PostgreSQL
- 备份恢复：支持 S3 对象存储备份

### 配置参数

#### 对话压缩配置
```python
# 在 src/agents/agent.py 中修改
AgentManagers.initialize(
    llm=llm,
    compression_threshold=100,      # 消息数阈值
    compression_interval_hours=24,  # 压缩间隔（小时）
    enable_compression=True,        # 启用压缩
)
```

#### 上下文感知配置
```python
# 在 src/agents/agent.py 中修改
AgentManagers.initialize(
    llm=llm,
    kb_table_name="long_term_conversations",  # 知识库数据集名称
    min_score=0.6,                           # 最小相似度阈值
    max_contexts=5,                          # 最大上下文数量
    enable_injection=True,                   # 启用注入
)
```

### 数据库表说明

#### memory.long_term_conversations
存储压缩后的对话摘要
- `thread_id`: 会话 ID
- `summary`: 对话摘要
- `key_info`: 关键信息（JSONB）
- `metadata`: 元数据（JSONB）
- `compressed_at`: 压缩时间
- `retention_days`: 保留天数（默认 90 天）

#### memory.conversation_key_info
存储对话关键信息索引
- `conversation_id`: 对话 ID
- `key_type`: 类型（topic/intent/decision/conclusion/technical_detail）
- `key_value`: 关键信息值
- `importance_score`: 重要性评分

#### memory.sql_examples
存储 SQL 示例（从本地文件迁移）
- `thread_id`: 会话 ID
- `business_requirement`: 业务需求
- `generated_sql`: 生成的 SQL
- `feedback_type`: 反馈类型（positive/negative）
- `feedback_comment`: 反馈评论

#### memory.language_styles
存储语言风格配置（从本地文件迁移）
- `style_id`: 风格 ID
- `style_name`: 风格名称
- `description`: 描述
- `称呼`: 用户称呼
- `tone`: 语气
- `greeting`: 问候语
- `closing`: 结束语
- `is_default`: 是否默认

### 数据迁移
v2.0 会自动将本地文件数据迁移到 PostgreSQL：
- SQL 示例：`assets/sql_examples/*.jsonl` → `memory.sql_examples`
- 语言风格：`assets/language_styles.json` → `memory.language_styles`

### S3 备份
如需使用 S3 备份功能，配置以下环境变量：
```bash
COZE_BUCKET_ENDPOINT_URL=https://your-s3-endpoint
COZE_BUCKET_NAME=your-bucket-name
```

备份方式：
```python
from storage.backup.s3_backup_manager import S3BackupManager

manager = S3BackupManager()
results = await manager.backup_all()  # 全量备份
```

### 数据清理
定期清理过期数据：
```python
# 清理过期长期记忆（90 天）
from storage.long_term.long_term_storage import LongTermMemoryStorage
storage = LongTermMemoryStorage()
await storage.cleanup_old_records(days=90)
```

## 常见问题

### Q1: 如何获取 API Key？
A: 请联系相关平台获取 Doubao 模型的 API Key。

### Q2: 如何修改端口号？
A: 修改 `scripts/http_run.sh` 中的 `-p` 参数。

### Q3: 如何查看日志？
A: 日志位置：`/app/work/logs/bypass/app.log`

### Q4: Docker 部署失败怎么办？
A: 检查 Docker 是否正确安装，使用 `docker logs` 查看详细错误信息。

### Q5: 如何更新到最新版本？
A:
```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 联系方式

- Issue: https://github.com/EligahYy/GBase-Wise/issues
- Email: eligahwsw@163.com

---

**祝你使用愉快！** 🚀
