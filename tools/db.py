# tools/db.py
import os, json, hashlib, datetime, psycopg2
from psycopg2.extras import RealDictCursor

PG_EPOCH_FAR = "9999-12-31"

def get_conn():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        host = os.environ.get("PGHOST","localhost")
        port = os.environ.get("PGPORT","5432")
        user = os.environ.get("PGUSER","postgres")
        pwd  = os.environ.get("PGPASSWORD","postgres")
        db   = os.environ.get("PGDATABASE","postgres")
        dsn  = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    return psycopg2.connect(dsn)

def _now_utc():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

def upsert_canonical_bt(cur, key:str, value, bundle_hash:str, version:str,
                        valid_from=None, valid_to=PG_EPOCH_FAR):
    """
    - 이전 open txn(row)의 tx_to를 now()로 닫고
    - 새 row insert (bitemporal: valid_*는 호출자가 결정)
    """
    if valid_from is None:
        valid_from = _now_utc()
    # close previous tx
    cur.execute(
        """
        update memory_canonical_bt
           set tx_to = now()
         where key = %s
           and tx_to = %s
        """,
        (key, PG_EPOCH_FAR)
    )
    # insert new record
    cur.execute(
        """
        insert into memory_canonical_bt
          (key, value, bundle_hash, version, valid_from, valid_to)
        values
          (%s, %s::jsonb, %s, %s, %s, %s)
        """,
        (key, json.dumps(value), bundle_hash, version, valid_from, valid_to)
    )

def insert_answer_capsule(cur, capsule:dict):
    cur.execute(
        """
        insert into answer_ledger (qid, capsule)
        values (%s, %s::jsonb)
        on conflict (qid) do nothing
        """,
        (capsule["qid"], json.dumps(capsule))
    )

def _hash(s:str)->str:
    return hashlib.sha256(s.encode()).hexdigest()

def append_audit(cur, kind:str, details:dict, prev_hash:str|None=None):
    if prev_hash is None:
        cur.execute("select this_hash from audit_ledger order by id desc limit 1")
        row = cur.fetchone()
        prev_hash = row[0] if row else None
    payload = json.dumps(details, separators=(",",":"), ensure_ascii=False)
    base = (prev_hash or "") + payload + _now_utc().isoformat()
    this_hash = _hash(base)
    cur.execute(
        """
        insert into audit_ledger (kind, details, prev_hash, this_hash)
        values (%s, %s::jsonb, %s, %s)
        returning id
        """,
        (kind, payload, prev_hash, this_hash)
    )
    result = cur.fetchone()
    return result['id'] if result else None, this_hash

def with_tx(fn, *args, **kwargs):
    """
    conn 자동 열고 commit/rollback까지 처리하는 헬퍼.
    사용: with_tx(lambda cur: ..., args)
    """
    conn = get_conn()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                return fn(cur, *args, **kwargs)
    finally:
        conn.close()
