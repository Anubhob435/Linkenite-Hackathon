.PHONY: help install dev build test clean docker-dev docker-prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	@echo "Installing Python dependencies..."
	uv sync --dev
	@echo "Installing frontend dependencies..."
	cd frontend/dashboard && npm install

dev: ## Start development servers
	@echo "Starting development environment..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		./dev.bat; \
	else \
		./dev.sh; \
	fi

build: ## Build the application
	@echo "Building backend..."
	uv build
	@echo "Building frontend..."
	cd frontend/dashboard && npm run build

test: ## Run tests
	@echo "Running backend tests..."
	uv run pytest
	@echo "Running frontend tests..."
	cd frontend/dashboard && npm run test

lint: ## Run linting
	@echo "Linting backend..."
	uv run black backend/
	uv run isort backend/
	uv run flake8 backend/
	@echo "Linting frontend..."
	cd frontend/dashboard && npm run lint

docker-dev: ## Start development environment with Docker
	docker-compose up --build

docker-prod: ## Start production environment with Docker
	docker-compose -f docker-compose.prod.yml up --build -d

clean: ## Clean build artifacts
	@echo "Cleaning Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleaning frontend build..."
	rm -rf frontend/dashboard/dist
	rm -rf frontend/dashboard/node_modules/.cache