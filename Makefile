.PHONY: help install install-dev setup test lint format clean run-api run-frontend docker-up docker-down

help:
	@echo "Comandos disponibles:"
	@echo "  make install        - Instalar dependencias de producción"
	@echo "  make install-dev    - Instalar dependencias de desarrollo"
	@echo "  make setup          - Setup completo del proyecto"
	@echo "  make test           - Ejecutar tests"
	@echo "  make test-cov       - Ejecutar tests con coverage report"
	@echo "  make lint           - Ejecutar linters"
	@echo "  make format         - Formatear código"
	@echo "  make clean          - Limpiar archivos temporales"
	@echo "  make run-api        - Correr API FastAPI"
	@echo "  make run-frontend   - Correr frontend Streamlit"
	@echo "  make docker-up      - Levantar servicios con Docker"
	@echo "  make docker-down    - Detener servicios Docker"

install:
	./venv/bin/pip install -r requirements.txt

install-dev:
	./venv/bin/pip install -r requirements-dev.txt
	./venv/bin/pre-commit install

setup:
	@echo "🚀 Configurando proyecto..."
	./venv/bin/python scripts/setup_database.py
	./venv/bin/python scripts/seed_data.py
	./venv/bin/python scripts/test_setup.py

test:
	./venv/bin/pytest tests/ -v

test-cov:
	./venv/bin/pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

lint:
	@echo "🔍 Ejecutando linters..."
	./venv/bin/ruff check src/ tests/ config/
	./venv/bin/mypy src/ config/

format:
	@echo "✨ Formateando código..."
	./venv/bin/black src/ tests/ config/ scripts/
	./venv/bin/ruff check src/ tests/ config/ --fix

clean:
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache/ .ruff_cache/

run-api:
	@echo "🚀 Iniciando API FastAPI..."
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "🚀 Iniciando frontend Streamlit..."
	streamlit run frontend/app.py

docker-up:
	@echo "🐳 Levantando servicios con Docker..."
	docker compose up -d

docker-down:
	@echo "🐳 Deteniendo servicios Docker..."
	docker compose down
