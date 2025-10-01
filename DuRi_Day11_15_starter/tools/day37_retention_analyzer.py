#!/usr/bin/env python3
"""
Day37 Enhanced: PoU 유지율 분석 시스템 (기존 코드 통합)
- pou_metrics_ingest.py의 파싱 로직 재사용
- Wilson CI 계산 및 판정 자동화
- 기존 모니터링 시스템과 통합
"""

import argparse
import collections
import datetime as dt
import glob
import json
import logging
import math
import os
import statistics
from pathlib import Path
from typing import Any, Dict, List, Tuple


# 기존 pou_metrics_ingest.py의 함수들 재사용
def parse_json_lines(path: str) -> List[Dict[str, Any]]:
    """JSONL 파일 파싱 (기존 코드 재사용)"""
    items = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    # 리딩 제로 등 비정형 방어
                    line = line.replace(": .", ": 0.")
                    try:
                        items.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logging.warning(f"JSONL 파싱 실패 {path}:{line_num} - {e}")
    except Exception as e:
        logging.error(f"JSONL 파일 읽기 실패 {path}: {e}")

    return items


def daykey(ts: str) -> dt.date:
    """타임스탬프를 날짜로 변환"""
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).date()


def ci95_wilson(p: float, n: int) -> Tuple[float, float]:
    """Wilson score CI 계산"""
    if n == 0:
        return (0.0, 0.0)

    z = 1.96
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = (z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)) / denom

    return (max(0.0, center - margin), min(1.0, center + margin))


def retention_for_domain(
    domain: str, start_date: dt.date, glob_pattern: str
) -> Tuple[Dict[str, Any], int]:
    """도메인별 유지율 계산"""
    files = glob.glob(glob_pattern.format(dom=domain))
    by_user_by_day = collections.defaultdict(lambda: collections.defaultdict(int))

    for fp in files:
        for rec in parse_json_lines(fp):
            # 성공한 세션만 포함
            if rec.get("status") not in {"success", "ok"}:
                continue

            # Guard 2: UID fallback
            if "user_id" in rec and rec["user_id"]:
                uid = rec["user_id"]
            else:
                import os

                uid = os.path.splitext(os.path.basename(fp))[0]  # filename as user_id
            d = daykey(rec["timestamp"])
            by_user_by_day[uid][d] += 1

    # Cohort: D0 = START
    D = [start_date + dt.timedelta(days=i) for i in range(0, 8)]  # D0..D7
    cohort = [u for u, days in by_user_by_day.items() if days.get(D[0], 0) > 0]
    n0 = len(cohort)

    ret = {}
    for i in range(1, 8):
        active = sum(1 for u in cohort if by_user_by_day[u].get(D[i], 0) > 0)
        rate = (active / n0) if n0 else 0.0
        ret[f"D{i}"] = {"active": active, "total": n0, "rate": rate}

    return ret, n0


def analyze_retention(
    domains: List[str], start_date: dt.date, glob_pattern: str
) -> Dict[str, Any]:
    """전체 유지율 분석"""
    out = {
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "cohort_start": start_date.isoformat(),
        "analysis_type": "D7_retention",
        "thresholds": {"pass": 0.40, "warning": 0.35, "fail": 0.35},
    }

    summary = []

    for dom in domains:
        try:
            ret, n0 = retention_for_domain(dom, start_date, glob_pattern)
            d7 = ret["D7"]["rate"]
            lo, hi = ci95_wilson(d7, ret["D7"]["total"])

            # 판정 로직 (가드레일 추가)
            if n0 < 30:
                decision = "INSUFFICIENT"
                action = "데이터 부족 - 재평가 필요"
            elif d7 >= 0.40:
                decision = "PASS"
                action = "운영 유지"
            elif d7 >= 0.35:
                decision = "WARNING"
                action = "개선계획 필요"
            else:
                decision = "FAIL"
                action = "즉시 개선 필요"

            out[dom] = {
                "cohort_size": n0,
                "daily": ret,
                "day7_rate": d7,
                "day7_ci95": [lo, hi],
                "decision": decision,
                "action": action,
            }

            summary.append((dom, n0, d7, lo, hi, decision))

        except Exception as e:
            logging.error(f"도메인 {dom} 분석 실패: {e}")
            out[dom] = {
                "error": str(e),
                "decision": "ERROR",
                "action": "데이터 확인 필요",
            }
            summary.append((dom, 0, 0.0, 0.0, 0.0, "ERROR"))

    return out, summary


