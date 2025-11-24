# Cross-platform shell configuration
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# LitRevu - Project automation with Just
# Run 'just --list' to see all available commands

# Default recipe to display help
default:
    @just --list

# === Docker Commands ===

# Build and start the application with Docker Compose
docker-up:
    docker compose -f docker/compose.yml up --build

# Stop the Docker containers
docker-down:
    docker compose -f docker/compose.yml down

# Stop and remove containers, volumes, and images
docker-clean:
    docker compose -f docker/compose.yml down -v --rmi all
    rm -rf data/

# === Local Development Commands ===

# Install project dependencies with uv
install:
    uv sync

# Apply database migrations
migrate:
    python manage.py migrate

# Create test users (Bob and Tom)
create-test-users:
    python manage.py create_test_users

# Collect static files
collectstatic:
    python manage.py collectstatic --noinput

# Run the development server
run:
    python manage.py runserver

# Setup the project for local development (install + migrate + test users + collectstatic)
setup: install migrate create-test-users collectstatic
    @echo "✅ Local development setup complete!"
    @echo "Run 'just run' to start the development server"

# === Combined Commands ===

# Full setup with Docker
docker-setup: docker-clean docker-up

# Quick start for local development
quick-start: setup run

# === Database Commands ===

# Create a new Django migration
makemigrations:
    python manage.py makemigrations

# Reset the database (delete and recreate)
reset-db:
    rm -rf data/db.sqlite3
    python manage.py migrate
    python manage.py create_test_users
    @echo "✅ Database reset complete!"

# === Utility Commands ===

# Create a new Django superuser
createsuperuser:
    python manage.py createsuperuser

# Open Django shell
shell:
    python manage.py shell

# Check for Django issues
check:
    python manage.py check

# Format code with Black
format:
    black .

# Check formatting with Black (without modifying files)
format-check:
    black --check .

# Lint code with Flake8 (PEP8 compliance)
lint:
    flake8 .

# Lint with Ruff (modify files)
lint-ruff:
    ruff check --fix .

# Format with Ruff
format-ruff:
    ruff format .

# Run all quality checks (Black + Flake8)
qa:
    format-check lint


