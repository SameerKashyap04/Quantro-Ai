.PHONY: help start stop restart logs migrate seed clean dev test

# ── Default ───────────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Docker ────────────────────────────────────────────────────
start: ## Start all services
	docker compose up -d

stop: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose down && docker compose up -d

logs: ## Tail logs for all services
	docker compose logs -f

logs-api: ## Tail API logs
	docker compose logs -f api

logs-db: ## Tail database logs
	docker compose logs -f postgres

build: ## Rebuild all containers
	docker compose build --no-cache

# ── Database ──────────────────────────────────────────────────
db-shell: ## Open psql shell
	docker compose exec postgres psql -U quantro_user -d quantro

db-reset: ## Reset database (WARNING: destroys data)
	docker compose down -v
	docker compose up -d postgres redis
	@echo "Waiting for PostgreSQL..."
	@sleep 5
	docker compose up -d api dashboard

# ── Development ───────────────────────────────────────────────
dev-api: ## Run API locally (no Docker)
	cd apps/api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-dashboard: ## Run dashboard locally (no Docker)
	cd apps/dashboard && npm run dev

install-api: ## Install Python dependencies
	cd apps/api && pip install -r requirements.txt

install-dashboard: ## Install Node dependencies
	cd apps/dashboard && npm install

# ── Testing ───────────────────────────────────────────────────
test-api: ## Run API tests
	cd apps/api && python -m pytest tests/ -v

test-indicators: ## Run indicator tests
	cd packages/indicators && python -m pytest tests/ -v

test-dashboard: ## Run frontend tests
	cd apps/dashboard && npm test

# ── Utilities ─────────────────────────────────────────────────
env: ## Copy .env.example to .env
	cp .env.example .env
	@echo "✅ Created .env — edit it with your credentials"

clean: ## Remove all containers, volumes, and build artifacts
	docker compose down -v --rmi local
	rm -rf apps/dashboard/node_modules apps/dashboard/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned"
