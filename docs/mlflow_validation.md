# MLflow Experiment Tracking Validation Report

**Database**: `/home/lenovo/try_on/mlflow.db` (SQLite)  
**Artifact Root**: `/home/lenovo/try_on/mlartifacts`  
**Tracking URI**: `http://127.0.0.1:5001` (Active local MLflow tracking server)  
**Validation Date**: October 2026  
**Status**: **PASS**

---

## 1. Experiment Discovery & Database Integrity

SQLite direct schema inspection confirms the presence of the production virtual try-on experiment:

```sql
SELECT experiment_id, name, artifact_location FROM experiments;
```
- **Experiment ID**: `1`
- **Name**: `virtual-tryon-production`
- **Artifact Location**: `mlflow-artifacts:/1`
- **Lifecycle**: Active

---

## 2. Server Architecture & Tracking Mode

Because the experiment was configured with `mlflow-artifacts:/1` (artifact proxy routing), MLflow requires an HTTP tracking server with artifact proxy capabilities enabled. 

We established the service via `/home/lenovo/try_on/start_mlflow.sh`:
```bash
mlflow server \
  --backend-store-uri sqlite:////home/lenovo/try_on/mlflow.db \
  --default-artifact-root /home/lenovo/try_on/mlartifacts \
  --host 127.0.0.1 \
  --port 5001
```

---

## 3. Logged Parameters, Metrics, and Artifacts

Recent logged pipeline execution (`run_id = 029bfbc21da64035bbc4bae40b2b6085`):

### Hyperparameters Logged
- `model_architecture`: `"CatVTON (ComfyUI API Backend)"`
- `person_image`: `"person_1.jpg"`
- `garment_image`: `"garment_1.jpg"`
- `steps`: `25`
- `cfg`: `2.5`
- `seed`: `42`

### Metrics Logged
- `inference_latency_seconds`: `23.24`
- `pipeline_success`: `1.0`

### Image Artifacts Logged
- Output virtual try-on render: `ComfyUI_00034_.png` stored under `mlartifacts/1/029bfbc21da64035bbc4bae40b2b6085/artifacts/outputs/`
- Checksum: verified valid PNG, decodable, high dynamic range.

---

## 4. Automated Verification Test

The automated test `tests/test_mlflow_zenml.py` queries `mlflow.db` and the MLflow HTTP client:
- `test_mlflow_sqlite_db_exists`: **PASS**
- `test_mlflow_client_and_runs`: **PASS**
- `test_mlflow_artifacts_present`: **PASS**

