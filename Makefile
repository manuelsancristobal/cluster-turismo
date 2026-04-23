.PHONY: help install-dev lint test generate-assets deploy clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install-dev      Instalar proyecto + dependencias de desarrollo"
	@echo "  make lint             Ejecutar linting y formateo con ruff"
	@echo "  make test             Ejecutar tests con pytest"
	@echo "  make generate-assets  Generar todos los gráficos y mapas"
	@echo "  make deploy           Copiar assets al repo Jekyll"
	@echo "  make clean            Eliminar archivos generados y caché"

install-dev:
	pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check src/ tests/
	ruff format src/ tests/

test:
	pytest tests/ -v

generate-assets:
	python run.py generate-assets

deploy:
	python run.py deploy

clean:
	rm -rf build/ dist/ src/*.egg-info
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf assets/

.DEFAULT_GOAL := help
