# deepforest-cwf

Benchmark kit for comparing DeepForest training performance on `yi-cwf`, especially for memory-configuration changes such as DDR -> MRDIMM.

## Goals

This repo is for reproducible performance comparison, not just smoke testing.

It aims to provide:
- application-level benchmarking with DeepForest on OpenML workloads
- repeatable timing for data load / fit / predict / end-to-end runtime
- structured result output in JSON and CSV
- system metadata capture for fair A/B comparison
- guidance for DDR vs MRDIMM experiments
- integration with serverinfo-based STREAM, Intel MLC, and PerfSpect tools

## Recommended datasets

For memory-performance comparison:
- primary: OpenML did `159` (`RandomRBF_50_1E-3`)
- secondary: OpenML did `1111` (`KDDCup09_appetency`)
- optional categorical complement: OpenML did `40668` (`connect-4`)

## Layout

```text
benchmark/
  deepforest/
    benchmark_df_openml.py      # precise timers + structured output
    repeat_runner.py            # multi-run driver and summary stats
    compare_runs.py             # baseline vs candidate result comparison
    analyze_scaling.py          # summarize n_jobs scaling sweeps
scripts/
  setup_env.sh
  collect_system_info.sh
  prepare_serverinfo_tools.sh   # unpack MLC / STREAM / PerfSpect from /mnt/nvme1p5t/serverinfo
  run_benchmark.sh
  run_scaling_sweep.sh          # sweep multiple n_jobs points and emit scaling summary
  run_stream.sh
  run_mlc.sh
  run_perfspect.sh
configs/
  benchmark-default.yaml
docs/
  methodology.md
results/
  .gitkeep
smoke/
  df_openml.py
```

## Quick start

```bash
./scripts/setup_env.sh
./scripts/prepare_serverinfo_tools.sh
./scripts/run_stream.sh results/ddr_baseline/stream.txt
./scripts/run_mlc.sh results/ddr_baseline/mlc.txt
TAG=ddr_baseline DF_N_JOBS=288 ./scripts/run_benchmark.sh

TAG=mrdimm_candidate DF_N_JOBS=288 ./scripts/run_benchmark.sh
python benchmark/deepforest/compare_runs.py \
  --baseline results/ddr_baseline/summary.json \
  --candidate results/mrdimm_candidate/summary.json

CORE_LIST=1,12,24,48,96,144,192,240,288 \
REPEATS=3 WARMUP_RUNS=1 SWEEP_NAME=ddr_scaling \
./scripts/run_scaling_sweep.sh
cat results/ddr_scaling/scaling_analysis.txt
```

## What the benchmark records

Per measured run, the benchmark captures:
- dataset load time
- split time
- fit time
- predict time
- total time
- accuracy
- Python / package versions
- git commit
- host / kernel / CPU summary

For multi-core scaling sweeps (`scripts/run_scaling_sweep.sh`), the repo also emits:
- one result directory per `n_jobs` point
- `scaling_analysis.json` with baseline-relative speedup / efficiency
- `scaling_analysis.txt` as a terminal-readable summary table

## Core-count scaling workflow

To study how `n_jobs` affects DeepForest on the same machine, run a scaling sweep instead of a single fixed-point benchmark.

Recommended sweep points on `yi-cwf`:
- single-socket sweep: `1,12,24,48,96,144,192,240,288`
- quick smoke: `1,48,96,192,288`

Example:

```bash
CORE_LIST=1,12,24,48,96,144,192,240,288 \
REPEATS=3 WARMUP_RUNS=1 SWEEP_NAME=ddr_scaling \
./scripts/run_scaling_sweep.sh
```

This creates:
- `results/ddr_scaling/n_jobs_<N>/summary.json` for each point
- `results/ddr_scaling/scaling_analysis.json`
- `results/ddr_scaling/scaling_analysis.txt`

The scaling analysis reports:
- `fit_speedup_vs_baseline`
- `fit_efficiency_vs_baseline`
- `total_speedup_vs_baseline`
- `total_efficiency_vs_baseline`

By default the lowest `n_jobs` point is used as the baseline. If you want a different reference point, set `BASELINE_N_JOBS=<N>`.

## Sources
- OpenML Covertype dataset lookup and dataset metadata via OpenML API: https://www.openml.org/
- deep-forest 0.1.7: https://pypi.org/project/deep-forest/0.1.7/
- NumPy 1.23.5: https://pypi.org/project/numpy/1.23.5/
- SciPy 1.13.1: https://pypi.org/project/scipy/1.13.1/
- scikit-learn 1.5.2: https://pypi.org/project/scikit-learn/1.5.2/
- OpenML Python API: https://pypi.org/project/openml/
