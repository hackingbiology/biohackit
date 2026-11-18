.PHONY: install migrate test lint dev shell psql

PNPM := node /home/gl-auditor/.local/lib/node_modules/pnpm/bin/pnpm.cjs
UV   := python3 -m uv

# ---- Setup -----------------------------------------------------------------

install: ## Install all backend and frontend dependencies
	cd backend && $(UV) sync
	cd frontend && $(PNPM) install

# ---- Database --------------------------------------------------------------

migrate: ## Apply Django migrations (requires DB running)
	cd backend && $(UV) run python manage.py migrate --noinput

makemigrations: ## Create new Django migrations
	cd backend && $(UV) run python manage.py makemigrations $(ARGS)

# ---- Tests -----------------------------------------------------------------

test: ## Run backend pytest + frontend jest
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend: ## Run backend pytest only (requires DB via Docker or local PG)
	cd backend && $(UV) run pytest

test-frontend: ## Run frontend Jest tests
	cd frontend && $(PNPM) test:ci

# ---- Linting / formatting --------------------------------------------------

lint: ## Run ruff (backend) + eslint (frontend)
	cd backend && $(UV) run ruff check .
	cd backend && $(UV) run ruff format --check .
	cd frontend && $(PNPM) lint

format: ## Auto-fix backend formatting with ruff
	cd backend && $(UV) run ruff check --fix .
	cd backend && $(UV) run ruff format .

# ---- Local dev (without Docker) --------------------------------------------

dev-backend: ## Start Django dev server
	cd backend && $(UV) run python manage.py runserver

dev-frontend: ## Start Next.js dev server
	cd frontend && $(PNPM) dev

# ---- Docker dev ------------------------------------------------------------

dev: ## Start all services with Docker Compose
	docker compose up

dev-build: ## Rebuild and start all services
	docker compose up --build

down: ## Stop all Docker Compose services
	docker compose down

# ---- Helpers ----------------------------------------------------------------

shell: ## Open Django shell
	cd backend && $(UV) run python manage.py shell

psql: ## Open psql in the Docker db container
	docker compose exec db psql -U biohackit -d biohackit

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
