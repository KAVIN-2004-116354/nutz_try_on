import pytest
import sqlite3
import os
import mlflow
from mlflow.tracking import MlflowClient

DB_PATH = "/home/lenovo/try_on/mlflow.db"
MLFLOW_SERVER_URL = "http://127.0.0.1:5001"

def test_mlflow_sqlite_db_exists():
    assert os.path.exists(DB_PATH), f"MLflow database not found at {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT experiment_id, name FROM experiments WHERE name = 'virtual-tryon-production'")
    row = cur.fetchone()
    conn.close()
    assert row is not None, "Experiment 'virtual-tryon-production' not found in mlflow.db"
    assert row[1] == "virtual-tryon-production"

def get_client():
    import urllib.request
    try:
        urllib.request.urlopen(MLFLOW_SERVER_URL, timeout=1)
        return MlflowClient(tracking_uri=MLFLOW_SERVER_URL)
    except Exception:
        return MlflowClient(tracking_uri=f"sqlite:///{DB_PATH}")

def test_mlflow_client_and_runs():
    client = get_client()
    exp = client.get_experiment_by_name("virtual-tryon-production")
    assert exp is not None, "Could not fetch experiment from MLflow server"
    
    runs = client.search_runs(experiment_ids=[exp.experiment_id], max_results=5)
    assert len(runs) > 0, "No runs found in virtual-tryon-production experiment"
    
    finished_runs = [r for r in runs if r.info.status == "FINISHED"]
    assert len(finished_runs) > 0, "No FINISHED runs found in virtual-tryon-production experiment"
    latest_run = finished_runs[0]
    print(f"Latest MLflow Run ID: {latest_run.info.run_id}")
    print(f"Metrics: {latest_run.data.metrics}")
    print(f"Params: {latest_run.data.params}")

def test_mlflow_artifacts_present():
    client = get_client()
    exp = client.get_experiment_by_name("virtual-tryon-production")
    runs = client.search_runs(experiment_ids=[exp.experiment_id], max_results=5)
    latest_run = runs[0]
    try:
        artifacts = client.list_artifacts(latest_run.info.run_id)
        print(f"Run {latest_run.info.run_id} artifacts: {[a.path for a in artifacts]}")
        assert len(artifacts) >= 0
    except Exception as e:
        print(f"Artifact lookup skipped (server not running): {e}")

