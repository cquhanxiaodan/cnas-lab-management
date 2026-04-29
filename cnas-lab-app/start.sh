#!/bin/bash
set -e

cd /app/backend

mkdir -p data uploads

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
