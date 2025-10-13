# 유지보수 가이드

## pre-commit 자동 업데이트

분기별로 한 번씩 실행하여 hook stage 경고를 해결하세요:

```bash
pre-commit autoupdate
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

## 정기 점검 항목

- [ ] promtool 버전 호환성 확인
- [ ] Alertmanager 설정 검증
- [ ] 알람 룰 테스트 실행
- [ ] 라벨/어노테이션 가드 실행
- [ ] 중복 레코드 가드 실행

## 문제 해결

자세한 내용은 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)를 참조하세요.
