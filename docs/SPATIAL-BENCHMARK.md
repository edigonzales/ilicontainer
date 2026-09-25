# Spatial format-5 acceptance

The local acceptance dataset is under `benchmark-data/swisstopo-wkb/`, ignored by
Git. Preserve format-4 files plus the old `build/install/ibx` under
`baseline-format4/cli` and the old Python package under
`baseline-format4/ibx_browser` before updating. Create format-5 files separately
under `format5/` using identical source/model/compression/index settings.

Compile `scripts/SpatialBenchmark.java` against the baseline distribution into
`baseline-format4/`, then run `python3 scripts/benchmark-spatial.py`.
`IBX_BENCH_READERS`, `IBX_BENCH_VERSIONS`, and `IBX_BENCH_DATASET` select subsets.
`python3 scripts/report-spatial-benchmark.py benchmark-data/swisstopo-wkb/format5`
checks identical ordered result digests and reports median/p95 and metrics.

Each paired scenario has at least three warm-ups and ten measurements. Java repetitions can be increased through IBX_BENCH_WARMUPS and IBX_BENCH_RUNS. BBox half-widths
are 20 m, 1 km and 10 km at the same Swiss coordinate. Address/locality indexes
are exercised; streets have no spatial index and serve as an object-ID control.
Both readers also resolve a known object ID in every dataset.

Spatial timings isolate candidate selection and compare complete ordered
basket/chunk/ordinal digests. Java object-chunk prefetch is disabled for this
measurement; Python calls its spatial candidate API directly. Object-ID controls
include object decoding. Earlier end-to-end runs are retained separately under
`format5/end-to-end/`; those must not be combined with index-only timings.
Full semantic transfer verification is a separate full-file test.

Cold means cleared reader caches, not a cold OS cache. Python clears frame,
unpacked-chunk and record-position caches. HTTP is a loopback Range server with
strong ETags and no simulated WAN latency. Additional coalescing gap bytes are
reported explicitly. Do not interpret tiny sub-millisecond control differences
as a meaningful performance claim without paired repetitions. Investigate
repeatable regressions above 10 percent before publishing.
