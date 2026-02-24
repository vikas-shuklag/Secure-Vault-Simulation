#!/bin/bash
echo "Starting Virtual HSM API Service..."
echo "To stop the service, press CTRL+C"

# Ensure script halts on errors
set -e

# Run standard dev server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
