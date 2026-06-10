# DDR vs MRDIMM comparison methodology

## Goal

Compare memory-configuration impact on real application performance using DeepForest on the OpenML Covertype workload, supported by system-level measurements.

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
3. Run 1 warm-up iteration.
4. Run 5 measured iterations.
5. Compare median / mean / stddev across configurations.
6. Supplement with STREAM and Intel MLC results if available.

## Compare at least these metrics

- dataset load time
- fit time
- predict time
- total runtime
- accuracy
- per-layer timing from DeepForest logs
- system memory benchmark results (STREAM / MLC)

## Interpretation

If MRDIMM improves memory behavior, the strongest signal is usually reduced fit time and better consistency across repeated runs. Accuracy should remain effectively unchanged when the seed and data split are fixed.
