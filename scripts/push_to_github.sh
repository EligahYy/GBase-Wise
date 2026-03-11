#!/bin/bash

# GitHub 推送脚本
# 使用此脚本推送代码到 GitHub

echo "========================================="
echo "GitHub 代码推送脚本"
echo "========================================="
echo ""

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告：存在未提交的更改"
    echo "请先提交更改："
    echo "  git add -A"
    echo "  git commit -m 'your message'"
    echo ""
    read -p "是否继续推送？（y/n）" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 准备推送到 GitHub..."
echo ""

# 获取当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"
echo ""

# 推送代码
echo "正在推送..."
git push origin $CURRENT_BRANCH

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "访问您的仓库: https://github.com/EligahYy/GBase-Wise"
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "可能的原因："
    echo "1. 未配置 GitHub 凭据"
    echo "2. 权限不足"
    echo ""
    echo "解决方案："
    echo "1. 使用 GitHub Token:"
    echo "   git remote set-url origin https://<TOKEN>@github.com/EligahYy/GBase-Wise.git"
    echo "   git push origin main"
    echo ""
    echo "2. 使用 SSH:"
    echo "   git remote set-url origin git@github.com:EligahYy/GBase-Wise.git"
    echo "   git push origin main"
    echo ""
    echo "3. 配置 Git 凭据:"
    echo "   git config --global credential.helper store"
    echo "   git push origin main"
    echo "   （按提示输入用户名和密码/token）"
fi
