#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_summary(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def pct_change(old, new):
    if old == 0:
        return None
    return (new - old) / old * 100.0


def safe_round(value):
    if value is None:
        return None
    return round(value, 6)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', required=True, help='Path to baseline summary.json')
    p.add_argument('--candidate', required=True, help='Path to candidate summary.json')
    args = p.parse_args()

    base = load_summary(args.baseline)
    cand = load_summary(args.candidate)

    metrics = [
        'fit_seconds_median',
        'fit_seconds_mean',
        'predict_seconds_median',
        'total_seconds_median',
        'accuracy_percent_median',
    ]

    report = {
        'baseline': str(Path(args.baseline).resolve()),
        'candidate': str(Path(args.candidate).resolve()),
        'comparisons': {},
    }

    for metric in metrics:
        b = base.get(metric)
        c = cand.get(metric)
        delta = None if b is None or c is None else (c - b)
        pct = None if b is None or c is None or b == 0 else pct_change(b, c)
        report['comparisons'][metric] = {
            'baseline': b,
            'candidate': c,
            'delta': safe_round(delta),
            'pct_change': safe_round(pct),
        }

    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
