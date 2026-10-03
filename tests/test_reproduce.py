import csv
import json
import os
import subprocess
import sys
from pathlib import Path


def test_regenerate_real_reports(tmp_path):
    root = Path(__file__).parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")
    subprocess.run(
        [sys.executable, str(root / "scripts/reproduce.py"), "--output", str(tmp_path)],
        env=env,
        cwd=root,
        check=True,
        capture_output=True,
    )
    rows = list(csv.DictReader((tmp_path / "reports/metrics.csv").open()))
    assert len(rows) == 6
    assert {row["ordering"] for row in rows} == {"sequential", "keyed"}
    assert all(float(row["mse"]) > 0 for row in rows)
    manifest = json.loads((tmp_path / "reports/run_manifest.json").read_text())
    assert "Synthetic" in manifest["scope"]
    assert manifest["config"]["seed"] == 20261003
    assert (tmp_path / "docs/assets/hero.png").stat().st_size > 1000
