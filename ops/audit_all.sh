#!/usr/bin/env bash
set -euo pipefail

# 전체 코드 건강검진 루틴 (1~2시간컷)
# 각 노드(duri_core / evolution / brain / control) + 백업/HDD + GitHub를 한 번에 스캔

echo "=== 🔍 전체 코드 건강검진 시작 ==="
echo "실행 시간: $(date)"
echo ""

# A. 전 레포 인벤토리 + git 상태
echo "📋 A. 전 레포 인벤토리 + git 상태"
find . -maxdepth 3 -type d -name ".git" -printf '%h\n' | while read repo; do
  echo "=== $repo ==="
  (cd "$repo" && git remote -v | head -1 && git rev-parse --abbrev-ref HEAD \
   && git status -s && git log -1 --pretty=format:'%ad %h %s' --date=iso)
  echo
done > _audit_git_status.txt
echo "✅ Git 상태 저장: _audit_git_status.txt"

# B. 비밀/키 유출 스캔(빠른 버전)
echo "🔐 B. 비밀/키 유출 스캔"
rg -n --hidden --ignore-file .gitignore -e 'AKIA[0-9A-Z]{16}|SECRET|BEGIN RSA|password\s*=' . > _audit_secrets.txt 2>/dev/null || echo "⚠️ ripgrep 없음, 기본 grep 사용" && grep -r -n -i "secret\|password\|key" . --exclude-dir=.git > _audit_secrets.txt 2>/dev/null || true
echo "✅ 비밀 스캔 저장: _audit_secrets.txt"

# C. 종속 그래프(러프) + 죽은 코드 후보
echo "📦 C. 종속 그래프 + 죽은 코드 후보"
rg -n "from\s+(\S+)|import\s+(\S+)" duri_* > _audit_imports.txt 2>/dev/null || grep -r -n "from\|import" duri_* > _audit_imports.txt 2>/dev/null || true
rg -n "TODO|FIXME|HACK|XXX" duri_* > _audit_todos.txt 2>/dev/null || grep -r -n -i "todo\|fixme\|hack\|xxx" duri_* > _audit_todos.txt 2>/dev/null || true
echo "✅ 종속성 저장: _audit_imports.txt"
echo "✅ TODO 저장: _audit_todos.txt"

# D. SQL/DDL 서명(변경 감지)
echo "🗄️ D. SQL/DDL 서명(변경 감지)"
if [ -f "v_feedback_events_clean_ddl.sql" ]; then
    sha256sum v_feedback_events_clean_ddl.sql > _audit_schema.sha256
    echo "✅ DDL 체크섬 저장: _audit_schema.sha256"
else
    echo "⚠️ v_feedback_events_clean_ddl.sql 없음"
fi

# E. 테스트·정적분석(있다면)
echo "🧪 E. 테스트·정적분석"
pytest -q 2>/dev/null || echo "⚠️ pytest 없음"
ruff check 2>/dev/null || echo "⚠️ ruff 없음"

# F. Docker 컨테이너 상태
echo "🐳 F. Docker 컨테이너 상태"
docker compose ps > _audit_docker_status.txt
echo "✅ Docker 상태 저장: _audit_docker_status.txt"

# G. 디스크 사용량
echo "💾 G. 디스크 사용량"
df -h > _audit_disk_usage.txt
echo "✅ 디스크 사용량 저장: _audit_disk_usage.txt"

# H. 최근 로그 샘플
echo "📝 H. 최근 로그 샘플"
docker compose logs --tail=50 aggregation_worker > _audit_recent_logs.txt 2>/dev/null || true
echo "✅ 최근 로그 저장: _audit_recent_logs.txt"

echo ""
echo "=== ✅ 전체 코드 건강검진 완료 ==="
echo "생성된 파일들:"
ls -la _audit_*.txt _audit_*.sha256 2>/dev/null || true
echo ""
echo "📊 요약:"
echo "  - Git 상태: $(wc -l < _audit_git_status.txt 2>/dev/null || echo 0) 라인"
echo "  - 비밀 스캔: $(wc -l < _audit_secrets.txt 2>/dev/null || echo 0) 라인"
echo "  - TODO 항목: $(wc -l < _audit_todos.txt 2>/dev/null || echo 0) 라인"
echo "  - Docker 컨테이너: $(docker compose ps -q | wc -l) 개"
echo ""
echo "🎯 다음 단계: SSD 최적화 및 인덱스 생성"
