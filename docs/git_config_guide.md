# GitHub 仓库配置指南

## 当前状态检查

### ✅ 远程仓库已配置
```
origin	https://github.com/EligahYy/GBase-Wise.git (fetch)
origin	https://github.com/EligahYy/GBase-Wise.git (push)
```

你的远程仓库已经正确配置为：`https://github.com/EligahYy/GBase-Wise.git`

### ⚠️ Git 用户信息需要更新
当前配置：
```
用户名: agent
邮箱: 2033455007539676-agent@noreply.coze.cn
```

需要配置为你自己的 GitHub 用户信息。

---

## 配置步骤

### 步骤 1：配置 Git 用户信息

```bash
# 配置用户名（替换为你的 GitHub 用户名）
git config --global user.name "EligahYy"

# 配置邮箱（替换为你的 GitHub 邮箱）
git config --global user.email "eligahwsw@163.com"
```

### 步骤 2：验证配置

```bash
# 查看配置
git config --global user.name
git config --global user.email
```

### 步骤 3：配置 GitHub Token（推荐使用 SSH）

#### 方式一：使用 Personal Access Token（HTTPS）

1. 生成 GitHub Token：
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 勾选 `repo` 权限
   - 点击 "Generate token"
   - 复制生成的 token（只显示一次，请妥善保存）

2. 配置 Git 凭证：
```bash
# 方式 A：使用 Git Credential Helper（推荐）
git config --global credential.helper store

# 方式 B：每次推送时手动输入 token
# 在推送时输入用户名和 token 作为密码
```

#### 方式二：使用 SSH 密钥（推荐，更安全）

1. 生成 SSH 密钥：
```bash
ssh-keygen -t ed25519 -C "eligahwsw@163.com"
```

2. 查看公钥：
```bash
cat ~/.ssh/id_ed25519.pub
```

3. 添加 SSH 密钥到 GitHub：
   - 访问 https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴公钥内容
   - 点击 "Add SSH key"

4. 更新远程仓库地址：
```bash
git remote set-url origin git@github.com:EligahYy/GBase-Wise.git
```

5. 测试连接：
```bash
ssh -T git@github.com
```

---

## 安全说明

### ⚠️ 重要提示

**Git 配置脚本和自动化脚本应保存在本地，不应提交到远程仓库！**

为了保护你的仓库安全：

1. **本地脚本目录**：
   - 使用 `.scripts-local/` 目录存储本地脚本
   - 该目录已在 `.gitignore` 中，不会被提交到仓库

2. **敏感信息保护**：
   - 不要在代码中硬编码 API Key、Token 等敏感信息
   - 使用环境变量存储敏感信息
   - 定期更换 Token 和密码

3. **SSH 密钥管理**：
   - SSH 私钥应妥善保管
   - 不要将私钥提交到仓库
   - 使用强密码保护私钥

### 安全检查清单

- [ ] Git 配置脚本保存在本地（`.scripts-local/` 目录）
- [ ] 不要在代码中硬编码敏感信息
- [ ] 使用环境变量存储 API Key 和 Token
- [ ] SSH 私钥已妥善保管
- [ ] 定期更换 Token
- [ ] 使用强密码
- [ ] 启用双因素认证（2FA）

---

## 自动提交和推送脚本

> **安全提示**：此脚本应保存在本地 `.scripts-local/` 目录中，不应提交到远程仓库。

创建一个便捷的脚本来自动提交和推送代码：

### 创建 `scripts/git_push.sh`

```bash
#!/bin/bash

# 检查是否有更改
if [ -z "$(git status --porcelain)" ]; then
    echo "没有需要提交的更改"
    exit 0
fi

# 拉取最新代码
echo "正在拉取最新代码..."
git pull origin main

# 添加所有更改
echo "正在添加所有更改..."
git add .

# 提交更改
if [ -n "$1" ]; then
    # 使用传入的提交信息
    git commit -m "$1"
else
    # 使用默认提交信息
    git commit -m "chore: 更新代码 $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送到远程仓库
echo "正在推送到远程仓库..."
git push origin main

echo "完成！"
```

### 使用方法

```bash
# 添加执行权限
chmod +x scripts/git_push.sh

# 使用默认提交信息
bash scripts/git_push.sh

# 使用自定义提交信息
bash scripts/git_push.sh "feat: 添加新功能"
```

---

## 工作流程

### 方式一：手动提交和推送

