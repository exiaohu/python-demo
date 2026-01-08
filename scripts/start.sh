#!/bin/bash
set -e

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start server
echo "Starting server..."
python -m app.cli server
