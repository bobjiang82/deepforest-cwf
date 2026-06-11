#!/usr/bin/env python3
import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    yaml = None


def extract_json_from_stdout(stdout: str):
    lines = stdout.strip().splitlines()
    for i in range(len(lines) - 1, -1, -1):
        candidate = "\n".join(lines[i:]).strip()
        if not candidate.startswith("{"):
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise json.JSONDecodeError("No JSON object found in stdout", stdout, 0)


def run_once(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    data = extract_json_from_stdout(proc.stdout)
    return data


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if yaml is not None:
        return yaml.safe_load(content)
    return load_simple_yaml_config(content)


def load_simple_yaml_config(content: str):
    root = {}
    stack = [(-1, root)]
    for raw_line in content.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith('#'):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(' '))
        stripped = raw_line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f'Invalid indentation in config line: {raw_line!r}')
        current = stack[-1][1]
        if stripped.startswith('- '):
            if not isinstance(current, list):
                raise ValueError(f'List item found outside list context: {raw_line!r}')
            current.append(parse_scalar(stripped[2:].strip()))
            continue
        if ':' not in stripped:
            raise ValueError(f'Unsupported YAML line: {raw_line!r}')
        key, value = stripped.split(':', 1)
        key = key.strip()
        value = value.strip()
        if value == '':
            new_container = [] if next_significant_line_is_list_item(content, raw_line) else {}
            current[key] = new_container
            stack.append((indent, new_container))
        else:
            current[key] = parse_scalar(value)
    return root


def next_significant_line_is_list_item(content: str, current_line: str):
    seen_current = False
    for candidate in content.splitlines():
        if not seen_current:
            if candidate == current_line:
                seen_current = True
            continue
        stripped = candidate.strip()
        if not stripped or stripped.startswith('#'):
            continue
        return stripped.startswith('- ')
    return False


def parse_scalar(value: str):
    lowered = value.lower()
    if lowered == 'true':
        return True
    if lowered == 'false':
        return False
    if lowered in {'null', 'none'}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        if any(ch in value for ch in '.eE'):
            return float(value)
        return int(value)
    except ValueError:
        return value


def first_or_default(cli_value, config_value):
    return cli_value if cli_value is not None else config_value


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', default='configs/benchmark-default.yaml')
    p.add_argument('--python', default=sys.executable)
    p.add_argument('--script', default='benchmark/deepforest/benchmark_df_openml.py')
    p.add_argument('--repeats', type=int)
    p.add_argument('--warmup-runs', type=int)
    p.add_argument('--n-jobs', type=int)
    p.add_argument('--dataset-id', type=int)
    p.add_argument('--test-size', type=float)
    p.add_argument('--random-state', type=int)
    p.add_argument('--cache-dir')
    p.add_argument('--backend')
    p.add_argument('--out-dir')
    p.add_argument('--tag')
    args = p.parse_args()

    cfg = load_config(args.config)
    dataset_id = first_or_default(args.dataset_id, cfg['dataset']['openml_id'])
    test_size = first_or_default(args.test_size, cfg['split']['test_size'])
    random_state = first_or_default(args.random_state, cfg['split']['random_state'])
    n_jobs = first_or_default(args.n_jobs, cfg['model']['n_jobs'])
    backend = first_or_default(args.backend, cfg['model'].get('backend', 'custom'))
    cache_dir = first_or_default(args.cache_dir, cfg['dataset']['cache_dir'])
    repeats = first_or_default(args.repeats, cfg['run']['repeats'])
    warmup_runs = first_or_default(args.warmup_runs, cfg['run']['warmup_runs'])
    out_dir = Path(first_or_default(args.out_dir, cfg['run']['output_dir']))
    tag = first_or_default(args.tag, cfg['run']['tag'])

    out_dir.mkdir(parents=True, exist_ok=True)

    base_cmd = [
        args.python,
        args.script,
        '--dataset-id', str(dataset_id),
        '--test-size', str(test_size),
        '--random-state', str(random_state),
        '--n-jobs', str(n_jobs),
        '--backend', str(backend),
        '--cache-dir', str(cache_dir),
        '--tag', str(tag),
    ]

    run_manifest = {
        'config': str(args.config),
        'dataset_id': dataset_id,
        'test_size': test_size,
        'random_state': random_state,
        'n_jobs': n_jobs,
        'backend': backend,
        'cache_dir': str(cache_dir),
        'repeats': repeats,
        'warmup_runs': warmup_runs,
        'out_dir': str(out_dir),
        'tag': str(tag),
    }
    (out_dir / 'run_manifest.json').write_text(json.dumps(run_manifest, indent=2) + '\n', encoding='utf-8')

    for i in range(warmup_runs):
        print(f'Warmup {i+1}/{warmup_runs}...', file=sys.stderr)
        run_once(base_cmd)

    runs = []
    csv_path = out_dir / 'benchmark_runs.csv'
    for i in range(repeats):
        json_path = out_dir / f'run_{i+1:02d}.json'
        cmd = base_cmd + ['--json-out', str(json_path), '--csv-out', str(csv_path)]
        print(f'Measured run {i+1}/{repeats}...', file=sys.stderr)
        runs.append(run_once(cmd))

    fit_times = [r['fit_seconds'] for r in runs]
    predict_times = [r['predict_seconds'] for r in runs]
    total_times = [r['total_seconds'] for r in runs]
    accuracies = [r['accuracy_percent'] for r in runs]
    load_times = [r['load_seconds'] for r in runs]

    summary = {
        'runs': len(runs),
        'fit_seconds_mean': round(statistics.mean(fit_times), 6),
        'fit_seconds_median': round(statistics.median(fit_times), 6),
        'fit_seconds_stdev': round(statistics.stdev(fit_times), 6) if len(fit_times) > 1 else 0.0,
        'predict_seconds_mean': round(statistics.mean(predict_times), 6),
        'predict_seconds_median': round(statistics.median(predict_times), 6),
        'load_seconds_mean': round(statistics.mean(load_times), 6),
        'load_seconds_median': round(statistics.median(load_times), 6),
        'total_seconds_mean': round(statistics.mean(total_times), 6),
        'total_seconds_median': round(statistics.median(total_times), 6),
        'total_seconds_stdev': round(statistics.stdev(total_times), 6) if len(total_times) > 1 else 0.0,
        'accuracy_percent_mean': round(statistics.mean(accuracies), 6),
        'accuracy_percent_median': round(statistics.median(accuracies), 6),
        'tag': str(tag),
        'backend': str(backend),
        'n_jobs': n_jobs,
    }

    summary_path = out_dir / 'summary.json'
    summary_path.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
