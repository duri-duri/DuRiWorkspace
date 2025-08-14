#!/usr/bin/env bash
set -euo pipefail

# DuRi Day1~5 통합 검증 스크립트
# 위치 가정: repo 루트 또는 modules/ml_integration 하위
# 출력: 콘솔 표 + artifacts_phase1/verify_day1_5_report.json

ROOT="$(pwd)"
ARTIFACT_DIR="${ROOT}/artifacts_phase1"
REPORT_JSON="${ARTIFACT_DIR}/verify_day1_5_report.json"
mkdir -p "${ARTIFACT_DIR}"

# pretty print helper
hr(){ printf '%s\n' "----------------------------------------------------------------"; }
ok(){ printf "✅ %-28s : %s\n" "$1" "$2"; }
warn(){ printf "⚠️  %-28s : %s\n" "$1" "$2"; }
fail(){ printf "❌ %-28s : %s\n" "$1" "$2"; }

# result accumulators
declare -A PASS REASON

set +e

###############################################################################
# Check 1) trace_v2_schema.json 존재 + 필수 키 검증
###############################################################################
# 후보 경로 탐색 (깊이 완화: 3→5)
SCHEMA_PATH=""
while IFS= read -r p; do
  SCHEMA_PATH="$p"; break
done < <(find "${ROOT}" -maxdepth 5 -type f -name "trace_v2_schema.json" 2>/dev/null)

if [[ -z "${SCHEMA_PATH}" ]]; then
  PASS[trace_schema]="false"
  REASON[trace_schema]="trace_v2_schema.json 파일을 찾지 못함(./configs/ 아래 권장)."
else
  # 필수 키 검사
  PY_OUT="$(python3 -c "
import json,sys
req = ['input','intent','options','decision','rationale','uncertainty','next_action','audit']
try:
    with open('${SCHEMA_PATH}', 'r') as f:
        j=json.load(f)
    missing=[k for k in req if k not in j]
    print('MISSING:'+','.join(missing) if missing else 'MISSING:')
except Exception as e:
    print('ERROR:'+str(e))
")"
  
  # JSON 스키마 실제 검증 (jsonschema가 있으면)
  SCHEMA_VALID="$(python3 -c "
import json,sys
try:
    import jsonschema
    s=json.load(open('${SCHEMA_PATH}'))
    jsonschema.Draft202012Validator.check_schema(s)
    print('VALID')
except ImportError:
    print('NO_JS')
except Exception as e:
    print('INVALID:'+str(e))
" 2>/dev/null || echo "ERROR")"
  
  if [[ "${PY_OUT}" == "MISSING:" ]]; then
    if [[ "${SCHEMA_VALID}" == "VALID" ]]; then
      PASS[trace_schema]="true"
      REASON[trace_schema]="필수 키 모두 존재 + JSON 스키마 유효 (${SCHEMA_PATH})."
    elif [[ "${SCHEMA_VALID}" == "NO_JS" ]]; then
      PASS[trace_schema]="true"
      REASON[trace_schema]="필수 키 모두 존재 (${SCHEMA_PATH}). jsonschema 미설치로 스키마 검증 생략."
    else
      PASS[trace_schema]="false"
      REASON[trace_schema]="필수 키 존재하나 JSON 스키마 무효: ${SCHEMA_VALID#INVALID:} (${SCHEMA_PATH})."
    fi
  else
    PASS[trace_schema]="false"
    REASON[trace_schema]="필수 키 누락: ${PY_OUT#MISSING:} (${SCHEMA_PATH})."
  fi
fi

