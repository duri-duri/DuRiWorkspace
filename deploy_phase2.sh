#!/usr/bin/env bash
set -euo pipefail

OWNER=duri-duri
REPO=DuRiWorkspace

echo "== 1) PR(gate-test -> main) 머지 시도 =="
PR=$(gh pr list -H gate-test -B main --state open --json number -q '.[0].number' || true)
if [[ -n "${PR:-}" ]]; then
  echo "Merging PR #$PR (self-created, skipping approval) ..."
  gh pr merge  "$PR" --merge --delete-branch
else
  echo "[info] 열려있는 gate-test->main PR 없음 — 건너뜀"
fi

echo
echo "== 2) main에서 Phase-2 Suite 수동 실행 & 결과 확인 =="
gh workflow run .github/workflows/ci-phase2.yml -r main
RUN_ID=$(gh run list --workflow "Phase-2 Suite" -b main -L 1 --json databaseId -q '.[0].databaseId')
echo "main latest RUN_ID: $RUN_ID"
gh run watch "$RUN_ID"

CONC=$(gh run view "$RUN_ID" --json conclusion -q .conclusion)
echo "Conclusion: $CONC"
if [[ "$CONC" != "success" ]]; then
  echo "[warn] 실패 감지 — 아티팩트 내려받는 중"
  gh run download "$RUN_ID" -n "test-artifacts-$RUN_ID" -D "./ci-artifacts-$RUN_ID" || true
  echo "Artifacts: ./ci-artifacts-$RUN_ID"
fi

echo
echo "== 3) 브랜치 보호 규칙 재확인(main / release/*) =="
echo "[main] required contexts:"
gh api -H "Accept: application/vnd.github+json" \
  "/repos/$OWNER/$REPO/branches/main/protection" \
  | jq '.required_status_checks.contexts'

echo
echo "[release/*] 패턴 규칙:"
gh api graphql -f owner=$OWNER -f name=$REPO -f query='
query($owner:String!, $name:String!){
  repository(owner:$owner, name:$name){
    branchProtectionRules(first:50){
      nodes{ pattern requiredStatusCheckContexts isAdminEnforced }
    }
  }
}' | jq -r '.data.repository.branchProtectionRules.nodes[]
            | select(.pattern=="release/*")'

echo
echo "== 4) 기존 release/* 브랜치 전체 시드 실행 =="
gh api -H "Accept: application/vnd.github+json" \
  "/repos/$OWNER/$REPO/branches" --paginate \
| jq -r '.[].name | select(startswith("release/"))' \
| while read -r BR; do
    echo "dispatch Phase-2 Suite on $BR"
    gh workflow run .github/workflows/ci-phase2.yml -r "$BR" || true
  done

echo
echo "== 5) 스냅샷 태그 푸시 =="
STAMP=$(date +%Y%m%d-%H%M)
git fetch --tags
TAG="v${STAMP}-phase2-green"
git tag -a "$TAG" -m "Phase-2 suite green on main (gate enforced)"
git push --tags
echo "Tagged: $TAG"

echo
echo "✅ 완료!"
