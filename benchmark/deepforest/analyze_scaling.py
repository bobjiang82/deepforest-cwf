#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


DEFAULT_COLUMNS = [
    "n_jobs",
    "fit_seconds_median",
    "total_seconds_median",
    "accuracy_percent_median",
    "fit_speedup_vs_baseline",
    "fit_efficiency_vs_baseline",
    "total_speedup_vs_baseline",
    "total_efficiency_vs_baseline",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--json-out", default="")
    parser.add_argument("--table-out", default="")
    parser.add_argument("--baseline-n-jobs", type=int)
    return parser.parse_args()


def load_summary(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_points(input_dir: Path):
    points = []
    for summary_path in sorted(input_dir.glob("n_jobs_*/summary.json")):
        summary = load_summary(summary_path)
        n_jobs = int(summary["n_jobs"])
        points.append(
            {
                "n_jobs": n_jobs,
                "fit_seconds_median": float(summary["fit_seconds_median"]),
                "total_seconds_median": float(summary["total_seconds_median"]),
                "accuracy_percent_median": float(summary["accuracy_percent_median"]),
                "summary_path": str(summary_path.resolve()),
            }
        )
    if not points:
        raise SystemExit(f"No summary.json files found under {input_dir}")
    points.sort(key=lambda row: row["n_jobs"])
    return points


def pick_baseline(points, baseline_n_jobs=None):
    if baseline_n_jobs is None:
        return points[0]
    for point in points:
        if point["n_jobs"] == baseline_n_jobs:
            return point
    raise SystemExit(f"Requested baseline n_jobs={baseline_n_jobs} not found")


def round6(value):
    return round(float(value), 6)


def enrich_points(points, baseline):
    baseline_fit = baseline["fit_seconds_median"]
    baseline_total = baseline["total_seconds_median"]
    baseline_n_jobs = baseline["n_jobs"]
    enriched = []
    for point in points:
        fit_speedup = baseline_fit / point["fit_seconds_median"]
        total_speedup = baseline_total / point["total_seconds_median"]
        jobs_ratio = point["n_jobs"] / baseline_n_jobs
        enriched.append(
            {
                **point,
                "fit_speedup_vs_baseline": round6(fit_speedup),
                "fit_efficiency_vs_baseline": round6(fit_speedup / jobs_ratio),
                "total_speedup_vs_baseline": round6(total_speedup),
                "total_efficiency_vs_baseline": round6(total_speedup / jobs_ratio),
            }
        )
    return enriched


def build_table(points):
    rows = []
    widths = {}
    for column in DEFAULT_COLUMNS:
        values = [format_value(row[column]) for row in points]
        widths[column] = max(len(column), *(len(value) for value in values))
    header = " | ".join(column.ljust(widths[column]) for column in DEFAULT_COLUMNS)
    divider = "-+-".join("-" * widths[column] for column in DEFAULT_COLUMNS)
    rows.extend([header, divider])
    for row in points:
        rows.append(" | ".join(format_value(row[column]).ljust(widths[column]) for column in DEFAULT_COLUMNS))
    return "\n".join(rows) + "\n"


def format_value(value):
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def build_analysis(points, baseline):
    best_fit = min(points, key=lambda row: row["fit_seconds_median"])
    best_total = min(points, key=lambda row: row["total_seconds_median"])
    return {
        "baseline_n_jobs": baseline["n_jobs"],
        "best_fit_median": {
            "n_jobs": best_fit["n_jobs"],
            "fit_seconds_median": best_fit["fit_seconds_median"],
        },
        "best_total_median": {
            "n_jobs": best_total["n_jobs"],
            "total_seconds_median": best_total["total_seconds_median"],
        },
        "points": points,
    }


def main():
    args = parse_args()
    input_dir = Path(args.input_dir).resolve()
    points = discover_points(input_dir)
    baseline = pick_baseline(points, baseline_n_jobs=args.baseline_n_jobs)
    enriched = enrich_points(points, baseline)
    analysis = build_analysis(enriched, baseline)
    output = json.dumps(analysis, indent=2)
    print(output)

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")

    if args.table_out:
        out_path = Path(args.table_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(build_table(enriched), encoding="utf-8")


if __name__ == "__main__":
    main()
