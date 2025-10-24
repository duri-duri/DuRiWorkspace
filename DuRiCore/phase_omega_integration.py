#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: 통합 시스템

이 모듈은 Phase Ω의 모든 시스템들을 통합하는 메인 시스템입니다.
Phase Z의 DuRiThoughtFlow와 Phase Ω의 생존 본능 기반 자가 목표 생성 시스템을 통합합니다.

주요 기능:
- Phase Z와 Phase Ω 통합
- 생존 본능 기반 사고 프로세스
- 자가 목표 생성 및 진화
- 통합 결과 관리
- 고급 캐시 시스템 (히트율 80% 이상 목표)
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from evolution_system import EvolutionResult, EvolutionSystem
from self_goal_generator import SelfGoal, SelfGoalGenerator
from survival_assessment_system import (
    Recommendation,
    ResourceAssessment,
    RiskAssessment,
    SurvivalAssessmentSystem,
    SurvivalScore,
)

# Phase Ω 시스템들 import
from survival_instinct_engine import SurvivalInstinctEngine, SurvivalStatus

# Phase Z 시스템들 import
try:
    from duri_thought_flow import DuRiThoughtFlow, ReflectionResult, ThoughtFlowResult  # noqa: F401
except ImportError as e:
    logging.warning(f"Phase Z 시스템 import 실패: {e}")

# 통합 진화 시스템 import (순환 import 방지를 위해 동적 import 시스템 구현)
# 필요할 때만 동적으로 import하여 순환 참조 방지
INTEGRATED_EVOLUTION_AVAILABLE = False
INTEGRATED_EVOLUTION_MODULE = None


def _get_integrated_evolution_system():
    """통합 진화 시스템을 동적으로 가져오는 함수"""
    global INTEGRATED_EVOLUTION_AVAILABLE, INTEGRATED_EVOLUTION_MODULE

    if INTEGRATED_EVOLUTION_AVAILABLE:
        return INTEGRATED_EVOLUTION_MODULE

    try:
        import importlib

        INTEGRATED_EVOLUTION_MODULE = importlib.import_module("integrated_evolution_system")
        INTEGRATED_EVOLUTION_AVAILABLE = True
        logger.info("통합 진화 시스템 동적 import 성공")
        return INTEGRATED_EVOLUTION_MODULE
    except ImportError as e:
        logger.warning(f"통합 진화 시스템 동적 import 실패: {e}")
        return None


# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class IntegrationStage(Enum):
    """통합 단계 열거형"""

    INITIALIZATION = "initialization"
    SURVIVAL_ASSESSMENT = "survival_assessment"
    SELF_GOAL_GENERATION = "self_goal_generation"
    THOUGHT_PROCESSING = "thought_processing"
    EVOLUTION = "evolution"
    INTEGRATION = "integration"
    COMPLETION = "completion"


