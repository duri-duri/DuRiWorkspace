#!/usr/bin/env python3
"""
DuRi 실시간 학습 및 적응 시스템 - Phase 1-3 Week 3 Day 8
실시간 학습 및 시스템 적응 능력을 강화하는 시스템

기능:
1. 실시간 학습 데이터 수집
2. 적응적 모델 업데이트
3. 학습 성과 평가
4. 시스템 적응 메커니즘
"""

import asyncio
import logging
import statistics
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Set

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class LearningType(Enum):
    """학습 유형"""

    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    TRANSFER = "transfer"
    META = "meta"


class AdaptationType(Enum):
    """적응 유형"""

    INCREMENTAL = "incremental"
    BATCH = "batch"
    ONLINE = "online"
    ACTIVE = "active"


class LearningStatus(Enum):
    """학습 상태"""

    IDLE = "idle"
    LEARNING = "learning"
    EVALUATING = "evaluating"
    ADAPTING = "adapting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LearningData:
    """학습 데이터"""

    data_id: str
    data_type: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0


@dataclass
class LearningModel:
    """학습 모델"""

    model_id: str
    model_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    status: str = "active"


@dataclass
class LearningResult:
    """학습 결과"""

    result_id: str
    model_id: str
    learning_type: LearningType
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    adaptation_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    success: bool = True


@dataclass
class AdaptationResult:
    """적응 결과"""

    adaptation_id: str
    system_name: str
    adaptation_type: AdaptationType
    changes: Dict[str, Any] = field(default_factory=dict)
    performance_improvement: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    success: bool = True


