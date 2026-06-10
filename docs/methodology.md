# DDR vs MRDIMM comparison methodology

## Goal

Compare memory-configuration impact on real application performance using DeepForest on the OpenML workload, supported by system-level measurements from STREAM, Intel MLC, and optionally PerfSpect.

## Dataset recommendation

Recommended application-level benchmark sets:
- primary: OpenML did `159` (`RandomRBF_50_1E-3`) for long, repeatable runs
- secondary: OpenML did `1111` (`KDDCup09_appetency`) for a higher-dimensional workload
- optional categorical complement: OpenML did `40668` (`connect-4`)

## Keep fixed

- same host and CPU
- same BIOS settings except the memory configuration under test
- same OS / kernel / Python / package versions
- same dataset and random seed
- same `n_jobs`
- same thermal and background-load conditions

## Recommended protocol

1. Reboot into the target memory configuration.
2. Record system information with `scripts/collect_system_info.sh`.
3. Run STREAM and Intel MLC from the serverinfo tool bundle.
4. Run 1 warm-up DeepForest iteration.
5. Run 5 measured DeepForest iterations.
6. Compare median / mean / stddev across configurations.
7. Optionally add a PerfSpect report for platform-level context.

## Example commands

```bash
./scripts/setup_env.sh
./scripts/prepare_serverinfo_tools.sh
./scripts/run_stream.sh results/ddr_baseline/stream.txt
./scripts/run_mlc.sh results/ddr_baseline/mlc.txt
TAG=ddr_baseline DF_N_JOBS=288 ./scripts/run_benchmark.sh

./scripts/run_stream.sh results/mrdimm_candidate/stream.txt
./scripts/run_mlc.sh results/mrdimm_candidate/mlc.txt
TAG=mrdimm_candidate DF_N_JOBS=288 ./scripts/run_benchmark.sh

python benchmark/deepforest/compare_runs.py \
  --baseline results/ddr_baseline/summary.json \
  --candidate results/mrdimm_candidate/summary.json
```

## Compare at least these metrics

System level:
- STREAM bandwidth
- Intel MLC latency / bandwidth output
- optional PerfSpect report

Application level:
- dataset load time
- fit time
- predict time
- total runtime
- accuracy
- per-layer timing from DeepForest logs

## Interpretation

If MRDIMM improves memory behavior, the strongest signal is usually reduced fit time and better consistency across repeated runs. STREAM and MLC should help explain whether any improvement comes from higher bandwidth, lower latency, or NUMA behavior changes.
