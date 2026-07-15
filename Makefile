.PHONY: help install dev build up down logs test db-migrate db-show

help:
	@echo "SLFN Nexus Platform - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install all dependencies"
	@echo "  make dev          Start development environment"
	@echo ""
	@echo "Docker:"
	@echo "  make up           Start all services"
	@echo "  make down         Stop all services"
	@echo "  make logs         View logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate   Run database migrations"
	@echo "  make db-show      Show database tables"
	@echo ""
	@echo "Testing:"
	@echo "  make test         Run tests"
	@echo ""
	@echo "Build:"
	@echo "  make build        Build Docker images"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Start development environment
dev:
	@echo "Starting development environment..."
	docker-compose up -d
	@echo "Services starting..."
	@sleep 5
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run database migrations
db-migrate:
	cd backend && alembic upgrade head

# Show database tables
db-show:
	docker-compose exec db psql -U hl_user -d hl_nexus -c "\dt"

# Run tests
test:
	cd backend && pytest tests/ -v

# Build Docker images
build:
	docker-compose build

# Clean up
clean:
	docker-compose down -v
	docker system prune -f

# Reset database
reset-db:
	docker-compose down -v
	docker volume rm $$(docker volume ls -q) || true
	docker-compose up -d