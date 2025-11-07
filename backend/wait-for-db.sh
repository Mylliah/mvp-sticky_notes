#!/bin/sh
set -e

echo "Waiting for database connection at host: db..."
until pg_isready -h db -p 5432 -U "app"; do
  sleep 2
done

echo "Database is ready, starting Flask..."
exec "$@"