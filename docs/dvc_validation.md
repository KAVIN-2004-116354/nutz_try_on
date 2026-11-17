# DVC Data Version Control Validation Report

**Tracking File**: `data.dvc`  
**Ignore File**: `.dvcignore`  
**Dataset Path**: `data/benchmark/`  
**Validation Date**: October 2026  
**Status**: **PASS**

---

## 1. DVC Configuration & Manifest Inspection

The project tracks core benchmark images to guarantee deterministic regression benchmarking across models and hardware changes:

### `data.dvc` Specification
```yaml
outs:
- md5: e92734da664ac4fa75af2c03758f4bc2.dir
  size: 223694
  nfiles: 2
  hash: md5
  path: data
```

### Tracked File Tree & Hashes
1. `data/benchmark/person/person_1.jpg`
   - **Size**: 165,599 bytes
   - **Dimensions**: 1204 x 1600 pixels
   - **Description**: High-resolution studio female fashion model in neutral standing pose.
2. `data/benchmark/garment/garment_1.jpg`
   - **Size**: 58,095 bytes
   - **Dimensions**: 768 x 1024 pixels
   - **Description**: Flat-lay casual upper-body blouse.

- **Combined Tracked Size**: 223,694 bytes across 2 files.
- **Match with `data.dvc`**: Exactly 223,694 bytes and 2 files.

---

## 2. `.dvcignore` Verification

`.dvcignore` contains:
```text
outputs/
mlartifacts/
*.log
__pycache__/
```
This ensures large runtime outputs, temporary logs, and generated try-on PNGs do not pollute the Git or DVC cache.

---

## 3. Runtime DVC Status Verification

Running `dvc status` in `/home/lenovo/try_on`:
```text
$ dvc status
Data and pipelines are up to date.
```
All tracked benchmark datasets are verified intact and synchronized with the repository hash manifest.

