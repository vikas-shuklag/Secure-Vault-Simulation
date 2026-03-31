@echo off
echo Starting Virtual HSM API Service...
echo To stop the service, press CTRL+C

call .\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
