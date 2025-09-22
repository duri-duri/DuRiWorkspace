-- 1) Bitemporal Canonical (Core)
create table if not exists memory_canonical_bt (
  key text,
  value jsonb not null,
  bundle_hash char(64) not null,
  version text not null,
  valid_from timestamptz not null,
  valid_to   timestamptz not null,
  tx_from    timestamptz not null default now(),
  tx_to      timestamptz not null default '9999-12-31',
  primary key (key, tx_from)
);
create index if not exists mc_bt_lookup on memory_canonical_bt(key, valid_from, valid_to);
create index if not exists mc_bt_asof on memory_canonical_bt(key, valid_from, valid_to, tx_from);

-- 2) Answer Capsule (append-only)
create table if not exists answer_ledger (
  qid text primary key,
  capsule jsonb not null,
  created_at timestamptz not null default now()
);

-- 3) Event Ledger (hash-chain; transparency)
create table if not exists audit_ledger (
  id bigserial primary key,
  kind text not null,            -- e.g., bundle_verified, canary_passed, core_conflict
  details jsonb not null,
  prev_hash char(64),
  this_hash char(64) not null,
  created_at timestamptz not null default now()
);
create index if not exists audit_kind_time on audit_ledger(kind, created_at desc);
