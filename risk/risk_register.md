| Risk | Scenario | Mitigation | Owner | SLO |
|------|----------|------------|-------|-----|
| Prompt injection | Untrusted input hijacks tools | sanitizer + allow/deny list | AI | 0.1% |
| Data leakage | Sensitive context exfiltration | redaction + privacy mode | AI | 0% |
| Cost runaway | Looping / tool spam | budget gate + kill-switch | AI | hard cap |
| Rollback failure | Bad deploy persists | pre-deploy snapshot + auto-rollback | Ops | <5m |
| Eval drift | Bench not predictive | frozen suite + monthly refresh | R&D | monthly |
