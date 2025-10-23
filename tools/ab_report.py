#!/usr/bin/env python3
"""
Day 37: A/B 테스트 결과 리포트 생성 도구
JSONL → Markdown 변환
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_jsonl_results(file_path: str) -> List[Dict[str, Any]]:
    """JSONL 파일에서 결과 로드"""
    results = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return []

    return results


def format_retention_rate(rate: float) -> str:
    """유지율을 퍼센트로 포맷"""
    return f"{rate:.1%}"


def format_p_value(p: float) -> str:
    """p-value 포맷"""
    if p < 0.001:
        return "< 0.001"
    elif p < 0.01:
        return f"{p:.3f}"
    else:
        return f"{p:.3f}"


def format_effect_size(effect: float) -> str:
    """효과 크기 포맷"""
    if abs(effect) < 0.01:
        return f"{effect:.4f}"
    else:
        return f"{effect:.3f}"


def generate_markdown_report(results: List[Dict[str, Any]]) -> str:
    """Markdown 리포트 생성"""
    if not results:
        return "# A/B 테스트 결과 리포트\n\n결과가 없습니다.\n"

    # 가장 최근 결과 사용
    result = results[-1]

    # 기본 정보
    report = f"""# A/B 테스트 결과 리포트

## 📊 **실험 정보**
- **실험 ID**: {result.get('exp_id', 'N/A')}
- **메트릭**: {result.get('metric', 'N/A')}
- **생성 시간**: {result.get('created_at_utc', 'N/A')}
- **테스트 타입**: {result.get('test_type', 'N/A')}
- **데이터 소스**: {result.get('source', 'N/A')}

## 📈 **통계 결과**

| 지표 | A 그룹 | B 그룹 | 차이 | 효과 크기 |
|------|--------|--------|------|-----------|
| **샘플 수** | {result.get('n_A', 'N/A')} | {result.get('n_B', 'N/A')} | - | - |
| **평균** | {format_retention_rate(result.get('mean_A', 0))} | {format_retention_rate(result.get('mean_B', 0))} | {format_effect_size(result.get('objective_delta', 0))} | {format_effect_size(result.get('effect_size', 0))} |
| **t-통계량** | - | - | {format_effect_size(result.get('t_stat', 0))} | - |
| **자유도** | - | - | {result.get('df', 'N/A')} | - |

## 🎯 **유의성 검정**

