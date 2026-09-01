.PHONY: help up down down-v logs \
	backend-install backend-dev backend-test \
	frontend-install frontend-dev frontend-typecheck \
	pipeline-install pipeline-local pipeline-test \
	sample-data export-orders generate-traffic

help:
	@echo "Docker (app + full observability stack):"
	@echo "  make up                - docker compose up --build"
	@echo "  make down              - docker compose down"
	@echo "  make down-v            - docker compose down -v (also wipes volumes/data)"
	@echo "  make logs              - tail logs for all services"
	@echo ""
	@echo "Backend (run outside Docker):"
	@echo "  make backend-install   - pip install backend requirements"
	@echo "  make backend-dev       - run FastAPI with reload on :8000"
	@echo "  make backend-test      - run backend pytest suite"
	@echo ""
	@echo "Frontend (run outside Docker):"
	@echo "  make frontend-install  - npm install"
	@echo "  make frontend-dev      - run Vite dev server on :5173"
	@echo "  make frontend-typecheck- run tsc --noEmit"
	@echo ""
	@echo "Data pipeline:"
	@echo "  make pipeline-install  - pip install data_pipeline requirements (pyspark, delta-spark)"
	@echo "  make sample-data       - regenerate data/orders.csv sample dataset"
	@echo "  make pipeline-local    - run Bronze -> Silver -> Gold locally (no Databricks)"
	@echo "  make pipeline-test     - run data_pipeline pytest suite"
	@echo ""
	@echo "Demo helpers (require the backend to be running):"
	@echo "  make export-orders     - export SQLite orders -> data/orders.csv"
	@echo "  make generate-traffic  - send sample traffic to the API for Grafana"

# --- Docker ---

up:
	docker compose up --build

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f

# --- Backend ---

backend-install:
	pip install -r backend/requirements.txt

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

backend-test:
	cd backend && pytest

# --- Frontend ---

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-typecheck:
	cd frontend && npm run typecheck

# --- Data pipeline ---

pipeline-install:
	pip install -r data_pipeline/requirements.txt

sample-data:
	python data_pipeline/generate_sample_orders.py

pipeline-local:
	python data_pipeline/run_local_pipeline.py

pipeline-test:
	cd data_pipeline && pytest

# --- Demo helpers ---

export-orders:
	cd backend && python scripts/export_orders.py

generate-traffic:
	cd backend && python scripts/generate_traffic.py