def generate_report(summary: List[Tuple], output_dir: Path) -> str:
    """Markdown 리포트 생성"""
    md_lines = [
        "# Day37 PoU 유지율 분석 리포트",
        "",
        "## 📊 D7 유지율 요약",
        "",
        "| 도메인 | 코호트 크기 | D7 유지율 | 95% CI | 판정 | 조치 |",
        "|---|---:|---:|---:|---:|---|",
    ]

    for dom, n0, d7, lo, hi, decision in summary:
        ci_str = f"[{lo:.3f}, {hi:.3f}]"
        md_lines.append(
            f"| {dom} | {n0} | {d7:.3f} | {ci_str} | {decision} | {get_action_text(decision)} |"
        )

    md_lines.extend(
        [
            "",
            "## 🎯 판정 기준",
            "- **PASS**: D7 ≥ 40% → 운영 유지",
            "- **WARNING**: 35% ≤ D7 < 40% → 개선계획 필요",
            "- **FAIL**: D7 < 35% → 즉시 개선 필요",
            "",
            "## 🚀 권장 조치사항",
            "",
        ]
    )

    # 도메인별 조치사항
    for dom, n0, d7, lo, hi, decision in summary:
        if decision == "PASS":
            md_lines.append(f"- **{dom}**: ✅ 유지율 양호 ({d7:.1%}) - 현재 설정 유지")
        elif decision == "WARNING":
            md_lines.append(f"- **{dom}**: ⚠️ 유지율 주의 ({d7:.1%}) - 개선 레버 적용:")
            md_lines.append(f"  - 실패 제어 강화 (리스크 프롬프트 보강)")
            md_lines.append(f"  - 응답 스트리밍 활성화")
            md_lines.append(f"  - 설명성 보강 (근거 스니펫 2→3개)")
        elif decision == "FAIL":
            md_lines.append(f"- **{dom}**: ❌ 유지율 부족 ({d7:.1%}) - 즉시 개선:")
            md_lines.append(f"  - 이탈 원인 분석 (Top3 로그 샘플 50건)")
            md_lines.append(f"  - 개선안 A/B 테스트 설계")
            md_lines.append(f"  - 사용자 피드백 수집 강화")

    report_content = "\n".join(md_lines)

    # 리포트 파일 저장
    report_file = output_dir / "day37_retention_report.md"
    report_file.write_text(report_content, encoding="utf-8")

    return str(report_file)


def get_action_text(decision: str) -> str:
    """판정에 따른 조치 텍스트"""
    actions = {
        "PASS": "운영 유지",
        "WARNING": "개선계획 필요",
        "FAIL": "즉시 개선 필요",
        "ERROR": "데이터 확인 필요",
    }
    return actions.get(decision, "미정")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Day37 PoU 유지율 분석")
    parser.add_argument(
        "--domains",
        nargs="+",
        default=["medical", "rehab", "coding"],
        help="분석할 도메인 목록",
    )
    parser.add_argument(
        "--glob", default="samples/logs/{dom}_*.jsonl", help="로그 파일 패턴"
    )
    parser.add_argument(
        "--start-date", default="2025-01-16", help="코호트 시작일 (YYYY-MM-DD)"
    )
    parser.add_argument("--output-dir", default="artifacts/day37", help="출력 디렉토리")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")
    parser.add_argument(
        "--auto-start", action="store_true", help="로그의 최소 날짜를 D0로 사용"
    )

    args = parser.parse_args()

    # 로깅 설정
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # 시작일 파싱
    try:
        start_date = dt.datetime.strptime(args.start_date, "%Y-%m-%d").date()
    except ValueError:
        logging.error(f"잘못된 날짜 형식: {args.start_date}")
        return 1

    # 출력 디렉토리 생성
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 유지율 분석 실행
    logging.info(f"Day37 유지율 분석 시작: {args.domains}")

    try:
        results, summary = analyze_retention(args.domains, start_date, args.glob)

        # JSON 결과 저장
        json_file = output_dir / "pou_retention_day7.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # 리포트 생성
        report_file = generate_report(summary, output_dir)

        # 콘솔 출력
        print("# Day37 D7 Retention Analysis")
        print(f"Generated: {results['generated_at']}")
        print(f"Cohort Start: {results['cohort_start']}")
        print()

        for dom, n0, d7, lo, hi, decision in summary:
            print(
                f"{dom:8s}  n0={n0:4d}  D7={d7:.3f}  CI95=[{lo:.3f},{hi:.3f}]  {decision}"
            )

        print(f"\nResults saved to: {json_file}")
        print(f"Report saved to: {report_file}")

        # 전체 통과 여부 확인
        all_pass = all(decision == "PASS" for _, _, _, _, _, decision in summary)
        if all_pass:
            print("\n✅ Day37 PASS: 모든 도메인 유지율 기준 충족")
            return 0
        else:
            print("\n⚠️ Day37 WARNING: 일부 도메인 개선 필요")
            return 1

    except Exception as e:
        logging.error(f"분석 실패: {e}")
        return 2


if __name__ == "__main__":
    exit(main())
