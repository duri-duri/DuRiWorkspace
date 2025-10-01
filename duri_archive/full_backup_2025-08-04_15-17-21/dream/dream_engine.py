"""
DuRi의 Dream Engine

무의식적 연산, 랜덤 조합, 창의 탐색을 담당하는 시스템입니다.
비동기/무한 루프로 지속적으로 실행되어 창의적 전략을 채굴합니다.
"""

import hashlib
import json
import logging
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class DreamType(Enum):
    """Dream 유형"""

    RANDOM_COMBINATION = "random_combination"  # 랜덤 조합
    PATTERN_MUTATION = "pattern_mutation"  # 패턴 변형
    CONCEPT_FUSION = "concept_fusion"  # 개념 융합
    INTUITION_EXPLORATION = "intuition_exploration"  # 직관 탐색


class DreamStatus(Enum):
    """Dream 상태"""

    ACTIVE = "active"  # 활성
    EVALUATING = "evaluating"  # 평가 중
    PROMOTED = "promoted"  # 승격됨
    DISCARDED = "discarded"  # 폐기됨


@dataclass
class DreamCandidate:
    """Dream 후보"""

    dream_id: str
    dream_type: DreamType
    creation_time: datetime
    strategy_data: Dict[str, Any]
    confidence_score: float
    novelty_score: float
    complexity_score: float
    status: DreamStatus
    evaluation_count: int
    last_evaluation: Optional[datetime]


@dataclass
class DreamResult:
    """Dream 결과"""

    dream_id: str
    success: bool
    strategy: Dict[str, Any]
    confidence: float
    novelty: float
    complexity: float
    creation_time: datetime
    evaluation_time: Optional[datetime]


