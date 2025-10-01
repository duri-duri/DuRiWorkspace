package duri.guard
default allow = false

pii_fields := input.core.pii_fields
violates_privacy {
  input.mode == "external"
  some f
  f := pii_fields[_]
  input.output[f] != null
}

conflicts_core {
  some k
  input.core.values[k] != null
  input.output[k] != null
  input.output[k] != input.core.values[k]
}

allow { not violates_privacy; not conflicts_core }
