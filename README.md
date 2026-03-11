# GBase8a 数据库产品经理助手

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
- ✅ **长期记忆**：自动压缩过期对话并存储到知识库，支持历史上下文检索
- ✅ **上下文感知**：基于历史对话上下文智能回答，提升回答质量
- ✅ **数据持久化**：所有数据存储在 PostgreSQL，支持分布式部署
- ✅ **S3 备份**：支持自动备份数据到 S3 对象存储

### 工具清单（22 个）
- 搜索工具（4 个）：web_search, search_competitor_info, search_market_trends, search_database_best_practices
- 知识库工具（3 个）：import_document_to_knowledge, search_knowledge_base, query_technical_detail
- 文档生成工具（4 个）：generate_requirement_doc, generate_competitor_report, generate_market_analysis_doc, generate_optimization_proposal
- 网页获取工具（4 个）：fetch_url, fetch_webpage_content, fetch_article_summary, fetch_document_content
- 语言风格工具（3 个）：list_available_styles, switch_language_style, get_current_style_info
- SQL 工具（4 个）：generate_sql, validate_sql, record_sql_feedback, manage_sql_examples

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
├── config/                       # 配置目录
│   └── agent_llm_config.json     # LLM 配置文件
├── docs/                         # 文档
├── scripts/                      # 脚本（本地运行、HTTP 服务、初始化迁移）
│   ├── init_migrate.py           # 数据库和数据迁移脚本
│   └── ...
├── assets/                       # 资源目录
│   ├── sql_examples/             # SQL 示例库（已迁移到 PostgreSQL）
│   │   ├── positive_examples.jsonl
│   │   └── negative_examples.jsonl
│   ├── language_styles.json      # 语言风格配置（已迁移到 PostgreSQL）
│   ├── context_and_storage_optimization.md  # 优化方案文档
│   └── implementation_summary.md # 实施总结文档
├── migrations/                   # 数据库迁移脚本
│   ├── 001_long_term_memory.sql  # 长期记忆表结构
│   └── 002_data_storage.sql      # SQL 示例和语言风格表结构
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
│   │   ├── memory/
│   │   │   └── memory_saver.py   # 短期记忆（PostgreSQL checkpointer）
│   │   ├── database/
│   │   │   └── db.py             # 数据库连接管理
│   │   ├── long_term/            # 长期记忆模块
│   │   │   ├── models.py         # 数据模型
│   │   │   ├── conversation_compressor.py  # 对话压缩引擎
│   │   │   ├── long_term_storage.py        # 长期记忆存储
│   │   │   ├── compression_manager.py      # 对话压缩管理器
│   │   │   ├── context_retriever.py        # 上下文检索引擎
│   │   │   ├── context_injector.py         # 上下文注入器
│   │   │   └── agent_managers.py           # Agent 管理器单例
│   │   ├── migration/            # 数据迁移模块
│   │   │   └── migrator.py       # 数据迁移工具
│   │   └── backup/               # 备份模块
│   │       └── s3_backup_manager.py  # S3 备份管理器
│   └── utils/                    # 业务封装代码
├── tests/                        # 单元测试
├── requirements.txt              # 依赖包列表
├── .coze                         # 配置文件
└── README.md                     # 项目说明
```

## 快速开始

### 前置要求

- Python 3.8+
- pip

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

### 方式一：本地部署

适用于开发和测试环境。

#### 1. 克隆项目
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
```bash
# Linux/Mac
export COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
export COZE_INTEGRATION_MODEL_BASE_URL=your_base_url

# Windows (PowerShell)
$env:COZE_WORKLOAD_IDENTITY_API_KEY="your_api_key"
$env:COZE_INTEGRATION_MODEL_BASE_URL="your_base_url"
```

#### 4. 运行
```bash
bash scripts/local_run.sh -m flow
```

### 方式二：Docker 部署（推荐）

适用于生产环境，一键部署。

#### 1. 安装 Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# macOS
brew install --cask docker

# Windows
# 下载并安装 Docker Desktop
```

