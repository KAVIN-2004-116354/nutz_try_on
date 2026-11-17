import os
import shutil
import subprocess

def test_dvc_files_exist():
    assert os.path.exists("data.dvc"), "data.dvc tracking file missing"
    assert os.path.exists(".dvcignore"), ".dvcignore file missing"
    assert os.path.exists("data/benchmark/person/person_1.jpg"), "Benchmark person image missing"
    assert os.path.exists("data/benchmark/garment/garment_1.jpg"), "Benchmark garment image missing"

def test_dvc_status():
    dvc_bin = shutil.which("dvc") or os.path.expanduser("~/try_on/venv/bin/dvc")
    result = subprocess.run(
        [dvc_bin, "status"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"DVC status error: {result.stderr}"
    assert "Data and pipelines are up to date" in result.stdout or result.stdout.strip() == ""
