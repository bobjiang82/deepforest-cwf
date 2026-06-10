#!/usr/bin/env python3
import argparse
import csv
import json
import os
import platform
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import openml
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from deepforest import CascadeForestClassifier


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat()


def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def append_csv(path: Path, row: dict):
    ensure_parent(path)
    write_header = not path.exists()
    with path.open('a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-id', type=int, default=159)
    parser.add_argument('--test-size', type=float, default=0.2)
    parser.add_argument('--random-state', type=int, default=42)
    parser.add_argument('--n-jobs', type=int, default=os.cpu_count() or 1)
    parser.add_argument('--cache-dir', default='./data/openml_cache')
    parser.add_argument('--json-out', default='')
    parser.add_argument('--csv-out', default='')
    parser.add_argument('--tag', default='')
    args = parser.parse_args()

    effective_n_jobs = min(args.n_jobs, os.cpu_count() or args.n_jobs)
    cache_dir = Path(args.cache_dir).resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('OPENML_CACHE_DIR', str(cache_dir))

    t0 = time.perf_counter()
    dataset = openml.datasets.get_dataset(args.dataset_id, download_data=True)
    X, y, categorical_indicator, attribute_names = dataset.get_data(
        target=dataset.default_target_attribute
    )
    t1 = time.perf_counter()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )
    t2 = time.perf_counter()

    model = CascadeForestClassifier(
        n_jobs=effective_n_jobs,
        random_state=args.random_state,
    )

    fit_start = time.perf_counter()
    model.fit(X_train, y_train)
    fit_end = time.perf_counter()

    pred_start = time.perf_counter()
    y_pred = model.predict(X_test)
    pred_end = time.perf_counter()

    acc = accuracy_score(y_test, y_pred) * 100.0
    total_end = time.perf_counter()

    result = {
        'timestamp': now_iso(),
        'host': socket.gethostname(),
        'platform': platform.platform(),
        'python_version': sys.version.split()[0],
        'dataset_id': args.dataset_id,
        'dataset_name': getattr(dataset, 'name', 'unknown'),
        'samples': int(X.shape[0]),
        'features': int(X.shape[1]),
        'train_samples': int(X_train.shape[0]),
        'test_samples': int(X_test.shape[0]),
        'test_size': args.test_size,
        'random_state': args.random_state,
        'requested_n_jobs': args.n_jobs,
        'effective_n_jobs': effective_n_jobs,
        'cache_dir': str(cache_dir),
        'tag': args.tag,
        'load_seconds': round(t1 - t0, 6),
        'split_seconds': round(t2 - t1, 6),
        'fit_seconds': round(fit_end - fit_start, 6),
        'predict_seconds': round(pred_end - pred_start, 6),
        'total_seconds': round(total_end - t0, 6),
        'accuracy_percent': round(acc, 6),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.json_out:
        out = Path(args.json_out)
        ensure_parent(out)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    if args.csv_out:
        append_csv(Path(args.csv_out), result)


if __name__ == '__main__':
    main()
