.PHONY: help install install-dev lint test coverage clean maps run-notebooks generate-assets deploy

help:
	@echo "Comandos disponibles:"
	@echo "  make install          Instalar dependencias del proyecto"
	@echo "  make install-dev      Instalar proyecto + dependencias de desarrollo"
	@echo "  make lint             Ejecutar linting y formateo con ruff"
	@echo "  make test             Ejecutar tests con pytest"
	@echo "  make coverage         Ejecutar tests con reporte de cobertura"
	@echo "  make maps             Exportar notebooks como mapas HTML"
	@echo "  make run-notebooks    Ejecutar todos los notebooks"
	@echo "  make generate-assets  Generar todos los gráficos y mapas"
	@echo "  make deploy           Generar assets + copiar al repo Jekyll"
	@echo "  make clean            Eliminar archivos generados y caché"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,notebooks]"
	pre-commit install

lint:
	ruff check src/ tests/
	ruff format src/ tests/

test:
	pytest tests/ -v

coverage:
	pytest tests/ -v --cov=src/cluster_turismo --cov-report=html --cov-report=term-missing
	@echo "\nReporte de cobertura generado en htmlcov/index.html"

maps:
	jupyter nbconvert --execute --to html "notebooks/Publico_Visualización_de_Atractivos.ipynb" --output-dir assets/maps/
	jupyter nbconvert --execute --to html "notebooks/Comparacion_Atractivos_Destinos.ipynb" --output-dir assets/maps/
	@echo "Mapas exportados a assets/maps/"

run-notebooks:
	jupyter nbconvert --execute --to notebook "notebooks/Publico_Visualización_de_Atractivos.ipynb" --output "Publico_Visualización_de_Atractivos.ipynb"
	jupyter nbconvert --execute --to notebook "notebooks/Comparacion_Atractivos_Destinos.ipynb" --output "Comparacion_Atractivos_Destinos.ipynb"

generate-assets:
	python scripts/generate_assets.py

deploy: generate-assets
	python scripts/deploy.py

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ipynb_checkpoints -exec rm -rf {} + 2>/dev/null || true
	rm -rf assets/

.DEFAULT_GOAL := help
