#!/usr/bin/env python3
import argparse, json, os, sys, hashlib, subprocess, datetime
from pathlib import Path
from typing import Dict, Any, List

DEFAULT_GLOBS = [
    "models/**/*",
    "artifacts/**/*",
    "var/checkpoints/**/*",
    "var/metadata/**/*"
]

def sha256_file(p: Path, chunk: int = 1<<20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def utcnow_iso():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()

def relpath_from_root(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)

def ensure_dirs(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def load_state(p: Path) -> Dict[str, Any]:
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    # minimal skeleton
    return {
        "schema_version": "1.1",
        "run_id": "",
        "timestamp": utcnow_iso(),
        "git": {"commit":"", "branch":"", "repo_remote":""},
        "host": {"hostname": os.uname().nodename, "os": os.uname().sysname},
        "phase": {"name":"unknown", "step": 0},
        "params": {},
        "metrics": {},
        "artifacts": [],
        "backup": {},
        "notes": ""
    }

def git_info(repo: Path) -> Dict[str,str]:
    def sh(cmd): return subprocess.check_output(cmd, shell=True, cwd=repo).decode().strip()
    commit = sh("git rev-parse HEAD")
    branch = sh("git rev-parse --abbrev-ref HEAD")
    remote = ""
    try: remote = sh("git remote get-url origin")
    except: pass
    return {"commit":commit, "branch":branch, "repo_remote":remote}

def upsert_artifact(arts: List[Dict[str,Any]], new: Dict[str,Any]) -> None:
    # key by (logical_name, sha256) to avoid duplicates across backups
    for a in arts:
        if a.get("logical_name")==new["logical_name"] and a.get("sha256")==new["sha256"]:
            # merge backup_refs/local_path if missing
            if new.get("local_path"): a["local_path"] = new["local_path"]
            exist_refs = set(a.get("backup_refs") or [])
            for r in new.get("backup_refs",[]):
                if r not in exist_refs:
                    exist_refs.add(r)
            a["backup_refs"] = sorted(list(exist_refs))
            return
    arts.append(new)

def main():
    ap = argparse.ArgumentParser(description="Generate/Update state.json and backup_refs")
    ap.add_argument("--workspace-root", required=True)
    ap.add_argument("--state", required=True, help="learning_journal/state.json")
    ap.add_argument("--backup-root", required=True, help=".../두리백업")
    ap.add_argument("--backup-archive", required=True, help="새로 생성한 *.tar.zst (FULL/EXTENDED/CORE)")
    ap.add_argument("--scan-glob", action="append", help="추가 스캔 글롭", default=[])
    ap.add_argument("--logical-prefix", default="", help="logical_name 접두사 (예: run_2025-08-14_)")
    args = ap.parse_args()

    root = Path(args.workspace_root).resolve()
    state_path = Path(args.state)
    backup_root = Path(args.backup_root)
    archive = Path(args.backup_archive)
    scan_globs = (args.scan_glob or []) + DEFAULT_GLOBS

    data = load_state(state_path)
    data["schema_version"] = "1.1"
    data["timestamp"] = utcnow_iso()
    # git 정보 갱신
    try:
        data["git"] = git_info(root)
    except Exception as e:
        print(f"[WARN] git info: {e}", file=sys.stderr)

    # backup info 갱신
    # 추정: archive 경로 = {backup_root}/{YYYY}/{MM}/{DD}/{NAME.tar.zst}
    try:
        relative = archive.relative_to(backup_root)
        date_bucket = "/".join(relative.parts[:3])
        data["backup"] = {
            "primary_root": str(backup_root),
            "date_bucket": date_bucket,
            "bundle_name": relative.name
        }
        archive_ref_prefix = f"{date_bucket}/{relative.name}:"
    except Exception as e:
        print(f"[WARN] backup ref compose: {e}", file=sys.stderr)
        archive_ref_prefix = f"{archive.name}:"

    artifacts = data.get("artifacts") or []

    # 파일 스캔
    seen = 0
    for pattern in scan_globs:
        for p in root.glob(pattern):
            if not p.is_file():
                continue
            # 소형 텍스트/캐시 제외 규칙 일부
            if any(part in p.parts for part in [".git", "__pycache__", ".pytest_cache", "logs", "temp_"]):
                continue
            size = p.stat().st_size
            if size <= 0:
                continue
            sha = sha256_file(p)
            rel = relpath_from_root(p, root)
            logical = f"{args.logical_prefix}{Path(rel).name}"
            typ = "checkpoint" if "checkpoints" in rel else (
                  "model" if "models" in rel else (
                  "log" if rel.endswith(".log") else "dataset" if "dataset" in rel else "cache"))
            new = {
                "logical_name": logical,
                "type": typ,
                "created_at": utcnow_iso(),
                "size_bytes": size,
                "sha256": sha,
                "local_path": str(p),
                "backup_refs": [archive_ref_prefix + rel.replace("\\","/")],
                "tags": [],
                "notes": "",
                "source_host": os.uname().nodename,
                "storage_class": "hot"
            }
            upsert_artifact(artifacts, new)
            seen += 1

    data["artifacts"] = artifacts

    ensure_dirs(state_path)
    state_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] state updated: {state_path} (scan_added_or_merged={seen})")
    # 선택: 스키마 검증(로컬에 jsonschema 있으면)
    try:
        import jsonschema  # type: ignore
        schema = json.loads(Path("schemas/state.schema.json").read_text(encoding="utf-8"))
        jsonschema.validate(instance=data, schema=schema)
        print("[OK] schema validated")
    except Exception as e:
        print(f"[INFO] schema validation skipped or warn: {e}")

if __name__ == "__main__":
    main()
