#!/usr/bin/env bash
# Lyapunov Tuning Rules
# Purpose: Document tuning rules for Lyapunov control function
# Usage: Reference document for manual tuning

# Initial Values (Recommended)
# α = 2.0 (GREEN uptime weight)
# β = 1.0 (Alert rate weight)
# γ = 0.5 (MTTR weight)
# δ = 1.5 (DR success weight)
# ε = 0.8 (EV/h target weight)

# Tuning Rules

# Rule 1: Increase alert/budget sensitivity if V increasing
# If ΔV > 0 for ≥3 times in 72h window:
#   β += 0.05  (increase alert sensitivity)
#   δ += 0.05  (increase DR sensitivity)

# Rule 2: Decrease MTTR sensitivity if MTTR alerts too sensitive
# If MTTR false positives > 10%:
#   γ -= 0.1   (reduce MTTR weight)

# Rule 3: Promotion signal
# If all conditions met for 2 hours:
#   rate(lyapunov_V[30m]) < 0  (V decreasing)
#   canary_failure_ratio < 0.08
#   canary_unique_ratio ≥ 0.92
# Then: Enable canary promotion

# Rule 4: Auto-correction trigger
# If ΔV > 0 for 2 consecutive checks (10 minutes):
#   - Throttle merge queue (reduce merge rate by 50%)
#   - Increase self-heal retry rate
#   - Strengthen canary requirements

# Rule 5: Stability signal
# If duri_lyapunov_v < v_threshold for 30 minutes:
#   - Increase canary intensity
#   - Reduce experiment throttling

# Manual Tuning Script
# To adjust constants:
# 1. Edit prometheus/rules/slo_constants.rules.yml
# 2. Reload Prometheus: curl -X POST http://localhost:9090/-/reload
# 3. Monitor duri_lyapunov_v for 24 hours
# 4. Adjust if needed

