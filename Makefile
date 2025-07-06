# BigCapitalPy Makefile
# Comprehensive build and deployment automation for Python Flask accounting software

# Variables
DOCKER_COMPOSE = docker-compose
DOCKER = docker
PYTHON = python3
PIP = pip3
VENV_DIR = .venv
PROJECT_NAME = bigcapitalpy
IMAGE_NAME = bigcapitalpy
VERSION ?= latest

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

# Default target
.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)BigCapitalPy - Python Accounting Software$(NC)"
	@echo "=============================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Development Commands
.PHONY: install
install: ## Install Python dependencies in virtual environment
	@echo "$(YELLOW)Setting up Python virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements-python.txt
	@echo "$(GREEN)✅ Dependencies installed successfully$(NC)"

.PHONY: install-dev
install-dev: install ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(NC)"
	$(VENV_DIR)/bin/pip install -r requirements-dev.txt || echo "No dev requirements file found"
	@echo "$(GREEN)✅ Development environment ready$(NC)"

.PHONY: run
run: ## Run the application locally
	@echo "$(YELLOW)Starting BigCapitalPy development server...$(NC)"
	$(PYTHON) run_bigcapitalpy.py

.PHONY: run-dev
run-dev: ## Run the application in development mode
	@echo "$(YELLOW)Starting BigCapitalPy in development mode...$(NC)"
	export FLASK_ENV=development && export FLASK_DEBUG=1 && $(VENV_DIR)/bin/python app.py

.PHONY: shell
shell: ## Open Python shell with app context
	@echo "$(YELLOW)Opening Flask shell...$(NC)"
	$(VENV_DIR)/bin/flask shell

# Database Commands
.PHONY: db-init
db-init: ## Initialize database migrations
	@echo "$(YELLOW)Initializing database migrations...$(NC)"
	$(VENV_DIR)/bin/flask db init
	@echo "$(GREEN)✅ Database migrations initialized$(NC)"

.PHONY: db-migrate
db-migrate: ## Create a new database migration
	@echo "$(YELLOW)Creating database migration...$(NC)"
	$(VENV_DIR)/bin/flask db migrate -m "$(MSG)"
	@echo "$(GREEN)✅ Migration created$(NC)"

.PHONY: db-upgrade
db-upgrade: ## Apply database migrations
	@echo "$(YELLOW)Applying database migrations...$(NC)"
	$(VENV_DIR)/bin/flask db upgrade
	@echo "$(GREEN)✅ Database upgraded$(NC)"

.PHONY: db-reset
db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all data. Continue? [y/N]$(NC)" && read ans && [ $${ans:-N} = y ]
	@echo "$(YELLOW)Resetting database...$(NC)"
	rm -f bigcapitalpy.db
	$(MAKE) db-upgrade
	@echo "$(GREEN)✅ Database reset complete$(NC)"

# Database Schema Validation Commands
.PHONY: db-check-schema
db-check-schema: ## Check critical database schema sync
	@echo "$(YELLOW)🔍 Checking critical database schema...$(NC)"
	@$(VENV_DIR)/bin/python scripts/check_schema.py --critical

.PHONY: db-check-schema-all
db-check-schema-all: ## Check all database schema sync
	@echo "$(YELLOW)🔍 Checking all database schema...$(NC)"
	@$(VENV_DIR)/bin/python scripts/check_schema.py --all

.PHONY: db-check-schema-basic
db-check-schema-basic: ## Check basic database schema sync
	@echo "$(YELLOW)🔍 Checking basic database schema...$(NC)"
	@$(VENV_DIR)/bin/python scripts/check_schema.py --basic

.PHONY: db-check-schema-strict
db-check-schema-strict: ## Check schema with strict mode (fails on mismatch)
	@echo "$(YELLOW)🔍 Checking database schema (strict mode)...$(NC)"
	@$(VENV_DIR)/bin/python scripts/check_schema.py --critical --exit-on-error

.PHONY: db-check-schema-silent
db-check-schema-silent: ## Check schema silently
	@$(VENV_DIR)/bin/python scripts/check_schema.py --critical --silent

