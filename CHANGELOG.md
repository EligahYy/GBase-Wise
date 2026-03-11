# 更新日志

## [2.0.1] - 2025-01-14

### 安全

- 🔒 删除明文 GitHub token 存储文件（`~/.git-credentials`）
- 🔒 移除 HTTPS 凭证助手配置（`credential.helper store`）
- 🔒 切换到 SSH 认证方式，提高安全性
- 🔒 验证 SSH 连接正常工作

### 文档

- 📚 精简 `README.md`，删除冗余部署说明
- 📚 重写 `QUICKSTART.md`，专注于快速开始和常用命令
- 📚 重写 `docs/git_quickstart.md`，添加常用命令速查表
- 📚 重写 `docs/git_config_guide.md`，详细说明 SSH 和 HTTPS 配置
- 📚 更新 `docs/security_audit_report.md`，记录安全改进
- 📚 所有文档推荐使用 SSH 认证方式

### 改进

- 🚀 简化文档结构，提高可读性
- 🚀 添加常用命令速查表
- 🚀 添加故障排查指南

---

## [2.0.0] - 2025-01-14

### 新增

#### 对话压缩与长期记忆
- ✨ 新增对话压缩引擎，自动将过期对话压缩为摘要
- ✨ 新增长期记忆存储，支持 PostgreSQL + 知识库双重存储
- ✨ 新增对话压缩管理器，支持自动触发和异步压缩
- ✨ 新增关键信息提取（主题、意图、决策、结论、技术细节）
- ✨ 新增对话摘要生成（200-300 字）

#### 上下文感知
- ✨ 新增上下文检索引擎，支持语义相似性匹配
- ✨ 新增上下文注入器，支持两种注入方式
- ✨ 新增智能排序算法（语义相似度 70%，时间权重 20%，重要性 10%）
- ✨ 新增上下文感知能力，基于历史对话优化回答质量

#### 数据持久化
- ✨ 新增 PostgreSQL 数据存储支持
- ✨ 新增 SQL 示例表（`memory.sql_examples`）
- ✨ 新增语言风格表（`memory.language_styles`）
- ✨ 新增长期记忆表（`memory.long_term_conversations`）
- ✨ 新增关键信息索引表（`memory.conversation_key_info`）

#### 数据迁移
- ✨ 新增数据迁移工具（`DataMigrator`）
- ✨ 支持将本地 JSONL 文件迁移到 PostgreSQL
- ✨ 支持将本地 JSON 文件迁移到 PostgreSQL
- ✨ 支持增量迁移（跳过已存在的记录）

#### S3 备份
- ✨ 新增 S3 备份管理器（`S3BackupManager`）
- ✨ 支持备份 SQL 示例到 S3
- ✨ 支持备份语言风格配置到 S3
- ✨ 支持备份长期记忆到 S3
- ✨ 支持全量备份、列出、下载和生成签名 URL

#### 语言风格
- ✨ 新增"温柔大姐姐"语言风格
- 🎨 现在支持 7 种对话风格

#### 工具增强
- 🔧 优化工具错误处理，添加自定义错误消息
- 🔧 优化工具调用体验

### 优化

- 🚀 Agent 架构优化，使用单例模式管理组件
- 🚀 数据库连接优化，支持连接池
- 🚀 异步压缩，不阻塞主流程
- 🚀 智能排序，优先返回相关上下文
- 📝 完善文档和代码注释

### 修复

- 🐛 修复 SQL 验证工具将 `DATE_FORMAT` 中 `FORM` 误判为拼写错误的问题
- 🐛 修复数据迁移工具的语言风格解析问题

### 安全

- 🔒 将 Git 配置脚本移动到 `.scripts-local/` 目录，防止提交到远程仓库
- 🔒 更新 `.gitignore`，添加 `.scripts-local/` 目录
- 🔒 完成项目安全审计，确认无敏感信息泄露风险
- 🔒 验证所有 SQL 查询使用参数化查询，防止 SQL 注入
- 🔒 验证文件操作使用固定路径前缀，防止路径遍历

### 文档

- 📚 新增 `assets/context_and_storage_optimization.md` 优化方案文档
- 📚 新增 `assets/implementation_summary.md` 实施总结文档
- 📚 新增 `docs/security_audit_report.md` 安全审计报告
- 📚 新增 `docs/git_config_guide.md` Git 配置完整指南
- 📚 新增 `docs/git_quickstart.md` Git 快速开始指南
- 📚 更新 `README.md`，添加 v2.0 新特性说明
- 📚 更新 `QUICKSTART.md`，添加升级指南

### 新增文件

#### 数据库迁移脚本
- `migrations/001_long_term_memory.sql` - 长期记忆表结构
- `migrations/002_data_storage.sql` - SQL 示例和语言风格表结构

#### 长期记忆模块
- `src/storage/long_term/__init__.py` - 模块初始化
- `src/storage/long_term/models.py` - 数据模型
- `src/storage/long_term/conversation_compressor.py` - 对话压缩引擎
- `src/storage/long_term/long_term_storage.py` - 长期记忆存储
- `src/storage/long_term/compression_manager.py` - 对话压缩管理器
- `src/storage/long_term/context_retriever.py` - 上下文检索引擎
- `src/storage/long_term/context_injector.py` - 上下文注入器
- `src/storage/long_term/agent_managers.py` - Agent 管理器单例

#### 数据迁移模块
- `src/storage/migration/migrator.py` - 数据迁移工具

#### 备份模块
- `src/storage/backup/s3_backup_manager.py` - S3 备份管理器

#### 脚本
- `scripts/init_migrate.py` - 初始化和迁移脚本

### 修改文件

- `src/agents/agent.py` - 集成对话压缩和上下文感知功能

### 依赖更新

- 新增 `coze-coding-dev-sdk` 依赖（S3 对象存储）

---

## [1.0.0] - 2024-XX-XX

### 新增

- ✨ 初始版本发布
- ✨ 竞品数据库调研功能
- ✨ 市场趋势分析功能
- ✨ 需求文档编写功能
- ✨ 技术支持功能
- ✨ SQL 生成与验证功能
- ✨ 持续学习功能
- ✨ 网页内容获取功能
- ✨ 多语言风格支持（6 种）

### 核心功能

- 搜索工具（4 个）：web_search, search_competitor_info, search_market_trends, search_database_best_practices
- 知识库工具（3 个）：import_document_to_knowledge, search_knowledge_base, query_technical_detail
- 文档生成工具（4 个）：generate_requirement_doc, generate_competitor_report, generate_market_analysis_doc, generate_optimization_proposal
- 网页获取工具（4 个）：fetch_url, fetch_webpage_content, fetch_article_summary, fetch_document_content
- 语言风格工具（3 个）：list_available_styles, switch_language_style, get_current_style_info
- SQL 工具（4 个）：generate_sql, validate_sql, record_sql_feedback, manage_sql_examples

### 技术栈

- Python 3.x
- LangChain 1.0
- LangGraph 1.0
- LangChain OpenAI
- Doubao (doubao-seed-1-6-251015)
- coze-coding-dev-sdk

---

## 版本说明

### 版本号规则

- **主版本号**：重大功能更新或不兼容的 API 变更
- **次版本号**：新增功能，向后兼容
- **修订号**：Bug 修复和小改进

### 标记说明

- ✨ 新增功能
- 🚀 性能优化
- 🐛 Bug 修复
- 📝 文档更新
- 🎨 UI/UX 改进
- 🔧 工具/配置更新
- 🗑️ 删除功能
- 🔒 安全更新