"""  # noqa: E501

    # p-value 정보 추가
    if "p_value" in result:
        report += f"- **p-value**: {format_p_value(result['p_value'])}\n"
    else:
        report += "- **p-value**: N/A\n"

    # 유의수준 확인
    alpha = 0.05
    if "p_value" in result:
        if result["p_value"] < alpha:
            report += f"- **결론**: 통계적으로 유의함 (p < {alpha})\n"
        else:
            report += f"- **결론**: 통계적으로 유의하지 않음 (p ≥ {alpha})\n"
    else:
        report += "- **결론**: p-value 정보 없음\n"

    report += "\n## 🚪 **게이트 결과**\n\n"

    # 게이트 정보
    gate_pass = result.get("gate_pass")
    if gate_pass is True:
        report += "✅ **게이트 통과**: 승격 가능\n"
    elif gate_pass is False:
        report += "❌ **게이트 실패**: 승격 불가\n"
    else:
        report += "⚠️ **게이트 미적용**: 게이트 정책 없음\n"

    # 게이트 이유
    gate_reasons = result.get("gate_reasons", [])
    if gate_reasons:
        report += "\n**게이트 이유**:\n"
        for reason in gate_reasons:
            report += f"- {reason}\n"

    # 게이트 정책 해시
    gate_policy_sha = result.get("gate_policy_sha256")
    if gate_policy_sha:
        report += f"\n**게이트 정책 해시**: `{gate_policy_sha[:16]}...`\n"

    # 배지 추가
    report += "\n## 🏷️ **상태 배지**\n\n"

    # 통계적 유의성 배지
    if "p_value" in result:
        if result["p_value"] < alpha:
            report += "![Statistically Significant](https://img.shields.io/badge/Statistically%20Significant-green)\n"
        else:
            report += "![Not Significant](https://img.shields.io/badge/Not%20Significant-yellow)\n"

    # 게이트 상태 배지
    if gate_pass is True:
        report += "![Gate Passed](https://img.shields.io/badge/Gate%20Passed-green)\n"
    elif gate_pass is False:
        report += "![Gate Failed](https://img.shields.io/badge/Gate%20Failed-red)\n"
    else:
        report += "![No Gate](https://img.shields.io/badge/No%20Gate-gray)\n"

    # 효과 크기 배지
    effect_size = abs(result.get("effect_size", 0))
    if effect_size >= 0.1:
        report += "![Large Effect](https://img.shields.io/badge/Large%20Effect-blue)\n"
    elif effect_size >= 0.05:
        report += "![Medium Effect](https://img.shields.io/badge/Medium%20Effect-orange)\n"
    else:
        report += "![Small Effect](https://img.shields.io/badge/Small%20Effect-lightgray)\n"

    # 권장사항
    report += "\n## 💡 **권장사항**\n\n"

    if gate_pass is True:
        report += "✅ **승격 권장**: 게이트를 통과했으므로 B 그룹을 승격할 수 있습니다.\n"
    elif gate_pass is False:
        report += "❌ **승격 금지**: 게이트를 통과하지 못했으므로 추가 개선이 필요합니다.\n"
    else:
        report += "⚠️ **게이트 미적용**: 게이트 정책을 설정하여 승격 기준을 명확히 하세요.\n"

    # 효과 크기 기반 권장사항
    if "objective_delta" in result:
        delta = result["objective_delta"]
        if abs(delta) >= 0.03:  # 3%p 이상
            if delta > 0:
                report += f"📈 **실질적 개선**: {format_retention_rate(delta)}p 개선으로 실질적 효과가 있습니다.\n"
            else:
                report += f"📉 **성능 저하**: {format_retention_rate(abs(delta))}p 저하로 개선이 필요합니다.\n"
        else:
            report += f"📊 **미미한 차이**: {format_retention_rate(abs(delta))}p 차이로 실질적 효과가 제한적입니다.\n"

    # 다음 단계
    report += "\n## 🔄 **다음 단계**\n\n"

    if gate_pass is True:
        report += "1. **승격 실행**: B 그룹을 전체 사용자에게 적용\n"
        report += "2. **모니터링**: 승격 후 성능 지표 지속 모니터링\n"
        report += "3. **롤백 준비**: 문제 발생 시 즉시 롤백 가능한 상태 유지\n"
    else:
        report += "1. **개선안 도출**: 게이트 실패 원인 분석 및 개선안 수립\n"
        report += "2. **재실험**: 개선된 버전으로 A/B 테스트 재실행\n"
        report += "3. **가드레일 점검**: 안전성 및 성능 기준 재검토\n"

    report += "\n---\n\n"
    report += f"*리포트 생성 시간: {result.get('created_at_utc', 'N/A')}*\n"

    return report


def main():
    """CLI 인터페이스"""
    parser = argparse.ArgumentParser(description="A/B 테스트 결과 리포트 생성")

    parser.add_argument("input_files", nargs="+", help="입력 JSONL 파일 경로")
    parser.add_argument("--output", "-o", help="출력 파일 경로 (기본: stdout)")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그 출력")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 모든 입력 파일에서 결과 로드
    all_results = []
    for file_path in args.input_files:
        results = load_jsonl_results(file_path)
        all_results.extend(results)
        logger.info(f"Loaded {len(results)} results from {file_path}")

    if not all_results:
        logger.error("No results found in input files")
        sys.exit(1)

    # 리포트 생성
    report = generate_markdown_report(all_results)

    # 출력
    if args.output:
        try:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)

            logger.info(f"Report saved to: {args.output}")
        except Exception as e:
            logger.error(f"Error writing output file: {e}")
            sys.exit(1)
    else:
        print(report)


if __name__ == "__main__":
    main()