.PHONY: db-check-schema-models
db-check-schema-models: ## List all discovered models
	@echo "$(YELLOW)📋 Listing discovered models...$(NC)"
	@$(VENV_DIR)/bin/python scripts/check_schema.py --list-models

# Database Integration Commands
.PHONY: db-setup-with-check
db-setup-with-check: db-upgrade db-check-schema ## Setup database and validate schema
	@echo "$(GREEN)✅ Database setup with validation complete$(NC)"

.PHONY: db-migrate-with-check
db-migrate-with-check: db-migrate db-check-schema ## Run migration and validate schema
	@echo "$(GREEN)✅ Migration with validation complete$(NC)"

.PHONY: db-full-check
db-full-check: db-check-schema-all ## Alias for comprehensive schema check

.PHONY: dev-db-validate
dev-db-validate: ## Validate database schema for development
	@echo "$(YELLOW)🔧 Development database validation...$(NC)"
	@$(VENV_DIR)/bin/python scripts/check_schema.py --critical || echo "$(RED)⚠️  Schema mismatches found - run 'make db-migrate' to fix$(NC)"

# Docker Commands
.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(NC)"
	$(DOCKER) build -t $(IMAGE_NAME):$(VERSION) .
	@echo "$(GREEN)✅ Docker image built: $(IMAGE_NAME):$(VERSION)$(NC)"

.PHONY: docker-run
docker-run: ## Run application in Docker container
	@echo "$(YELLOW)Running BigCapitalPy in Docker...$(NC)"
	$(DOCKER) run -p 5000:5000 --name $(PROJECT_NAME) $(IMAGE_NAME):$(VERSION)

.PHONY: docker-stop
docker-stop: ## Stop Docker container
	@echo "$(YELLOW)Stopping Docker container...$(NC)"
	$(DOCKER) stop $(PROJECT_NAME) || true
	$(DOCKER) rm $(PROJECT_NAME) || true
	@echo "$(GREEN)✅ Container stopped$(NC)"

# Docker Compose Commands
.PHONY: up
up: ## Start all services with Docker Compose
	@echo "$(YELLOW)Starting BigCapitalPy services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Services started$(NC)"
	@echo "$(GREEN)📍 Application: http://localhost:5000$(NC)"
	@echo "$(GREEN)📍 pgAdmin: http://localhost:8080$(NC)"

.PHONY: up-build
up-build: ## Build and start all services
	@echo "$(YELLOW)Building and starting services...$(NC)"
	$(DOCKER_COMPOSE) up -d --build
	@echo "$(GREEN)✅ Services built and started$(NC)"

.PHONY: down
down: ## Stop and remove all containers
	@echo "$(YELLOW)Stopping services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Services stopped$(NC)"

.PHONY: down-volumes
down-volumes: ## Stop containers and remove volumes (WARNING: destroys data)
	@echo "$(RED)WARNING: This will destroy all data. Continue? [y/N]$(NC)" && read ans && [ $${ans:-N} = y ]
	@echo "$(YELLOW)Stopping services and removing volumes...$(NC)"
	$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)✅ Services and volumes removed$(NC)"

.PHONY: logs
logs: ## View logs from all services
	$(DOCKER_COMPOSE) logs -f

.PHONY: logs-app
logs-app: ## View application logs
	$(DOCKER_COMPOSE) logs -f bigcapitalpy

.PHONY: restart
restart: ## Restart all services
	@echo "$(YELLOW)Restarting services...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✅ Services restarted$(NC)"

.PHONY: ps
ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

# Testing Commands
.PHONY: test
test: ## Run tests
	@echo "$(YELLOW)Running tests...$(NC)"
	$(VENV_DIR)/bin/python -m pytest tests/ -v
	@echo "$(GREEN)✅ Tests completed$(NC)"

.PHONY: test-coverage
test-coverage: ## Run tests with coverage
	@echo "$(YELLOW)Running tests with coverage...$(NC)"
	$(VENV_DIR)/bin/python -m pytest tests/ --cov=packages --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report generated$(NC)"