```bash
# 1. 查看更改
git status

# 2. 添加更改
git add .

# 3. 提交更改
git commit -m "你的提交信息"

# 4. 推送到远程仓库
git push origin main
```

### 方式二：使用自动脚本

```bash
# 一键提交和推送
bash scripts/git_push.sh "feat: 添加新功能"
```

### 方式三：推送到不同分支

```bash
# 创建并切换到新分支
git checkout -b feature/new-feature

# 提交更改
git add .
git commit -m "feat: 添加新功能"

# 推送到远程仓库
git push -u origin feature/new-feature
```

---

## 常用 Git 命令

### 查看状态
```bash
git status
```

### 查看更改
```bash
git diff                    # 查看未暂存的更改
git diff --staged          # 查看已暂存的更改
git diff HEAD             # 查看所有更改
```

### 添加更改
```bash
git add .                  # 添加所有更改
git add filename           # 添加特定文件
git add *.py              # 添加所有 Python 文件
```

### 提交更改
```bash
git commit -m "提交信息"
git commit -am "提交信息"  # 添加并提交所有已跟踪文件的更改
```

### 推送和拉取
```bash
git push origin main                    # 推送到 main 分支
git pull origin main                    # 拉取 main 分支
git pull origin main --rebase          # 使用 rebase 方式拉取
```

### 分支操作
```bash
git branch                    # 查看所有分支
git branch -a                # 查看所有本地和远程分支
git checkout -b new-branch   # 创建并切换到新分支
git checkout main            # 切换到 main 分支
git branch -d branch-name   # 删除本地分支
git push origin --delete branch-name  # 删除远程分支
```

### 撤销操作
```bash
git checkout -- filename     # 撤销对文件的更改
git reset HEAD filename      # 从暂存区移除文件
git reset --soft HEAD~1      # 撤销上一次提交（保留更改）
git reset --hard HEAD~1      # 撤销上一次提交（丢弃更改）
```

---

## 配置检查清单

- [ ] 配置 Git 用户名和邮箱
- [ ] 生成 GitHub Token 或 SSH 密钥
- [ ] 配置 Git 凭证或 SSH 密钥
- [ ] 测试连接到 GitHub
- [ ] 创建便捷的提交脚本
- [ ] 测试提交和推送

---

## 常见问题

### Q1: 推送时提示 authentication failed？
A: 检查 Token 是否正确，或者重新生成 Token。

### Q2: 推送时提示 Permission denied？
A: 检查仓库权限，确保你有推送权限。

### Q3: 如何撤销上一次推送？
A:
```bash
git reset --hard HEAD~1          # 撤销本地提交
git push origin main --force     # 强制推送（谨慎使用）
```

### Q4: 如何合并分支？
A:
```bash
git checkout main              # 切换到 main 分支
git merge feature-branch       # 合并 feature-branch
git push origin main           # 推送合并结果
```

### Q5: 如何解决冲突？
A:
1. 编辑冲突的文件
2. 标记冲突已解决
3. 提交更改
```bash
git status                     # 查看冲突文件
git add filename               # 标记冲突已解决
git commit                     # 提交更改
```

---

## 推荐的 Git 工作流

### 功能开发流程
1. 从 main 分支创建功能分支
2. 在功能分支上进行开发
3. 提交更改并推送到远程
4. 创建 Pull Request（可选）
5. 合并到 main 分支

### 日常更新流程
1. 拉取最新代码：`git pull origin main`
2. 进行开发或修改
3. 提交更改：`git add . && git commit -m "信息"`
4. 推送到远程：`git push origin main`

---

## 安全建议

1. **使用 SSH 密钥**：比 Token 更安全，无需频繁输入密码
2. **定期更换 Token**：如果使用 Token，建议定期更换
3. **不要提交敏感信息**：不要提交 API Key、密码等敏感信息
4. **使用 .gitignore**：忽略不需要提交的文件
5. **定期备份**：定期备份重要代码

---

## 快速参考

### 完整的推送流程
```bash
# 1. 查看状态
git status

# 2. 添加更改
git add .

# 3. 提交更改
git commit -m "你的提交信息"

# 4. 拉取最新代码
git pull origin main

# 5. 推送到远程
git push origin main
```

### 使用脚本一键推送
```bash
bash scripts/git_push.sh "你的提交信息"
```

---

**配置完成后，你就可以随时将代码推送到自己的 GitHub 仓库了！** 🚀
