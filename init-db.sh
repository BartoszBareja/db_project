#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
until pg_isready -U postgres; do
  sleep 1
done

echo "Importing SQL dump..."
psql -U postgres -d not_steam < /docker-entrypoint-initdb.d/not_steam_dump.sql

echo "Dump import complete."
