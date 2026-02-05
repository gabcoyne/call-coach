# Makefile for Gong Call Coaching Agent

.PHONY: help install test lint format clean docker-up docker-down db-migrate sync

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv sync

install-dev: ## Install with dev dependencies
	uv sync --all-extras

test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ --cov=. --cov-report=html --cov-report=term

lint: ## Run linting checks
	uv run ruff check .
	uv run mypy .

format: ## Format code
	uv run black .
	uv run ruff check --fix .

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
	uv run python webhook_server.py

dev: docker-up ## Start local development environment
	@echo "Waiting for services to start..."
	@sleep 5
	@echo "Services ready! Webhook server: http://localhost:8000"
	@echo "MCP server: http://localhost:3000"

env-example: ## Copy .env.example to .env
	cp .env.example .env
	@echo "Created .env file. Please update with your credentials."

kb-load: ## Load complete knowledge base (rubrics + docs)
	uv run python -m knowledge.loader all

kb-load-rubrics: ## Load coaching rubrics only
	uv run python -m knowledge.loader rubrics

kb-load-docs: ## Load product documentation only
	uv run python -m knowledge.loader docs

kb-verify: ## Verify knowledge base is loaded correctly
	uv run python -m knowledge.loader verify

sync: ## Sync beads and commit (replaces manual git commits)
	bd sync --flush-only
