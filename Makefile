.PHONY: build up down ps logs clean

# Build all containers
build:
	docker-compose build

# Start all services in background
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Show status of services
ps:
	docker-compose ps

# Tail logs
logs:
	docker-compose logs -f

# Run backend locally (for development)
run-backend:
	cd backend && pip install -r requirements.txt && python main.py

# Run frontend locally (for development)
run-frontend:
	cd frontend && npm install && npm run dev

# Full cleanup
clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf frontend/node_modules frontend/dist
