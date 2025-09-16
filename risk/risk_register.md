| Risk | Scenario | Mitigation | Owner | SLO |
|------|----------|------------|-------|-----|
| Prompt injection | Untrusted input hijacks tools | sanitizer + allow/deny list | AI | 0.1% |
| Data leakage | Sensitive context exfiltration | redaction + privacy mode | AI | 0% |
| Cost runaway | Looping/tool spam | budget gate + kill-switch | AI | hard cap |
| Rollback failure | Bad deploy persists | snapshot + auto-rollback | Ops | <5m |
| Eval drift | Bench not predictive | frozen suite + weekly refresh | R&D | weekly |
| Backup staleness | incr/full 지연 | schedule guard + verify | Ops | incr≤48h, full≤168h |
| Tool outage | 외부 의존 중단 | graceful degrade + retry(1) | Ops | MTTR<30m |
