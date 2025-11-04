.PHONY: help install test lint format typecheck clean dev pre-commit ci

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install package and dependencies
	uv venv
	uv pip install -e .

dev:  ## Install package with dev dependencies
	uv venv
	uv pip install -e ".[dev]"

test:  ## Run tests with coverage
	pytest tests/ -v --cov=tree --cov-report=term-missing

test-fast:  ## Run tests without coverage
	pytest tests/ -v

lint:  ## Run ruff linter
	ruff check tree tests

lint-fix:  ## Run ruff linter with auto-fix
	ruff check tree tests --fix

format:  ## Run ruff formatter
	ruff format tree tests

format-check:  ## Check formatting without changes
	ruff format --check tree tests

typecheck:  ## Run mypy type checker
	mypy tree --strict

pre-commit:  ## Install pre-commit hooks
	pre-commit install

pre-commit-run:  ## Run pre-commit on all files
	pre-commit run --all-files

ci:  ## Run all CI checks locally
	@echo "Running linter..."
	@make lint
	@echo "\nRunning formatter check..."
	@make format-check
	@echo "\nRunning type checker..."
	@make typecheck
	@echo "\nRunning tests..."
	@make test
	@echo "\n✅ All CI checks passed!"

clean:  ## Clean up generated files
	rm -rf .venv
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

server:  ## Run development server
	uvicorn tree.main:app --reload

server-prod:  ## Run production server
	uvicorn tree.main:app --host 0.0.0.0 --port 8000
