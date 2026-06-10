#!/usr/bin/env python3
import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path


def run_once(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    data = json.loads(proc.stdout)
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--python', default=sys.executable)
    p.add_argument('--script', default='benchmark/deepforest/benchmark_df_openml.py')
    p.add_argument('--repeats', type=int, default=5)
    p.add_argument('--warmup-runs', type=int, default=1)
    p.add_argument('--n-jobs', type=int, default=1)
    p.add_argument('--dataset-id', type=int, default=159)
    p.add_argument('--test-size', type=float, default=0.2)
    p.add_argument('--random-state', type=int, default=42)
    p.add_argument('--cache-dir', default='./data/openml_cache')
    p.add_argument('--out-dir', default='./results')
    p.add_argument('--tag', default='')
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    base_cmd = [
        args.python,
        args.script,
        '--dataset-id', str(args.dataset_id),
        '--test-size', str(args.test_size),
        '--random-state', str(args.random_state),
        '--n-jobs', str(args.n_jobs),
        '--cache-dir', args.cache_dir,
        '--tag', args.tag,
    ]

    for i in range(args.warmup_runs):
        print(f'Warmup {i+1}/{args.warmup_runs}...', file=sys.stderr)
        run_once(base_cmd)

    runs = []
    csv_path = out_dir / 'benchmark_runs.csv'
    for i in range(args.repeats):
        json_path = out_dir / f'run_{i+1:02d}.json'
        cmd = base_cmd + ['--json-out', str(json_path), '--csv-out', str(csv_path)]
        print(f'Measured run {i+1}/{args.repeats}...', file=sys.stderr)
        runs.append(run_once(cmd))

    fit_times = [r['fit_seconds'] for r in runs]
    predict_times = [r['predict_seconds'] for r in runs]
    total_times = [r['total_seconds'] for r in runs]
    accuracies = [r['accuracy_percent'] for r in runs]

    summary = {
        'runs': len(runs),
        'fit_seconds_mean': round(statistics.mean(fit_times), 6),
        'fit_seconds_median': round(statistics.median(fit_times), 6),
        'fit_seconds_stdev': round(statistics.stdev(fit_times), 6) if len(fit_times) > 1 else 0.0,
        'predict_seconds_mean': round(statistics.mean(predict_times), 6),
        'predict_seconds_median': round(statistics.median(predict_times), 6),
        'total_seconds_mean': round(statistics.mean(total_times), 6),
        'total_seconds_median': round(statistics.median(total_times), 6),
        'total_seconds_stdev': round(statistics.stdev(total_times), 6) if len(total_times) > 1 else 0.0,
        'accuracy_percent_mean': round(statistics.mean(accuracies), 6),
        'accuracy_percent_median': round(statistics.median(accuracies), 6),
    }

    summary_path = out_dir / 'summary.json'
    summary_path.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