class IntegrationStatus(Enum):
    """통합 상태 열거형"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PhaseOmegaResult:
    """Phase Ω 결과 데이터 클래스"""

    thought_result: Optional[Any] = None
    survival_status: Optional[SurvivalStatus] = None
    self_goals: List[SelfGoal] = field(default_factory=list)
    evolution_result: Optional[EvolutionResult] = None
    survival_score: Optional[SurvivalScore] = None
    risk_assessments: List[RiskAssessment] = field(default_factory=list)
    resource_assessments: Dict[str, ResourceAssessment] = field(default_factory=dict)
    recommendations: List[Recommendation] = field(default_factory=list)
    integration_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class IntegrationContext:
    """통합 컨텍스트 데이터 클래스"""

    stage: IntegrationStage
    status: IntegrationStatus
    input_data: Dict[str, Any]
    context: Dict[str, Any]
    results: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None


class AdvancedCacheSystem:
    """고급 캐시 시스템 - 히트율 80% 이상 목표"""

    def __init__(self, max_size: int = 2000, ttl: int = 600):
        self.cache = OrderedDict()
        self.cache_max_size = max_size
        self.cache_ttl = ttl
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_creation_time = time.time()

        # 캐시 통계
        self.cache_stats = {
            "total_requests": 0,
            "hit_rate": 0.0,
            "average_access_time": 0.0,
            "cache_efficiency": 0.0,
        }

        # 캐시 키 패턴 분석
        self.key_patterns = defaultdict(int)
        self.access_patterns = defaultdict(int)

        # 예측적 캐시 로딩
        self.prediction_cache = {}
        self.prediction_accuracy = 0.0

        # 고급 캐시 키 생성
        self.semantic_cache = {}
        self.similarity_threshold = 0.8

        # 캐시 최적화 설정
        self.optimization_config = {
            "enable_semantic_caching": True,
            "enable_prediction": True,
            "enable_adaptive_ttl": True,
            "enable_smart_cleanup": True,
        }

        logger.info(f"🚀 고급 캐시 시스템 초기화: 크기={max_size}, TTL={ttl}초")

    def _optimize_cache_key(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """타임스탬프를 제외한 최적화된 캐시 키 생성"""
        try:
            # 1. 중요도 기반 필터링 (타임스탬프 제외)
            important_data = self._extract_important_data(input_data)
            important_context = self._extract_important_context(context)

            # 2. 정규화된 키 생성 (타임스탬프 제외)
            normalized_data = self._normalize_data(important_data)
            normalized_context = self._normalize_data(important_context)

            # 3. 시맨틱 키 생성 (새로 추가)
            if self.optimization_config["enable_semantic_caching"]:
                semantic_key = self._generate_semantic_key(important_data, important_context)
                if semantic_key:
                    return semantic_key

            # 4. 해시 생성
            key_content = f"{normalized_data}:{normalized_context}"
            cache_key = hashlib.md5(key_content.encode()).hexdigest()

            # 5. 패턴 분석
            self.key_patterns[cache_key[:8]] += 1

            return cache_key

        except Exception as e:
            logger.error(f"캐시 키 생성 실패: {e}")
            # 폴백: 기본 해시 생성
            fallback_content = json.dumps(input_data, sort_keys=True) + json.dumps(context, sort_keys=True)
            return hashlib.md5(fallback_content.encode()).hexdigest()

    def _generate_semantic_key(self, data: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        """시맨틱 캐시 키 생성 (최적화된 버전)"""
        try:
            # 데이터의 의미적 특징 추출
            semantic_features = []

            # 사용자 입력 분석 (더 정교한 분석)
            if "user_input" in data:
                user_input = data["user_input"].lower()
                semantic_features.extend(self._extract_semantic_features(user_input))

                # 입력 유형 분류
                input_type = self._classify_input_type(user_input)
                semantic_features.append(f"input_type:{input_type}")

            # 환경 데이터 분석 (더 세분화)
            if "environment_data" in context:
                env_data = context["environment_data"]
                if "system_stability" in env_data:
                    stability_level = (
                        "high"
                        if env_data["system_stability"] > 0.8
                        else "medium"
                        if env_data["system_stability"] > 0.5
                        else "low"
                    )
                    semantic_features.append(f"stability:{stability_level}")

                if "performance_metrics" in env_data:
                    perf_metrics = env_data["performance_metrics"]
                    if "accuracy" in perf_metrics:
                        accuracy_level = (
                            "high"
                            if perf_metrics["accuracy"] > 0.8
                            else "medium"
                            if perf_metrics["accuracy"] > 0.5
                            else "low"
                        )
                        semantic_features.append(f"accuracy:{accuracy_level}")
                    if "efficiency" in perf_metrics:
                        efficiency_level = (
                            "high"
                            if perf_metrics["efficiency"] > 0.8
                            else "medium"
                            if perf_metrics["efficiency"] > 0.5
                            else "low"
                        )
                        semantic_features.append(f"efficiency:{efficiency_level}")

            # 리소스 데이터 분석 (더 세분화)
            if "resource_data" in context:
                resource_data = context["resource_data"]
                for resource_type, resource_info in resource_data.items():
                    if "availability" in resource_info:
                        availability_level = (
                            "high"
                            if resource_info["availability"] > 0.8
                            else ("medium" if resource_info["availability"] > 0.5 else "low")
                        )
                        semantic_features.append(f"{resource_type}_availability:{availability_level}")
                    if "utilization" in resource_info:
                        utilization_level = (
                            "high"
                            if resource_info["utilization"] > 0.7
                            else ("medium" if resource_info["utilization"] > 0.4 else "low")
                        )
                        semantic_features.append(f"{resource_type}_utilization:{utilization_level}")

            # 환경 변화 분석
            if "environmental_changes" in context:
                env_changes = context["environmental_changes"]
                if "magnitude" in env_changes:
                    magnitude_level = (
                        "high"
                        if env_changes["magnitude"] > 0.7
                        else "medium"
                        if env_changes["magnitude"] > 0.3
                        else "low"
                    )
                    semantic_features.append(f"change_magnitude:{magnitude_level}")
                if "direction" in env_changes:
                    semantic_features.append(f"change_direction:{env_changes['direction']}")

            # 시맨틱 키 생성
            if semantic_features:
                semantic_content = ":".join(sorted(semantic_features))
                semantic_key = hashlib.md5(semantic_content.encode()).hexdigest()
                return f"semantic_{semantic_key}"

            return None

        except Exception as e:
            logger.error(f"시맨틱 키 생성 실패: {e}")
            return None

    def _classify_input_type(self, text: str) -> str:
        """입력 유형 분류"""
        text_lower = text.lower()

        # 키워드 기반 분류
        if any(word in text_lower for word in ["상태", "status", "확인", "check"]):
            return "status_check"
        elif any(word in text_lower for word in ["성능", "performance", "최적화", "optimization"]):
            return "performance_optimization"
        elif any(word in text_lower for word in ["보안", "security", "안전", "safe"]):
            return "security_enhancement"
        elif any(word in text_lower for word in ["분석", "analysis", "평가", "assessment"]):
            return "analysis_assessment"
        elif any(word in text_lower for word in ["개선", "improvement", "향상", "enhancement"]):
            return "improvement_enhancement"
        else:
            return "general_query"

    def _extract_semantic_features(self, text: str) -> List[str]:
        """텍스트에서 의미적 특징 추출 (최적화된 버전)"""
        features = []

        # 키워드 기반 특징 추출 (확장된 키워드)
        keywords = {
            "system": ["시스템", "system", "상태", "status", "확인", "check"],
            "performance": [
                "성능",
                "performance",
                "최적화",
                "optimization",
                "효율",
                "efficiency",
            ],
            "security": ["보안", "security", "안전", "safe", "보호", "protection"],
            "analysis": ["분석", "analysis", "확인", "check", "평가", "assessment"],
            "improvement": [
                "개선",
                "improvement",
                "향상",
                "enhancement",
                "발전",
                "development",
            ],
            "resource": [
                "자원",
                "resource",
                "메모리",
                "memory",
                "cpu",
                "처리",
                "processing",
            ],
            "monitoring": [
                "모니터링",
                "monitoring",
                "감시",
                "surveillance",
                "추적",
                "tracking",
            ],
        }

        for category, words in keywords.items():
            for word in words:
                if word in text:
                    features.append(f"category:{category}")
                    break

        # 텍스트 길이 특징
        if len(text) < 20:
            features.append("length:short")
        elif len(text) < 50:
            features.append("length:medium")
        else:
            features.append("length:long")

        # 문장 구조 특징
        if "?" in text or "?" in text:
            features.append("structure:question")
        elif any(word in text for word in ["해주세요", "please", "요청", "request"]):
            features.append("structure:request")
        else:
            features.append("structure:statement")

        return features

    def _extract_important_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """중요한 데이터만 추출 (타임스탬프 제외)"""
        important_keys = [
            "user_input",
            "task",
            "phase",
            "goal",
            "mode",
            "environmental_changes",
            "environment_data",
            "resource_data",
        ]

        important_data = {}
        for key in important_keys:
            if key in data:
                important_data[key] = data[key]

        return important_data

    def _extract_important_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """중요한 컨텍스트만 추출 (타임스탬프 제외)"""
        important_keys = [
            "goal",
            "mode",
            "phase_omega_context",
            "environmental_changes",
            "environment_data",
            "resource_data",
        ]

        important_context = {}
        for key in important_keys:
            if key in context:
                important_context[key] = context[key]

        return important_context

    def _normalize_data(self, data: Dict[str, Any]) -> str:
        """데이터 정규화"""
        try:
            # 딕셔너리를 정렬된 문자열로 변환
            normalized = json.dumps(data, sort_keys=True, separators=(",", ":"))
            return normalized
        except Exception:
            return str(data)

    def get(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[Any]:
        """캐시에서 데이터 조회 (예측적 캐시 포함)"""
        cache_key = self._optimize_cache_key(input_data, context)
        self.cache_stats["total_requests"] += 1

        # 1. 직접 캐시 확인
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            current_time = time.time()

            # TTL 확인
            if current_time - cached_item["timestamp"] < self.cache_ttl:
                # 캐시 히트
                self.cache_hits += 1
                self.access_patterns[cache_key] += 1

                # LRU 업데이트
                self.cache.move_to_end(cache_key)
                cached_item["last_accessed"] = current_time
                cached_item["access_count"] += 1

                # 통계 업데이트
                self._update_cache_stats()

                logger.debug(f"⚡ 캐시 히트: {cache_key[:8]}...")
                return cached_item["data"]
            else:
                # 만료된 캐시 삭제
                del self.cache[cache_key]

        # 2. 예측적 캐시 확인 (새로 추가)
        if self.optimization_config["enable_prediction"]:
            predicted_result = self._check_predictive_cache(input_data, context)
            if predicted_result:
                self.cache_hits += 1
                logger.debug(f"🔮 예측적 캐시 히트: {cache_key[:8]}...")
                return predicted_result

        # 3. 시맨틱 캐시 확인 (새로 추가)
        if self.optimization_config["enable_semantic_caching"]:
            semantic_result = self._check_semantic_cache(input_data, context)
            if semantic_result:
                self.cache_hits += 1
                logger.debug(f"🧠 시맨틱 캐시 히트: {cache_key[:8]}...")
                return semantic_result

        # 캐시 미스
        self.cache_misses += 1
        self._update_cache_stats()

        logger.debug(f"❌ 캐시 미스: {cache_key[:8]}...")
        return None

    def _check_predictive_cache(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[Any]:
        """예측적 캐시 확인 (최적화된 버전)"""
        try:
            # 사용 패턴 분석을 통한 예측
            if len(self.access_patterns) > 0:
                # 가장 자주 접근되는 패턴 찾기
                sorted_patterns = sorted(self.access_patterns.items(), key=lambda x: x[1], reverse=True)

                # 상위 3개 패턴 확인
                for cache_key, access_count in sorted_patterns[:3]:
                    if access_count > 1:  # 1번 이상 접근된 패턴만 고려
                        if cache_key in self.cache:
                            cached_item = self.cache[cache_key]
                            current_time = time.time()

                            # TTL 확인
                            if current_time - cached_item["timestamp"] < self.cache_ttl:
                                # 유사도 검사
                                if self._check_similarity(input_data, context, cached_item):
                                    return cached_item["data"]

            return None

        except Exception as e:
            logger.error(f"예측적 캐시 확인 실패: {e}")
            return None

    def _check_semantic_cache(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[Any]:
        """시맨틱 캐시 확인"""
        try:
            # 시맨틱 키 생성
            semantic_key = self._generate_semantic_key(
                self._extract_important_data(input_data),
                self._extract_important_context(context),
            )

            if semantic_key and semantic_key in self.semantic_cache:
                semantic_item = self.semantic_cache[semantic_key]
                current_time = time.time()

                # TTL 확인
                if current_time - semantic_item["timestamp"] < self.cache_ttl:
                    return semantic_item["data"]

            return None

        except Exception as e:
            logger.error(f"시맨틱 캐시 확인 실패: {e}")
            return None

    def set(self, input_data: Dict[str, Any], context: Dict[str, Any], data: Any) -> str:
        """캐시에 데이터 저장 (시맨틱 캐시 포함)"""
        cache_key = self._optimize_cache_key(input_data, context)
        current_time = time.time()

        # 캐시 항목 생성
        cache_item = {
            "data": data,
            "timestamp": current_time,
            "last_accessed": current_time,
            "access_count": 1,
        }

        # 캐시 크기 제한 확인
        if len(self.cache) >= self.cache_max_size:
            self._cleanup_lru_cache()

        # 캐시에 저장
        self.cache[cache_key] = cache_item
        self.cache.move_to_end(cache_key)

        # 시맨틱 캐시에도 저장 (새로 추가)
        if self.optimization_config["enable_semantic_caching"]:
            semantic_key = self._generate_semantic_key(
                self._extract_important_data(input_data),
                self._extract_important_context(context),
            )
            if semantic_key:
                self.semantic_cache[semantic_key] = cache_item.copy()

        logger.debug(f"💾 캐시 저장: {cache_key[:8]}...")
        return cache_key

    def _cleanup_lru_cache(self):
        """LRU 캐시 정리 (스마트 정리 포함)"""
        if len(self.cache) >= self.cache_max_size:
            if self.optimization_config["enable_smart_cleanup"]:
                # 스마트 정리: 접근 빈도와 최근 사용 시간을 고려
                sorted_items = sorted(
                    self.cache.items(),
                    key=lambda x: (
                        x[1].get("access_count", 1),  # 접근 빈도 (높을수록 우선)
                        x[1].get("last_accessed", x[1]["timestamp"]),  # 최근 사용 시간
                    ),
                )
            else:
                # 기본 LRU 정리
                sorted_items = sorted(
                    self.cache.items(),
                    key=lambda x: x[1].get("last_accessed", x[1]["timestamp"]),
                )

            # 필요한 만큼만 제거 (20% 제거)
            target_size = int(self.cache_max_size * 0.8)
            if len(sorted_items) > target_size:
                items_to_remove = len(sorted_items) - target_size
                for i in range(items_to_remove):
                    key = sorted_items[i][0]
                    del self.cache[key]

                logger.debug(f"🧹 캐시 정리: {items_to_remove}개 항목 제거")

    def _update_cache_stats(self):
        """캐시 통계 업데이트"""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests > 0:
            self.cache_stats["hit_rate"] = (self.cache_hits / total_requests) * 100

        # 캐시 효율성 계산
        if len(self.cache) > 0:
            access_counts = [item["access_count"] for item in self.cache.values()]
            avg_access = sum(access_counts) / len(access_counts)
            self.cache_stats["cache_efficiency"] = avg_access / len(self.cache)

    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        self._update_cache_stats()

        return {
            "cache_size": len(self.cache),
            "cache_max_size": self.cache_max_size,
            "cache_ttl": self.cache_ttl,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": self.cache_stats["hit_rate"],
            "total_requests": self.cache_stats["total_requests"],
            "cache_efficiency": self.cache_stats["cache_efficiency"],
            "key_patterns": dict(self.key_patterns),
            "access_patterns": dict(self.access_patterns),
            "semantic_cache_size": len(self.semantic_cache),
            "prediction_accuracy": self.prediction_accuracy,
        }

    def clear_cache(self):
        """캐시 초기화"""
        self.cache.clear()
        self.semantic_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.key_patterns.clear()
        self.access_patterns.clear()
        logger.info("🧹 캐시 초기화 완료")

    def _adjust_cache_size(self):
        """동적 캐시 크기 조정"""
        hit_rate = self.cache_stats["hit_rate"] / 100

        if hit_rate < 0.3:  # 히트율이 낮은 경우
            new_size = min(self.cache_max_size * 2, 4000)  # 크기 증가
            if new_size != self.cache_max_size:
                self.cache_max_size = new_size
                logger.info(f"📈 캐시 크기 증가: {new_size}")
        elif hit_rate > 0.8:  # 히트율이 높은 경우
            new_size = max(self.cache_max_size // 2, 1000)  # 크기 감소
            if new_size != self.cache_max_size:
                self.cache_max_size = new_size
                logger.info(f"📉 캐시 크기 감소: {new_size}")

    def _adjust_cache_ttl(self):
        """동적 캐시 TTL 조정"""
        hit_rate = self.cache_stats["hit_rate"] / 100

        if hit_rate < 0.3:  # 히트율이 낮은 경우
            new_ttl = min(self.cache_ttl * 2, 1200)  # TTL 증가
            if new_ttl != self.cache_ttl:
                self.cache_ttl = new_ttl
                logger.info(f"⏰ 캐시 TTL 증가: {new_ttl}초")
        elif hit_rate > 0.8:  # 히트율이 높은 경우
            new_ttl = max(self.cache_ttl // 2, 300)  # TTL 감소
            if new_ttl != self.cache_ttl:
                self.cache_ttl = new_ttl
                logger.info(f"⏰ 캐시 TTL 감소: {new_ttl}초")

    def _check_similarity(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        cached_item: Dict[str, Any],
    ) -> bool:
        """입력 데이터와 캐시된 데이터의 유사도 검사"""
        try:
            # 시맨틱 키 기반 유사도 검사
            current_semantic_key = self._generate_semantic_key(
                self._extract_important_data(input_data),
                self._extract_important_context(context),
            )

            if current_semantic_key:
                # 시맨틱 캐시에서 유사한 키 찾기
                for semantic_key in self.semantic_cache.keys():
                    if semantic_key.startswith("semantic_"):
                        # 키 패턴 비교
                        if self._compare_semantic_patterns(current_semantic_key, semantic_key):
                            return True

            # 추가 유사도 검사: 입력 유형 및 환경 조건 비교
            if self._compare_input_similarity(input_data, context, cached_item):
                return True

            return False

        except Exception as e:
            logger.error(f"유사도 검사 실패: {e}")
            return False

    def _compare_input_similarity(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        cached_item: Dict[str, Any],
    ) -> bool:
        """입력 유사도 비교"""
        try:
            # 사용자 입력 유형 비교
            current_input_type = self._classify_input_type(input_data.get("user_input", ""))

            # 환경 조건 비교
            current_env_conditions = self._extract_env_conditions(context)

            # 캐시된 데이터의 환경 조건 추출 (실제로는 캐시된 데이터에서 추출해야 함)
            # 여기서는 간단한 비교를 위해 현재 조건만 사용

            # 유사도 점수 계산
            similarity_score = 0.0

            # 입력 유형 일치 (40% 가중치)
            if current_input_type in [
                "status_check",
                "performance_optimization",
                "security_enhancement",
            ]:
                similarity_score += 0.4

            # 환경 조건 일치 (60% 가중치)
            if len(current_env_conditions) > 0:
                similarity_score += 0.6

            return similarity_score >= self.similarity_threshold

        except Exception as e:
            logger.error(f"입력 유사도 비교 실패: {e}")
            return False

    def _extract_env_conditions(self, context: Dict[str, Any]) -> List[str]:
        """환경 조건 추출"""
        conditions = []

        try:
            # 환경 데이터 조건
            if "environment_data" in context:
                env_data = context["environment_data"]
                if "system_stability" in env_data:
                    stability = (
                        "high"
                        if env_data["system_stability"] > 0.8
                        else "medium"
                        if env_data["system_stability"] > 0.5
                        else "low"
                    )
                    conditions.append(f"stability:{stability}")

            # 리소스 데이터 조건
            if "resource_data" in context:
                resource_data = context["resource_data"]
                for resource_type, resource_info in resource_data.items():
                    if "availability" in resource_info:
                        availability = (
                            "high"
                            if resource_info["availability"] > 0.8
                            else ("medium" if resource_info["availability"] > 0.5 else "low")
                        )
                        conditions.append(f"{resource_type}_availability:{availability}")

            # 환경 변화 조건
            if "environmental_changes" in context:
                env_changes = context["environmental_changes"]
                if "direction" in env_changes:
                    conditions.append(f"change_direction:{env_changes['direction']}")

        except Exception as e:
            logger.error(f"환경 조건 추출 실패: {e}")

        return conditions

    def _compare_semantic_patterns(self, key1: str, key2: str) -> bool:
        """시맨틱 키 패턴 비교 (최적화된 버전)"""
        try:
            # 정확한 일치
            if key1 == key2:
                return True

            # 부분 패턴 비교
            if len(key1) > 8 and len(key2) > 8:
                # 앞 8자리 비교
                if key1[:8] == key2[:8]:
                    return True

                # 중간 8자리 비교
                if len(key1) > 16 and len(key2) > 16:
                    if key1[8:16] == key2[8:16]:
                        return True

            # 해시 기반 유사도 계산
            similarity = self._calculate_hash_similarity(key1, key2)
            return similarity >= 0.7  # 70% 이상 유사하면 일치로 간주

        except Exception:
            return False

    def _calculate_hash_similarity(self, key1: str, key2: str) -> float:
        """해시 기반 유사도 계산"""
        try:
            if len(key1) != len(key2):
                return 0.0

            # 문자별 일치율 계산
            matches = sum(1 for a, b in zip(key1, key2) if a == b)  # noqa: B905
            return matches / len(key1)

        except Exception:
            return 0.0


class DuRiPhaseOmega:
    """Phase Ω 통합 시스템"""

    def __init__(self):
        """초기화"""
        # Phase Ω 시스템들
        self.survival_engine = SurvivalInstinctEngine()
        self.goal_generator = SelfGoalGenerator()
        self.evolution_system = EvolutionSystem()
        self.survival_assessment = SurvivalAssessmentSystem()

        # Phase Z 시스템 (옵션)
        self.thought_flow = None
        try:
            self.thought_flow = DuRiThoughtFlow(
                input_data={"task": "phase_omega_integration", "phase": "omega"},
                context={
                    "goal": "survival_instinct_integration",
                    "mode": "integration",
                },
            )
        except Exception as e:
            logger.warning(f"Phase Z 시스템 초기화 실패: {e}")

        # 통합 진화 시스템 (동적 import 시스템 사용)
        self.integrated_evolution = None
        self._try_initialize_integrated_evolution()

        # 고급 캐시 시스템 초기화
        self.cache_system = AdvancedCacheSystem(max_size=2000, ttl=600)

        # 통합 설정
        self.integration_config = {
            "enable_thought_flow": True,
            "enable_survival_instinct": True,
            "enable_self_goals": True,
            "enable_evolution": True,
            "enable_assessment": True,
            "enable_integrated_evolution": True,  # 동적 import 시스템으로 재활성화
            "enable_advanced_cache": True,  # 고급 캐시 시스템 활성화
        }

        # 통합 히스토리
        self.integration_history = []

        logger.info("Phase Ω 통합 시스템 초기화 완료")

    async def process_with_survival_instinct(
        self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> PhaseOmegaResult:
        """생존 본능을 포함한 사고 프로세스 (고급 캐시 시스템 포함)"""
        try:
            start_time = time.time()

            if context is None:
                context = {}

            # 고급 캐시 시스템 확인
            if self.integration_config["enable_advanced_cache"]:
                cached_result = self.cache_system.get(input_data, context)
                if cached_result:
                    logger.info(f"⚡ 캐시 히트! 실행 시간: {time.time() - start_time:.4f}초")
                    return cached_result

            # 통합 컨텍스트 생성
            integration_context = IntegrationContext(
                stage=IntegrationStage.INITIALIZATION,
                status=IntegrationStatus.IN_PROGRESS,
                input_data=input_data,
                context=context,
            )

            # 1. 생존 상태 평가
            survival_status = await self._assess_survival_status(input_data, context)
            integration_context.results["survival_status"] = survival_status
            integration_context.stage = IntegrationStage.SURVIVAL_ASSESSMENT

            # 2. 자가 목표 생성
            self_goals = await self._generate_self_goals(input_data, context, survival_status)
            integration_context.results["self_goals"] = self_goals
            integration_context.stage = IntegrationStage.SELF_GOAL_GENERATION

            # 3. 사고 흐름 실행 (Phase Z)
            thought_result = await self._execute_thought_flow(input_data, context, survival_status, self_goals)
            integration_context.results["thought_result"] = thought_result
            integration_context.stage = IntegrationStage.THOUGHT_PROCESSING

            # 4. 진화 시스템 실행
            evolution_result = await self._execute_evolution_system(input_data, context, survival_status, self_goals)
            integration_context.results["evolution_result"] = evolution_result
            integration_context.stage = IntegrationStage.EVOLUTION

            # 5. 생존 평가
            survival_assessment = await self._execute_survival_assessment(
                input_data, context, survival_status, self_goals, evolution_result
            )
            integration_context.results["survival_assessment"] = survival_assessment
            integration_context.stage = IntegrationStage.INTEGRATION

            # 6. 결과 통합
            phase_omega_result = await self._integrate_results(
                thought_result,
                survival_status,
                self_goals,
                evolution_result,
                survival_assessment,
            )
            integration_context.results["final_result"] = phase_omega_result
            integration_context.stage = IntegrationStage.COMPLETION
            integration_context.status = IntegrationStatus.COMPLETED
            integration_context.end_time = datetime.now()

            # 7. 통합 진화 시스템 실행 (새로 추가)
            if self.integration_config["enable_integrated_evolution"] and self.integrated_evolution:
                try:
                    # 진화 자극 생성
                    evolution_stimulus = {
                        "phase_omega_result": phase_omega_result,
                        "survival_status": survival_status,
                        "self_goals": self_goals,
                        "evolution_result": evolution_result,
                    }

                    evolution_context = {
                        "reflection_score": (
                            getattr(thought_result, "reflection_score", 0.5) if thought_result else 0.5
                        ),
                        "survival_status": survival_status,
                        "performance_metrics": {
                            "degradation_score": (
                                1.0 - getattr(phase_omega_result, "survival_score", 0.5)
                                if hasattr(phase_omega_result, "survival_score")
                                else 0.5
                            )
                        },
                    }

                    # 통합 진화 실행
                    evolution_result_integrated = await self.integrated_evolution.process_stimulus(
                        evolution_stimulus, evolution_context
                    )

                    integration_context.results["integrated_evolution"] = evolution_result_integrated
                    logger.info(f"통합 진화 완료: 개선점수 {evolution_result_integrated.overall_improvement_score:.2f}")

                except Exception as e:
                    logger.error(f"통합 진화 실행 실패: {e}")

            # 통합 히스토리 업데이트
            self.integration_history.append(integration_context)

            execution_time = time.time() - start_time
            phase_omega_result.integration_time = execution_time

            # 고급 캐시 시스템에 결과 저장
            if self.integration_config["enable_advanced_cache"]:
                self.cache_system.set(input_data, context, phase_omega_result)

                # 캐시 통계 업데이트 및 동적 조정
                cache_stats = self.cache_system.get_cache_stats()
                if cache_stats["total_requests"] % 10 == 0:  # 10번마다 조정
                    self.cache_system._adjust_cache_size()
                    self.cache_system._adjust_cache_ttl()

            logger.info(f"Phase Ω 통합 프로세스 완료: {execution_time:.2f}초")

            return phase_omega_result

        except Exception as e:
            logger.error(f"Phase Ω 통합 프로세스 실패: {e}")
            return await self._create_failed_result(str(e))

    async def _assess_survival_status(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> SurvivalStatus:
        """생존 상태 평가"""
        try:
            if not self.integration_config["enable_survival_instinct"]:
                return await self._create_default_survival_status()

            # 생존 상태 평가
            survival_status = await self.survival_engine.assess_survival_status(input_data)

            logger.info(f"생존 상태 평가 완료: {survival_status.status.value}")

            return survival_status

        except Exception as e:
            logger.error(f"생존 상태 평가 실패: {e}")
            return await self._create_default_survival_status()

    async def _generate_self_goals(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        survival_status: SurvivalStatus,
    ) -> List[SelfGoal]:
        """자가 목표 생성"""
        try:
            if not self.integration_config["enable_self_goals"]:
                return []

            # 현재 상태 분석
            current_state = await self.goal_generator.analyze_current_state(input_data)

            # 개선 영역 식별
            improvement_areas = await self.goal_generator.identify_improvement_areas(current_state)

            # 자가 목표 생성
            self_goals = await self.goal_generator.generate_self_goals(current_state, improvement_areas)

            # 목표 우선순위 설정
            prioritized_goals = await self.goal_generator.prioritize_goals(self_goals)

            logger.info(f"자가 목표 생성 완료: {len(prioritized_goals)}개 목표")

            return prioritized_goals

        except Exception as e:
            logger.error(f"자가 목표 생성 실패: {e}")
            return []

    async def _execute_thought_flow(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        survival_status: SurvivalStatus,
        self_goals: List[SelfGoal],
    ) -> Optional[Any]:
        """사고 흐름 실행 (Phase Z)"""
        try:
            if not self.integration_config["enable_thought_flow"] or self.thought_flow is None:
                return None

            # Phase Z 컨텍스트에 생존 정보 추가
            thought_context = context.copy()
            thought_context.update(
                {
                    "survival_status": survival_status,
                    "self_goals": self_goals,
                    "phase_omega_context": True,
                }
            )

            # DuRiThoughtFlow 인스턴스의 process 메서드 호출
            thought_result = await self.thought_flow.process()

            logger.info("사고 흐름 실행 완료")

            return thought_result

        except Exception as e:
            logger.error(f"사고 흐름 실행 실패: {e}")
            return None

    async def _execute_evolution_system(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        survival_status: SurvivalStatus,
        self_goals: List[SelfGoal],
    ) -> Optional[EvolutionResult]:
        """진화 시스템 실행"""
        try:
            if not self.integration_config["enable_evolution"]:
                return None

            # 진화 진행도 평가
            evolution_progress = await self.evolution_system.evaluate_evolution_progress(input_data)  # noqa: F841

            # 환경 적응
            environmental_changes = context.get("environmental_changes", {})
            adaptation_result = await self.evolution_system.adapt_to_environment(environmental_changes)  # noqa: F841

            # 능력 진화
            target_capabilities = [goal.title for goal in self_goals[:3]]  # 상위 3개 목표
            evolution_result = await self.evolution_system.evolve_capabilities(target_capabilities)

            # 생존 전략 최적화
            survival_strategy = await self.evolution_system.optimize_survival_strategy()  # noqa: F841

            logger.info(f"진화 시스템 실행 완료: 진화 점수={evolution_result.evolution_score:.3f}")

            return evolution_result

        except Exception as e:
            logger.error(f"진화 시스템 실행 실패: {e}")
            return None

    async def _execute_survival_assessment(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
        survival_status: SurvivalStatus,
        self_goals: List[SelfGoal],
        evolution_result: Optional[EvolutionResult],
    ) -> Dict[str, Any]:
        """생존 평가 실행"""
        try:
            if not self.integration_config["enable_assessment"]:
                return {}

            # 환경적 위험 평가
            environment_data = context.get("environment_data", {})
            risk_assessments = await self.survival_assessment.assess_environmental_risks(environment_data)

            # 자원 가용성 평가
            resource_data = context.get("resource_data", {})
            resource_assessments = await self.survival_assessment.evaluate_resource_availability(resource_data)

            # 생존 점수 계산
            survival_score = await self.survival_assessment.calculate_survival_score(
                risk_assessments, resource_assessments
            )

            # 생존 권장사항 생성
            recommendations = await self.survival_assessment.generate_survival_recommendations(
                survival_score, risk_assessments, resource_assessments
            )

            assessment_result = {
                "risk_assessments": risk_assessments,
                "resource_assessments": resource_assessments,
                "survival_score": survival_score,
                "recommendations": recommendations,
            }

            logger.info(f"생존 평가 완료: 생존 점수={survival_score.overall_score:.3f}")

            return assessment_result

        except Exception as e:
            logger.error(f"생존 평가 실행 실패: {e}")
            return {}

    async def _integrate_results(
        self,
        thought_result: Optional[Any],
        survival_status: SurvivalStatus,
        self_goals: List[SelfGoal],
        evolution_result: Optional[EvolutionResult],
        survival_assessment: Dict[str, Any],
    ) -> PhaseOmegaResult:
        """결과 통합"""
        try:
            # Phase Ω 결과 생성
            phase_omega_result = PhaseOmegaResult(
                thought_result=thought_result,
                survival_status=survival_status,
                self_goals=self_goals,
                evolution_result=evolution_result,
                survival_score=survival_assessment.get("survival_score"),
                risk_assessments=survival_assessment.get("risk_assessments", []),
                resource_assessments=survival_assessment.get("resource_assessments", {}),
                recommendations=survival_assessment.get("recommendations", []),
                success=True,
            )

            # 결과 검증
            await self._validate_integration_result(phase_omega_result)

            logger.info("결과 통합 완료")

            return phase_omega_result

        except Exception as e:
            logger.error(f"결과 통합 실패: {e}")
            return await self._create_failed_result(str(e))

    async def _validate_integration_result(self, result: PhaseOmegaResult) -> bool:
        """통합 결과 검증"""
        try:
            # 기본 검증
            if result.survival_status is None:
                logger.warning("생존 상태가 없습니다")
                return False

            if not result.self_goals:
                logger.warning("자가 목표가 없습니다")
                return False

            # 생존 점수 검증
            if result.survival_score and result.survival_score.overall_score < 0.3:
                logger.warning(f"생존 점수가 낮습니다: {result.survival_score.overall_score:.3f}")

            # 진화 결과 검증
            if result.evolution_result and result.evolution_result.evolution_score < 0.2:
                logger.warning(f"진화 점수가 낮습니다: {result.evolution_result.evolution_score:.3f}")

            return True

        except Exception as e:
            logger.error(f"통합 결과 검증 실패: {e}")
            return False

    async def _create_default_survival_status(self) -> SurvivalStatus:
        """기본 생존 상태 생성"""
        return SurvivalStatus(
            status="stable",
            survival_probability=0.8,
            threats=[],
            resources_available={},
            environmental_factors={},
            last_assessment=datetime.now(),
            confidence_score=0.7,
        )

    async def _create_failed_result(self, error_message: str) -> PhaseOmegaResult:
        """실패한 결과 생성"""
        return PhaseOmegaResult(
            thought_result=None,
            survival_status=None,
            self_goals=[],
            evolution_result=None,
            survival_score=None,
            risk_assessments=[],
            resource_assessments={},
            recommendations=[],
            integration_time=0.0,
            success=False,
            error_message=error_message,
        )

    async def get_integration_summary(self) -> Dict[str, Any]:
        """통합 요약 정보 반환"""
        try:
            summary = {
                "total_integrations": len(self.integration_history),
                "successful_integrations": len(
                    [h for h in self.integration_history if h.status == IntegrationStatus.COMPLETED]
                ),
                "failed_integrations": len(
                    [h for h in self.integration_history if h.status == IntegrationStatus.FAILED]
                ),
                "average_integration_time": 0.0,
                "last_integration": None,
                "system_status": {
                    "survival_engine": "active",
                    "goal_generator": "active",
                    "evolution_system": "active",
                    "survival_assessment": "active",
                    "thought_flow": "active" if self.thought_flow else "inactive",
                },
            }

            # 캐시 통계 추가
            if self.integration_config["enable_advanced_cache"]:
                cache_stats = self.cache_system.get_cache_stats()
                summary["cache_stats"] = cache_stats

            if self.integration_history:
                # 평균 통합 시간 계산
                integration_times = []
                for history in self.integration_history:
                    if history.end_time:
                        duration = (history.end_time - history.start_time).total_seconds()
                        integration_times.append(duration)

                if integration_times:
                    summary["average_integration_time"] = sum(integration_times) / len(integration_times)

                # 마지막 통합 정보
                last_integration = self.integration_history[-1]
                summary["last_integration"] = {
                    "stage": last_integration.stage.value,
                    "status": last_integration.status.value,
                    "start_time": last_integration.start_time.isoformat(),
                    "end_time": (last_integration.end_time.isoformat() if last_integration.end_time else None),
                }

            return summary

        except Exception as e:
            logger.error(f"통합 요약 정보 생성 실패: {e}")
            return {"error": str(e)}

    async def reset_integration_system(self) -> bool:
        """통합 시스템 초기화"""
        try:
            # 통합 히스토리 초기화
            self.integration_history.clear()

            # 각 시스템 초기화
            self.survival_engine = SurvivalInstinctEngine()
            self.goal_generator = SelfGoalGenerator()
            self.evolution_system = EvolutionSystem()
            self.survival_assessment = SurvivalAssessmentSystem()

            # 캐시 시스템 초기화
            if self.integration_config["enable_advanced_cache"]:
                self.cache_system.clear_cache()

            logger.info("통합 시스템 초기화 완료")
            return True

        except Exception as e:
            logger.error(f"통합 시스템 초기화 실패: {e}")
            return False

    async def update_integration_config(self, new_config: Dict[str, Any]) -> bool:
        """통합 설정 업데이트"""
        try:
            # 설정 검증
            valid_keys = [
                "enable_thought_flow",
                "enable_survival_instinct",
                "enable_self_goals",
                "enable_evolution",
                "enable_assessment",
                "enable_integrated_evolution",  # 새로 추가
                "enable_advanced_cache",  # 새로 추가
            ]

            for key, value in new_config.items():
                if key in valid_keys and isinstance(value, bool):
                    self.integration_config[key] = value

            logger.info(f"통합 설정 업데이트 완료: {new_config}")
            return True

        except Exception as e:
            logger.error(f"통합 설정 업데이트 실패: {e}")
            return False

    def _try_initialize_integrated_evolution(self):
        """통합 진화 시스템을 동적으로 초기화하는 메서드"""
        if self.integrated_evolution is None:
            try:
                self.integrated_evolution = _get_integrated_evolution_system()
                if self.integrated_evolution:
                    logger.info("통합 진화 시스템 동적 import 및 초기화 완료")
                else:
                    logger.warning("통합 진화 시스템 동적 import 실패 또는 모듈을 찾을 수 없습니다.")
            except Exception as e:
                logger.error(f"통합 진화 시스템 동적 초기화 실패: {e}")

    async def get_cache_performance_report(self) -> Dict[str, Any]:
        """캐시 성능 리포트 반환"""
        try:
            if not self.integration_config["enable_advanced_cache"]:
                return {"error": "고급 캐시 시스템이 비활성화되어 있습니다."}

            cache_stats = self.cache_system.get_cache_stats()

            # 성능 분석
            performance_analysis = {
                "hit_rate_category": (
                    "우수"
                    if cache_stats["hit_rate"] >= 80
                    else "양호"
                    if cache_stats["hit_rate"] >= 60
                    else "개선 필요"
                ),
                "cache_efficiency": (
                    "높음"
                    if cache_stats["cache_efficiency"] > 0.5
                    else "보통"
                    if cache_stats["cache_efficiency"] > 0.2
                    else "낮음"
                ),
                "recommendations": [],
            }

            # 권장사항 생성
            if cache_stats["hit_rate"] < 80:
                performance_analysis["recommendations"].append("캐시 키 생성 알고리즘 최적화 필요")
                performance_analysis["recommendations"].append("캐시 크기 증가 고려")
                performance_analysis["recommendations"].append("TTL 조정 검토")

            if cache_stats["cache_efficiency"] < 0.3:
                performance_analysis["recommendations"].append("캐시 접근 패턴 분석 필요")
                performance_analysis["recommendations"].append("LRU 정리 알고리즘 개선")

            return {
                "cache_stats": cache_stats,
                "performance_analysis": performance_analysis,
                "optimization_status": ("완료" if cache_stats["hit_rate"] >= 80 else "진행 중"),
            }

        except Exception as e:
            logger.error(f"캐시 성능 리포트 생성 실패: {e}")
            return {"error": str(e)}


async def main():
    """메인 함수"""
    # Phase Ω 통합 시스템 초기화
    phase_omega = DuRiPhaseOmega()

    # 테스트 데이터
    test_cases = [
        {
            "user_input": "시스템 상태를 확인하고 개선 방안을 제시해주세요",
            "context": {
                "environmental_changes": {"magnitude": 0.3, "direction": "positive"},
                "environment_data": {
                    "system_stability": 0.8,
                    "performance_metrics": {"accuracy": 0.75, "efficiency": 0.7},
                },
                "resource_data": {
                    "computational": {
                        "availability": 0.8,
                        "utilization": 0.6,
                        "efficiency": 0.7,
                        "capacity": 1.0,
                    },
                    "memory": {
                        "availability": 0.7,
                        "utilization": 0.5,
                        "efficiency": 0.8,
                        "capacity": 1.0,
                    },
                },
            },
        },
        {
            "user_input": "성능 최적화 방안을 분석해주세요",
            "context": {
                "environmental_changes": {"magnitude": 0.5, "direction": "positive"},
                "environment_data": {
                    "system_stability": 0.9,
                    "performance_metrics": {"accuracy": 0.85, "efficiency": 0.8},
                },
                "resource_data": {
                    "computational": {
                        "availability": 0.9,
                        "utilization": 0.7,
                        "efficiency": 0.8,
                        "capacity": 1.0,
                    },
                    "memory": {
                        "availability": 0.8,
                        "utilization": 0.6,
                        "efficiency": 0.9,
                        "capacity": 1.0,
                    },
                },
            },
        },
        {
            "user_input": "보안 강화 방안을 제시해주세요",
            "context": {
                "environmental_changes": {"magnitude": 0.2, "direction": "negative"},
                "environment_data": {
                    "system_stability": 0.7,
                    "performance_metrics": {"accuracy": 0.65, "efficiency": 0.6},
                },
                "resource_data": {
                    "computational": {
                        "availability": 0.6,
                        "utilization": 0.4,
                        "efficiency": 0.6,
                        "capacity": 1.0,
                    },
                    "memory": {
                        "availability": 0.5,
                        "utilization": 0.3,
                        "efficiency": 0.7,
                        "capacity": 1.0,
                    },
                },
            },
        },
    ]

    print("🚀 Phase Ω 통합 프로세스 시작 (캐시 히트율 향상 테스트)...")

    # 여러 번 테스트하여 캐시 히트율 측정
    for i, test_case in enumerate(test_cases * 2):  # 각 테스트 케이스를 2번씩 실행
        print(f"\n📊 테스트 {i+1}/6 실행 중...")

        start_time = time.time()
        result = await phase_omega.process_with_survival_instinct(test_case, test_case["context"])  # noqa: F841
        execution_time = time.time() - start_time

        print(f"✅ 테스트 {i+1} 완료: {execution_time:.4f}초")

        # 캐시 통계 출력
        if phase_omega.integration_config["enable_advanced_cache"]:
            cache_stats = phase_omega.cache_system.get_cache_stats()
            print(
                f"📈 캐시 히트율: {cache_stats['hit_rate']:.1f}% (히트: {cache_stats['cache_hits']}, 미스: {cache_stats['cache_misses']})"  # noqa: E501
            )

    # 최종 성능 리포트
    print("\n🎯 최종 성능 리포트:")
    performance_report = await phase_omega.get_cache_performance_report()

    if "error" not in performance_report:
        cache_stats = performance_report["cache_stats"]
        analysis = performance_report["performance_analysis"]

        print(f"📊 캐시 히트율: {cache_stats['hit_rate']:.1f}%")
        print(f"🎯 목표 달성: {'✅ 달성' if cache_stats['hit_rate'] >= 80 else '🔄 진행 중'}")
        print(f"📈 성능 등급: {analysis['hit_rate_category']}")
        print(f"⚡ 캐시 효율성: {analysis['cache_efficiency']}")

        if analysis["recommendations"]:
            print("💡 권장사항:")
            for rec in analysis["recommendations"]:
                print(f"  - {rec}")
    else:
        print(f"❌ 성능 리포트 생성 실패: {performance_report['error']}")

    # 통합 요약 정보
    summary = await phase_omega.get_integration_summary()
    print("\n📋 통합 요약:")
    print(f"총 통합 횟수: {summary['total_integrations']}")
    print(f"성공한 통합: {summary['successful_integrations']}")
    print(f"실패한 통합: {summary['failed_integrations']}")
    print(f"평균 실행 시간: {summary['average_integration_time']:.2f}초")


if __name__ == "__main__":
    asyncio.run(main())
