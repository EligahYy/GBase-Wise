#!/bin/bash

# GBase8a 数据库产品经理助手 - 服务器部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
INSTALL_DIR="/opt/gbase8a-assistant"
SERVICE_NAME="gbase8a-assistant"
GIT_REPO_URL=""  # 请填入你的 GitHub 仓库地址

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用 root 用户或 sudo 运行此脚本"
        exit 1
    fi
}

# 安装系统依赖
install_system_deps() {
    print_info "安装系统依赖..."

    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y python3 python3-pip git curl
    elif command -v yum &> /dev/null; then
        yum install -y python3 python3-pip git curl
    else
        print_error "不支持的操作系统"
        exit 1
    fi

    print_info "系统依赖安装完成！"
}

# 克隆或更新项目
clone_or_update_repo() {
    if [ -z "$GIT_REPO_URL" ]; then
        print_error "请设置 GIT_REPO_URL 环境变量"
        exit 1
    fi

    print_info "克隆/更新项目..."

    if [ -d "$INSTALL_DIR/.git" ]; then
        cd $INSTALL_DIR
        git pull origin main
    else
        git clone $GIT_REPO_URL $INSTALL_DIR
        cd $INSTALL_DIR
    fi

    print_info "项目更新完成！"
}

# 安装 Python 依赖
install_python_deps() {
    print_info "安装 Python 依赖..."
    cd $INSTALL_DIR
    pip3 install -r requirements.txt
    print_info "Python 依赖安装完成！"
}

# 配置环境变量
configure_env() {
    print_info "配置环境变量..."

    if [ ! -f "$INSTALL_DIR/.env" ]; then
        cat > $INSTALL_DIR/.env << EOF
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here
COZE_INTEGRATION_MODEL_BASE_URL=your_base_url_here
COZE_WORKSPACE_PATH=$INSTALL_DIR
EOF
        print_warning "请编辑 $INSTALL_DIR/.env 文件，填入正确的 API Key"
    fi

    print_info "环境变量配置完成！"
}

# 创建日志目录
create_log_dir() {
    mkdir -p $INSTALL_DIR/logs
    print_info "日志目录创建完成！"
}

# 配置 systemd 服务
configure_systemd() {
    print_info "配置 systemd 服务..."

    cp $INSTALL_DIR/scripts/gbase8a-assistant.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME

    print_info "systemd 服务配置完成！"
}

# 启动服务
start_service() {
    print_info "启动服务..."
    systemctl start $SERVICE_NAME
    sleep 3

    if systemctl is-active --quiet $SERVICE_NAME; then
        print_info "服务启动成功！"
    else
        print_error "服务启动失败！"
        print_error "查看日志: journalctl -u $SERVICE_NAME -f"
        exit 1
    fi
}

# 显示服务状态
show_status() {
    print_info "服务状态:"
    systemctl status $SERVICE_NAME --no-pager
}

# 显示访问信息
show_access_info() {
    print_info "======================================"
    print_info "服务器部署完成！"
    print_info "======================================"
    echo ""
    print_info "服务名称: $SERVICE_NAME"
    print_info "安装目录: $INSTALL_DIR"
    print_info ""
    print_info "常用命令:"
    print_info "  查看状态: systemctl status $SERVICE_NAME"
    print_info "  启动服务: systemctl start $SERVICE_NAME"
    print_info "  停止服务: systemctl stop $SERVICE_NAME"
    print_info "  重启服务: systemctl restart $SERVICE_NAME"
    print_info "  查看日志: journalctl -u $SERVICE_NAME -f"
    echo ""
}

# 主函数
main() {
    print_info "======================================"
    print_info "GBase8a 数据库产品经理助手 - 服务器部署"
    print_info "======================================"
    echo ""

    check_root
    install_system_deps
    clone_or_update_repo
    install_python_deps
    configure_env
    create_log_dir
    configure_systemd
    start_service
    show_status
    show_access_info
}

# 执行主函数
main
