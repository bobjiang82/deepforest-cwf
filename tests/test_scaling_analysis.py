import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "benchmark" / "deepforest" / "analyze_scaling.py"


def write_summary(path: Path, *, n_jobs: int, fit_seconds_median: float, total_seconds_median: float, accuracy_percent_median: float = 53.4):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "runs": 3,
                "fit_seconds_mean": fit_seconds_median,
                "fit_seconds_median": fit_seconds_median,
                "fit_seconds_stdev": 0.1,
                "predict_seconds_mean": 1.0,
                "predict_seconds_median": 1.0,
                "load_seconds_mean": 0.1,
                "load_seconds_median": 0.1,
                "total_seconds_mean": total_seconds_median,
                "total_seconds_median": total_seconds_median,
                "total_seconds_stdev": 0.2,
                "accuracy_percent_mean": accuracy_percent_median,
                "accuracy_percent_median": accuracy_percent_median,
                "tag": f"scale_{n_jobs}",
                "backend": "custom",
                "n_jobs": n_jobs,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_analyze_scaling_produces_speedup_and_efficiency(tmp_path: Path):
    sweep_dir = tmp_path / "scaling"
    write_summary(sweep_dir / "n_jobs_1" / "summary.json", n_jobs=1, fit_seconds_median=100.0, total_seconds_median=104.0)
    write_summary(sweep_dir / "n_jobs_4" / "summary.json", n_jobs=4, fit_seconds_median=30.0, total_seconds_median=34.0)
    write_summary(sweep_dir / "n_jobs_8" / "summary.json", n_jobs=8, fit_seconds_median=20.0, total_seconds_median=24.0)

    out_json = tmp_path / "analysis.json"
    out_table = tmp_path / "analysis.txt"

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input-dir",
            str(sweep_dir),
            "--json-out",
            str(out_json),
            "--table-out",
            str(out_table),
        ],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["baseline_n_jobs"] == 1
    assert [row["n_jobs"] for row in data["points"]] == [1, 4, 8]
    assert data["points"][1]["fit_speedup_vs_baseline"] == 3.333333
    assert data["points"][1]["fit_efficiency_vs_baseline"] == 0.833333
    assert data["best_fit_median"]["n_jobs"] == 8
    table_text = out_table.read_text(encoding="utf-8")
    assert "fit_speedup_vs_baseline" in table_text
    assert "n_jobs" in table_text


def test_analyze_scaling_uses_lowest_n_jobs_as_default_baseline(tmp_path: Path):
    sweep_dir = tmp_path / "scaling"
    write_summary(sweep_dir / "n_jobs_12" / "summary.json", n_jobs=12, fit_seconds_median=60.0, total_seconds_median=65.0)
    write_summary(sweep_dir / "n_jobs_48" / "summary.json", n_jobs=48, fit_seconds_median=20.0, total_seconds_median=25.0)

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--input-dir", str(sweep_dir)],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["baseline_n_jobs"] == 12
    assert data["points"][1]["fit_speedup_vs_baseline"] == 3.0
    assert data["points"][1]["fit_efficiency_vs_baseline"] == 0.75
