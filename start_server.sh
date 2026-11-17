#!/bin/bash
cd /home/lenovo/try_on
source venv/bin/activate
exec uvicorn src.gateway.app:app --host 0.0.0.0 --port 8000
