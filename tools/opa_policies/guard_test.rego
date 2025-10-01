package duri.guard_test
import data.duri.guard

test_privacy_block {
  input := {
    "mode": "external",
    "core": {"pii_fields": ["name_priv"], "values": {}},
    "output": {"name_priv": "secret"}
  }
  not guard.allow with input as input
}

test_core_conflict_block {
  input := {
    "mode": "external",
    "core": {"pii_fields": [], "values": {"role": "mother"}},
    "output": {"role": "aunt"}
  }
  not guard.allow with input as input
}

test_allow_pub_ok {
  input := {
    "mode": "external",
    "core": {"pii_fields": ["name_priv"], "values": {"role": "mother"}},
    "output": {"role": "mother"}
  }
  guard.allow with input as input
}
