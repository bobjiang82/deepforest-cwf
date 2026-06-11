import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPEAT_RUNNER = ROOT / "benchmark" / "deepforest" / "repeat_runner.py"


def test_repeat_runner_can_read_simple_yaml_config_without_pyyaml(tmp_path: Path):
    config_path = tmp_path / "benchmark.yaml"
    config_path.write_text(
        """

dataset:
  openml_id: 159
  cache_dir: ./data/openml_cache
split:
  test_size: 0.2
  random_state: 42
model:
  n_jobs: 48
  backend: custom
run:
  repeats: 1
  warmup_runs: 0
  output_dir: ./results
  tag: smoke
comparison:
  metrics:
    - fit_seconds_mean
    - fit_seconds_median
""".lstrip(),
        encoding="utf-8",
    )

    script_path = tmp_path / "emit_json.py"
    script_path.write_text(
        """
import argparse
import json

p = argparse.ArgumentParser()
p.add_argument('--json-out', default='')
p.add_argument('--csv-out', default='')
p.add_argument('--dataset-id')
p.add_argument('--test-size')
p.add_argument('--random-state')
p.add_argument('--n-jobs')
p.add_argument('--backend')
p.add_argument('--cache-dir')
p.add_argument('--tag')
args = p.parse_args()
result = {
    'fit_seconds': 1.0,
    'predict_seconds': 0.1,
    'total_seconds': 1.2,
    'accuracy_percent': 50.0,
    'load_seconds': 0.05,
}
if args.json_out:
    with open(args.json_out, 'w', encoding='utf-8') as f:
        json.dump(result, f)
print(json.dumps(result))
""".lstrip(),
        encoding="utf-8",
    )

    out_dir = tmp_path / "out"
    yaml_blocker = tmp_path / "yaml.py"
    yaml_blocker.write_text("raise ModuleNotFoundError('No module named yaml')\n", encoding="utf-8")

    env = dict(**__import__('os').environ)
    env["PYTHONPATH"] = str(tmp_path)

    proc = subprocess.run(
        [
            sys.executable,
            str(REPEAT_RUNNER),
            "--config",
            str(config_path),
            "--python",
            sys.executable,
            "--script",
            str(script_path),
            "--out-dir",
            str(out_dir),
            "--tag",
            "fallback_test",
        ],
        capture_output=True,
        text=True,
        env=env,
    )

    assert proc.returncode == 0, proc.stderr
    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["n_jobs"] == 48
    assert summary["fit_seconds_median"] == 1.0
