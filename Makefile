PYTHON := python3

.PHONY: help install-deps run test lint fmt dev release swagger deploy migrate migrate-up migrate-down clean

help:
	@echo "Available commands:"
	@echo "  make install-deps    - Install production and dev dependencies"
	@echo "  make dev             - Start development server with hot reload"
	@echo "  make run             - Start production server"
	@echo "  make test            - Run tests with coverage"
	@echo "  make lint            - Run code checks (Ruff & Mypy)"
	@echo "  make fmt             - Format code (Ruff)"
	@echo "  make clean           - Remove temporary files"
	@echo "  make migrate msg=... - Generate migration script"
	@echo "  make migrate-up      - Apply migrations"
	@echo "  make migrate-down    - Revert last migration"

install-deps:
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

run:
	$(PYTHON) main.py server

test:
	pytest --cov=app --cov-report=term-missing tests/

lint:
	ruff check .
	mypy .

fmt:
	ruff check --fix .
	ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov

migrate:
	alembic revision --autogenerate -m "$(msg)"

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

release:
	# Placeholder for release
	echo "Release"

swagger:
	# Placeholder for swagger generation
	echo "Swagger"

deploy:
	# Placeholder for deploy
	echo "Deploy"
