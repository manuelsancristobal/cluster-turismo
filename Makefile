.PHONY: help install install-dev lint test coverage clean maps notebooks run-notebooks

help:
	@echo "Available commands:"
	@echo "  make install          Install project dependencies"
	@echo "  make install-dev      Install project + development dependencies"
	@echo "  make lint             Run ruff linting and formatting"
	@echo "  make test             Run pytest tests"
	@echo "  make coverage         Run tests with coverage report"
	@echo "  make maps             Export notebooks as HTML maps"
	@echo "  make run-notebooks    Execute all notebooks"
	@echo "  make clean            Remove generated files and cache"

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
	pytest tests/ -v --cov=src/tourism_gaps --cov-report=html --cov-report=term-missing
	@echo "\nCoverage report generated in htmlcov/index.html"

maps:
	jupyter nbconvert --execute --to html "notebooks/Publico_Visualización_de_Atractivos.ipynb" --output-dir outputs/maps/
	jupyter nbconvert --execute --to html "notebooks/Comparacion_Atractivos_Destinos.ipynb" --output-dir outputs/maps/
	@echo "Maps exported to outputs/maps/"

run-notebooks:
	jupyter nbconvert --execute --to notebook "notebooks/Publico_Visualización_de_Atractivos.ipynb" --output "Publico_Visualización_de_Atractivos.ipynb"
	jupyter nbconvert --execute --to notebook "notebooks/Comparacion_Atractivos_Destinos.ipynb" --output "Comparacion_Atractivos_Destinos.ipynb"

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ipynb_checkpoints -exec rm -rf {} + 2>/dev/null || true
	rm -rf outputs/maps/*.html outputs/figures/*.png

.DEFAULT_GOAL := help
