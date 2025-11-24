# Build stage
FROM python:3.13-alpine AS build-stage

WORKDIR /usr/src/app

# Install build dependencies
RUN apk add --no-cache --update gcc libc-dev

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install Python dependencies in a virtual environment
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

# Runtime stage
FROM python:3.13-alpine

WORKDIR /usr/src/app

# Environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=litrevu.settings

RUN adduser --system --no-create-home nonroot

# Copy UV and virtual environment from build stage
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY --from=build-stage /usr/src/app/.venv /usr/src/app/.venv

ENV PATH="/usr/src/app/.venv/bin:$PATH"

# Copy the application code
COPY . .

# Copy and set permissions for entrypoint script
COPY docker/entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Create directory for SQLite database and static files
RUN mkdir -p /usr/src/app/data /usr/src/app/staticfiles

# Collect static files and run migrations
RUN python manage.py collectstatic --noinput

# Change ownership of data directory, db file, staticfiles, and logs
RUN chown -R nonroot:nogroup /usr/src/app/data /usr/src/app/staticfiles /usr/src/app/logs
RUN if [ -f "db.sqlite3" ]; then chown nonroot:nogroup db.sqlite3; fi


USER nonroot

EXPOSE 8000

# Start the Django application with its custom commands
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
