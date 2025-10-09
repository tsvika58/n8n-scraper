# N8N Scraper - Development Makefile
# Quick commands for common development tasks

.PHONY: help install install-dev test lint format clean run docker-build docker-run db-init

# Default target
help:
	@echo "n8n-scraper Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install production dependencies"
	@echo "  make install-dev    Install dev dependencies"
	@echo "  make db-init        Initialize database"
	@echo ""
	@echo "Development:"
	@echo "  make test           Run tests with coverage"
	@echo "  make lint           Run linting (ruff + mypy)"
	@echo "  make format         Format code (black + isort)"
	@echo "  make clean          Remove cache and temp files"
	@echo ""
	@echo "Running:"
	@echo "  make run            Run scraper locally"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run in Docker"

# Installation
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	playwright install chromium

install-dev:
	pip install -r requirements-dev.txt
	playwright install chromium

# Database
db-init:
	python scripts/init_db.py

# Testing
test:
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-fast:
	pytest tests/ -v -x

# Code Quality
lint:
	@echo "Running ruff..."
	ruff check src/ tests/ scripts/
	@echo "Running mypy..."
	mypy src/

format:
	@echo "Running black..."
	black src/ tests/ scripts/
	@echo "Running isort..."
	isort src/ tests/ scripts/

check: lint test

# Cleaning
clean:
	@echo "Cleaning Python cache..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaning test artifacts..."
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache/ .ruff_cache/
	@echo "Done!"

clean-data:
	@echo "⚠️  This will delete all scraped data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf data/ media/ logs/; \
		echo "Data cleaned!"; \
	fi

# Running
run:
	python scripts/scrape.py

run-sample:
	python scripts/scrape.py --workflows 10

validate:
	python scripts/validate.py

export:
	python scripts/export.py --format jsonl

# Docker
docker-build:
	docker-compose build

docker-run:
	docker-compose up scraper

docker-shell:
	docker-compose run --rm scraper /bin/bash

docker-test:
	docker-compose run --rm scraper pytest tests/ -v

docker-clean:
	docker-compose down -v
	docker image prune -f

# Development workflow
dev: format lint test
	@echo "✅ Development checks passed!"

# CI simulation
ci: install lint test
	@echo "✅ CI checks passed!"

