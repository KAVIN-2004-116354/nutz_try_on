import sqlite3
import os
import mlflow

db_path = "/home/lenovo/try_on/mlflow.db"
print(f"Connecting to SQLite database: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Query experiments
cur.execute("SELECT experiment_id, name, artifact_location FROM experiments")
experiments = cur.fetchall()
print("\n--- MLflow Experiments ---")
for exp in experiments:
    print(f"ID: {exp[0]} | Name: {exp[1]} | Artifacts: {exp[2]}")

# Query recent runs
cur.execute("SELECT run_uuid, experiment_id, status, start_time, end_time FROM runs ORDER BY start_time DESC LIMIT 10")
runs = cur.fetchall()
print("\n--- Recent MLflow Runs ---")
for r in runs:
    print(f"Run UUID: {r[0]} | Exp ID: {r[1]} | Status: {r[2]} | Start: {r[3]}")

# Test direct MLflow connection via file tracking URI
file_uri = f"sqlite:///{db_path}"
print(f"\nTesting MLflow client with tracking URI: {file_uri}")
mlflow.set_tracking_uri(file_uri)
client = mlflow.tracking.MlflowClient(file_uri)
all_exps = client.search_experiments()
print(f"Successfully connected via MLflow Client. Found {len(all_exps)} experiments.")
for exp in all_exps:
    print(f"  - {exp.name} (id={exp.experiment_id})")

conn.close()

