# Trace v2 Sweep Report — 2025-09-10T05:33:47.561946Z
- Baseline p95: **750.00 ms**, size: **100.0 KB**
- Target: overhead ≤ **5.0%**, error_rate ≤ **0.500%**, weight={'overhead': 0.6000000000000001, 'error': 0.30000000000000004, 'size': 0.10000000000000002}
- Total runs: **36**
## Best Config
- sampling_rate: **1.0**, serialization: **msgpack**, compression: **none**
- p95: **629.09 ms** (over 0.00%)
- error_rate: **0.1710%**, size: **94.8 KB**
- J(score): **0.000513**, feasible: **True**
## Top-5 by J
- 1.0, msgpack, none → p95=629.09ms, over=0.00%, err=0.171%, size=94.8KB, J=0.000513, feas=True
- 1.0, msgpack, gzip → p95=616.57ms, over=0.00%, err=0.171%, size=66.8KB, J=0.000513, feas=True
- 1.0, msgpack, zstd → p95=604.04ms, over=0.00%, err=0.171%, size=52.7KB, J=0.000513, feas=True
- 1.0, protobuf, none → p95=616.04ms, over=0.00%, err=0.171%, size=89.3KB, J=0.000513, feas=True
- 1.0, protobuf, gzip → p95=603.78ms, over=0.00%, err=0.171%, size=62.9KB, J=0.000513, feas=True