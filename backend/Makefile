.PHONY: help install test lint typecheck coverage clean

help:
	@echo "HSE Enterprise Platform - Development Commands"
	@echo "=============================================="
	@echo ""
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests with coverage"
	@echo "  make test-fast    - Run tests without coverage"
	@echo "  make lint         - Run ruff linter"
	@echo "  make typecheck    - Run mypy type checker"
	@echo "  make coverage     - Generate HTML coverage report"
	@echo "  make clean        - Remove cache and coverage files"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov factory-boy faker sqlalchemy-utils ruff mypy

test:
	python -m pytest tests/ -v --tb=short

test-fast:
	python -m pytest tests/ -v --tb=short --no-cov

lint:
	ruff check app/ tests/ --select E,F,W,I
	ruff format app/ tests/ --check

lint-fix:
	ruff check app/ tests/ --select E,F,W,I --fix
	ruff format app/ tests/

typecheck:
	mypy app/ --ignore-missing-imports

coverage:
	python -m pytest tests/ --cov=app --cov-report=html
	@echo "HTML coverage report generated in htmlcov/index.html"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
