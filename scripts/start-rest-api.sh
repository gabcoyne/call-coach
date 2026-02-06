#!/bin/bash
# Start the REST API server for frontend integration

echo "Starting Call Coaching REST API..."
echo "Endpoints will be available at http://localhost:8000"
echo ""

uv run uvicorn api.rest_server:app --host 0.0.0.0 --port 8000 --reload
