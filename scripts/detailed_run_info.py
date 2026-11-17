import sqlite3

conn = sqlite3.connect("/home/lenovo/try_on/mlflow.db")
c = conn.cursor()

for run_id in ["77fd10b5be724eb4a158d7e83a484697", "e0eb0d5255ca4418b3a8d23a634328ba", "cad78a2fc27a4d4681c2fe8a5ea5ea80"]:
    print(f"=== RUN {run_id[:8]} ===")
    params = c.execute("SELECT key, value FROM params WHERE run_uuid = ?", (run_id,)).fetchall()
    print("PARAMS:", params)
    metrics = c.execute("SELECT key, value, step FROM metrics WHERE run_uuid = ?", (run_id,)).fetchall()
    print("METRICS:", metrics)

