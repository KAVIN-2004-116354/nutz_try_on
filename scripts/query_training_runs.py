import sqlite3

conn = sqlite3.connect("/home/lenovo/try_on/mlflow.db")
c = conn.cursor()

print("--- TRAINING RUNS IN MLFLOW ---")
runs = c.execute("SELECT run_uuid, experiment_id, status, start_time, end_time FROM runs ORDER BY start_time DESC").fetchall()
for r in runs:
    run_id, exp_id, status, start, end = r
    # Get params
    params = dict(c.execute("SELECT key, value FROM params WHERE run_uuid = ?", (run_id,)).fetchall())
    # Get max metrics
    metrics = dict(c.execute("SELECT key, MAX(value) FROM metrics WHERE run_uuid = ? GROUP BY key", (run_id,)).fetchall())
    print(f"Run: {run_id[:8]} | Exp: {exp_id} | Status: {status} | Epochs/Steps: {params.get('num_epochs') or params.get('epochs') or metrics.get('epoch', 'N/A')} | LR: {params.get('learning_rate', 'N/A')} | Final Loss: {metrics.get('train_loss') or metrics.get('loss', 'N/A')}")

