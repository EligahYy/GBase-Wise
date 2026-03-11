# Git 配置指南

## 前置要求

- Git 2.x
- SSH 密钥（推荐）或 Personal Access Token

---

## 方式一：SSH 认证（推荐）

### 1. 生成 SSH 密钥

```bash
# 生成 ed25519 密钥（推荐）
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""

# 或生成 RSA 密钥（兼容性更好）
ssh-keygen -t rsa -b 4096 -C "your_email@example.com" -f ~/.ssh/id_rsa -N ""
```

### 2. 添加公钥到 GitHub

```bash
# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 或
cat ~/.ssh/id_rsa.pub
```

访问 [GitHub SSH Keys](https://github.com/settings/keys)，点击 "New SSH key"，将公钥粘贴进去。

### 3. 配置 Git 用户信息

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### 4. 配置远程仓库

```bash
# 初始化仓库（如果还没有）
git init

# 添加远程仓库（SSH 方式）
git remote add origin git@github.com:username/repo.git

# 或更新现有远程仓库地址为 SSH
git remote set-url origin git@github.com:username/repo.git
```

### 5. 测试连接

```bash
ssh -T git@github.com
```

如果看到类似 `Hi username! You've successfully authenticated...` 的消息，说明配置成功。

---

## 方式二：HTTPS 认证

### 1. 配置 Git 用户信息

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### 2. 配置远程仓库

```bash
# 添加远程仓库（HTTPS 方式）
git remote add origin https://github.com/username/repo.git

# 或更新现有远程仓库地址
git remote set-url origin https://github.com/username/repo.git
```

### 3. 配置凭证助手

```bash
# macOS（使用 Keychain）
git config --global credential.helper osxkeychain

# Windows（使用 Credential Manager）
git config --global credential.helper manager

# Linux（使用 store，明文存储，不推荐）
git config --global credential.helper store
```

### 4. 生成 Personal Access Token

1. 访问 [GitHub Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择权限：`repo`（完全控制仓库）
4. 点击 "Generate token"
5. **立即复制 token**（只显示一次）

### 5. 测试连接

```bash
git fetch origin main
```

输入用户名和 token（密码）即可。

---

## 常用命令

### 查看配置

```bash
# 查看所有配置
git config --global --list

# 查看用户信息
git config --global user.name
git config --global user.email

# 查看远程仓库
git remote -v
```

### 管理远程仓库

```bash
# 添加远程仓库
git remote add origin git@github.com:username/repo.git

# 删除远程仓库
git remote remove origin

# 修改远程仓库地址
git remote set-url origin git@github.com:username/repo.git

# 查看远程仓库信息
git remote show origin
```

### 提交和推送

```bash
# 查看状态
git status

# 添加所有文件
git add .

# 提交
git commit -m "feat: your message"

# 推送到远程仓库
git push origin main

# 或设置默认分支后直接推送
git push -u origin main
```

### 拉取和合并

```bash
# 拉取最新代码
git pull origin main

# 获取但不合并
git fetch origin

# 合并远程分支
git merge origin/main
```

---

## 安全最佳实践

1. **使用 SSH 认证**：
   - 更安全，无需每次输入 token
   - 密钥可以设置密码保护
   - 适合生产环境

2. **保护 SSH 私钥**：
   - 不要将私钥分享给他人
   - 不要将私钥提交到仓库
   - 定期更新密钥

3. **管理 Personal Access Token**：
   - 不要在代码中硬编码 token
   - 定期更新 token
   - 只授予必要的权限

4. **使用 2FA**：
   - 启用 GitHub 双因素认证
   - 提高账户安全性

---

## 故障排查

### SSH 连接失败

```bash
# 测试 SSH 连接
ssh -T git@github.com

# 查看详细日志
ssh -Tvvv git@github.com

# 重新生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""
```

### 凭证问题

```bash
# 清除凭证缓存
git config --global --unset credential.helper

# 查看保存的凭证
cat ~/.git-credentials
```

### 权限问题

```bash
# 修复私钥权限
chmod 600 ~/.ssh/id_ed25519

# 修复 .ssh 目录权限
chmod 700 ~/.ssh
```

---

## 相关文档

- [GitHub SSH 官方文档](https://docs.github.com/zh/authentication/connecting-to-github-with-ssh)
- [GitHub Git 官方文档](https://docs.github.com/zh/get-started/using-git)
- [Git 官方文档](https://git-scm.com/doc)
