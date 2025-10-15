#!/usr/bin/env python3
"""
DuRi 지능형 리스크 분석기 - 입력 정책 고정
"""

import math
import time
from typing import Dict, Any, List
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("risk_analyzer")

class IntelligentRiskAnalyzer:
    """지능형 리스크 분석기"""
    
    def __init__(self):
        """초기화"""
        self.analysis_count = 0
        logger.info("IntelligentRiskAnalyzer 초기화 완료")
    
    def _sanitize_value(self, value: Any, name: str) -> float:
        """값 정규화 - NaN/Inf/비정상 입력 처리"""
        try:
            x = float(value)
            if math.isnan(x) or math.isinf(x):
                logger.warning(f"{name} NaN/Inf 입력 감지, 0으로 클램프")
                return 0.0
            # 0~100 범위로 클램프
            return max(0.0, min(100.0, x))
        except (ValueError, TypeError) as e:
            logger.warning(f"{name} 비정상 입력({value!r}), 0으로 대체: {e}")
            return 0.0
    
    def analyze_risk(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """리스크 분석"""
        start_time = time.time()
        
        try:
            # 입력 검증 및 정규화
            if not metrics or not isinstance(metrics, dict):
                logger.warning("빈 또는 잘못된 메트릭 입력, 기본값 사용")
                cpu_usage = 0.0
                memory_usage = 0.0
            else:
                cpu_usage = self._sanitize_value(metrics.get("cpu_usage", 0), "cpu_usage")
                memory_usage = self._sanitize_value(metrics.get("memory_usage", 0), "memory_usage")
            
            # 개별 리스크 계산
            cpu_risk = self._calculate_cpu_risk(cpu_usage)
            memory_risk = self._calculate_memory_risk(memory_usage)
            
            # 종합 리스크 계산
            overall_score = (cpu_risk["score"] + memory_risk["score"]) / 2
            risk_level = self._determine_risk_level(overall_score)
            confidence = self._calculate_confidence(cpu_usage, memory_usage)
            
            # 권장사항 생성
            recommendations = self._generate_recommendations(cpu_risk, memory_risk)
            
            result = {
                "risk_level": risk_level,
                "confidence": confidence,
                "recommendations": recommendations,
                "cpu_risk": cpu_risk["level"],
                "memory_risk": memory_risk["level"],
                "overall_score": overall_score,
                "analysis_time_ms": (time.time() - start_time) * 1000,
                "input_values": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage
                }
            }
            
            self.analysis_count += 1
            logger.debug(f"리스크 분석 완료: {risk_level} (신뢰도: {confidence:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"리스크 분석 실패: {e}")
            return {
                "risk_level": "LOW",
                "confidence": 0.5,
                "recommendations": ["시스템 오류로 인한 분석 실패"],
                "cpu_risk": "LOW",
                "memory_risk": "LOW",
                "overall_score": 0.3,
                "error": str(e)
            }
    
    def _calculate_cpu_risk(self, cpu_usage: float) -> Dict[str, Any]:
        """CPU 리스크 계산"""
        if cpu_usage >= 90:
            return {"level": "HIGH", "score": 0.9}
        elif cpu_usage >= 70:
            return {"level": "MEDIUM", "score": 0.7}
        else:
            return {"level": "LOW", "score": 0.3}
    
    def _calculate_memory_risk(self, memory_usage: float) -> Dict[str, Any]:
        """메모리 리스크 계산"""
        if memory_usage >= 90:
            return {"level": "HIGH", "score": 0.9}
        elif memory_usage >= 70:
            return {"level": "MEDIUM", "score": 0.7}
        else:
            return {"level": "LOW", "score": 0.3}
    
    def _determine_risk_level(self, overall_score: float) -> str:
        """전체 리스크 레벨 결정"""
        if overall_score >= 0.8:
            return "HIGH"
        elif overall_score >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_confidence(self, cpu_usage: float, memory_usage: float) -> float:
        """신뢰도 계산"""
        # 극단값일수록 신뢰도 높음
        if cpu_usage >= 90 or memory_usage >= 90:
            return 0.9
        elif cpu_usage >= 70 or memory_usage >= 70:
            return 0.7
        else:
            return 0.5
    
    def _generate_recommendations(self, cpu_risk: Dict[str, Any], memory_risk: Dict[str, Any]) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        if cpu_risk["level"] == "HIGH":
            recommendations.append("CPU 사용률 긴급 조치 필요")
        elif cpu_risk["level"] == "MEDIUM":
            recommendations.append("CPU 사용률 모니터링 필요")
        
        if memory_risk["level"] == "HIGH":
            recommendations.append("메모리 사용률 긴급 조치 필요")
        elif memory_risk["level"] == "MEDIUM":
            recommendations.append("메모리 사용률 모니터링 필요")
        
        if not recommendations:
            recommendations.append("시스템 상태 양호")
        
        return recommendations
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """분석 통계 반환"""
        return {
            "total_analyses": self.analysis_count,
            "analyzer_status": "active"
        }
