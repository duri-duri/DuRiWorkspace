#!/usr/bin/env python3
"""
Day36 Enhanced: PoU 지표 수집→정규화→저장 자동화 시스템
- 기존 로그 분석 코드와 통합
- JSON/JSONL/CSV/TXT(k=v) 포맷 지원
- 실시간 J 계산 및 A/B 테스트 준비
"""

import argparse
import csv
from datetime import datetime
import glob
import json
import logging
import os
from pathlib import Path
import re
import statistics
import sys
from typing import Any, Dict, List, Optional, Union

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_yaml(path: str) -> Dict[str, Any]:
    """YAML 파일 로드"""
    try:
        import yaml
    except ImportError:
        raise SystemExit("PyYAML 필요: pip install pyyaml")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def to_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    """값을 float로 변환"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def normalize_to_01(value: Any) -> Optional[float]:
    """값을 0-1 범위로 정규화"""
    if value is None:
        return None

    try:
        val = float(value)
        # 100보다 크면 퍼센트로 처리
        if val > 1.000001:
            return max(0.0, min(1.0, val / 100.0))
        return max(0.0, min(1.0, val))
    except (ValueError, TypeError):
        return None


def parse_json_lines(path: str) -> List[Dict[str, Any]]:
    """JSONL 파일 파싱"""
    items = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"JSONL 파싱 실패 {path}:{line_num} - {e}")
    except Exception as e:
        logger.error(f"JSONL 파일 읽기 실패 {path}: {e}")

    return items


def parse_json(path: str) -> List[Dict[str, Any]]:
    """JSON 파일 파싱"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            return []
    except Exception as e:
        logger.error(f"JSON 파일 읽기 실패 {path}: {e}")
        return []


def parse_csv(path: str) -> List[Dict[str, Any]]:
    """CSV 파일 파싱"""
    rows = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception as e:
        logger.error(f"CSV 파일 읽기 실패 {path}: {e}")

    return rows


# 키-값 패턴 정규식
KV_PATTERN = re.compile(r"([A-Za-z0-9_.-]+)\s*[:=]\s*([^\s,;]+)")


def parse_kv_txt(path: str) -> List[Dict[str, Any]]:
    """키=값 형식 텍스트 파일 파싱"""
    rows = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                record = {}
                matches = KV_PATTERN.findall(line.strip())
                for key, value in matches:
                    record[key] = value

                if record:
                    rows.append(record)
    except Exception as e:
        logger.error(f"TXT 파일 읽기 실패 {path}: {e}")

    return rows


def detect_format(path: str) -> str:
    """파일 형식 감지"""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".jsonl", ".ndjson"):
        return "jsonl"
    elif ext == ".json":
        return "json"
    elif ext == ".csv":
        return "csv"
    else:
        return "kv"


def parse_any_file(path: str) -> List[Dict[str, Any]]:
    """파일 형식에 따라 자동 파싱"""
    fmt = detect_format(path)

    if fmt == "jsonl":
        return parse_json_lines(path)
    elif fmt == "json":
        return parse_json(path)
    elif fmt == "csv":
        return parse_csv(path)
    else:
        return parse_kv_txt(path)


