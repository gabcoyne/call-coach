# Makefile for Gong Call Coaching Agent

.PHONY: help install test lint format clean docker-up docker-down db-migrate

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=. --cov-report=html --cov-report=term

lint: ## Run linting checks
	ruff check .
	mypy .

format: ## Format code
	black .
	ruff check --fix .

clean: ## Clean up generated files
	rm -rf __pycache__ .pytest_cache .mypy_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-up: ## Start Docker Compose services
	docker-compose up -d

docker-down: ## Stop Docker Compose services
	docker-compose down

docker-logs: ## View Docker Compose logs
	docker-compose logs -f

db-migrate: ## Run database migrations
	psql $(DATABASE_URL) -f db/migrations/001_initial_schema.sql

webhook-server: ## Run webhook server locally
	python webhook_server.py

dev: docker-up ## Start local development environment
	@echo "Waiting for services to start..."
	@sleep 5
	@echo "Services ready! Webhook server: http://localhost:8000"
	@echo "MCP server: http://localhost:3000"

env-example: ## Copy .env.example to .env
	cp .env.example .env
	@echo "Created .env file. Please update with your credentials."