#### 2. 使用一键部署脚本
```bash
# 给脚本添加执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

部署脚本会自动：
- 构建镜像
- 启动容器
- 配置端口映射
- 持久化数据

#### 3. 手动 Docker 部署

如果一键脚本失败，可以手动部署：

```bash
# 构建镜像
docker build -t gbase8a-assistant:latest .

# 运行容器
docker run -d \
  --name gbase8a-assistant \
  -p 5000:5000 \
  -v $(pwd)/assets:/app/assets \
  -v $(pwd)/config:/app/config \
  -e COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key \
  -e COZE_INTEGRATION_MODEL_BASE_URL=your_base_url \
  gbase8a-assistant:latest

# 查看日志
docker logs -f gbase8a-assistant

# 停止容器
docker stop gbase8a-assistant

# 删除容器
docker rm gbase8a-assistant
```

### 方式三：服务器部署

适用于云服务器（阿里云、腾讯云、AWS 等）。

#### 1. 准备服务器
- 操作系统：Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- Python 3.8+
- 至少 2GB 内存

#### 2. 克隆项目
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

#### 3. 使用部署脚本
```bash
chmod +x deploy.sh
./deploy.sh
```

#### 4. 使用 systemd 管理服务（可选）
```bash
# 创建服务文件
sudo cp scripts/gbase8a-assistant.service /etc/systemd/system/

# 启动服务
sudo systemctl start gbase8a-assistant

# 设置开机自启
sudo systemctl enable gbase8a-assistant

# 查看状态
sudo systemctl status gbase8a-assistant

# 查看日志
sudo journalctl -u gbase8a-assistant -f
```

## 配置说明

### 数据库配置

项目使用 PostgreSQL 作为主数据库，支持以下功能：
- 短期记忆存储（对话 checkpointer）
- 长期记忆存储（压缩后的对话）
- SQL 示例存储
- 语言风格配置存储

#### 环境变量

```bash
# 数据库连接（可选，默认使用平台提供）
PGDATABASE_URL=postgresql://user:password@host:port/database
```

#### 初始化数据库

首次部署需要执行数据库迁移：

```bash
# 执行所有迁移（数据库 + 数据）
python scripts/init_migrate.py

# 仅执行数据库迁移
python scripts/init_migrate.py --skip-data-migration

# 仅执行数据迁移
python scripts/init_migrate.py --skip-db-migration
```

### S3 对象存储配置（可选）

用于数据备份和灾难恢复。

#### 环境变量

```bash
# S3 配置
COZE_BUCKET_ENDPOINT_URL=https://your-s3-endpoint.com
COZE_BUCKET_NAME=your-bucket-name
```

#### 备份数据

```python
from storage.backup.s3_backup_manager import S3BackupManager

manager = S3BackupManager()

# 备份所有数据
results = await manager.backup_all()

# 仅备份 SQL 示例
key = await manager.backup_sql_examples()

