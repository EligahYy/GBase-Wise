# Git 快速开始指南

## 最快方式（5 分钟）

### 1. 配置 SSH 访问（推荐）

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

访问 [GitHub SSH Keys](https://github.com/settings/keys)，将公钥添加进去。

### 2. 配置 Git 用户信息

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### 3. 克隆项目

```bash
git clone git@github.com:EligahYy/GBase-Wise.git
cd GBase-Wise
```

### 4. 开始工作

```bash
# 查看状态
git status

# 添加文件
git add .

# 提交
git commit -m "feat: your message"

# 推送
git push origin main
```

---

## 常用命令速查

### 初始化和克隆

```bash
# 初始化仓库
git init

# 克隆仓库（SSH）
git clone git@github.com:username/repo.git

# 克隆仓库（HTTPS）
git clone https://github.com/username/repo.git
```

### 日常操作

```bash
# 查看状态
git status

# 查看修改
git diff

# 查看提交历史
git log

# 查看最近的提交
git log --oneline -5
```

### 暂存和提交

```bash
# 添加所有文件
git add .

# 添加指定文件
git add file.txt

# 提交
git commit -m "feat: your message"

# 修改最后一次提交
git commit --amend
```

### 分支操作

```bash
# 查看分支
git branch

# 创建分支
git branch feature-x

# 切换分支
git checkout feature-x

# 创建并切换分支
git checkout -b feature-x

# 删除分支
git branch -d feature-x
```

### 远程操作

```bash
# 查看远程仓库
git remote -v

# 拉取最新代码
git pull origin main

# 推送到远程仓库
git push origin main

# 首次推送并设置默认分支
git push -u origin main

# 强制推送（谨慎使用）
git push -f origin main
```

---

## 提交消息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```bash
# 新功能
git commit -m "feat: 添加用户登录功能"

# 修复 Bug
git commit -m "fix: 修复登录页面样式问题"

# 文档更新
git commit -m "docs: 更新 README.md"

# 性能优化
git commit -m "perf: 优化数据库查询"

# 重构
git commit -m "refactor: 重构用户模块"

# 测试
git commit -m "test: 添加单元测试"

# 构建或工具
git commit -m "chore: 更新依赖项"
```

---

## 常见问题

### 问题 1：推送失败

```bash
# 拉取最新代码后合并
git pull origin main --rebase
git push origin main
```

### 问题 2：取消暂存的文件

```bash
# 取消所有暂存
git reset

# 取消指定文件
git reset file.txt
```

### 问题 3：撤销提交

```bash
# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD~1

# 撤销多次提交
git reset --hard HEAD~3
```

### 问题 4：忽略文件

创建 `.gitignore` 文件：

```bash
# 忽略 .env 文件
echo ".env" >> .gitignore

# 忽略 node_modules 目录
echo "node_modules/" >> .gitignore

# 忽略日志文件
echo "*.log" >> .gitignore
```

---

## 更多资源

- [完整 Git 配置指南](git_config_guide.md)
- [Git 官方文档](https://git-scm.com/docs)
- [GitHub Git 指南](https://guides.github.com/introduction/git/)
- [Conventional Commits 规范](https://www.conventionalcommits.org/)
