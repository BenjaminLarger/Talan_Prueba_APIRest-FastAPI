.PHONY: help install run test migrate migrate-new clean lint

help:
	@echo "FastAPI Task Management API - Available Commands"
	@echo ""
	@echo "  make install        Install dependencies from requirements.txt"
	@echo "  make run            Start the development server"
	@echo "  make test           Run test suite with pytest"
	@echo "  make lint           Auto-format code with black and isort"
	@echo "  make clean          Remove cache and temporary files"

install:
	pip install -r requirements.txt

venv:
	source /tmp/claude/-media-blarger-T7-projects-interview-Talan_Prueba_APIRest-FastAPI/f6a5aecd-1413-4e89-891c-0874d33d05c0/scratchpad/.venv/bin/activate

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	black app/ tests/
	isort app/ tests/

lint-check:
	flake8 app/ tests/ --max-line-length=120

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".eggs" -exec rm -rf {} + 2>/dev/null || true