###############################################################################
# Check 2) 문자열 출력 제거율 ≥ 80% (최근 로그의 JSON형 비율로 근사)
###############################################################################
# 대상: artifacts_phase1/*.log (없으면 tools/logs/*.log, logs/*.log 순)
LOG_CAND=( "${ARTIFACT_DIR}" "${ROOT}/tools" "${ROOT}/logs" )
LOG_FILES=()
for d in "${LOG_CAND[@]}"; do
  if [[ -d "$d" ]]; then
    while IFS= read -r f; do LOG_FILES+=("$f"); done < <(ls -1 "$d"/*.log 2>/dev/null | tail -n 10)
  fi
done

if (( ${#LOG_FILES[@]} == 0 )); then
  # JSON 산출물(.json) 라인으로 대체 측정
  while IFS= read -r f; do LOG_FILES+=("$f"); done < <(ls -1 "${ARTIFACT_DIR}"/*.json 2>/dev/null | tail -n 5)
fi

if (( ${#LOG_FILES[@]} == 0 )); then
  PASS[string_elim]="false"
  REASON[string_elim]="최근 로그/JSON 산출물을 찾지 못해 측정 불가(최소 1개 필요)."
else
  total=0
  jsonlike=0
  for f in "${LOG_FILES[@]}"; do
    # 총 라인
    t=$(wc -l < "$f" | tr -d ' ')
    (( total+=t ))
    # JSON-like 라인(대괄호/중괄호로 시작)
    j=$(grep -E '^[[:space:]]*[\{\[]' "$f" | wc -l | tr -d ' ')
    (( jsonlike+=j ))
  done
  ratio=0
  if (( total > 0 )); then
    ratio=$(python3 -c "print(round((${jsonlike}/${total})*100,2))")
  fi
  if (( $(python3 -c "print(1 if ${ratio} >= 80 else 0)") == 1 )); then
    PASS[string_elim]="true"
    REASON[string_elim]="JSON형 라인 비율 ${ratio}% (기준≥80%)."
  else
    PASS[string_elim]="false"
    REASON[string_elim]="JSON형 라인 비율 ${ratio}% (기준≥80% 미만)."
  fi
fi

###############################################################################
# Check 3) regression_bench_list.yaml 존재 + 항목 수 ≥ 12
###############################################################################
BENCH_PATH=""
for c in "${ROOT}/configs" "${ROOT}" "."; do
  [[ -f "${c}/regression_bench_list.yaml" ]] && BENCH_PATH="${c}/regression_bench_list.yaml" && break
done

if [[ -z "${BENCH_PATH}" ]]; then
  PASS[bench_yaml]="false"
  REASON[bench_yaml]="configs/regression_bench_list.yaml 미존재."
else
  # YAML 정밀 파싱으로 항목 수 계산
  COUNT_ITEMS=$(python3 -c "
import yaml, sys
try:
    with open('${BENCH_PATH}', 'r') as f:
        d = yaml.safe_load(f)
    items = d if isinstance(d, list) else (d.get('benches', []) if isinstance(d, dict) else [])
    print(len(items))
except Exception as e:
    print(0)
" 2>/dev/null || echo "0")
  
  if (( COUNT_ITEMS >= 12 )); then
    PASS[bench_yaml]="true"
    REASON[bench_yaml]="항목 수 ${COUNT_ITEMS}개 (기준≥12) - ${BENCH_PATH}"
  else
    PASS[bench_yaml]="false"
    REASON[bench_yaml]="항목 수 ${COUNT_ITEMS}개 (기준≥12 필요) - ${BENCH_PATH}"
  fi
fi

###############################################################################
# Check 4) run_regression_tests.sh 존재 + 로그 저장 루틴 포함 여부
###############################################################################
RUN_SCRIPT=""
for c in "${ROOT}/scripts" "${ROOT}" "."; do
  [[ -x "${c}/run_regression_tests.sh" ]] && RUN_SCRIPT="${c}/run_regression_tests.sh" && break
done

if [[ -z "${RUN_SCRIPT}" ]]; then
  PASS[bench_runner]="false"
  REASON[bench_runner]="run_regression_tests.sh 실행 파일을 찾지 못함."
else
  if grep -Eq '(tee|>>|>\s*[^/]*artifacts|artifacts_phase1|bench|logs)' "${RUN_SCRIPT}"; then
    PASS[bench_runner]="true"
    REASON[bench_runner]="스크립트 존재+실행 가능, 로그/아티팩트 기록 루틴 감지."
  else
    PASS[bench_runner]="false"
    REASON[bench_runner]="스크립트 존재하나 로그/아티팩트 기록 루틴 미감지(tee 또는 artifacts 경로 권장)."
  fi
fi

###############################################################################
# Check 5) failure_types_catalog.md 에 4유형 명시
###############################################################################
FAILCAT_PATH=""
for c in "${ROOT}/docs" "${ROOT}" "."; do
  [[ -f "${c}/failure_types_catalog.md" ]] && FAILCAT_PATH="${c}/failure_types_catalog.md" && break
done

if [[ -z "${FAILCAT_PATH}" ]]; then
  PASS[failure_catalog]="false"
  REASON[failure_catalog]="failure_types_catalog.md 미존재."
else
  miss=()
  for k in "Validation" "Transient" "System" "Spec"; do
    grep -qi "${k}" "${FAILCAT_PATH}" || miss+=("${k}")
  done
  if (( ${#miss[@]} == 0 )); then
    PASS[failure_catalog]="true"
    REASON[failure_catalog]="4유형 모두 명시됨 (${FAILCAT_PATH})."
  else
    PASS[failure_catalog]="false"
    REASON[failure_catalog]="누락: ${miss[*]} (${FAILCAT_PATH})."
  fi
fi

set -e

###############################################################################
# 출력
###############################################################################
hr
echo "DuRi Day1~5 통합 검증 결과"
hr

total_ok=0; total=0
for key in trace_schema string_elim bench_yaml bench_runner failure_catalog; do
  ((total++))
  if [[ "${PASS[$key]}" == "true" ]]; then
    ((total_ok++))
    ok "$key" "${REASON[$key]}"
  else
    fail "$key" "${REASON[$key]}"
  fi
done

hr
if (( total_ok == total )); then
  echo "🎉 ALL PASS: Day 6로 진행해도 안전합니다."
else
  echo "⚠️  PARTIAL: 보완 필요 항목을 해결 후 Day 6로 진행하세요."
fi
hr

###############################################################################
# JSON 리포트 저장
###############################################################################
python3 -c "
import json
report = {
    'checks': {
        'trace_schema': {'pass': '${PASS[trace_schema]}' == 'true', 'reason': '${REASON[trace_schema]}'},
        'string_elim': {'pass': '${PASS[string_elim]}' == 'true', 'reason': '${REASON[string_elim]}'},
        'bench_yaml': {'pass': '${PASS[bench_yaml]}' == 'true', 'reason': '${REASON[bench_yaml]}'},
        'bench_runner': {'pass': '${PASS[bench_runner]}' == 'true', 'reason': '${REASON[bench_runner]}'},
        'failure_catalog': {'pass': '${PASS[failure_catalog]}' == 'true', 'reason': '${REASON[failure_catalog]}'},
    },
    'summary': {'passed': ${total_ok}, 'total': ${total}}
}
with open('${REPORT_JSON}', 'w') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f'JSON report saved -> {REPORT_JSON}')
"
