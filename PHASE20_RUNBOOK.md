# DuRi Phase 20 운영 문서 (Runbook)

## 📋 현재 레포 설정 요약

### ✅ 활성화된 기능
- **Auto-merge**: `allow_auto_merge=true`
- **브랜치 자동 삭제**: `delete_branch_on_merge=true`
- **브랜치 보호**: 필수 체크 + 선형 히스토리
- **자동 머지 워크플로우**: `enable-auto-merge.yml`

### 🔒 브랜치 보호 규칙
- **필수 체크**: `freeze-guard/guard`, `repo-guards/guards`, `Phase-2 Suite/tests`
- **선형 히스토리**: 활성화
- **강제 푸시**: 금지
- **브랜치 삭제**: 금지

## 🚀 브랜치/PR 운영 플로우

### 기본 워크플로우
```bash
# 1. 변경사항 커밋
git add .
git commit -m "feat: 설명"

# 2. 푸시 및 PR 생성/업데이트
./scripts/pr-open.sh
# 또는
git push -u origin HEAD
gh pr create --fill --base main --head $(git rev-parse --abbrev-ref HEAD)
```

### ops/* 브랜치 자동 머지
```bash
# ops/* 브랜치에 automerge 라벨 추가
gh pr edit <번호> --add-label "automerge"

# GitHub 네이티브 auto-merge 활성화
gh pr merge <번호> --squash --auto
```

## 🔄 Auto-merge 조건 및 점검

### 자동 머지 조건
- ✅ `automerge` 라벨 존재
- ✅ 모든 필수 체크 통과
- ✅ 충돌 없음
- ✅ 브랜치 보호 규칙 준수

### 점검 방법
```bash
# PR 상태 확인
gh pr view <번호> --json mergeStateStatus,mergeable

# 체크 상태 확인
gh pr checks <번호>

# 자동 머지 상태 확인
gh pr view <번호> --json autoMergeRequest
```

## 🛠️ 리베이스/충돌 해결

### 리베이스 실행
```bash
# 최신 main으로 리베이스
git fetch origin
git rebase origin/main

# 충돌 해결 후
git add .
git rebase --continue

# 푸시 (force-push 필요)
git push --force-with-lease origin HEAD
```

### 충돌 해결 팁
- **VS Code**: 충돌 마커 자동 감지
- **터미널**: `git status`로 충돌 파일 확인
- **복사/붙여넣기**: `Ctrl+Alt+C` (복사), `Ctrl+Alt+V` (붙여넣기)

## 🚨 규칙 위반 오류 대처

### freeze-guard 차단
```bash
# 허용 목록에 파일 추가
echo "파일경로" >> .github/freeze-allow.txt
git add .github/freeze-allow.txt
git commit -m "chore: freeze-allow 업데이트"

# 긴급 우회 (비추천)
FREEZE_BYPASS=1 git push
```

### 브랜치 보호 위반
```bash
# 필수 체크 재실행
gh pr checks <번호> --watch

# 수동 머지 (관리자 권한 필요)
gh pr merge <번호> --squash --admin
```

## 🔒 Freeze/Repo Guards 운용

### Freeze 활성화
```bash
# freeze 라벨 추가로 즉시 차단
gh pr edit <번호> --add-label "freeze"
```

### Repo Guards 점검
- **Freeze Check**: 변경사항 허용 여부
- **Repo Guards**: 레포 정책 준수
- **Phase-2 Suite**: 테스트 통과

## 🧹 머지 후 정리

### 자동 정리 (설정됨)
- ✅ 브랜치 자동 삭제
- ✅ PR 자동 닫기
- ✅ 커밋 히스토리 정리

### 수동 정리 (필요시)
```bash
# 로컬 브랜치 정리
git branch -d <브랜치명>

# 원격 브랜치 정리
git push origin --delete <브랜치명>
```

## 🔧 서브모듈 트러블슈팅

### 서브모듈 업데이트
```bash
# 서브모듈 상태 확인
git submodule status

# 서브모듈 업데이트
git submodule update --remote

# 서브모듈 커밋
git add .
git commit -m "chore: 서브모듈 업데이트"
```

## 📚 치트시트

### 자주 사용하는 명령어
```bash
# PR 생성/업데이트
./scripts/pr-open.sh

# PR 상태 확인
gh pr view <번호>

# 체크 상태 확인
gh pr checks <번호>

# 자동 머지 활성화
gh pr merge <번호> --squash --auto

# 수동 머지
gh pr merge <번호> --squash

# PR 닫기
gh pr close <번호>
```

### API 설정 예시
```bash
# 리포 설정 확인
gh api repos/:owner/:repo --jq '{auto_merge:.allow_auto_merge,delete_branch:.delete_branch_on_merge}'

# 브랜치 보호 확인
gh api repos/:owner/:repo/branches/main/protection --jq '{strict:.required_status_checks.strict,contexts:.required_status_checks.contexts}'
```

## 🆘 긴급 상황 대처

### 자동 머지 실패
1. **체크 상태 확인**: `gh pr checks <번호>`
2. **충돌 해결**: 리베이스 실행
3. **수동 머지**: `gh pr merge <번호> --squash`

### 브랜치 보호 우회
1. **관리자 권한 확인**
2. **수동 머지**: `gh pr merge <번호> --squash --admin`
3. **설정 수정**: 웹 UI에서 브랜치 보호 규칙 조정

### Freeze 우회
1. **긴급 우회**: `FREEZE_BYPASS=1 git push`
2. **허용 목록 수정**: `.github/freeze-allow.txt` 업데이트
3. **정상 플로우 복구**: 허용 목록 커밋 후 재시도

---

## 📝 참고사항

- **터미널 단축키**: `Ctrl+Alt+C` (복사), `Ctrl+Alt+V` (붙여넣기)
- **Pyright 설정**: 대용량 디렉토리 제외로 성능 최적화
- **백업 스크립트**: `smart_backup_cleanup.sh` 사용 가능
- **문서 업데이트**: 이 문서는 Phase 20 킥오프 기준으로 작성됨

**마지막 업데이트**: 2025-09-19
