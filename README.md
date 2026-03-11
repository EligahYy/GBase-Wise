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
- ✅ **多语言风格**：支持 6 种对话风格（专业/亲和/简洁/幽默/技术/导师）

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
├── scripts/                      # 脚本（本地运行、HTTP 服务）
├── assets/                       # 资源目录
│   ├── sql_examples/             # SQL 示例库
│   │   ├── positive_examples.jsonl
│   │   └── negative_examples.jsonl
│   └── language_styles.json      # 语言风格配置
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
│   │   └── memory/
│   │       └── memory_saver.py
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

- Issue: https://github.com/your-username/your-repo/issues
- Email: your-email@example.com

---

**祝你使用愉快！** 🚀
