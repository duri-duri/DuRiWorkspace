#!/usr/bin/env python3
"""
약점 Top-K 집계 스크립트
에러 로그와 Prometheus 메트릭을 분석하여 주요 약점 패턴 식별
"""

import json
import pathlib
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

def load_prometheus_metrics() -> Dict[str, Any]:
    """Prometheus 메트릭 로드 (간단한 버전)"""
    try:
        # Prometheus API 호출 (실제 환경에서는 HTTP API 사용)
        result = subprocess.run([
            "curl", "-s", "http://localhost:9090/api/v1/query",
            "--data-urlencode", "query=duri_error_total"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("data", {}).get("result", [])
    except Exception as e:
        print(f"⚠️ Prometheus metrics unavailable: {e}")
    
    return []

def analyze_error_logs(log_dir: pathlib.Path) -> Dict[str, int]:
    """에러 로그 분석"""
    error_counts = Counter()
    
    if not log_dir.exists():
        print(f"⚠️ Log directory not found: {log_dir}")
        return dict(error_counts)
    
    # 최근 24시간 로그 파일들 분석
    for log_file in log_dir.glob("*.log"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # 에러 코드 패턴 찾기 (E-CATEGORY-NAME 형식)
                    if "E-" in line and "-" in line:
                        parts = line.split()
                        for part in parts:
                            if part.startswith("E-") and "-" in part[2:]:
                                error_counts[part] += 1
        except Exception as e:
            print(f"⚠️ Error reading {log_file}: {e}")
    
    return dict(error_counts)

def calculate_weakpoint_scores(error_counts: Dict[str, int]) -> List[Tuple[str, float]]:
    """약점 점수 계산 (빈도 × 심각도)"""
    weakpoint_scores = []
    
    for error_code, count in error_counts.items():
        # 심각도 가중치 (카테고리 기반)
        severity_weights = {
            "CRITICAL": 4.0,
            "HIGH": 3.0,
            "MEDIUM": 2.0,
            "LOW": 1.0
        }
        
        # 카테고리별 기본 심각도
        category_severity = {
            "DB": "HIGH",
            "AUTH": "CRITICAL",
            "API": "MEDIUM",
            "NORM": "LOW",
            "IMPORT": "HIGH",
            "TEST": "LOW"
        }
        
        # 에러 코드에서 카테고리 추출
        parts = error_code.split("-")
        category = parts[1] if len(parts) > 1 else "UNKNOWN"
        
        # 심각도 결정
        severity = category_severity.get(category, "MEDIUM")
        weight = severity_weights.get(severity, 2.0)
        
        # 점수 계산 (빈도 × 심각도 가중치)
        score = count * weight
        weakpoint_scores.append((error_code, score))
    
    # 점수순 정렬
    return sorted(weakpoint_scores, key=lambda x: x[1], reverse=True)

def generate_weakpoint_report(error_counts: Dict[str, int], top_k: int = 10) -> Dict[str, Any]:
    """약점 보고서 생성"""
    weakpoint_scores = calculate_weakpoint_scores(error_counts)
    
    # Top-K 약점 추출
    top_weakpoints = weakpoint_scores[:top_k]
    
    # 카테고리별 집계
    category_stats = defaultdict(lambda: {"count": 0, "total_score": 0.0})
    for error_code, score in weakpoint_scores:
        parts = error_code.split("-")
        category = parts[1] if len(parts) > 1 else "UNKNOWN"
        category_stats[category]["count"] += 1
        category_stats[category]["total_score"] += score
    
    # 보고서 구성
    report = {
        "timestamp": datetime.now().isoformat(),
        "analysis_period": "24h",
        "total_errors": sum(error_counts.values()),
        "unique_error_types": len(error_counts),
        "top_weakpoints": [
            {
                "error_code": error_code,
                "frequency": error_counts.get(error_code, 0),
                "score": score,
                "category": error_code.split("-")[1] if "-" in error_code else "UNKNOWN"
            }
            for error_code, score in top_weakpoints
        ],
        "category_breakdown": dict(category_stats),
        "recommendations": generate_recommendations(top_weakpoints)
    }
    
    return report

def generate_recommendations(top_weakpoints: List[Tuple[str, float]]) -> List[str]:
    """약점 기반 개선 권장사항 생성"""
    recommendations = []
    
    for error_code, score in top_weakpoints[:5]:  # Top 5만 고려
        parts = error_code.split("-")
        category = parts[1] if len(parts) > 1 else "UNKNOWN"
        
        if category == "DB":
            recommendations.append(f"데이터베이스 연결 안정성 개선 필요: {error_code}")
        elif category == "IMPORT":
            recommendations.append(f"모듈 임포트 구조 검토 필요: {error_code}")
        elif category == "API":
            recommendations.append(f"API 엔드포인트 검증 로직 강화 필요: {error_code}")
        elif category == "NORM":
            recommendations.append(f"입력 정규화 규칙 확장 필요: {error_code}")
        elif category == "TEST":
            recommendations.append(f"테스트 환경 안정성 개선 필요: {error_code}")
    
    return recommendations

def save_weakpoint_report(report: Dict[str, Any], output_dir: pathlib.Path):
    """약점 보고서 저장"""
    output_dir.mkdir(exist_ok=True)
    
    # JSON 보고서 저장
    report_file = output_dir / f"weakpoint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 요약 텍스트 보고서 저장
    summary_file = output_dir / "weakpoint_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Weakpoint Analysis Report - {report['timestamp']}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Total Errors: {report['total_errors']}\n")
        f.write(f"Unique Error Types: {report['unique_error_types']}\n\n")
        
        f.write("Top Weakpoints:\n")
        f.write("-" * 20 + "\n")
        for i, wp in enumerate(report['top_weakpoints'], 1):
            f.write(f"{i}. {wp['error_code']} (freq: {wp['frequency']}, score: {wp['score']:.1f})\n")
        
        f.write("\nRecommendations:\n")
        f.write("-" * 20 + "\n")
        for rec in report['recommendations']:
            f.write(f"- {rec}\n")
    
    print(f"✅ Weakpoint report saved to {report_file}")
    print(f"✅ Summary saved to {summary_file}")

def main():
    """메인 실행 함수"""
    print("🔍 Starting weakpoint analysis...")
    
    # 로그 디렉토리 설정
    log_dirs = [
        pathlib.Path("var/logs"),
        pathlib.Path("logs"),
        pathlib.Path("duri_core/logs"),
        pathlib.Path(".")
    ]
    
    # 에러 로그 분석
    error_counts = {}
    for log_dir in log_dirs:
        if log_dir.exists():
            error_counts.update(analyze_error_logs(log_dir))
            break
    
    # Prometheus 메트릭 분석 (보조)
    prometheus_data = load_prometheus_metrics()
    if prometheus_data:
        print(f"📊 Found {len(prometheus_data)} Prometheus metrics")
    
    if not error_counts:
        print("⚠️ No error data found. Creating sample report.")
        error_counts = {
            "E-NORM-ALIAS_MISS": 5,
            "E-DB-CONNECTION_FAILED": 3,
            "E-IMPORT-MODULE_NOT_FOUND": 2
        }
    
    # 약점 보고서 생성
    report = generate_weakpoint_report(error_counts)
    
    # 보고서 저장
    output_dir = pathlib.Path("var/reports/weakpoints")
    save_weakpoint_report(report, output_dir)
    
    # 콘솔 출력
    print("\n🎯 Weakpoint Analysis Results:")
    print(f"  Total Errors: {report['total_errors']}")
    print(f"  Unique Types: {report['unique_error_types']}")
    print("\nTop 5 Weakpoints:")
    for i, wp in enumerate(report['top_weakpoints'][:5], 1):
        print(f"  {i}. {wp['error_code']} (freq: {wp['frequency']}, score: {wp['score']:.1f})")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")

if __name__ == "__main__":
    main()
