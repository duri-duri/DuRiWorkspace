# Trace v2 Sweep Report — 2025-09-10T05:41:01.110989Z
- Baseline p95: **750.00 ms**, size: **100.0 KB**
- Target: overhead ≤ **5.0%**, error_rate ≤ **0.500%**, weight={'overhead': 0.6000000000000001, 'error': 0.30000000000000004, 'size': 0.10000000000000002}
- Total runs: **36**
## Best Config
- sampling_rate: **1.0**, serialization: **msgpack**, compression: **none**
- p95: **626.61 ms** (over 0.00%)
- error_rate: **0.1550%**, size: **94.5 KB**
- J(score): **0.000465**, feasible: **True**
## Top-5 by J
- 1.0, msgpack, none → p95=626.61ms, over=0.00%, err=0.155%, size=94.5KB, J=0.000465, feas=True
- 1.0, msgpack, gzip → p95=614.09ms, over=0.00%, err=0.155%, size=66.4KB, J=0.000465, feas=True
- 1.0, msgpack, zstd → p95=601.56ms, over=0.00%, err=0.155%, size=52.4KB, J=0.000465, feas=True
- 1.0, protobuf, none → p95=613.56ms, over=0.00%, err=0.155%, size=89.0KB, J=0.000465, feas=True
- 1.0, protobuf, gzip → p95=601.30ms, over=0.00%, err=0.155%, size=62.6KB, J=0.000465, feas=True