class AdaptiveLearningSystem:
    """적응적 학습 시스템"""

    def __init__(self):
        """초기화"""
        self.learning_data: Dict[str, LearningData] = {}
        self.learning_models: Dict[str, LearningModel] = {}
        self.learning_results: Dict[str, LearningResult] = {}
        self.adaptation_results: Dict[str, AdaptationResult] = {}
        self.system_registry: Dict[str, Any] = {}

        # 학습 설정
        self.learning_config = {
            "max_data_points": 10000,
            "learning_batch_size": 100,
            "learning_rate": 0.01,
            "evaluation_interval": 100,
            "adaptation_threshold": 0.1,
        }

        # 적응 설정
        self.adaptation_config = {
            "max_adaptations": 50,
            "adaptation_cooldown": 60.0,
            "performance_threshold": 0.8,
            "stability_threshold": 0.9,
        }

        # 모니터링 데이터
        self.learning_metrics = {
            "total_learning_sessions": 0,
            "successful_learning_sessions": 0,
            "failed_learning_sessions": 0,
            "average_learning_time": 0.0,
            "total_adaptations": 0,
            "successful_adaptations": 0,
            "failed_adaptations": 0,
            "average_adaptation_time": 0.0,
        }

        # 학습 큐
        self.learning_queue = asyncio.Queue()
        self.adaptation_queue = asyncio.Queue()

        # 활성 학습 및 적응
        self.active_learning: Set[str] = set()
        self.active_adaptations: Set[str] = set()

        logger.info("적응적 학습 시스템 초기화 완료")

    async def register_system(self, system_name: str, system_instance: Any) -> bool:
        """시스템 등록"""
        try:
            self.system_registry[system_name] = system_instance
            logger.info(f"시스템 등록 완료: {system_name}")
            return True
        except Exception as e:
            logger.error(f"시스템 등록 실패: {system_name} - {e}")
            return False

    async def collect_learning_data(
        self,
        data_type: str,
        content: Dict[str, Any],
        source: str = "",
        quality_score: float = 0.0,
    ) -> str:
        """학습 데이터 수집"""
        data_id = f"data_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        learning_data = LearningData(
            data_id=data_id,
            data_type=data_type,
            content=content,
            source=source,
            quality_score=quality_score,
        )

        self.learning_data[data_id] = learning_data

        # 데이터 품질 검증
        if quality_score >= 0.7:  # 높은 품질 데이터만 학습 큐에 추가
            await self.learning_queue.put(learning_data)
            logger.info(f"학습 데이터 수집: {data_id} (품질: {quality_score:.2f})")
        else:
            logger.info(f"낮은 품질 데이터 수집: {data_id} (품질: {quality_score:.2f})")

        return data_id

    async def create_learning_model(self, model_type: str, parameters: Dict[str, Any] = None) -> str:
        """학습 모델 생성"""
        model_id = f"model_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        learning_model = LearningModel(model_id=model_id, model_type=model_type, parameters=parameters or {})

        self.learning_models[model_id] = learning_model
        logger.info(f"학습 모델 생성: {model_id} ({model_type})")
        return model_id

    async def train_model(self, model_id: str, learning_type: LearningType, data_ids: List[str] = None) -> str:
        """모델 학습"""
        if model_id not in self.learning_models:
            raise ValueError(f"모델을 찾을 수 없음: {model_id}")

        result_id = f"result_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        try:
            # 학습 상태 업데이트
            self.active_learning.add(result_id)
            logger.info(f"모델 학습 시작: {model_id} ({learning_type.value})")

            # 학습 데이터 준비
            if data_ids is None:
                # 모든 데이터 사용
                training_data = list(self.learning_data.values())
            else:
                # 지정된 데이터만 사용
                training_data = [self.learning_data[data_id] for data_id in data_ids if data_id in self.learning_data]

            if not training_data:
                raise ValueError("학습 데이터가 없습니다")

            # 모델 학습 실행
            learning_result = await self._execute_learning(model_id, learning_type, training_data)

            # 학습 결과 저장
            learning_result.result_id = result_id
            learning_result.duration = time.time() - start_time
            self.learning_results[result_id] = learning_result

            # 모델 업데이트
            model = self.learning_models[model_id]
            model.performance_metrics.update(learning_result.performance_metrics)
            model.updated_at = datetime.now()

            # 메트릭 업데이트
            self._update_learning_metrics(True, learning_result.duration)

            logger.info(f"모델 학습 완료: {model_id} ({learning_result.duration:.2f}초)")
            return result_id

        except Exception as e:
            # 학습 실패
            learning_result = LearningResult(
                result_id=result_id,
                model_id=model_id,
                learning_type=learning_type,
                duration=time.time() - start_time,
                success=False,
            )
            self.learning_results[result_id] = learning_result

            # 메트릭 업데이트
            self._update_learning_metrics(False, learning_result.duration)

            logger.error(f"모델 학습 실패: {model_id} - {e}")
            raise
        finally:
            self.active_learning.discard(result_id)

    async def adapt_system(
        self,
        system_name: str,
        adaptation_type: AdaptationType,
        adaptation_data: Dict[str, Any] = None,
    ) -> str:
        """시스템 적응"""
        if system_name not in self.system_registry:
            raise ValueError(f"시스템을 찾을 수 없음: {system_name}")

        adaptation_id = f"adaptation_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        try:
            # 적응 상태 업데이트
            self.active_adaptations.add(adaptation_id)
            logger.info(f"시스템 적응 시작: {system_name} ({adaptation_type.value})")

            # 시스템 적응 실행
            adaptation_result = await self._execute_adaptation(system_name, adaptation_type, adaptation_data)

            # 적응 결과 저장
            adaptation_result.adaptation_id = adaptation_id
            adaptation_result.duration = time.time() - start_time
            self.adaptation_results[adaptation_id] = adaptation_result

            # 메트릭 업데이트
            self._update_adaptation_metrics(True, adaptation_result.duration)

            logger.info(f"시스템 적응 완료: {system_name} ({adaptation_result.duration:.2f}초)")
            return adaptation_id

        except Exception as e:
            # 적응 실패
            adaptation_result = AdaptationResult(
                adaptation_id=adaptation_id,
                system_name=system_name,
                adaptation_type=adaptation_type,
                duration=time.time() - start_time,
                success=False,
            )
            self.adaptation_results[adaptation_id] = adaptation_result

            # 메트릭 업데이트
            self._update_adaptation_metrics(False, adaptation_result.duration)

            logger.error(f"시스템 적응 실패: {system_name} - {e}")
            raise
        finally:
            self.active_adaptations.discard(adaptation_id)

    async def evaluate_learning_performance(self, model_id: str) -> Dict[str, float]:
        """학습 성과 평가"""
        if model_id not in self.learning_models:
            raise ValueError(f"모델을 찾을 수 없음: {model_id}")

        model = self.learning_models[model_id]

        # 성과 지표 계산
        performance_metrics = {
            "accuracy": self._calculate_accuracy(model),
            "precision": self._calculate_precision(model),
            "recall": self._calculate_recall(model),
            "f1_score": self._calculate_f1_score(model),
            "learning_efficiency": self._calculate_learning_efficiency(model),
            "adaptation_speed": self._calculate_adaptation_speed(model),
        }

        # 모델 성과 업데이트
        model.performance_metrics.update(performance_metrics)
        model.updated_at = datetime.now()

        logger.info(f"학습 성과 평가 완료: {model_id}")
        return performance_metrics

    async def get_learning_recommendations(self, system_name: str = None) -> List[Dict[str, Any]]:
        """학습 권장사항 생성"""
        recommendations = []

        # 데이터 품질 기반 권장사항
        data_quality_recommendations = self._analyze_data_quality()
        recommendations.extend(data_quality_recommendations)

        # 모델 성과 기반 권장사항
        model_performance_recommendations = self._analyze_model_performance()
        recommendations.extend(model_performance_recommendations)

        # 시스템 적응 기반 권장사항
        if system_name:
            system_adaptation_recommendations = await self._analyze_system_adaptation(system_name)
            recommendations.extend(system_adaptation_recommendations)

        return recommendations

    async def _execute_learning(
        self,
        model_id: str,
        learning_type: LearningType,
        training_data: List[LearningData],
    ) -> LearningResult:
        """학습 실행"""
        model = self.learning_models[model_id]

        # 학습 유형에 따른 학습 실행
        if learning_type == LearningType.SUPERVISED:
            performance_metrics = await self._execute_supervised_learning(model, training_data)
        elif learning_type == LearningType.UNSUPERVISED:
            performance_metrics = await self._execute_unsupervised_learning(model, training_data)
        elif learning_type == LearningType.REINFORCEMENT:
            performance_metrics = await self._execute_reinforcement_learning(model, training_data)
        elif learning_type == LearningType.TRANSFER:
            performance_metrics = await self._execute_transfer_learning(model, training_data)
        elif learning_type == LearningType.META:
            performance_metrics = await self._execute_meta_learning(model, training_data)
        else:
            raise ValueError(f"지원하지 않는 학습 유형: {learning_type}")

        # 적응 메트릭 계산
        adaptation_metrics = await self._calculate_adaptation_metrics(model, training_data)

        return LearningResult(
            result_id="",
            model_id=model_id,
            learning_type=learning_type,
            performance_metrics=performance_metrics,
            adaptation_metrics=adaptation_metrics,
        )

    async def _execute_adaptation(
        self,
        system_name: str,
        adaptation_type: AdaptationType,
        adaptation_data: Dict[str, Any],
    ) -> AdaptationResult:
        """적응 실행"""
        system_instance = self.system_registry[system_name]

        # 적응 유형에 따른 적응 실행
        if adaptation_type == AdaptationType.INCREMENTAL:
            changes = await self._execute_incremental_adaptation(system_instance, adaptation_data)
        elif adaptation_type == AdaptationType.BATCH:
            changes = await self._execute_batch_adaptation(system_instance, adaptation_data)
        elif adaptation_type == AdaptationType.ONLINE:
            changes = await self._execute_online_adaptation(system_instance, adaptation_data)
        elif adaptation_type == AdaptationType.ACTIVE:
            changes = await self._execute_active_adaptation(system_instance, adaptation_data)
        else:
            raise ValueError(f"지원하지 않는 적응 유형: {adaptation_type}")

        # 성능 개선 계산
        performance_improvement = await self._calculate_performance_improvement(system_name, changes)

        return AdaptationResult(
            adaptation_id="",
            system_name=system_name,
            adaptation_type=adaptation_type,
            changes=changes,
            performance_improvement=performance_improvement,
        )

    async def _execute_supervised_learning(
        self, model: LearningModel, training_data: List[LearningData]
    ) -> Dict[str, float]:
        """지도 학습 실행"""
        # 지도 학습 시뮬레이션
        accuracy = np.random.uniform(0.7, 0.95)
        precision = np.random.uniform(0.6, 0.9)
        recall = np.random.uniform(0.6, 0.9)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "learning_efficiency": np.random.uniform(0.7, 0.9),
        }

    async def _execute_unsupervised_learning(
        self, model: LearningModel, training_data: List[LearningData]
    ) -> Dict[str, float]:
        """비지도 학습 실행"""
        # 비지도 학습 시뮬레이션
        clustering_accuracy = np.random.uniform(0.6, 0.85)
        feature_learning_score = np.random.uniform(0.5, 0.8)

        return {
            "clustering_accuracy": clustering_accuracy,
            "feature_learning_score": feature_learning_score,
            "learning_efficiency": np.random.uniform(0.6, 0.8),
        }

    async def _execute_reinforcement_learning(
        self, model: LearningModel, training_data: List[LearningData]
    ) -> Dict[str, float]:
        """강화 학습 실행"""
        # 강화 학습 시뮬레이션
        reward_score = np.random.uniform(0.5, 0.9)
        policy_accuracy = np.random.uniform(0.6, 0.85)

        return {
            "reward_score": reward_score,
            "policy_accuracy": policy_accuracy,
            "learning_efficiency": np.random.uniform(0.5, 0.8),
        }

    async def _execute_transfer_learning(
        self, model: LearningModel, training_data: List[LearningData]
    ) -> Dict[str, float]:
        """전이 학습 실행"""
        # 전이 학습 시뮬레이션
        transfer_accuracy = np.random.uniform(0.7, 0.9)
        knowledge_transfer_score = np.random.uniform(0.6, 0.85)

        return {
            "transfer_accuracy": transfer_accuracy,
            "knowledge_transfer_score": knowledge_transfer_score,
            "learning_efficiency": np.random.uniform(0.7, 0.9),
        }

    async def _execute_meta_learning(self, model: LearningModel, training_data: List[LearningData]) -> Dict[str, float]:
        """메타 학습 실행"""
        # 메타 학습 시뮬레이션
        meta_learning_score = np.random.uniform(0.6, 0.9)
        adaptation_speed = np.random.uniform(0.5, 0.8)

        return {
            "meta_learning_score": meta_learning_score,
            "adaptation_speed": adaptation_speed,
            "learning_efficiency": np.random.uniform(0.6, 0.85),
        }

    async def _execute_incremental_adaptation(
        self, system_instance: Any, adaptation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """점진적 적응 실행"""
        # 점진적 적응 시뮬레이션
        changes = {
            "parameter_updates": np.random.randint(1, 10),
            "performance_improvement": np.random.uniform(0.05, 0.2),
            "adaptation_speed": np.random.uniform(0.3, 0.7),
        }
        return changes

    async def _execute_batch_adaptation(self, system_instance: Any, adaptation_data: Dict[str, Any]) -> Dict[str, Any]:
        """배치 적응 실행"""
        # 배치 적응 시뮬레이션
        changes = {
            "batch_updates": np.random.randint(5, 20),
            "performance_improvement": np.random.uniform(0.1, 0.3),
            "adaptation_speed": np.random.uniform(0.2, 0.5),
        }
        return changes

    async def _execute_online_adaptation(self, system_instance: Any, adaptation_data: Dict[str, Any]) -> Dict[str, Any]:
        """온라인 적응 실행"""
        # 온라인 적응 시뮬레이션
        changes = {
            "real_time_updates": np.random.randint(10, 50),
            "performance_improvement": np.random.uniform(0.15, 0.35),
            "adaptation_speed": np.random.uniform(0.4, 0.8),
        }
        return changes

    async def _execute_active_adaptation(self, system_instance: Any, adaptation_data: Dict[str, Any]) -> Dict[str, Any]:
        """능동적 적응 실행"""
        # 능동적 적응 시뮬레이션
        changes = {
            "active_updates": np.random.randint(3, 15),
            "performance_improvement": np.random.uniform(0.2, 0.4),
            "adaptation_speed": np.random.uniform(0.5, 0.9),
        }
        return changes

    async def _calculate_adaptation_metrics(
        self, model: LearningModel, training_data: List[LearningData]
    ) -> Dict[str, float]:
        """적응 메트릭 계산"""
        return {
            "adaptation_speed": np.random.uniform(0.3, 0.8),
            "adaptation_accuracy": np.random.uniform(0.6, 0.9),
            "adaptation_stability": np.random.uniform(0.5, 0.85),
        }

    async def _calculate_performance_improvement(self, system_name: str, changes: Dict[str, Any]) -> float:
        """성능 개선 계산"""
        # 성능 개선 시뮬레이션
        base_improvement = changes.get("performance_improvement", 0.0)
        adaptation_speed = changes.get("adaptation_speed", 0.5)

        # 적응 속도와 성능 개선의 조합
        total_improvement = base_improvement * (1 + adaptation_speed)
        return min(total_improvement, 1.0)

    def _calculate_accuracy(self, model: LearningModel) -> float:
        """정확도 계산"""
        return model.performance_metrics.get("accuracy", np.random.uniform(0.7, 0.9))

    def _calculate_precision(self, model: LearningModel) -> float:
        """정밀도 계산"""
        return model.performance_metrics.get("precision", np.random.uniform(0.6, 0.9))

    def _calculate_recall(self, model: LearningModel) -> float:
        """재현율 계산"""
        return model.performance_metrics.get("recall", np.random.uniform(0.6, 0.9))

    def _calculate_f1_score(self, model: LearningModel) -> float:
        """F1 점수 계산"""
        precision = self._calculate_precision(model)
        recall = self._calculate_recall(model)
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    def _calculate_learning_efficiency(self, model: LearningModel) -> float:
        """학습 효율성 계산"""
        return model.performance_metrics.get("learning_efficiency", np.random.uniform(0.6, 0.9))

    def _calculate_adaptation_speed(self, model: LearningModel) -> float:
        """적응 속도 계산"""
        return model.performance_metrics.get("adaptation_speed", np.random.uniform(0.4, 0.8))

    def _analyze_data_quality(self) -> List[Dict[str, Any]]:
        """데이터 품질 분석"""
        recommendations = []

        if not self.learning_data:
            recommendations.append(
                {
                    "type": "data_quality",
                    "priority": "high",
                    "message": "학습 데이터가 부족합니다. 더 많은 데이터를 수집하세요.",
                    "action": "collect_more_data",
                }
            )
            return recommendations

        # 데이터 품질 분석
        quality_scores = [data.quality_score for data in self.learning_data.values()]
        avg_quality = statistics.mean(quality_scores)

        if avg_quality < 0.7:
            recommendations.append(
                {
                    "type": "data_quality",
                    "priority": "medium",
                    "message": f"평균 데이터 품질이 낮습니다 ({avg_quality:.2f}). 데이터 품질을 개선하세요.",
                    "action": "improve_data_quality",
                }
            )

        return recommendations

    def _analyze_model_performance(self) -> List[Dict[str, Any]]:
        """모델 성과 분석"""
        recommendations = []

        if not self.learning_models:
            recommendations.append(
                {
                    "type": "model_performance",
                    "priority": "high",
                    "message": "학습 모델이 없습니다. 모델을 생성하세요.",
                    "action": "create_model",
                }
            )
            return recommendations

        # 모델 성과 분석
        for model_id, model in self.learning_models.items():
            accuracy = self._calculate_accuracy(model)
            if accuracy < 0.8:
                recommendations.append(
                    {
                        "type": "model_performance",
                        "priority": "medium",
                        "message": f"모델 {model_id}의 정확도가 낮습니다 ({accuracy:.2f}). 모델을 재학습하세요.",
                        "action": "retrain_model",
                        "model_id": model_id,
                    }
                )

        return recommendations

    async def _analyze_system_adaptation(self, system_name: str) -> List[Dict[str, Any]]:
        """시스템 적응 분석"""
        recommendations = []

        # 시스템 적응 이력 분석
        system_adaptations = [
            result for result in self.adaptation_results.values() if result.system_name == system_name
        ]

        if not system_adaptations:
            recommendations.append(
                {
                    "type": "system_adaptation",
                    "priority": "low",
                    "message": f"시스템 {system_name}의 적응 이력이 없습니다. 적응을 시도해보세요.",
                    "action": "try_adaptation",
                    "system_name": system_name,
                }
            )
        else:
            # 최근 적응 성과 분석
            recent_adaptations = sorted(system_adaptations, key=lambda x: x.timestamp, reverse=True)[:5]
            avg_improvement = statistics.mean([a.performance_improvement for a in recent_adaptations])

            if avg_improvement < 0.1:
                recommendations.append(
                    {
                        "type": "system_adaptation",
                        "priority": "medium",
                        "message": f"시스템 {system_name}의 최근 적응 성과가 낮습니다 ({avg_improvement:.2f}). 적응 전략을 개선하세요.",  # noqa: E501
                        "action": "improve_adaptation_strategy",
                        "system_name": system_name,
                    }
                )

        return recommendations

    def _update_learning_metrics(self, success: bool, duration: float):
        """학습 메트릭 업데이트"""
        self.learning_metrics["total_learning_sessions"] += 1

        if success:
            self.learning_metrics["successful_learning_sessions"] += 1
        else:
            self.learning_metrics["failed_learning_sessions"] += 1

        # 평균 학습 시간 업데이트
        total = self.learning_metrics["total_learning_sessions"]
        current_avg = self.learning_metrics["average_learning_time"]
        self.learning_metrics["average_learning_time"] = (current_avg * (total - 1) + duration) / total

    def _update_adaptation_metrics(self, success: bool, duration: float):
        """적응 메트릭 업데이트"""
        self.learning_metrics["total_adaptations"] += 1

        if success:
            self.learning_metrics["successful_adaptations"] += 1
        else:
            self.learning_metrics["failed_adaptations"] += 1

        # 평균 적응 시간 업데이트
        total = self.learning_metrics["total_adaptations"]
        current_avg = self.learning_metrics["average_adaptation_time"]
        self.learning_metrics["average_adaptation_time"] = (current_avg * (total - 1) + duration) / total

    def get_learning_metrics(self) -> Dict[str, Any]:
        """학습 메트릭 반환"""
        return self.learning_metrics.copy()

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "registered_systems": list(self.system_registry.keys()),
            "total_learning_data": len(self.learning_data),
            "total_learning_models": len(self.learning_models),
            "total_learning_results": len(self.learning_results),
            "total_adaptation_results": len(self.adaptation_results),
            "active_learning": len(self.active_learning),
            "active_adaptations": len(self.active_adaptations),
        }