# 列出备份文件
backups = manager.list_backups(backup_type="sql_examples")
```

### LLM 配置

编辑 `config/agent_llm_config.json`：

```json
{
    "config": {
        "model": "doubao-seed-1-6-251015",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_completion_tokens": 10000,
        "timeout": 600,
        "thinking": "disabled"
    },
    "sp": "...",
    "tools": [...]
}
```

### 语言风格配置

编辑 `assets/language_styles.json`：

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

## 最新更新（v2.0）

### 🚀 对话上下文与数据存储优化

本次更新引入了长期记忆和上下文感知能力，大幅提升了系统的智能性和可靠性。

#### 核心改进

1. **对话压缩机制**
   - 自动压缩超过 100 条消息的对话
   - 使用 LLM 提取关键信息（主题、意图、决策、结论、技术细节）
   - 生成 200-300 字的对话摘要
   - 将压缩后的对话存储到 PostgreSQL 和知识库
   - 异步压缩，不阻塞主流程

2. **上下文感知引擎**
   - 从短期记忆检索最近的消息
   - 从长期记忆检索相关历史上下文（通过知识库）
   - 语义相似性匹配 + 时间权重 + 重要性评分
   - 综合排序（语义相似度 70%，时间权重 20%，重要性 10%）
   - 支持最多 5 个上下文的检索和注入

3. **数据持久化优化**
   - 所有数据存储在 PostgreSQL，支持分布式部署
   - SQL 示例和语言风格配置从本地文件迁移到数据库
   - 支持 S3 对象存储备份，提供灾难恢复能力

4. **数据迁移工具**
   - 自动将本地 JSONL 文件迁移到 PostgreSQL
   - 支持增量迁移（跳过已存在的记录）
   - 迁移结果统计

#### 新增功能

- ✅ 长期记忆能力（保留历史对话）
- ✅ 上下文感知能力（基于历史上下文智能回答）
- ✅ 数据持久化能力（PostgreSQL + S3）
- ✅ S3 备份能力（自动备份数据）
- ✅ 7 种语言风格（新增温柔大姐姐风格）

#### 技术实现

**新增模块：**
- `src/storage/long_term/` - 长期记忆模块
  - `models.py` - 数据模型
  - `conversation_compressor.py` - 对话压缩引擎
  - `long_term_storage.py` - 长期记忆存储
  - `compression_manager.py` - 对话压缩管理器
  - `context_retriever.py` - 上下文检索引擎
  - `context_injector.py` - 上下文注入器
  - `agent_managers.py` - Agent 管理器单例

- `src/storage/migration/` - 数据迁移模块
  - `migrator.py` - 数据迁移工具

- `src/storage/backup/` - 备份模块
  - `s3_backup_manager.py` - S3 备份管理器

**数据库表结构：**
- `memory.long_term_conversations` - 长期记忆表
- `memory.conversation_key_info` - 关键信息索引表
- `memory.sql_examples` - SQL 示例表
- `memory.language_styles` - 语言风格表

**配置参数：**
- 对话压缩阈值：100 条消息
- 压缩间隔：24 小时
- 短期记忆保留：20 轮对话（40 条消息）
- 长期记忆保留：90 天
- 上下文检索数量：最多 5 条

#### 使用示例

**对话压缩（自动触发）：**
```python
# 当对话消息数达到 100 时，自动触发压缩
# 压缩后的对话存储到长期记忆，保留最近 20 条消息
```

**上下文检索（自动注入）：**
```python
# Agent 会自动检索相关历史上下文
# 并将上下文注入到当前对话中
# 提升回答的连贯性和准确性
```

**数据备份：**
```python
from storage.backup.s3_backup_manager import S3BackupManager

manager = S3BackupManager()
results = await manager.backup_all()
# 结果包含：SQL 示例、语言风格、长期记忆的备份 key
```

#### 详细文档

完整的优化方案和实施总结请参考：
- [优化方案文档](assets/context_and_storage_optimization.md)
- [实施总结文档](assets/implementation_summary.md)

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

### Q6: 首次部署需要做什么？
A: 首次部署需要执行数据库迁移：
```bash
python scripts/init_migrate.py
```

### Q7: 如何备份数据？
A: 使用 S3 备份管理器：
```python
from storage.backup.s3_backup_manager import S3BackupManager

manager = S3BackupManager()
await manager.backup_all()
```

### Q8: 对话压缩如何工作？
A: 当对话消息数达到 100 条时，系统会自动：
1. 使用 LLM 提取关键信息（主题、意图、决策、结论、技术细节）
2. 生成对话摘要
3. 将压缩后的对话存储到 PostgreSQL 和知识库
4. 保留最近 20 条消息在短期记忆中

### Q9: 如何清理过期的长期记忆？
A: 系统会自动清理 90 天前的长期记忆记录。如需手动清理：
```python
from storage.long_term.long_term_storage import LongTermMemoryStorage

storage = LongTermMemoryStorage()
await storage.cleanup_old_records(days=90)
```

### Q10: 如何配置 S3 备份？
A: 设置环境变量：
```bash
export COZE_BUCKET_ENDPOINT_URL=https://your-s3-endpoint.com
export COZE_BUCKET_NAME=your-bucket-name
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
