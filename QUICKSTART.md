# 快速开始指南

## v2.0 升级说明

如果你正在从 v1.x 升级到 v2.0，请先执行以下升级步骤：

### 升级前准备
1. 备份现有数据（如果有）
2. 确保已配置 PostgreSQL 环境变量 `PGDATABASE_URL`
3. 确保已配置 S3 对象存储环境变量（如需备份功能）
4. **安全提醒**：确保 `.env` 文件不会提交到远程仓库
5. **安全提醒**：确保配置文件（`config/agent_llm_config.json`）不会提交到远程仓库

### 安全最佳实践

在部署过程中，请务必遵循以下安全实践：

1. **环境变量管理**：
   - 使用 `.env` 文件管理本地环境变量
   - 将 `.env` 文件添加到 `.gitignore`
   - 生产环境通过平台配置注入

2. **敏感文件保护**：
   - 配置文件（`config/agent_llm_config.json`）已在 `.gitignore` 中
   - 本地脚本（`.scripts-local/` 目录）已在 `.gitignore` 中
   - 不要提交任何包含敏感信息的文件

3. **Git 安全**：
   - 使用 `.scripts-local/setup_git.sh` 配置本地 Git
   - 使用 `.scripts-local/git_push.sh` 自动提交和推送
   - 检查 `.gitignore` 配置，确保敏感文件不会被提交

4. **依赖项安全**：
   - 定期更新依赖项
   - 使用 `pip-audit` 扫描依赖项安全漏洞
   - 修复有安全问题的依赖项

5. **数据库安全**：
   - 使用强密码
   - 限制数据库访问权限
   - 定期备份数据

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

# systemd 服务
sudo systemctl restart gbase8a-assistant
```

### 验证升级
```bash
# 检查数据库表
python -c "
from storage.database.db import get_session
session = get_session()
result = session.execute('SELECT COUNT(*) FROM memory.long_term_conversations')
print(f'长期记忆表记录数: {result.scalar()}')
"
```

---

## 方式一：GitHub 仓库管理

### 1. 提交代码到 GitHub

```bash
# 初始化 git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "feat: 初始化 GBase8a 数据库产品经理助手"

# 关联远程仓库
git remote add origin https://github.com/your-username/your-repo.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 2. 配置 GitHub Secrets（用于 CI/CD）

在你的 GitHub 仓库中，进入 `Settings` -> `Secrets and variables` -> `Actions`，添加以下 secrets：

- `DOCKER_USERNAME`: Docker Hub 用户名
- `DOCKER_PASSWORD`: Docker Hub 密码
- `SERVER_HOST`: 服务器地址
- `SERVER_USERNAME`: 服务器用户名
- `SERVER_SSH_KEY`: 服务器 SSH 私钥

### 3. 自动部署

当代码推送到 `main` 分支时，GitHub Actions 会自动：
1. 运行测试
2. 构建 Docker 镜像
3. 推送到 Docker Hub
4. 部署到服务器

---

## 方式二：本地/服务器一键部署

### Docker 部署（推荐）

#### 1. 克隆项目
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

#### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入 API Key 和 Base URL
```

#### 3. 一键部署
```bash
./deploy.sh
```

#### 4. 访问服务
```
http://localhost:5000
```

### 本地运行

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
export COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
export COZE_INTEGRATION_MODEL_BASE_URL=your_base_url
```

#### 4. 运行
```bash
# 运行完整流程
bash scripts/local_run.sh -m flow

# 或启动 HTTP 服务
bash scripts/http_run.sh -p 5000
```

---

## 方式三：服务器部署

### 使用自动化脚本

#### 1. 连接到服务器
```bash
ssh user@your-server
```

#### 2. 下载部署脚本
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

#### 3. 修改脚本配置
编辑 `scripts/server_deploy.sh`，设置 `GIT_REPO_URL` 变量为你的 GitHub 仓库地址。

#### 4. 运行部署脚本
```bash
sudo bash scripts/server_deploy.sh
```

#### 5. 配置环境变量
```bash
sudo nano /opt/gbase8a-assistant/.env
```

#### 6. 重启服务
```bash
sudo systemctl restart gbase8a-assistant
```

#### 7. 查看服务状态
```bash
sudo systemctl status gbase8a-assistant
```

---

## 常用命令

### Docker 相关
```bash
# 查看容器状态
docker ps

# 查看日志
docker logs -f gbase8a-assistant

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 进入容器
docker exec -it gbase8a-assistant bash
```

### systemd 相关
```bash
# 查看服务状态
sudo systemctl status gbase8a-assistant

# 启动服务
sudo systemctl start gbase8a-assistant

# 停止服务
sudo systemctl stop gbase8a-assistant

# 重启服务
sudo systemctl restart gbase8a-assistant

# 查看日志
sudo journalctl -u gbase8a-assistant -f

# 开机自启
sudo systemctl enable gbase8a-assistant
```

---

## 验证部署

### 1. 检查服务是否运行
```bash
curl http://localhost:5000/health
```

### 2. 测试功能
```bash
# 发送测试请求
curl -X POST http://localhost:5000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

---

## 更新部署

### Docker 更新
```bash
git pull origin main
docker-compose down
docker-compose pull
docker-compose up -d
```

### 服务器更新
```bash
cd /opt/gbase8a-assistant
git pull origin main
sudo systemctl restart gbase8a-assistant
```

---

## 故障排查

### 问题 1: 容器无法启动
```bash
# 查看日志
docker logs gbase8a-assistant

# 检查端口占用
netstat -tuln | grep 5000
```

### 问题 2: 服务无法访问
```bash
# 检查防火墙
sudo firewall-cmd --list-ports

# 开放端口
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

### 问题 3: 依赖安装失败
```bash
# 清理缓存
pip cache purge

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 获取帮助

- 查看日志：`docker logs -f gbase8a-assistant` 或 `journalctl -u gbase8a-assistant -f`
- GitHub Issues: https://github.com/your-username/your-repo/issues
- Email: your-email@example.com

---

**祝你部署顺利！** 🚀
