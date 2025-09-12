#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTDIR="$ROOT/verify_out"
mkdir -p "$OUTDIR"

echo "=== Day 8-34 검증 결과 ==="
echo "검증 시간: $(date)"
echo ""

# 각 Day별 간단한 파일 존재성 검증
declare -a DAYS=({8..34})
PASS_COUNT=0
TOTAL_COUNT=${#DAYS[@]}

for day in "${DAYS[@]}"; do
    case "$day" in
        8|9|10)
            # 학습 시스템 파일들
            if [ -f "$ROOT/activate_learning_systems.py" ] && [ -f "$ROOT/test_learning_modules.py" ]; then
                echo "Day $day: ✅ PASS (학습 시스템 파일 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (학습 시스템 파일 누락)"
            fi
            ;;
        11)
            # 모델카드 파일들
            if [ -f "$ROOT/model_card_v1.md" ] && [ -f "$ROOT/model_card_autofill.py" ]; then
                echo "Day $day: ✅ PASS (모델카드 파일 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (모델카드 파일 누락)"
            fi
            ;;
        15)
            # 자가코딩 루프
            if [ -f "$ROOT/tools/auto_code_loop_beta.sh" ] || [ -f "$ROOT/auto_code_loop_beta.sh" ]; then
                echo "Day $day: ✅ PASS (자가코딩 루프 파일 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (자가코딩 루프 파일 누락)"
            fi
            ;;
        16)
            # 오류→학습목표 변환
            if [ -f "$ROOT/error_to_goal.py" ]; then
                echo "Day $day: ✅ PASS (오류→학습목표 변환 파일 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (오류→학습목표 변환 파일 누락)"
            fi
            ;;
        17)
            # 실패 예산 경고
            if [ -f "$ROOT/failure_budget_alerts.py" ]; then
                echo "Day $day: ✅ PASS (실패 예산 경고 파일 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (실패 예산 경고 파일 누락)"
            fi
            ;;
        18)
            # HITL 품질 리포트
            if [ -f "$ROOT/hitl_quality_report.json" ]; then
                echo "Day $day: ✅ PASS (HITL 품질 리포트 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (HITL 품질 리포트 누락)"
            fi
            ;;
        31)
            # PoU 파일럿 통합 실행
            if [ -f "$ROOT/pou_pilot_manager.py" ] && [ -f "$ROOT/pou_pilot_report_20250911_233110.json" ]; then
                echo "Day $day: ✅ PASS (PoU 파일럿 통합 실행 파일 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (PoU 파일럿 통합 실행 파일 누락)"
            fi
            ;;
        32)
            # 재활 개인화 & V1 프로토콜
            if [ -f "$ROOT/rehab_personalization_engine.py" ] && [ -f "$ROOT/v1_protocol_rehab_system.py" ]; then
                echo "Day $day: ✅ PASS (재활 개인화 & V1 프로토콜 파일 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (재활 개인화 & V1 프로토콜 파일 누락)"
            fi
            ;;
        33)
            # 코딩 PR 보조
            if [ -f "$ROOT/coding_pr_assistant.py" ] && [ -f "$ROOT/coding_pr_assistant_result_20250911_235424.json" ]; then
                echo "Day $day: ✅ PASS (코딩 PR 보조 파일 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (코딩 PR 보조 파일 누락)"
            fi
            ;;
        34)
            # 통합 모니터링
            if [ -f "$ROOT/integrated_pou_dashboard_20250912_000300.json" ] && [ -f "$ROOT/pou_performance_report_20250912_000300.json" ]; then
                echo "Day $day: ✅ PASS (통합 모니터링 파일 존재)"
                ((PASS_COUNT++))
            else
                echo "Day $day: ❌ FAIL (통합 모니터링 파일 누락)"
            fi
            ;;
        *)
            # 중간 작업군 (19-30)
            echo "Day $day: ⚠️ SKIP (중간 작업군)"
            ;;
    esac
done

echo ""
echo "=== 검증 결과 요약 ==="
echo "총 검증 Day: $TOTAL_COUNT"
echo "PASS: $PASS_COUNT"
echo "FAIL: $((TOTAL_COUNT - PASS_COUNT))"
echo "PASS 비율: $((PASS_COUNT * 100 / TOTAL_COUNT))%"

# 결과를 파일로 저장
cat > "$OUTDIR/simple_verification_report.txt" << EOF
Day 8-34 검증 결과
==================
검증 시간: $(date)
총 검증 Day: $TOTAL_COUNT
PASS: $PASS_COUNT
FAIL: $((TOTAL_COUNT - PASS_COUNT))
PASS 비율: $((PASS_COUNT * 100 / TOTAL_COUNT))%

상세 결과:
EOF

echo "검증 완료! 결과 저장: $OUTDIR/simple_verification_report.txt"
