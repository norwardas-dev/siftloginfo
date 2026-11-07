.PHONY: help install lint format typecheck test cov check docker clean

help:  ## Show available targets
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install:  ## Install the package in editable mode with dev tools
	pip install -e ".[dev]"

lint:  ## Run ruff linter and format check
	ruff check src tests
	ruff format --check src tests

format:  ## Auto-format and fix lint issues
	ruff format src tests
	ruff check --fix src tests

typecheck:  ## Run mypy in strict mode
	mypy

test:  ## Run the test suite
	pytest

cov:  ## Run tests with coverage report
	pytest --cov --cov-report=term-missing

check: lint typecheck test  ## Everything CI runs

docker:  ## Build the Docker image
	docker build -t logsift .

clean:  ## Remove build and cache artifacts
	rm -rf build dist .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