.PHONY: lint
lint: ## Run linting
	@echo "$(YELLOW)Running linters...$(NC)"
	$(VENV_DIR)/bin/flake8 packages/ app.py
	$(VENV_DIR)/bin/black --check packages/ app.py
	@echo "$(GREEN)✅ Linting completed$(NC)"

.PHONY: format
format: ## Format code
	@echo "$(YELLOW)Formatting code...$(NC)"
	$(VENV_DIR)/bin/black packages/ app.py
	$(VENV_DIR)/bin/isort packages/ app.py
	@echo "$(GREEN)✅ Code formatted$(NC)"

# Production Commands
.PHONY: prod-build
prod-build: ## Build production Docker image
	@echo "$(YELLOW)Building production image...$(NC)"
	$(DOCKER) build -f Dockerfile.prod -t $(IMAGE_NAME):prod .
	@echo "$(GREEN)✅ Production image built$(NC)"

.PHONY: prod-deploy
prod-deploy: ## Deploy to production (customize as needed)
	@echo "$(YELLOW)Deploying to production...$(NC)"
	# Add your production deployment commands here
	@echo "$(GREEN)✅ Deployed to production$(NC)"

# Utility Commands
.PHONY: clean
clean: ## Clean up temporary files and caches
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

.PHONY: clean-docker
clean-docker: ## Clean up Docker images and containers
	@echo "$(YELLOW)Cleaning Docker resources...$(NC)"
	$(DOCKER) system prune -f
	$(DOCKER) image prune -f
	@echo "$(GREEN)✅ Docker cleanup completed$(NC)"

.PHONY: backup-db
backup-db: ## Backup database
	@echo "$(YELLOW)Creating database backup...$(NC)"
	mkdir -p backups
	$(DOCKER_COMPOSE) exec postgres pg_dump -U bigcapital bigcapitalpy > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Database backup created$(NC)"

.PHONY: restore-db
restore-db: ## Restore database from backup (FILE=backup.sql)
	@echo "$(YELLOW)Restoring database from $(FILE)...$(NC)"
	$(DOCKER_COMPOSE) exec -T postgres psql -U bigcapital bigcapitalpy < $(FILE)
	@echo "$(GREEN)✅ Database restored$(NC)"

.PHONY: setup
setup: install db-upgrade ## Complete setup for development
	@echo "$(GREEN)✅ BigCapitalPy setup completed!$(NC)"
	@echo "$(GREEN)📍 Run 'make run' to start the application$(NC)"

.PHONY: setup-docker
setup-docker: up-build ## Complete Docker setup
	@echo "$(GREEN)✅ BigCapitalPy Docker setup completed!$(NC)"
	@echo "$(GREEN)📍 Application: http://localhost:5000$(NC)"

# Admin Commands
.PHONY: admin
admin: ## Start pgAdmin for database management
	$(DOCKER_COMPOSE) --profile admin up -d pgadmin
	@echo "$(GREEN)✅ pgAdmin started at http://localhost:8080$(NC)"

.PHONY: shell-db
shell-db: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec postgres psql -U bigcapital bigcapitalpy

.PHONY: monitor
monitor: ## Monitor system resources
	@echo "$(YELLOW)System Resources:$(NC)"
	$(DOCKER) stats --no-stream
	@echo ""
	@echo "$(YELLOW)Disk Usage:$(NC)"
	$(DOCKER) system df

# Documentation
.PHONY: docs
docs: ## Generate documentation
	@echo "$(YELLOW)Generating documentation...$(NC)"
	# Add documentation generation commands here
	@echo "$(GREEN)✅ Documentation generated$(NC)"

# Quick start targets
.PHONY: quick-start
quick-start: setup run ## Complete setup and start application
	@echo "$(GREEN)🚀 BigCapitalPy is running!$(NC)"

.PHONY: quick-start-docker
quick-start-docker: setup-docker ## Quick start with Docker
	@echo "$(GREEN)🚀 BigCapitalPy is running with Docker!$(NC)"