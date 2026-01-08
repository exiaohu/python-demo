#! /usr/bin/env bash

# Let the DB start
python -m app.backend_pre_start

# Run migrations
python -m app.cli migrate

# Create initial data in DB
python -m app.cli seed
