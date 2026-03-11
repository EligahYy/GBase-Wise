# 快速开始指南

## v2.0 升级说明

如果你正在从 v1.x 升级到 v2.0，请执行以下升级步骤：

### 1. 拉取最新代码
```bash
git pull origin main
```

### 2. 安装新依赖
```bash
pip install -r requirements.txt
```

### 3. 执行数据库迁移
```bash
# 自动执行数据库迁移和数据迁移
python scripts/init_migrate.py
```

### 4. 重启服务
```bash
# 本地运行
bash scripts/local_run.sh -m flow

# Docker 部署
docker-compose down
docker-compose up -d
```

### 5. 验证升级
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

## 本地运行

### 1. 克隆项目
```bash
git clone git@github.com:EligahYy/GBase-Wise.git
cd GBase-Wise
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
export COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
export COZE_INTEGRATION_MODEL_BASE_URL=your_base_url
```

### 4. 运行
```bash
bash scripts/local_run.sh -m flow
```

---

## Docker 部署

### 1. 克隆项目
```bash
git clone git@github.com:EligahYy/GBase-Wise.git
cd GBase-Wise
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入 API Key 和 Base URL
```

### 3. 运行
```bash
docker-compose up -d
```

### 4. 访问服务
```
http://localhost:5000
```

---

## 常用命令

### 开发命令

```bash
# 运行完整流程
bash scripts/local_run.sh -m flow

# 运行单个节点
bash scripts/local_run.sh -m node -n node_name

# 启动 HTTP 服务
bash scripts/http_run.sh -p 5000

# 初始化和迁移
python scripts/init_migrate.py
```

### Git 命令

```bash
# 查看状态
git status

# 提交更改
git add .
git commit -m "feat: your message"

# 推送到远程仓库
git push origin main

# 拉取最新代码
git pull origin main
```

### Docker 命令

```bash
# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down

# 重启容器
docker-compose restart
```

---

## 安全最佳实践

1. **环境变量管理**：
   - 使用 `.env` 文件管理本地环境变量
   - 将 `.env` 文件添加到 `.gitignore`
   - 生产环境通过平台配置注入

2. **SSH 访问**：
   - 使用 SSH 访问 GitHub（已配置）
   - 定期更新 SSH 密钥
   - 不要将私钥提交到仓库

3. **敏感信息保护**：
   - 不要将 `.env` 文件提交到仓库
   - 不要在代码中硬编码敏感信息
   - 配置文件已在 `.gitignore` 中

4. **依赖项安全**：
   - 定期更新依赖项
   - 使用 `pip-audit` 扫描安全漏洞

---

## 故障排查

### 问题 1：连接 PostgreSQL 失败
```bash
# 检查环境变量
echo $PGDATABASE_URL

# 测试连接
python -c "
from storage.database.db import get_session
session = get_session()
print('连接成功')
"
```

### 问题 2：SSH 连接失败
```bash
# 测试 SSH 连接
ssh -T git@github.com

# 重新生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""
```

### 问题 3：依赖项安装失败
```bash
# 清理缓存后重新安装
pip cache purge
pip install -r requirements.txt --upgrade
```

---

## 更多文档

- [完整 README](README.md) - 项目详细说明
- [安全审计报告](docs/security_audit_report.md) - 安全性评估
- [更新日志](CHANGELOG.md) - 版本更新记录

---

## 获取帮助

如果遇到问题，请：
1. 查看本文档的故障排查部分
2. 查看 [安全审计报告](docs/security_audit_report.md)
3. 提交 Issue 到 GitHub 仓库
