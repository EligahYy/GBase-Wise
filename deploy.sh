#!/bin/bash

# GBase8a 数据库产品经理助手 - 一键部署脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印信息函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    print_info "检查 Docker 是否安装..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，正在安装 Docker..."
        install_docker
    else
        print_info "Docker 已安装: $(docker --version)"
    fi
}

# 安装 Docker
install_docker() {
    print_info "正在安装 Docker..."

    # 检测操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if [ -f /etc/debian_version ]; then
            # Debian/Ubuntu
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
        elif [ -f /etc/redhat-release ]; then
            # CentOS/RHEL
            sudo yum install -y docker
            sudo systemctl start docker
            sudo systemctl enable docker
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_error "请手动安装 Docker Desktop: https://www.docker.com/products/docker-desktop"
        exit 1
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        print_error "请手动安装 Docker Desktop: https://www.docker.com/products/docker-desktop"
        exit 1
    fi

    print_info "Docker 安装完成！"
    print_warning "请重新登录或运行 'newgrp docker' 使权限生效"
}

# 检查 docker-compose 是否安装
check_docker_compose() {
    print_info "检查 docker-compose 是否安装..."
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "docker-compose 未安装，正在安装..."
        install_docker_compose
    else
        if command -v docker-compose &> /dev/null; then
            print_info "docker-compose 已安装: $(docker-compose --version)"
        else
            print_info "docker-compose 插件已安装: $(docker compose version)"
        fi
    fi
}

# 安装 docker-compose
install_docker_compose() {
    print_info "正在安装 docker-compose..."

    # Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi

    print_info "docker-compose 安装完成！"
}

# 检查环境变量
check_env_vars() {
    print_info "检查环境变量..."

    if [ ! -f .env ]; then
        print_warning ".env 文件不存在，创建示例 .env 文件..."
        cat > .env << EOF
# LLM 配置
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here
COZE_INTEGRATION_MODEL_BASE_URL=your_base_url_here

# 工作目录
COZE_WORKSPACE_PATH=/app
EOF
        print_warning "请编辑 .env 文件，填入正确的 API Key 和 Base URL"
        print_warning "编辑完成后，按任意键继续..."
        read -n 1 -s
    fi

    source .env

    if [ "$COZE_WORKLOAD_IDENTITY_API_KEY" == "your_api_key_here" ]; then
        print_error "请在 .env 文件中填入正确的 API Key"
        exit 1
    fi

    print_info "环境变量检查完成！"
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    mkdir -p assets/sql_examples
    mkdir -p config
    mkdir -p logs
    print_info "目录创建完成！"
}

# 停止并删除旧容器
stop_old_container() {
    print_info "检查是否有旧容器运行..."
    if docker ps -a --format '{{.Names}}' | grep -q gbase8a-assistant; then
        print_info "停止并删除旧容器..."
        docker stop gbase8a-assistant || true
        docker rm gbase8a-assistant || true
    fi
}

# 构建镜像
build_image() {
    print_info "开始构建 Docker 镜像..."
    docker-compose build
    print_info "镜像构建完成！"
}

# 启动容器
start_container() {
    print_info "启动容器..."
    docker-compose up -d
    print_info "容器启动完成！"
}

# 检查容器状态
check_container_status() {
    print_info "检查容器状态..."
    sleep 3

    if docker ps --format '{{.Names}}' | grep -q gbase8a-assistant; then
        print_info "容器运行正常！"
        docker ps --filter name=gbase8a-assistant --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        print_error "容器启动失败，查看日志..."
        docker logs gbase8a-assistant
        exit 1
    fi
}

# 显示访问信息
show_access_info() {
    echo ""
    print_info "======================================"
    print_info "部署完成！"
    print_info "======================================"
    echo ""
    print_info "访问地址: http://localhost:5000"
    print_info ""
    print_info "常用命令:"
    print_info "  查看日志: docker logs -f gbase8a-assistant"
    print_info "  停止服务: docker-compose down"
    print_info "  重启服务: docker-compose restart"
    print_info "  进入容器: docker exec -it gbase8a-assistant bash"
    echo ""
}

# 主函数
main() {
    print_info "======================================"
    print_info "GBase8a 数据库产品经理助手 - 一键部署"
    print_info "======================================"
    echo ""

    # 检查 Docker
    check_docker

    # 检查 docker-compose
    check_docker_compose

    # 检查环境变量
    check_env_vars

    # 创建目录
    create_directories

    # 停止旧容器
    stop_old_container

    # 构建镜像
    build_image

    # 启动容器
    start_container

    # 检查状态
    check_container_status

    # 显示访问信息
    show_access_info
}

# 执行主函数
main