def aggregate_metrics(
    rows: List[Dict[str, Any]], mapping: Dict[str, Any]
) -> Dict[str, float]:
    """지표 집계"""
    # 키 매핑 로드
    key_latency = mapping["keys"].get(
        "latency", ["p95_latency_ms", "latency_ms", "latency", "p95"]
    )
    key_accuracy = mapping["keys"].get(
        "accuracy", ["accuracy", "acc", "score_acc", "correct_rate"]
    )
    key_explainability = mapping["keys"].get(
        "explainability", ["explainability", "explain", "exp_score", "rubric"]
    )
    key_failure = mapping["keys"].get(
        "failure", ["failure_rate", "fail_rate", "error_rate"]
    )
    key_status = mapping["keys"].get("status", ["status", "ok", "success", "passed"])

    # 데이터 수집
    latencies, accuracies, explainabilities, failures, statuses = [], [], [], [], []

    for row in rows:
        # 지연시간 수집
        for key in key_latency:
            if key in row and row[key] not in ("", None):
                latencies.append(to_float(row[key]))
                break

        # 정확도 수집
        for key in key_accuracy:
            if key in row and row[key] not in ("", None):
                accuracies.append(to_float(row[key]))
                break

        # 설명성 수집
        for key in key_explainability:
            if key in row and row[key] not in ("", None):
                explainabilities.append(to_float(row[key]))
                break

        # 실패율 수집
        for key in key_failure:
            if key in row and row[key] not in ("", None):
                failures.append(to_float(row[key]))
                break

        # 상태 수집
        for key in key_status:
            if key in row and row[key] not in ("", None):
                statuses.append(str(row[key]).lower())
                break

    def aggregate_values(values: List[float], method: str) -> Optional[float]:
        """값 집계"""
        valid_values = [v for v in values if v is not None]
        if not valid_values:
            return None

        valid_values.sort()

        if method == "mean":
            return sum(valid_values) / len(valid_values)
        elif method == "median":
            return statistics.median(valid_values)
        else:  # p95 (기본값)
            idx = max(
                0,
                min(len(valid_values) - 1, int(round(0.95 * (len(valid_values) - 1)))),
            )
            return valid_values[idx]

    # 집계 방법 로드
    lat_method = mapping.get("aggregate", {}).get("latency", "p95")

    # 지연시간 집계
    latency_ms = aggregate_values(latencies, lat_method)

    # 정확도 집계 (정규화)
    accuracy = None
    if accuracies:
        normalized_accs = [
            normalize_to_01(acc)
            for acc in accuracies
            if normalize_to_01(acc) is not None
        ]
        if normalized_accs:
            accuracy = sum(normalized_accs) / len(normalized_accs)

    # 설명성 집계 (정규화)
    explainability = None
    if explainabilities:
        normalized_exps = [
            normalize_to_01(exp)
            for exp in explainabilities
            if normalize_to_01(exp) is not None
        ]
        if normalized_exps:
            explainability = sum(normalized_exps) / len(normalized_exps)

    # 실패율 집계
    failure_rate = None
    if failures:
        failure_rate = sum(f for f in failures if f is not None) / len(failures)
    elif statuses:
        # 상태에서 실패율 추정
        success_count = sum(
            1 for s in statuses if s in ("ok", "success", "true", "passed", "pass")
        )
        failure_rate = 1.0 - (success_count / len(statuses))

    # 결과 구성
    result = {
        "latency_ms": latency_ms,
        "accuracy": accuracy,
        "explainability": explainability,
        "failure_rate": failure_rate,
    }

    # 필수 지표 누락 확인
    missing = [k for k, v in result.items() if v is None]
    if missing:
        raise ValueError(f"필수 지표 누락: {missing}")

    return result


def run_objective_evaluation(
    metrics_file: str, config_file: str, preset: str, eval_script: str
) -> bool:
    """목적함수 평가 실행"""
    try:
        output_file = metrics_file.replace("metrics_", f"ab_A_{preset}_")
        cmd = f'python {eval_script} --metrics "{metrics_file}" --config "{config_file}" --weight_preset {preset} > "{output_file}"'

        result = os.system(cmd)
        if result == 0:
            logger.info(f"목적함수 평가 완료: {output_file}")
            return True
        else:
            logger.warning(f"목적함수 평가 실패: {output_file}")
            return False
    except Exception as e:
        logger.error(f"목적함수 평가 오류: {e}")
        return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="PoU 로그 → metrics_*.json (+옵션 J 계산)"
    )
    parser.add_argument("--glob", required=True, help="입력 파일 패턴")
    parser.add_argument("--mapping", required=True, help="매핑 설정 파일")
    parser.add_argument("--outdir", required=True, help="출력 디렉토리")
    parser.add_argument("--eval_config", help="목적함수 설정 파일")
    parser.add_argument("--weight_preset", default="safety_first", help="가중치 프리셋")
    parser.add_argument(
        "--evaluate_script", default="tools/evaluate_objective.py", help="평가 스크립트"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 출력 디렉토리 생성
    os.makedirs(args.outdir, exist_ok=True)

    # 매핑 설정 로드
    try:
        mapping = load_yaml(args.mapping)
    except Exception as e:
        logger.error(f"매핑 설정 로드 실패: {e}")
        sys.exit(1)

    # 입력 파일 찾기
    files = sorted(glob.glob(args.glob))
    if not files:
        logger.error("입력 파일을 찾을 수 없습니다")
        sys.exit(2)

    logger.info(f"처리할 파일 수: {len(files)}")

    produced_files = []

    for i, file_path in enumerate(files, 1):
        try:
            logger.info(f"처리 중: {file_path} ({i}/{len(files)})")

            # 파일 파싱
            rows = parse_any_file(file_path)
            if not rows:
                logger.warning(f"파일에서 데이터를 찾을 수 없음: {file_path}")
                continue

            # 지표 집계
            metrics = aggregate_metrics(rows, mapping)

            # 출력 파일 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(args.outdir, f"metrics_{timestamp}_{i:03d}.json")

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)

            produced_files.append(output_file)
            logger.info(f"지표 저장 완료: {output_file}")

            # 목적함수 평가 (옵션)
            if args.eval_config and os.path.exists(args.evaluate_script):
                run_objective_evaluation(
                    output_file,
                    args.eval_config,
                    args.weight_preset,
                    args.evaluate_script,
                )

        except Exception as e:
            logger.error(f"파일 처리 실패 {file_path}: {e}")
            continue

    # 결과 요약
    summary = {
        "processed_files": len(files),
        "produced_metrics": len(produced_files),
        "produced_files": produced_files,
        "timestamp": datetime.now().isoformat(),
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    logger.info(f"처리 완료: {len(produced_files)}개 지표 파일 생성")


if __name__ == "__main__":
    main()
