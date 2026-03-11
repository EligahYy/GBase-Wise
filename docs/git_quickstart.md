# Git 配置快速开始

## 一键配置（推荐）

运行快速配置脚本，交互式完成所有配置：

```bash
# 如果脚本不存在，先创建本地脚本目录
mkdir -p .scripts-local

# 从文档复制脚本内容到 .scripts-local/setup_git.sh
# 然后运行：
bash .scripts-local/setup_git.sh
```

**重要提示：**
- Git 配置脚本应保存在本地，不应提交到远程仓库
- 请将 `.scripts-local/` 目录的内容保留在本地
- `.scripts-local/` 目录已在 `.gitignore` 中，不会被提交到仓库

### 获取本地脚本

如果你还没有这些脚本，请从以下位置获取：

1. **setup_git.sh** - 一键配置脚本
   - 功能：交互式配置 Git 用户信息、SSH 密钥和远程仓库
   - 位置：项目根目录的 `.scripts-local/setup_git.sh`

2. **git_push.sh** - 自动提交和推送脚本
   - 功能：自动化提交和推送工作流
   - 位置：项目根目录的 `.scripts-local/git_push.sh`

你可以从项目维护者那里获取这些脚本，或者根据文档说明手动创建。

---

## 手动配置

### 步骤 1：配置 Git 用户信息

```bash
# 配置用户名
git config --global user.name "EligahYy"

# 配置邮箱
git config --global user.email "eligahwsw@163.com"

# 验证配置
git config --global user.name
git config --global user.email
```

### 步骤 2：配置认证方式

#### 方式 A：使用 SSH（推荐）

```bash
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "eligahwsw@163.com"

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 3. 添加到 GitHub：https://github.com/settings/keys

# 4. 更新远程仓库地址为 SSH
git remote set-url origin git@github.com:EligahYy/GBase-Wise.git

# 5. 测试连接
ssh -T git@github.com
```

#### 方式 B：使用 Personal Access Token

```bash
# 1. 生成 Token：https://github.com/settings/tokens
# 2. 配置凭证助手
git config --global credential.helper store
```

### 步骤 3：测试推送

```bash
# 使用推送脚本
bash scripts/git_push.sh "test: 初始化推送"
```

---

## 使用推送脚本

### 基本使用

```bash
# 使用默认提交信息
bash scripts/git_push.sh

# 使用自定义提交信息
bash scripts/git_push.sh "feat: 添加新功能"
```

### 脚本功能

- ✅ 自动检查是否有更改
- ✅ 自动拉取最新代码
- ✅ 自动添加所有更改
- ✅ 自动提交并推送
- ✅ 显示详细的状态信息
- ✅ 友好的错误提示

---

## 常用命令

### 查看状态
```bash
git status
```

### 手动提交和推送
```bash
# 1. 添加所有更改
git add .

# 2. 提交更改
git commit -m "你的提交信息"

# 3. 拉取最新代码
git pull origin main

# 4. 推送到远程仓库
git push origin main
```

### 查看日志
```bash
# 查看最近 5 条提交
git log -5

# 查看提交历史（图形化）
git log --oneline --graph --all
```

---

## 验证配置

```bash
# 查看远程仓库
git remote -v

# 查看用户配置
git config --global user.name
git config --global user.email

# 测试连接（SSH）
ssh -T git@github.com
```

---

## 故障排除

### 推送失败：authentication failed

**原因**：Token 无效或未配置

**解决方案**：
```bash
# 重新生成 Token
# 访问：https://github.com/settings/tokens

# 配置凭证助手
git config --global credential.helper store

# 重新推送，输入用户名和 Token
bash scripts/git_push.sh "test: 测试推送"
```

### 推送失败：Permission denied

**原因**：没有推送权限

**解决方案**：
- 检查是否是仓库的所有者或协作者
- 检查远程仓库地址是否正确

### 推送失败：Updates were rejected

**原因**：远程仓库有新的提交

**解决方案**：
```bash
# 方式 1：先拉取再推送
git pull origin main --rebase
bash scripts/git_push.sh "你的提交信息"

# 方式 2：强制推送（谨慎使用）
git push origin main --force
```

### SSH 连接失败

**原因**：SSH 密钥未添加到 GitHub

**解决方案**：
```bash
# 1. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 2. 添加到 GitHub
# 访问：https://github.com/settings/keys

# 3. 测试连接
ssh -T git@github.com
```

---

## 工作流建议

### 日常开发流程

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 进行开发或修改

# 3. 查看更改
git status

# 4. 提交并推送
bash scripts/git_push.sh "feat: 完成功能开发"
```

### 功能开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发功能

# 3. 提交更改
bash scripts/git_push.sh "feat: 添加新功能"

# 4. 合并到 main 分支
git checkout main
git pull origin main
git merge feature/new-feature
git push origin main
```

---

## 参考文档

- [Git 配置完整指南](git_config_guide.md)
- [GitHub 官方文档](https://docs.github.com)
- [Git 官方文档](https://git-scm.com/doc)

---

**配置完成后，你就可以随时将代码推送到自己的 GitHub 仓库了！** 🚀