class DreamEngine:
    """
    DuRi의 Dream Engine

    무의식적 연산, 랜덤 조합, 창의 탐색을 담당하는 시스템입니다.
    """

    def __init__(self):
        """DreamEngine 초기화"""
        self.is_running = False
        self.dream_thread: Optional[threading.Thread] = None
        self.dream_candidates: Dict[str, DreamCandidate] = {}
        self.dream_history: List[DreamResult] = []
        self.evaluation_callback: Optional[Callable] = None

        # Dream 설정
        self.dream_config = {
            "min_confidence_threshold": 0.3,
            "max_novelty_threshold": 0.9,
            "complexity_range": (0.2, 0.8),
            "evaluation_interval": 5,  # 5초마다 평가
            "max_candidates": 50,
            "dream_generation_rate": 2,  # 초당 2개 생성
            "decay_rate": 0.95,  # 오래된 아이디어 감쇠율
        }

        # Dream 생성기 초기화
        self._initialize_dream_generators()

        logger.info("DreamEngine 초기화 완료")

    def _initialize_dream_generators(self):
        """Dream 생성기를 초기화합니다."""
        self.dream_generators = {
            DreamType.RANDOM_COMBINATION: self._generate_random_combination,
            DreamType.PATTERN_MUTATION: self._generate_pattern_mutation,
            DreamType.CONCEPT_FUSION: self._generate_concept_fusion,
            DreamType.INTUITION_EXPLORATION: self._generate_intuition_exploration,
        }

    def start_dream_engine(self, evaluation_callback: Optional[Callable] = None):
        """
        Dream Engine을 시작합니다.

        Args:
            evaluation_callback: Dream 평가 콜백 함수
        """
        if self.is_running:
            logger.warning("Dream Engine이 이미 실행 중입니다.")
            return False

        self.evaluation_callback = evaluation_callback
        self.is_running = True

        # Dream 스레드 시작
        self.dream_thread = threading.Thread(target=self._run_dream_loop, daemon=True)
        self.dream_thread.start()

        logger.info("Dream Engine 시작됨")
        return True

    def stop_dream_engine(self):
        """Dream Engine을 중지합니다."""
        if not self.is_running:
            logger.warning("Dream Engine이 실행되지 않았습니다.")
            return False

        self.is_running = False

        if self.dream_thread:
            self.dream_thread.join(timeout=5)

        logger.info("Dream Engine 중지됨")
        return True

    def _run_dream_loop(self):
        """Dream 루프를 실행합니다."""
        logger.info("Dream 루프 시작")

        while self.is_running:
            try:
                # 1. Dream 후보 생성
                self._generate_dream_candidates()

                # 2. 기존 후보 평가
                self._evaluate_dream_candidates()

                # 3. 오래된 아이디어 감쇠
                self._decay_old_ideas()

                # 4. 후보 정리
                self._cleanup_candidates()

                # 5. 잠시 대기
                time.sleep(1)

            except Exception as e:
                logger.error(f"Dream 루프 실행 중 오류: {e}")
                time.sleep(5)

        logger.info("Dream 루프 종료")

    def _generate_dream_candidates(self):
        """Dream 후보를 생성합니다."""
        if len(self.dream_candidates) >= self.dream_config["max_candidates"]:
            return

        # Dream 유형별로 생성
        for dream_type in DreamType:
            if random.random() < 0.25:  # 25% 확률로 생성
                dream_candidate = self._create_dream_candidate(dream_type)
                if dream_candidate:
                    self.dream_candidates[dream_candidate.dream_id] = dream_candidate
                    logger.debug(
                        f"Dream 후보 생성: {dream_candidate.dream_id} ({dream_type.value})"
                    )

    def _create_dream_candidate(
        self, dream_type: DreamType
    ) -> Optional[DreamCandidate]:
        """Dream 후보를 생성합니다."""
        try:
            # Dream 생성기 호출
            generator = self.dream_generators.get(dream_type)
            if not generator:
                return None

            strategy_data = generator()
            if not strategy_data:
                return None

            # Dream ID 생성
            dream_id = f"dream_{dream_type.value}_{int(time.time() * 1000)}"

            # 점수 계산
            confidence_score = self._calculate_confidence_score(strategy_data)
            novelty_score = self._calculate_novelty_score(strategy_data)
            complexity_score = self._calculate_complexity_score(strategy_data)

            # 임계값 확인
            if confidence_score < self.dream_config["min_confidence_threshold"]:
                return None

            if novelty_score > self.dream_config["max_novelty_threshold"]:
                return None

            complexity_min, complexity_max = self.dream_config["complexity_range"]
            if not (complexity_min <= complexity_score <= complexity_max):
                return None

            dream_candidate = DreamCandidate(
                dream_id=dream_id,
                dream_type=dream_type,
                creation_time=datetime.now(),
                strategy_data=strategy_data,
                confidence_score=confidence_score,
                novelty_score=novelty_score,
                complexity_score=complexity_score,
                status=DreamStatus.ACTIVE,
                evaluation_count=0,
                last_evaluation=None,
            )

            return dream_candidate

        except Exception as e:
            logger.error(f"Dream 후보 생성 실패: {e}")
            return None

    def _generate_random_combination(self) -> Dict[str, Any]:
        """랜덤 조합 Dream을 생성합니다."""
        # 기존 전략 요소들
        strategy_elements = [
            {"speed": 0.8, "accuracy": 0.9, "efficiency": 0.85},
            {"precision": 0.95, "flexibility": 0.7, "stability": 0.8},
            {"creativity": 0.6, "consistency": 0.9, "adaptability": 0.75},
            {"innovation": 0.5, "reliability": 0.95, "scalability": 0.8},
        ]

        # 랜덤 조합
        selected_elements = random.sample(strategy_elements, random.randint(2, 4))
        combined_strategy = {}

        for element in selected_elements:
            for key, value in element.items():
                if key in combined_strategy:
                    # 기존 값과 평균
                    combined_strategy[key] = (combined_strategy[key] + value) / 2
                else:
                    # 새로운 값 추가
                    combined_strategy[key] = value * random.uniform(0.8, 1.2)

        return {
            "type": "random_combination",
            "parameters": combined_strategy,
            "execution_method": "hybrid",
            "priority": random.uniform(0.3, 0.8),
        }

    def _generate_pattern_mutation(self) -> Dict[str, Any]:
        """패턴 변형 Dream을 생성합니다."""
        # 기존 패턴
        base_patterns = [
            {"sequential": True, "parallel": False, "iterative": True},
            {"adaptive": True, "predictive": False, "reactive": True},
            {"exploratory": True, "exploitative": False, "balanced": True},
        ]

        base_pattern = random.choice(base_patterns)
        mutated_pattern = {}

        for key, value in base_pattern.items():
            # 30% 확률로 변형
            if random.random() < 0.3:
                mutated_pattern[key] = not value
            else:
                mutated_pattern[key] = value

        return {
            "type": "pattern_mutation",
            "pattern": mutated_pattern,
            "execution_method": "mutation",
            "priority": random.uniform(0.4, 0.9),
        }

    def _generate_concept_fusion(self) -> Dict[str, Any]:
        """개념 융합 Dream을 생성합니다."""
        # 융합할 개념들
        concepts = [
            "learning",
            "creativity",
            "efficiency",
            "innovation",
            "stability",
            "adaptability",
            "precision",
            "flexibility",
        ]

        # 2-3개 개념 선택
        selected_concepts = random.sample(concepts, random.randint(2, 3))

        fusion_strategy = {
            "type": "concept_fusion",
            "concepts": selected_concepts,
            "fusion_method": random.choice(["weighted", "hierarchical", "balanced"]),
            "execution_method": "fusion",
            "priority": random.uniform(0.5, 1.0),
        }

        # 각 개념별 가중치
        weights = {}
        total_weight = 0
        for concept in selected_concepts:
            weight = random.uniform(0.2, 0.8)
            weights[concept] = weight
            total_weight += weight

        # 정규화
        for concept in weights:
            weights[concept] /= total_weight

        fusion_strategy["concept_weights"] = weights

        return fusion_strategy

    def _generate_intuition_exploration(self) -> Dict[str, Any]:
        """직관 탐색 Dream을 생성합니다."""
        # 직관적 요소들
        intuition_elements = [
            "unexpected_combination",
            "counter_intuitive_approach",
            "simplified_complexity",
            "complex_simplicity",
            "reverse_logic",
            "lateral_thinking",
        ]

        selected_elements = random.sample(intuition_elements, random.randint(1, 2))

        return {
            "type": "intuition_exploration",
            "intuition_elements": selected_elements,
            "exploration_depth": random.uniform(0.3, 0.9),
            "execution_method": "intuitive",
            "priority": random.uniform(0.6, 1.0),
        }

    def _calculate_confidence_score(self, strategy_data: Dict[str, Any]) -> float:
        """신뢰도 점수를 계산합니다."""
        # 기본 신뢰도
        base_confidence = 0.5

        # 전략 유형별 가중치
        strategy_type = strategy_data.get("type", "unknown")
        type_weights = {
            "random_combination": 0.6,
            "pattern_mutation": 0.7,
            "concept_fusion": 0.8,
            "intuition_exploration": 0.5,
        }

        weight = type_weights.get(strategy_type, 0.5)

        # 우선순위 반영
        priority = strategy_data.get("priority", 0.5)

        # 최종 신뢰도 계산
        confidence = base_confidence * weight * priority

        return min(confidence, 1.0)

    def _calculate_novelty_score(self, strategy_data: Dict[str, Any]) -> float:
        """새로움 점수를 계산합니다."""
        # 기본 새로움
        base_novelty = 0.5

        # 전략 유형별 새로움
        strategy_type = strategy_data.get("type", "unknown")
        type_novelty = {
            "random_combination": 0.6,
            "pattern_mutation": 0.7,
            "concept_fusion": 0.8,
            "intuition_exploration": 0.9,
        }

        novelty = type_novelty.get(strategy_type, 0.5)

        # 복잡성 반영
        complexity = self._calculate_complexity_score(strategy_data)
        novelty *= 1 + complexity * 0.3

        return min(novelty, 1.0)

    def _calculate_complexity_score(self, strategy_data: Dict[str, Any]) -> float:
        """복잡성 점수를 계산합니다."""
        complexity = 0.5

        # 파라미터 수에 따른 복잡성
        if "parameters" in strategy_data:
            param_count = len(strategy_data["parameters"])
            complexity += min(param_count * 0.1, 0.3)

        # 개념 수에 따른 복잡성
        if "concepts" in strategy_data:
            concept_count = len(strategy_data["concepts"])
            complexity += min(concept_count * 0.15, 0.3)

        # 직관 요소 수에 따른 복잡성
        if "intuition_elements" in strategy_data:
            element_count = len(strategy_data["intuition_elements"])
            complexity += min(element_count * 0.2, 0.2)

        return min(complexity, 1.0)

    def _evaluate_dream_candidates(self):
        """Dream 후보를 평가합니다."""
        current_time = datetime.now()

        for dream_id, candidate in list(self.dream_candidates.items()):
            # 평가 간격 확인
            if (
                candidate.last_evaluation
                and (current_time - candidate.last_evaluation).seconds
                < self.dream_config["evaluation_interval"]
            ):
                continue

            # 평가 실행
            evaluation_result = self._evaluate_candidate(candidate)

            if evaluation_result:
                # 평가 결과 처리
                self._process_evaluation_result(candidate, evaluation_result)

            # 평가 시간 업데이트
            candidate.last_evaluation = current_time
            candidate.evaluation_count += 1

    def _evaluate_candidate(
        self, candidate: DreamCandidate
    ) -> Optional[Dict[str, Any]]:
        """후보를 평가합니다."""
        try:
            if self.evaluation_callback:
                return self.evaluation_callback(candidate)
            else:
                # 기본 평가 로직
                return self._default_evaluation(candidate)
        except Exception as e:
            logger.error(f"Dream 후보 평가 실패: {e}")
            return None

    def _default_evaluation(self, candidate: DreamCandidate) -> Dict[str, Any]:
        """기본 평가 로직"""
        # 종합 점수 계산
        total_score = (
            candidate.confidence_score * 0.4
            + candidate.novelty_score * 0.4
            + candidate.complexity_score * 0.2
        )

        # 평가 결과
        evaluation_result = {
            "dream_id": candidate.dream_id,
            "total_score": total_score,
            "confidence_score": candidate.confidence_score,
            "novelty_score": candidate.novelty_score,
            "complexity_score": candidate.complexity_score,
            "evaluation_time": datetime.now(),
            "recommendation": "continue" if total_score > 0.6 else "discard",
        }

        return evaluation_result

    def _process_evaluation_result(
        self, candidate: DreamCandidate, evaluation_result: Dict[str, Any]
    ):
        """평가 결과를 처리합니다."""
        recommendation = evaluation_result.get("recommendation", "continue")

        if recommendation == "promote":
            candidate.status = DreamStatus.PROMOTED
            logger.info(f"Dream {candidate.dream_id} 승격됨")
        elif recommendation == "discard":
            candidate.status = DreamStatus.DISCARDED
            logger.info(f"Dream {candidate.dream_id} 폐기됨")

    def _decay_old_ideas(self):
        """오래된 아이디어를 감쇠시킵니다."""
        current_time = datetime.now()
        decay_rate = self.dream_config["decay_rate"]

        for candidate in self.dream_candidates.values():
            if candidate.status != DreamStatus.ACTIVE:
                continue

            # 생성 후 경과 시간 계산
            age_hours = (current_time - candidate.creation_time).total_seconds() / 3600

            if age_hours > 1:  # 1시간 이상 된 아이디어
                # 신뢰도 감쇠
                candidate.confidence_score *= decay_rate

                # 너무 낮아진 경우 폐기
                if candidate.confidence_score < 0.1:
                    candidate.status = DreamStatus.DISCARDED
                    logger.debug(f"Dream {candidate.dream_id} 신뢰도 감쇠로 폐기")

    def _cleanup_candidates(self):
        """후보를 정리합니다."""
        # 폐기된 후보 제거
        discarded_candidates = [
            dream_id
            for dream_id, candidate in self.dream_candidates.items()
            if candidate.status == DreamStatus.DISCARDED
        ]

        for dream_id in discarded_candidates:
            del self.dream_candidates[dream_id]

        # 승격된 후보 기록
        promoted_candidates = [
            candidate
            for candidate in self.dream_candidates.values()
            if candidate.status == DreamStatus.PROMOTED
        ]

        for candidate in promoted_candidates:
            dream_result = DreamResult(
                dream_id=candidate.dream_id,
                success=True,
                strategy=candidate.strategy_data,
                confidence=candidate.confidence_score,
                novelty=candidate.novelty_score,
                complexity=candidate.complexity_score,
                creation_time=candidate.creation_time,
                evaluation_time=candidate.last_evaluation,
            )

            self.dream_history.append(dream_result)
            logger.info(f"Dream {candidate.dream_id} 기록됨")

    def get_dream_statistics(self) -> Dict[str, Any]:
        """Dream 통계를 반환합니다."""
        total_candidates = len(self.dream_candidates)
        active_candidates = len(
            [
                c
                for c in self.dream_candidates.values()
                if c.status == DreamStatus.ACTIVE
            ]
        )
        promoted_candidates = len(
            [
                c
                for c in self.dream_candidates.values()
                if c.status == DreamStatus.PROMOTED
            ]
        )
        discarded_candidates = len(
            [
                c
                for c in self.dream_candidates.values()
                if c.status == DreamStatus.DISCARDED
            ]
        )

        total_history = len(self.dream_history)

        # 유형별 통계
        type_stats = {}
        for dream_type in DreamType:
            type_count = len(
                [
                    c
                    for c in self.dream_candidates.values()
                    if c.dream_type == dream_type
                ]
            )
            type_stats[dream_type.value] = type_count

        return {
            "is_running": self.is_running,
            "total_candidates": total_candidates,
            "active_candidates": active_candidates,
            "promoted_candidates": promoted_candidates,
            "discarded_candidates": discarded_candidates,
            "total_history": total_history,
            "type_distribution": type_stats,
        }

    def get_promoted_dreams(self) -> List[DreamResult]:
        """승격된 Dream들을 반환합니다."""
        return self.dream_history.copy()


# 싱글톤 인스턴스
_dream_engine = None


def get_dream_engine() -> DreamEngine:
    """DreamEngine 싱글톤 인스턴스 반환"""
    global _dream_engine
    if _dream_engine is None:
        _dream_engine = DreamEngine()
    return _dream_engine
