.PHONY: install dev build run test lint

install:
	pip install -r backend/requirements.txt && cd frontend && npm install

dev:
	@echo "Starting backend and frontend dev servers..."
	(uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &) && \
	cd frontend && npm run dev

build:
	cd frontend && npm run build

run:
	uvicorn backend.main:app --host 0.0.0.0 --port 8000

test:
	pytest backend/tests/ -v

lint:
	ruff check backend/
