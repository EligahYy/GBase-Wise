#!/bin/bash

# Git 自动提交和推送脚本
# 使用方法: bash scripts/git_push.sh "提交信息"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否有更改
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✓ 没有需要提交的更改${NC}"
    exit 0
fi

# 显示当前状态
echo -e "${YELLOW}当前 Git 状态:${NC}"
git status --short

# 拉取最新代码
echo -e "${YELLOW}正在拉取最新代码...${NC}"
if git pull origin main; then
    echo -e "${GREEN}✓ 拉取成功${NC}"
else
    echo -e "${RED}✗ 拉取失败，请检查网络或解决冲突${NC}"
    exit 1
fi

# 添加所有更改
echo -e "${YELLOW}正在添加所有更改...${NC}"
git add .

# 检查是否有文件被添加
if [ -z "$(git diff --cached --name-only)" ]; then
    echo -e "${YELLOW}没有文件被添加，可能已经被提交${NC}"
    exit 0
fi

# 提交更改
if [ -n "$1" ]; then
    # 使用传入的提交信息
    echo -e "${YELLOW}正在提交更改...${NC}"
    if git commit -m "$1"; then
        echo -e "${GREEN}✓ 提交成功${NC}"
    else
        echo -e "${RED}✗ 提交失败${NC}"
        exit 1
    fi
else
    # 使用默认提交信息
    CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    COMMIT_MSG="chore: 更新代码 (${CURRENT_TIME})"
    echo -e "${YELLOW}正在提交更改...${NC}"
    if git commit -m "$COMMIT_MSG"; then
        echo -e "${GREEN}✓ 提交成功${NC}"
    else
        echo -e "${RED}✗ 提交失败${NC}"
        exit 1
    fi
fi

# 推送到远程仓库
echo -e "${YELLOW}正在推送到远程仓库 (origin/main)...${NC}"
if git push origin main; then
    echo -e "${GREEN}✓ 推送成功！${NC}"
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}提交信息: $(git log -1 --pretty=%s)${NC}"
    echo -e "${GREEN}提交时间: $(git log -1 --pretty=%ci)${NC}"
    echo -e "${GREEN}提交哈希: $(git log -1 --pretty=%h)${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}✗ 推送失败${NC}"
    echo -e "${YELLOW}可能的原因:${NC}"
    echo "1. 没有配置 GitHub Token 或 SSH 密钥"
    echo "2. Token 已过期或无效"
    echo "3. 没有推送权限"
    echo "4. 网络连接问题"
    echo ""
    echo -e "${YELLOW}解决方案:${NC}"
    echo "请查看 docs/git_config_guide.md 了解如何配置 Git"
    exit 1
fi
