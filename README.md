# deepforest-cwf

Benchmark kit for comparing DeepForest training performance on `yi-cwf`, especially for memory-configuration changes such as DDR -> MRDIMM.

## Goals

This repo is for reproducible performance comparison, not just smoke testing.

It aims to provide:
- application-level benchmarking with DeepForest on the OpenML Covertype workload
- repeatable timing for data load / fit / predict / end-to-end runtime
- structured result output in JSON and CSV
- system metadata capture for fair A/B comparison
- guidance for DDR vs MRDIMM experiments
- optional wrappers for system-level benchmarks such as STREAM and Intel MLC

## Planned layout

```text
benchmark/
  deepforest/
    benchmark_df_openml.py      # precise timers + structured output
    repeat_runner.py            # multi-run driver and summary stats
    metrics.py                  # timing/stat helpers
scripts/
  setup_env.sh                  # create venv and install pinned deps
  collect_system_info.sh        # lscpu, numa, mem, versions, kernel
  run_benchmark.sh              # convenient end-to-end runner
  run_stream.sh                 # optional STREAM wrapper
  run_mlc.sh                    # optional Intel MLC wrapper
configs/
  benchmark-default.yaml        # default benchmark parameters
results/
  .gitkeep
smoke/
  df_openml.py                  # simple smoke version migrated from earlier work
docs/
  methodology.md                # how to compare DDR vs MRDIMM fairly
```

## Benchmark principles

To compare memory configurations fairly, keep these fixed across runs:
- CPU model and socket topology
- BIOS settings relevant to power, turbo, NUMA, SNC, and C-states
- kernel / OS / Python / package versions
- dataset and train/test split
- benchmark parameters such as `n_jobs`
- thermal and background workload conditions

Recommended experiment shape:
- 1 warm-up run
- 5 measured runs per configuration
- compare median / mean / stddev
- report both app-level timings and system-level memory measurements

## Initial scope

The first deliverable will include:
- repaired `df_openml.py` smoke test
- benchmark-oriented DeepForest runner with split timers
- repeat runner with summary statistics
- environment setup script with pinned versions
- methodology note for DDR vs MRDIMM comparison

## Sources

- OpenML Covertype dataset id 159: https://www.openml.org/search?type=data&id=159
- deep-forest 0.1.7: https://pypi.org/project/deep-forest/0.1.7/
- NumPy 1.23.5: https://pypi.org/project/numpy/1.23.5/
- SciPy 1.13.1: https://pypi.org/project/scipy/1.13.1/
- scikit-learn 1.5.2: https://pypi.org/project/scikit-learn/1.5.2/
- OpenML Python API: https://pypi.org/project/openml/
