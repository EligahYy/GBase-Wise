#!/bin/bash

# Git 快速配置脚本
# 使用方法: bash scripts/setup_git.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Git 快速配置脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 检查当前配置
echo -e "${YELLOW}[1/4] 检查当前 Git 配置...${NC}"
CURRENT_NAME=$(git config --global user.name)
CURRENT_EMAIL=$(git config --global user.email)
echo -e "当前用户名: ${GREEN}${CURRENT_NAME}${NC}"
echo -e "当前邮箱: ${GREEN}${CURRENT_EMAIL}${NC}"
echo ""

# 2. 配置用户信息
if [ "$CURRENT_NAME" == "agent" ] || [ -z "$CURRENT_NAME" ]; then
    echo -e "${YELLOW}[2/4] 需要配置 Git 用户信息${NC}"
    echo -e "${BLUE}请输入你的 GitHub 用户名 (默认: EligahYy):${NC}"
    read -r NEW_NAME
    NEW_NAME=${NEW_NAME:-EligahYy}

    echo -e "${BLUE}请输入你的 GitHub 邮箱 (默认: eligahwsw@163.com):${NC}"
    read -r NEW_EMAIL
    NEW_EMAIL=${NEW_EMAIL:-eligahwsw@163.com}

    git config --global user.name "$NEW_NAME"
    git config --global user.email "$NEW_EMAIL"

    echo -e "${GREEN}✓ 用户信息配置成功${NC}"
    echo -e "用户名: ${GREEN}${NEW_NAME}${NC}"
    echo -e "邮箱: ${GREEN}${NEW_EMAIL}${NC}"
else
    echo -e "${GREEN}[2/4] ✓ Git 用户信息已配置${NC}"
fi
echo ""

# 3. 检查远程仓库
echo -e "${YELLOW}[3/4] 检查远程仓库配置...${NC}"
REMOTE_URL=$(git remote get-url origin)
echo -e "远程仓库: ${GREEN}${REMOTE_URL}${NC}"

if [[ $REMOTE_URL == *"github.com"* ]]; then
    echo -e "${GREEN}✓ 远程仓库已配置为 GitHub${NC}"
else
    echo -e "${YELLOW}当前远程仓库不是 GitHub，是否需要更新？ (y/n):${NC}"
    read -r UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" == "y" ] || [ "$UPDATE_REMOTE" == "Y" ]; then
        echo -e "${BLUE}请输入你的 GitHub 仓库地址 (格式: https://github.com/username/repo.git):${NC}"
        read -r NEW_REMOTE_URL
        git remote set-url origin "$NEW_REMOTE_URL"
        echo -e "${GREEN}✓ 远程仓库已更新${NC}"
    fi
fi
echo ""

# 4. 测试连接
echo -e "${YELLOW}[4/4] 测试与 GitHub 的连接...${NC}"
echo -e "${YELLOW}请选择连接方式:${NC}"
echo "1. HTTPS (使用 Personal Access Token)"
echo "2. SSH (推荐，更安全)"
echo -e "${BLUE}请输入选项 (1/2):${NC}"
read -r CONNECTION_TYPE

if [ "$CONNECTION_TYPE" == "2" ]; then
    # SSH 配置
    echo -e "${BLUE}配置 SSH 密钥...${NC}"

    # 检查是否已有 SSH 密钥
    if [ -f ~/.ssh/id_ed25519 ]; then
        echo -e "${YELLOW}检测到已有 SSH 密钥${NC}"
        echo -e "${BLUE}公钥内容:${NC}"
        cat ~/.ssh/id_ed25519.pub
        echo ""
        echo -e "${GREEN}请将上述公钥添加到你的 GitHub 账户:${NC}"
        echo -e "${BLUE}https://github.com/settings/keys${NC}"
    else
        echo -e "${YELLOW}生成新的 SSH 密钥...${NC}"
        ssh-keygen -t ed25519 -C "$NEW_EMAIL" -f ~/.ssh/id_ed25519 -N ""
        echo -e "${GREEN}✓ SSH 密钥已生成${NC}"
        echo -e "${BLUE}公钥内容:${NC}"
        cat ~/.ssh/id_ed25519.pub
        echo ""
        echo -e "${GREEN}请将上述公钥添加到你的 GitHub 账户:${NC}"
        echo -e "${BLUE}https://github.com/settings/keys${NC}"
    fi

    # 更新远程仓库地址为 SSH
    if [[ $REMOTE_URL == https://* ]]; then
        echo -e "${YELLOW}更新远程仓库地址为 SSH...${NC}"
        SSH_URL=$(echo "$REMOTE_URL" | sed 's|https://github.com/|git@github.com:|')
        git remote set-url origin "$SSH_URL"
        echo -e "${GREEN}✓ 远程仓库地址已更新为 SSH${NC}"
    fi

    # 测试连接
    echo -e "${YELLOW}测试 SSH 连接...${NC}"
    if ssh -T git@github.com 2>&1 | grep -q "success"; then
        echo -e "${GREEN}✓ SSH 连接测试成功${NC}"
    else
        echo -e "${YELLOW}SSH 连接测试可能失败，但这是正常的（如果这是你第一次使用 SSH）${NC}"
        echo -e "${YELLOW}请确保已将公钥添加到 GitHub 账户${NC}"
    fi
else
    # HTTPS 配置
    echo -e "${BLUE}配置 HTTPS 认证...${NC}"
    echo -e "${GREEN}请配置 Personal Access Token:${NC}"
    echo -e "${BLUE}1. 访问: https://github.com/settings/tokens${NC}"
    echo -e "${BLUE}2. 生成新 Token，勾选 repo 权限${NC}"
    echo -e "${BLUE}3. 复制生成的 Token${NC}"
    echo ""
    echo -e "${YELLOW}配置 Git 凭证助手...${NC}"
    git config --global credential.helper store
    echo -e "${GREEN}✓ 凭证助手已配置${NC}"
    echo -e "${YELLOW}下次推送时，输入用户名和 Token 作为密码即可${NC}"
fi
echo ""

# 完成
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}   Git 配置完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}当前配置:${NC}"
echo -e "用户名: ${GREEN}$(git config --global user.name)${NC}"
echo -e "邮箱: ${GREEN}$(git config --global user.email)${NC}"
echo -e "远程仓库: ${GREEN}$(git remote get-url origin)${NC}"
echo ""
echo -e "${YELLOW}下一步操作:${NC}"
echo "1. 测试推送: bash scripts/git_push.sh \"test: 初始化推送\""
echo "2. 查看帮助: docs/git_config_guide.md"
echo ""
