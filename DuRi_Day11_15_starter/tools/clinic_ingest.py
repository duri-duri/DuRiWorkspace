#!/usr/bin/env python3
from datetime import datetime
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "clinic" / "source_materials"
DER = ROOT / "clinic" / "_derived"
DER.mkdir(parents=True, exist_ok=True)

# 아주 보수적인 마스킹(기본형)
PATTERNS = {
    "phone": re.compile(r"(\+?\d[\d\-\s]{9,}\d)"),
    "rrn": re.compile(r"(\d{6}\-\d{7})"),  # 주민등록번호 형태
    "email": re.compile(r"([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})"),
    "addr": re.compile(r"(도로명|지번|호수|아파트|동\b.*?\d+호)"),
}


def mask(s):
    for k, p in PATTERNS.items():
        s = p.sub(f"__{k.upper()}__", s)
    return s


def read_text(p: pathlib.Path) -> str:
    if p.suffix.lower() in {".md", ".txt"}:
        return p.read_text(encoding="utf-8", errors="ignore")
    # pdf/docx는 지금은 스킵(메타만); 필요시 전용 추출기 추가
    return ""


index = []
redactions = []
for p in SRC.rglob("*"):
    if not p.is_file():
        continue
    rel = str(p.relative_to(SRC))
    raw = read_text(p)
    masked = mask(raw) if raw else ""
    h = hashlib.sha1((rel + str(len(raw))).encode()).hexdigest()
    out = DER / f"{h}.txt"
    if raw:
        out.write_text(masked, encoding="utf-8")
    index.append(
        {"path": rel, "size": p.stat().st_size, "hash": h, "extracted": bool(raw)}
    )
    if raw and masked != raw:
        redactions.append({"path": rel, "diff": "masked"})

report = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "files": index,
    "redactions": redactions,
}
(ROOT / "clinic" / "ingest_index.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(
    "[OK] ingest -> clinic/ingest_index.json; derived texts:",
    len([x for x in index if x["extracted"]]),
)