async def test_adaptive_learning_system():
    """적응적 학습 시스템 테스트"""
    print("=== 적응적 학습 시스템 테스트 시작 ===")

    # 적응적 학습 시스템 초기화
    learning_system = AdaptiveLearningSystem()

    # 가상 시스템 등록
    class MockSystem:
        def __init__(self, name: str):
            self.name = name
            self.parameters = {}

        async def adapt(self, changes: Dict[str, Any]):
            self.parameters.update(changes)
            return {"system": self.name, "adapted": True}

    # 시스템 등록
    systems = ["lida_attention", "realtime_learning", "dynamic_reasoning"]
    for system_name in systems:
        mock_system = MockSystem(system_name)
        await learning_system.register_system(system_name, mock_system)

    print(f"등록된 시스템 수: {len(learning_system.system_registry)}")

    # 1. 학습 데이터 수집 테스트
    print("\n1. 학습 데이터 수집 테스트")
    data_ids = []
    for i in range(5):
        data_id = await learning_system.collect_learning_data(
            "training_data",
            {"input": f"data_{i}", "output": f"result_{i}"},
            "test_source",
            quality_score=np.random.uniform(0.6, 0.9),
        )
        data_ids.append(data_id)

    print(f"수집된 데이터 수: {len(learning_system.learning_data)}")

    # 2. 학습 모델 생성 테스트
    print("\n2. 학습 모델 생성 테스트")
    model_id = await learning_system.create_learning_model(
        "neural_network", {"layers": [64, 32, 16], "learning_rate": 0.01}
    )

    print(f"생성된 모델: {model_id}")

    # 3. 모델 학습 테스트
    print("\n3. 모델 학습 테스트")
    result_id = await learning_system.train_model(model_id, LearningType.SUPERVISED, data_ids)

    print(f"학습 결과: {result_id}")

    # 4. 학습 성과 평가 테스트
    print("\n4. 학습 성과 평가 테스트")
    performance_metrics = await learning_system.evaluate_learning_performance(model_id)
    print(f"성과 지표: {performance_metrics}")

    # 5. 시스템 적응 테스트
    print("\n5. 시스템 적응 테스트")
    adaptation_id = await learning_system.adapt_system(
        "lida_attention",
        AdaptationType.INCREMENTAL,
        {"learning_rate": 0.02, "batch_size": 64},
    )

    print(f"적응 결과: {adaptation_id}")

    # 6. 학습 권장사항 테스트
    print("\n6. 학습 권장사항 테스트")
    recommendations = await learning_system.get_learning_recommendations("lida_attention")
    print(f"권장사항 수: {len(recommendations)}")

    # 7. 메트릭 확인
    print("\n7. 메트릭 확인")
    learning_metrics = learning_system.get_learning_metrics()
    system_status = learning_system.get_system_status()

    print(f"학습 메트릭: {learning_metrics}")
    print(f"시스템 상태: {system_status}")

    print("\n=== 적응적 학습 시스템 테스트 완료 ===")

    return {
        "learning_metrics": learning_metrics,
        "system_status": system_status,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    asyncio.run(test_adaptive_learning_system())
