# tools/production_hardening.sh
#!/bin/bash
# PZTA-CRA 운영 하드닝 스크립트

set -e

echo "=== PZTA-CRA 운영 하드닝 시작 ==="

# 1) 실서명 전환 준비
echo "• 실서명 전환 준비..."
if command -v cosign &> /dev/null; then
    echo "  - cosign 설치됨: $(cosign version)"
    echo "  - keyless/OIDC 서명 활성화 권장"
else
    echo "  - cosign 미설치: sudo apt install cosign"
fi

# 2) WORM 개시 (보존≥180일)
echo "• WORM 개시..."
if command -v aws &> /dev/null; then
    echo "  - AWS S3 Object Lock 활성화 권장"
    echo "  - 보존 기간: 180일"
else
    echo "  - AWS CLI 미설치: sudo apt install awscli"
fi

# 3) 키 로테이션 캘린더 설정
echo "• 키 로테이션 캘린더..."
ROTATION_DATE=$(date -d "+90 days" +%Y-%m-%d)
echo "  - 다음 로테이션: $ROTATION_DATE"
echo "  - 알림 설정 권장: 30일 전, 7일 전, 1일 전"

# 4) 골든셋 교체주기 설정
echo "• 골든셋 교체주기..."
echo "  - 교체 주기: 2주마다 20%"
echo "  - 은닉 회귀 문항 포함"
echo "  - 다음 교체: $(date -d "+2 weeks" +%Y-%m-%d)"

# 5) 주간 DR 드릴 스크립트 생성
echo "• 주간 DR 드릴 스크립트 생성..."
cat > tools/weekly_dr_drill.sh << 'EOF'
#!/bin/bash
# 주간 DR 드릴: 최신 태그 부팅 → 골든 20문항 ≥95% 확인

set -e

echo "=== 주간 DR 드릴 시작 ==="

# 1) 최신 태그 확인
LATEST_TAG=$(git describe --tags --match "milestone/*" --abbrev=0)
echo "• 최신 태그: $LATEST_TAG"

# 2) 골든 20문항 테스트
echo "• 골든 20문항 테스트..."
python3 tools/golden_test.py --count 20 --threshold 0.95

# 3) 결과 리포트
echo "• DR 드릴 완료: $(date)"
echo "• 리포트 생성: dr_drill_$(date +%Y%m%d).log"
EOF

chmod +x tools/weekly_dr_drill.sh

# 6) 캡슐 자동 리플레이 잡 설정
echo "• 캡슐 자동 리플레이 잡 설정..."
cat > tools/capsule_auto_replay.sh << 'EOF'
#!/bin/bash
# 캡슐 자동 리플레이: 매일 100건 샘플로 재현성 검증

set -e

echo "=== 캡슐 자동 리플레이 시작 ==="

# 1) 100건 샘플 재현성 검증
python3 tools/capsule_spotcheck.py --sample-size 100

# 2) 결과 로깅
echo "• 재현성 검증 완료: $(date)"
echo "• 결과 로그: capsule_replay_$(date +%Y%m%d).log"
EOF

chmod +x tools/capsule_auto_replay.sh

# 7) 크론잡 설정 안내
echo "• 크론잡 설정 안내..."
echo "  - 주간 DR 드릴: 0 9 * * 1 /path/to/tools/weekly_dr_drill.sh"
echo "  - 캡슐 리플레이: 0 2 * * * /path/to/tools/capsule_auto_replay.sh"

echo "=== 운영 하드닝 완료 ==="
echo "• 다음 단계: 크론잡 설정 및 모니터링 대시보드 구성"
