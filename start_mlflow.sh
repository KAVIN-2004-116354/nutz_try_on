#!/bin/bash
cd /home/lenovo/try_on
source /home/lenovo/try_on/venv/bin/activate
fuser -k 5001/tcp 2>/dev/null
pkill -9 -f 'huey_consumer' 2>/dev/null
sleep 1
exec mlflow server \
  --backend-store-uri sqlite:////home/lenovo/try_on/mlflow.db \
  --default-artifact-root /home/lenovo/try_on/mlartifacts \
  --host 0.0.0.0 \
  --port 5001 \
  --workers 1 > /home/lenovo/try_on/mlflow_server.log 2>&1
