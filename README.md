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
scripts/
  setup_env.sh
  collect_system_info.sh
  prepare_serverinfo_tools.sh   # unpack MLC / STREAM / PerfSpect from /mnt/nvme1p5t/serverinfo
  run_benchmark.sh
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

## Sources

- OpenML Covertype dataset lookup and dataset metadata via OpenML API: https://www.openml.org/
- deep-forest 0.1.7: https://pypi.org/project/deep-forest/0.1.7/
- NumPy 1.23.5: https://pypi.org/project/numpy/1.23.5/
- SciPy 1.13.1: https://pypi.org/project/scipy/1.13.1/
- scikit-learn 1.5.2: https://pypi.org/project/scikit-learn/1.5.2/
- OpenML Python API: https://pypi.org/project/openml/
