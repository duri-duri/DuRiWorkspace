#!/usr/bin/env python3
# tools/rebind_state_paths.py
import argparse, json, os, sys, hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple

def sha256_file(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def try_rebase(old_path: Path, new_root: Path) -> Path:
    # 가장 보편적인 규칙: 기존 절대경로의 마지막 2~4개 꼬리를 보존해 새 루트에 붙인다.
    parts = old_path.parts
    for tail_len in range(min(4, len(parts)), 1, -1):
        candidate = new_root.joinpath(*parts[-tail_len:])
        if candidate.exists():
            return candidate
    # 없으면 동일 상대경로를 그대로 붙여본다.
    return new_root.joinpath(*parts[1:]) if old_path.is_absolute() else new_root.joinpath(old_path)

def search_in_backup(backup_root: Path, ref: str) -> Path:
    """
    ref 예: "2025/08/14/FULL__...tar.zst:var/checkpoints/best.ckpt"
    여기서는 '압축 내부 경로'를 실제 추출 없이 백업 루트에 '평면 보관된 경우'도 대응하도록,
    우선적으로 backup_root/date/subpath 를 재구성해 검사한다.
    """
    if ":" in ref:
        date_path, inner = ref.split(":", 1)
        # 실제 압축 내부를 바로 읽진 않는다(백업은 read-only). 추출 정책은 별도.
        # 단, 이미 '동일 경로로 풀린 경우'에 대비해 존재 검사만 수행.
        candidate = backup_root.joinpath(date_path, inner)
        if candidate.exists():
            return candidate
    # ref가 단순 상대경로인 경우
    candidate = backup_root.joinpath(ref)
    return candidate if candidate.exists() else Path("")

def rebind(paths: List[Dict[str, Any]],
           new_root: Path,
           backup_root: Path,
           verify_hash: bool,
           dry_run: bool) -> Tuple[int, int]:
    changed = 0
    verified = 0
    for art in paths:
        old = Path(art.get("local_path") or "")
        refs = art.get("backup_refs", [])
        size = int(art.get("size_bytes", -1))
        want_sha = (art.get("sha256") or "").lower()

        new_path = None
        # 1) 우선 new_root로 rebasing 시도
        if old:
            candidate = try_rebase(old, new_root)
            if candidate.exists() and (size <= 0 or candidate.stat().st_size == size):
                new_path = candidate

        # 2) 실패하면 backup_refs 기반으로 백업 루트 탐색
        if not new_path and refs:
            for r in refs:
                candidate = search_in_backup(backup_root, r)
                if candidate and candidate.exists() and (size <= 0 or candidate.stat().st_size == size):
                    new_path = candidate
                    break

        # 3) 마지막으로 new_root 아래 전역 탐색(비권장: 비용↑) - 필요 시 주석 해제
        # if not new_path:
        #     for p in new_root.rglob(old.name if old.name else "*"):
        #         if p.is_file() and (size <= 0 or p.stat().st_size == size):
        #             new_path = p
        #             break

        if new_path:
            if verify_hash and want_sha:
                try:
                    got = sha256_file(new_path)
                    if got.lower() != want_sha:
                        print(f"[WARN] sha256 mismatch for {art.get('logical_name')}: {new_path}", file=sys.stderr)
                    else:
                        verified += 1
                except Exception as e:
                    print(f"[WARN] sha256 error {new_path}: {e}", file=sys.stderr)
            # 적용
            if str(new_path) != art.get("local_path"):
                art["local_path"] = str(new_path)
                changed += 1
        else:
            # 못 찾은 경우 빈 문자열로 표시(명시적 결손)
            art["local_path"] = ""

    return changed, verified

def main():
    ap = argparse.ArgumentParser(description="DuRi state.json 경로 재바인딩 도구")
    ap.add_argument("--state", required=True, help="state.json 경로")
    ap.add_argument("--new-root", required=True, help="새 로컬 루트 (예: /home/duri/DuRiWorkspace)")
    ap.add_argument("--backup-root", required=True, help="백업 루트 (예: /mnt/c/Users/admin/Desktop/두리백업)")
    ap.add_argument("--write", action="store_true", help="실제 파일 갱신(write). 없으면 dry-run")
    ap.add_argument("--verify-sha256", action="store_true", help="찾은 파일 sha256 검증")
    args = ap.parse_args()

    state_path = Path(args.state)
    if not state_path.exists():
        print(f"state.json not found: {state_path}", file=sys.stderr)
        sys.exit(2)

    data = json.loads(state_path.read_text(encoding="utf-8"))
    artifacts = data.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        print("artifacts 비어있음", file=sys.stderr)
        sys.exit(3)

    changed, verified = rebind(
        artifacts,
        new_root=Path(args.new_root),
        backup_root=Path(args.backup_root),
        verify_hash=args.verify_sha256,
        dry_run=(not args.write)
    )

    # dry-run이면 화면에 통계만
    if not args.write:
        print(f"[DRY-RUN] would change {changed} artifacts; verified={verified}")
        # 미리보기 출력(최대 5개)
        for a in artifacts[:5]:
            print(f"- {a.get('logical_name')}: {a.get('local_path')}")
        sys.exit(0)

    # write 모드: 파일 갱신
    state_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[WRITE] updated {state_path} (changed={changed}, verified={verified})")

if __name__ == "__main__":
    main()
