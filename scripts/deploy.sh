#!/bin/bash
# Production deployment script for Fast Embedding API

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="fast-embedding"
CONTAINER_NAME="fast-embedding-api"
PORT=8000

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_info "Docker is installed ✓"
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_warning "docker-compose is not installed. Will use docker commands instead."
        return 1
    fi
    print_info "docker-compose is installed ✓"
    return 0
}

check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_info "Created .env file. Please review and update it before deploying."
            read -p "Press enter to continue after reviewing .env file..."
        else
            print_error ".env.example not found. Cannot create .env file."
            exit 1
        fi
    else
        print_info ".env file found ✓"
    fi
}

build_image() {
    print_info "Building Docker image..."
    docker build -t ${IMAGE_NAME}:latest --target production .
    if [ $? -eq 0 ]; then
        print_info "Docker image built successfully ✓"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

stop_existing() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Stopping existing container..."
        docker stop ${CONTAINER_NAME} || true
        docker rm ${CONTAINER_NAME} || true
        print_info "Existing container removed ✓"
    fi
}

run_container() {
    print_info "Starting new container..."
    
    # Load environment variables from .env
    if [ -f .env ]; then
        docker run -d \
            --name ${CONTAINER_NAME} \
            -p ${PORT}:8000 \
            --env-file .env \
            --restart unless-stopped \
            --health-cmd "curl -f http://localhost:8000/health || exit 1" \
            --health-interval 30s \
            --health-timeout 10s \
            --health-retries 3 \
            --health-start-period 60s \
            -v model_cache:/app/.cache/fastembed \
            ${IMAGE_NAME}:latest
    else
        docker run -d \
            --name ${CONTAINER_NAME} \
            -p ${PORT}:8000 \
            --restart unless-stopped \
            --health-cmd "curl -f http://localhost:8000/health || exit 1" \
            --health-interval 30s \
            --health-timeout 10s \
            --health-retries 3 \
            --health-start-period 60s \
            -v model_cache:/app/.cache/fastembed \
            ${IMAGE_NAME}:latest
    fi
    
    if [ $? -eq 0 ]; then
        print_info "Container started successfully ✓"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

deploy_with_compose() {
    print_info "Deploying with docker-compose..."
    docker-compose up -d
    if [ $? -eq 0 ]; then
        print_info "Deployment successful ✓"
    else
        print_error "Deployment failed"
        exit 1
    fi
}

wait_for_health() {
    print_info "Waiting for service to be healthy..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf http://localhost:${PORT}/health > /dev/null 2>&1; then
            print_info "Service is healthy ✓"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    print_error "Service health check failed after ${max_attempts} attempts"
    print_info "Checking logs..."
    docker logs ${CONTAINER_NAME}
    return 1
}

show_status() {
    echo ""
    echo "========================================="
    echo "Deployment Complete!"
    echo "========================================="
    echo ""
    print_info "Service URL: http://localhost:${PORT}"
    print_info "Health Check: http://localhost:${PORT}/health"
    print_info "Metrics: http://localhost:${PORT}/metrics"
    print_info "API Docs: http://localhost:${PORT}/docs (if enabled)"
    echo ""
    print_info "View logs: docker logs -f ${CONTAINER_NAME}"
    print_info "Stop service: docker stop ${CONTAINER_NAME}"
    print_info "Restart service: docker restart ${CONTAINER_NAME}"
    echo ""
}

# Main deployment flow
main() {
    echo "========================================="
    echo "Fast Embedding API - Production Deploy"
    echo "========================================="
    echo ""
    
    # Pre-deployment checks
    check_docker
    
    if check_docker_compose; then
        # Use docker-compose if available
        check_env_file
        print_info "Deploying with docker-compose..."
        deploy_with_compose
        CONTAINER_NAME="fast-embedding-api"  # docker-compose uses this name
    else
        # Use docker commands
        check_env_file
        build_image
        stop_existing
        run_container
    fi
    
    # Wait for service to be ready
    wait_for_health
    
    # Show status
    show_status
}

# Parse command line arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    build)
        check_docker
        build_image
        ;;
    stop)
        print_info "Stopping service..."
        if check_docker_compose; then
            docker-compose down
        else
            docker stop ${CONTAINER_NAME}
            docker rm ${CONTAINER_NAME}
        fi
        print_info "Service stopped ✓"
        ;;
    restart)
        print_info "Restarting service..."
        if check_docker_compose; then
            docker-compose restart
        else
            docker restart ${CONTAINER_NAME}
        fi
        print_info "Service restarted ✓"
        ;;
    logs)
        if check_docker_compose; then
            docker-compose logs -f
        else
            docker logs -f ${CONTAINER_NAME}
        fi
        ;;
    status)
        if check_docker_compose; then
            docker-compose ps
        else
            docker ps --filter name=${CONTAINER_NAME}
        fi
        ;;
    clean)
        print_warning "This will remove the container and image. Continue? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_info "Cleaning up..."
            docker stop ${CONTAINER_NAME} 2>/dev/null || true
            docker rm ${CONTAINER_NAME} 2>/dev/null || true
            docker rmi ${IMAGE_NAME}:latest 2>/dev/null || true
            print_info "Cleanup complete ✓"
        fi
        ;;
    *)
        echo "Usage: $0 {deploy|build|stop|restart|logs|status|clean}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Build and deploy the service (default)"
        echo "  build   - Build the Docker image only"
        echo "  stop    - Stop and remove the service"
        echo "  restart - Restart the service"
        echo "  logs    - View service logs"
        echo "  status  - Show service status"
        echo "  clean   - Remove container and image"
        exit 1
        ;;
esac
