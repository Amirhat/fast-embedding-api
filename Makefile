.PHONY: help install dev-install test lint format clean run docker-build docker-up docker-down benchmark k6-benchmark all

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := pytest
BLACK := black
ISORT := isort
RUFF := ruff
DOCKER_COMPOSE := docker-compose
K6 := k6

# Directories
SRC_DIR := src
TEST_DIR := tests
BENCHMARK_DIR := benchmarks
DOCS_DIR := docs

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_BLUE := \033[34m
COLOR_YELLOW := \033[33m

## help: Show this help message
help:
	@echo "$(COLOR_BOLD)Fast Embedding API - Makefile Commands$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_GREEN)Setup:$(COLOR_RESET)"
	@echo "  make install          Install production dependencies"
	@echo "  make dev-install      Install development dependencies"
	@echo ""
	@echo "$(COLOR_GREEN)Development:$(COLOR_RESET)"
	@echo "  make run              Run the API locally"
	@echo "  make format           Format code with black and isort"
	@echo "  make lint             Run linters (ruff, black check)"
	@echo "  make test             Run tests with pytest"
	@echo "  make test-cov         Run tests with coverage report"
	@echo ""
	@echo "$(COLOR_GREEN)Docker:$(COLOR_RESET)"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-up        Start services with docker-compose"
	@echo "  make docker-down      Stop services"
	@echo "  make docker-logs      View Docker logs"
	@echo "  make docker-shell     Open shell in running container"
	@echo ""
	@echo "$(COLOR_GREEN)Benchmarks:$(COLOR_RESET)"
	@echo "  make benchmark        Run Python benchmarks"
	@echo "  make k6-benchmark     Run K6 load tests"
	@echo "  make all-benchmarks   Run all benchmarks"
	@echo ""
	@echo "$(COLOR_GREEN)Cleanup:$(COLOR_RESET)"
	@echo "  make clean            Remove generated files and caches"
	@echo "  make clean-all        Remove everything including venv"
	@echo ""
	@echo "$(COLOR_GREEN)All-in-one:$(COLOR_RESET)"
	@echo "  make all              Install, test, and build"
	@echo ""

## install: Install production dependencies
install:
	@echo "$(COLOR_BLUE)📦 Installing production dependencies...$(COLOR_RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(COLOR_GREEN)✅ Production dependencies installed$(COLOR_RESET)"

## dev-install: Install development dependencies
dev-install: install
	@echo "$(COLOR_BLUE)📦 Installing development dependencies...$(COLOR_RESET)"
	$(PIP) install pytest pytest-asyncio pytest-cov ruff black isort
	@echo "$(COLOR_GREEN)✅ Development dependencies installed$(COLOR_RESET)"

## run: Run the API locally
run:
	@echo "$(COLOR_BLUE)🚀 Starting Fast Embedding API...$(COLOR_RESET)"
	$(PYTHON) -m src.main

## format: Format code with black and isort
format:
	@echo "$(COLOR_BLUE)🎨 Formatting code...$(COLOR_RESET)"
	$(BLACK) $(SRC_DIR) $(TEST_DIR) $(BENCHMARK_DIR)
	$(ISORT) $(SRC_DIR) $(TEST_DIR) $(BENCHMARK_DIR)
	@echo "$(COLOR_GREEN)✅ Code formatted$(COLOR_RESET)"

## lint: Run linters
lint:
	@echo "$(COLOR_BLUE)🔍 Running linters...$(COLOR_RESET)"
	$(RUFF) check $(SRC_DIR) $(TEST_DIR) $(BENCHMARK_DIR)
	$(BLACK) --check $(SRC_DIR) $(TEST_DIR) $(BENCHMARK_DIR)
	$(ISORT) --check-only $(SRC_DIR) $(TEST_DIR) $(BENCHMARK_DIR)
	@echo "$(COLOR_GREEN)✅ Linting complete$(COLOR_RESET)"

## test: Run tests
test:
	@echo "$(COLOR_BLUE)🧪 Running tests...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/test_api.py -v
	@echo "$(COLOR_GREEN)✅ Tests complete$(COLOR_RESET)"

## test-cov: Run tests with coverage
test-cov:
	@echo "$(COLOR_BLUE)🧪 Running tests with coverage...$(COLOR_RESET)"
	$(PYTEST) $(TEST_DIR)/test_api.py -v --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo "$(COLOR_GREEN)✅ Coverage report generated in htmlcov/$(COLOR_RESET)"

## docker-build: Build Docker image
docker-build:
	@echo "$(COLOR_BLUE)🐳 Building Docker image...$(COLOR_RESET)"
	docker build -t fast-embedding:latest --target production .
	@echo "$(COLOR_GREEN)✅ Docker image built$(COLOR_RESET)"

## docker-up: Start services with docker-compose
docker-up:
	@echo "$(COLOR_BLUE)🐳 Starting Docker services...$(COLOR_RESET)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(COLOR_GREEN)✅ Services started$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)💡 API available at http://localhost:8000$(COLOR_RESET)"

## docker-down: Stop services
docker-down:
	@echo "$(COLOR_BLUE)🐳 Stopping Docker services...$(COLOR_RESET)"
	$(DOCKER_COMPOSE) down
	@echo "$(COLOR_GREEN)✅ Services stopped$(COLOR_RESET)"

## docker-logs: View Docker logs
docker-logs:
	$(DOCKER_COMPOSE) logs -f

## docker-shell: Open shell in running container
docker-shell:
	@echo "$(COLOR_BLUE)🐳 Opening shell in container...$(COLOR_RESET)"
	docker exec -it fast-embedding-api /bin/bash

## benchmark: Run Python benchmarks
benchmark:
	@echo "$(COLOR_BLUE)📊 Running Python benchmarks...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)⚠️  Make sure the API is running (make docker-up or make run)$(COLOR_RESET)"
	$(PYTHON) $(BENCHMARK_DIR)/benchmark.py
	@echo "$(COLOR_GREEN)✅ Benchmarks complete$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)📄 Results saved to benchmarks/benchmark_results.json$(COLOR_RESET)"

## k6-benchmark: Run K6 load tests
k6-benchmark:
	@echo "$(COLOR_BLUE)📊 Running K6 load tests...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)⚠️  Make sure the API is running (make docker-up or make run)$(COLOR_RESET)"
	@if command -v $(K6) >/dev/null 2>&1; then \
		$(K6) run $(BENCHMARK_DIR)/k6-load-test.js; \
		echo "$(COLOR_GREEN)✅ K6 benchmarks complete$(COLOR_RESET)"; \
		echo "$(COLOR_YELLOW)📄 Results saved to benchmarks/k6-results.json$(COLOR_RESET)"; \
	else \
		echo "$(COLOR_YELLOW)⚠️  K6 not found. Install from https://k6.io/docs/getting-started/installation/$(COLOR_RESET)"; \
		exit 1; \
	fi

## all-benchmarks: Run all benchmarks
all-benchmarks: benchmark k6-benchmark
	@echo "$(COLOR_GREEN)✅ All benchmarks complete$(COLOR_RESET)"

## clean: Remove generated files
clean:
	@echo "$(COLOR_BLUE)🧹 Cleaning up...$(COLOR_RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "$(COLOR_GREEN)✅ Cleanup complete$(COLOR_RESET)"

## clean-all: Remove everything including venv
clean-all: clean
	@echo "$(COLOR_BLUE)🧹 Deep cleaning...$(COLOR_RESET)"
	rm -rf venv
	$(DOCKER_COMPOSE) down -v
	@echo "$(COLOR_GREEN)✅ Deep cleanup complete$(COLOR_RESET)"

## all: Install, test, lint, and build
all: dev-install format lint test docker-build
	@echo "$(COLOR_GREEN)✅ All tasks complete!$(COLOR_RESET)"

# CI/CD targets
.PHONY: ci-test ci-lint ci-build

## ci-test: Run tests in CI environment
ci-test:
	$(PYTEST) $(TEST_DIR)/test_api.py -v --cov=$(SRC_DIR) --cov-report=xml

## ci-lint: Run linters in CI environment
ci-lint:
	$(RUFF) check $(SRC_DIR) $(TEST_DIR) $(BENCHMARK_DIR)
	$(BLACK) --check $(SRC_DIR) $(TEST_DIR) $(BENCHMARK_DIR)
	$(ISORT) --check-only $(SRC_DIR) $(TEST_DIR) $(BENCHMARK_DIR)

## ci-build: Build and test Docker image in CI
ci-build: docker-build
	@echo "$(COLOR_BLUE)🧪 Testing Docker image...$(COLOR_RESET)"
	docker run -d --name test-api -p 8001:8000 fast-embedding:latest
	sleep 30
	curl -f http://localhost:8001/health || (docker stop test-api && exit 1)
	docker stop test-api
	docker rm test-api
	@echo "$(COLOR_GREEN)✅ Docker image test passed$(COLOR_RESET)"
