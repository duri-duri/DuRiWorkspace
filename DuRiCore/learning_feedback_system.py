#!/usr/bin/env python3
"""
DuRi 학습 피드백 시스템 (Day 6)
일회성 판단 → 지속적 개선으로 전환
"""

import asyncio
import json
import logging
import pickle
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JudgmentType(Enum):
    """판단 유형"""

    ETHICAL = "ethical"
    PRACTICAL = "practical"
    LOGICAL = "logical"
    EMOTIONAL = "emotional"
    STRATEGIC = "strategic"


class FeedbackType(Enum):
    """피드백 유형"""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTIVE = "corrective"
    ENHANCING = "enhancing"


@dataclass
class JudgmentMemory:
    """판단 기억"""

    judgment_id: str
    situation: str
    judgment_type: JudgmentType
    reasoning_process: Dict[str, Any]
    conclusion: str
    confidence_score: float
    timestamp: datetime
    context_metadata: Dict[str, Any]


@dataclass
class FeedbackEntry:
    """피드백 항목"""

    feedback_id: str
    judgment_id: str
    feedback_type: FeedbackType
    content: str
    source: str
    impact_score: float  # 0.0-1.0
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class LearningPattern:
    """학습 패턴"""

    pattern_id: str
    pattern_type: str
    frequency: int
    success_rate: float
    last_occurrence: datetime
    improvement_suggestions: List[str]


class JudgmentMemorySystem:
    """판단 기억 시스템"""

    def __init__(self, db_path: str = "judgment_memory.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 판단 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS judgments (
                judgment_id TEXT PRIMARY KEY,
                situation TEXT,
                judgment_type TEXT,
                reasoning_process TEXT,
                conclusion TEXT,
                confidence_score REAL,
                timestamp TEXT,
                context_metadata TEXT
            )
        """
        )

        # 피드백 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id TEXT PRIMARY KEY,
                judgment_id TEXT,
                feedback_type TEXT,
                content TEXT,
                source TEXT,
                impact_score REAL,
                timestamp TEXT,
                metadata TEXT,
                FOREIGN KEY (judgment_id) REFERENCES judgments (judgment_id)
            )
        """
        )

        # 학습 패턴 테이블
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT,
                frequency INTEGER,
                success_rate REAL,
                last_occurrence TEXT,
                improvement_suggestions TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    async def store_judgment(self, judgment: JudgmentMemory) -> bool:
        """판단 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO judgments VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    judgment.judgment_id,
                    judgment.situation,
                    judgment.judgment_type.value,
                    json.dumps(judgment.reasoning_process),
                    judgment.conclusion,
                    judgment.confidence_score,
                    judgment.timestamp.isoformat(),
                    json.dumps(judgment.context_metadata),
                ),
            )

            conn.commit()
            conn.close()
            logger.info(f"판단 저장 완료: {judgment.judgment_id}")
            return True
        except Exception as e:
            logger.error(f"판단 저장 실패: {e}")
            return False

    async def retrieve_similar_judgments(
        self, situation: str, limit: int = 5
    ) -> List[JudgmentMemory]:
        """유사한 판단 검색"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 간단한 키워드 기반 유사성 검색
            keywords = situation.split()
            placeholders = ",".join(["?" for _ in keywords])

            cursor.execute(
                f"""
                SELECT * FROM judgments
                WHERE situation LIKE '%' || ? || '%'
                ORDER BY confidence_score DESC
                LIMIT ?
            """,
                (keywords[0], limit),
            )

            results = cursor.fetchall()
            conn.close()

            judgments = []
            for row in results:
                judgment = JudgmentMemory(
                    judgment_id=row[0],
                    situation=row[1],
                    judgment_type=JudgmentType(row[2]),
                    reasoning_process=json.loads(row[3]),
                    conclusion=row[4],
                    confidence_score=row[5],
                    timestamp=datetime.fromisoformat(row[6]),
                    context_metadata=json.loads(row[7]),
                )
                judgments.append(judgment)

            return judgments
        except Exception as e:
            logger.error(f"유사한 판단 검색 실패: {e}")
            return []

    async def add_feedback(self, feedback: FeedbackEntry) -> bool:
        """피드백 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO feedback VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    feedback.feedback_id,
                    feedback.judgment_id,
                    feedback.feedback_type.value,
                    feedback.content,
                    feedback.source,
                    feedback.impact_score,
                    feedback.timestamp.isoformat(),
                    json.dumps(feedback.metadata),
                ),
            )

            conn.commit()
            conn.close()
            logger.info(f"피드백 추가 완료: {feedback.feedback_id}")
            return True
        except Exception as e:
            logger.error(f"피드백 추가 실패: {e}")
            return False

    async def get_judgment_feedback(self, judgment_id: str) -> List[FeedbackEntry]:
        """판단에 대한 피드백 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM feedback WHERE judgment_id = ?
                ORDER BY timestamp DESC
            """,
                (judgment_id,),
            )

            results = cursor.fetchall()
            conn.close()

            feedback_entries = []
            for row in results:
                feedback = FeedbackEntry(
                    feedback_id=row[0],
                    judgment_id=row[1],
                    feedback_type=FeedbackType(row[2]),
                    content=row[3],
                    source=row[4],
                    impact_score=row[5],
                    timestamp=datetime.fromisoformat(row[6]),
                    metadata=json.loads(row[7]),
                )
                feedback_entries.append(feedback)

            return feedback_entries
        except Exception as e:
            logger.error(f"피드백 조회 실패: {e}")
            return []


class SelfImprovementSystem:
    """자기 개선 시스템"""

    def __init__(self, memory_system: JudgmentMemorySystem):
        self.memory_system = memory_system
        self.improvement_patterns = self._initialize_improvement_patterns()
        self.learning_metrics = self._initialize_learning_metrics()

    def _initialize_improvement_patterns(self) -> Dict[str, Dict]:
        """개선 패턴 초기화"""
        return {
            "confidence_improvement": {
                "pattern": "신뢰도 향상",
                "threshold": 0.1,
                "suggestions": ["더 많은 맥락 정보 수집", "다중 관점 분석 강화"],
            },
            "reasoning_consistency": {
                "pattern": "추론 일관성",
                "threshold": 0.8,
                "suggestions": ["논리적 단계 명확화", "전제 검증 강화"],
            },
            "feedback_integration": {
                "pattern": "피드백 통합",
                "threshold": 0.6,
                "suggestions": ["피드백 기반 학습", "패턴 인식 개선"],
            },
            "situation_adaptation": {
                "pattern": "상황 적응",
                "threshold": 0.7,
                "suggestions": ["유사 상황 학습", "맥락 분석 정교화"],
            },
        }

    def _initialize_learning_metrics(self) -> Dict[str, float]:
        """학습 메트릭 초기화"""
        return {
            "overall_improvement": 0.0,
            "confidence_trend": 0.0,
            "consistency_score": 0.0,
            "adaptation_rate": 0.0,
            "feedback_effectiveness": 0.0,
        }

    async def analyze_learning_progress(
        self, time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """학습 진행도 분석"""
        logger.info("학습 진행도 분석 시작")

        # 최근 판단들 조회
        recent_judgments = await self._get_recent_judgments(time_period)

        # 학습 메트릭 계산
        learning_metrics = await self._calculate_learning_metrics(recent_judgments)

        # 개선 패턴 식별
        improvement_patterns = await self._identify_improvement_patterns(recent_judgments)

        # 개선 제안 생성
        improvement_suggestions = await self._generate_improvement_suggestions(
            learning_metrics, improvement_patterns
        )

        return {
            "learning_metrics": learning_metrics,
            "improvement_patterns": improvement_patterns,
            "improvement_suggestions": improvement_suggestions,
            "analysis_period": time_period,
        }

    async def _get_recent_judgments(self, time_period: timedelta) -> List[JudgmentMemory]:
        """최근 판단들 조회"""
        try:
            conn = sqlite3.connect(self.memory_system.db_path)
            cursor = conn.cursor()

            cutoff_date = (datetime.now() - time_period).isoformat()

            cursor.execute(
                """
                SELECT * FROM judgments
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """,
                (cutoff_date,),
            )

            results = cursor.fetchall()
            conn.close()

            judgments = []
            for row in results:
                judgment = JudgmentMemory(
                    judgment_id=row[0],
                    situation=row[1],
                    judgment_type=JudgmentType(row[2]),
                    reasoning_process=json.loads(row[3]),
                    conclusion=row[4],
                    confidence_score=row[5],
                    timestamp=datetime.fromisoformat(row[6]),
                    context_metadata=json.loads(row[7]),
                )
                judgments.append(judgment)

            return judgments
        except Exception as e:
            logger.error(f"최근 판단 조회 실패: {e}")
            return []

    async def _calculate_learning_metrics(
        self, judgments: List[JudgmentMemory]
    ) -> Dict[str, float]:
        """학습 메트릭 계산"""
        if not judgments:
            return self.learning_metrics

        metrics = {}

        # 전체 개선도
        confidence_scores = [j.confidence_score for j in judgments]
        metrics["overall_improvement"] = sum(confidence_scores) / len(confidence_scores)

        # 신뢰도 트렌드
        if len(judgments) >= 2:
            recent_avg = sum(j.confidence_score for j in judgments[: len(judgments) // 2])
            older_avg = sum(j.confidence_score for j in judgments[len(judgments) // 2 :])
            metrics["confidence_trend"] = recent_avg - older_avg
        else:
            metrics["confidence_trend"] = 0.0

        # 일관성 점수
        judgment_types = [j.judgment_type for j in judgments]
        type_consistency = len(set(judgment_types)) / len(judgment_types)
        metrics["consistency_score"] = 1.0 - type_consistency

        # 적응률
        unique_situations = len(set(j.situation for j in judgments))
        metrics["adaptation_rate"] = unique_situations / len(judgments)

        # 피드백 효과성
        feedback_count = 0
        for judgment in judgments:
            feedback = await self.memory_system.get_judgment_feedback(judgment.judgment_id)
            feedback_count += len(feedback)

        metrics["feedback_effectiveness"] = min(feedback_count / len(judgments), 1.0)

        return metrics

    async def _identify_improvement_patterns(
        self, judgments: List[JudgmentMemory]
    ) -> List[Dict[str, Any]]:
        """개선 패턴 식별"""
        patterns = []

        if len(judgments) < 2:
            return patterns

        # 신뢰도 향상 패턴
        recent_judgments = judgments[: len(judgments) // 2]
        older_judgments = judgments[len(judgments) // 2 :]

        recent_avg_confidence = sum(j.confidence_score for j in recent_judgments) / len(
            recent_judgments
        )
        older_avg_confidence = sum(j.confidence_score for j in older_judgments) / len(
            older_judgments
        )

        if recent_avg_confidence - older_avg_confidence > 0.1:
            patterns.append(
                {
                    "pattern_type": "confidence_improvement",
                    "description": "신뢰도가 향상되고 있음",
                    "magnitude": recent_avg_confidence - older_avg_confidence,
                    "suggestions": self.improvement_patterns["confidence_improvement"][
                        "suggestions"
                    ],
                }
            )

        # 추론 일관성 패턴
        reasoning_consistency = self._calculate_reasoning_consistency(judgments)
        if reasoning_consistency > 0.8:
            patterns.append(
                {
                    "pattern_type": "reasoning_consistency",
                    "description": "추론 일관성이 높음",
                    "magnitude": reasoning_consistency,
                    "suggestions": self.improvement_patterns["reasoning_consistency"][
                        "suggestions"
                    ],
                }
            )

        return patterns

    def _calculate_reasoning_consistency(self, judgments: List[JudgmentMemory]) -> float:
        """추론 일관성 계산"""
        if not judgments:
            return 0.0

        # 간단한 일관성 계산: 동일한 상황에 대한 판단의 일관성
        situation_groups = {}
        for judgment in judgments:
            situation_key = judgment.situation[:50]  # 상황의 첫 50자로 그룹화
            if situation_key not in situation_groups:
                situation_groups[situation_key] = []
            situation_groups[situation_key].append(judgment)

        consistency_scores = []
        for group in situation_groups.values():
            if len(group) > 1:
                # 같은 상황에 대한 판단들의 신뢰도 분산 계산
                confidences = [j.confidence_score for j in group]
                variance = sum(
                    (c - sum(confidences) / len(confidences)) ** 2 for c in confidences
                ) / len(confidences)
                consistency_scores.append(1.0 - min(variance, 1.0))

        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0

    async def _generate_improvement_suggestions(
        self, metrics: Dict[str, float], patterns: List[Dict[str, Any]]
    ) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        # 메트릭 기반 제안
        if metrics["confidence_trend"] < 0:
            suggestions.append("신뢰도 향상을 위해 더 많은 맥락 정보를 수집하세요")

        if metrics["consistency_score"] < 0.7:
            suggestions.append("추론 일관성 향상을 위해 논리적 단계를 명확화하세요")

        if metrics["adaptation_rate"] < 0.5:
            suggestions.append("상황 적응력을 높이기 위해 다양한 상황에 대한 학습을 강화하세요")

        if metrics["feedback_effectiveness"] < 0.3:
            suggestions.append("피드백 활용도를 높이기 위해 피드백 수집 및 분석을 강화하세요")

        # 패턴 기반 제안
        for pattern in patterns:
            suggestions.extend(pattern["suggestions"])

        return list(set(suggestions))  # 중복 제거


class AdaptiveLearningEngine:
    """적응적 학습 엔진"""

    def __init__(
        self,
        memory_system: JudgmentMemorySystem,
        improvement_system: SelfImprovementSystem,
    ):
        self.memory_system = memory_system
        self.improvement_system = improvement_system
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.7

    async def adapt_to_feedback(self, judgment_id: str, feedback: FeedbackEntry) -> Dict[str, Any]:
        """피드백에 따른 적응"""
        logger.info(f"피드백 적응 시작: {judgment_id}")

        # 원본 판단 조회
        original_judgment = await self._get_judgment_by_id(judgment_id)
        if not original_judgment:
            return {"success": False, "reason": "판단을 찾을 수 없음"}

        # 피드백 분석
        feedback_analysis = self._analyze_feedback_impact(feedback, original_judgment)

        # 학습 패턴 업데이트
        learning_pattern = await self._update_learning_pattern(original_judgment, feedback)

        # 적응 제안 생성
        adaptation_suggestions = self._generate_adaptation_suggestions(
            feedback_analysis, learning_pattern
        )

        return {
            "success": True,
            "feedback_analysis": feedback_analysis,
            "learning_pattern": learning_pattern,
            "adaptation_suggestions": adaptation_suggestions,
        }

    async def _get_judgment_by_id(self, judgment_id: str) -> Optional[JudgmentMemory]:
        """ID로 판단 조회"""
        try:
            conn = sqlite3.connect(self.memory_system.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM judgments WHERE judgment_id = ?", (judgment_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                return JudgmentMemory(
                    judgment_id=result[0],
                    situation=result[1],
                    judgment_type=JudgmentType(result[2]),
                    reasoning_process=json.loads(result[3]),
                    conclusion=result[4],
                    confidence_score=result[5],
                    timestamp=datetime.fromisoformat(result[6]),
                    context_metadata=json.loads(result[7]),
                )

            return None
        except Exception as e:
            logger.error(f"판단 조회 실패: {e}")
            return None

    def _analyze_feedback_impact(
        self, feedback: FeedbackEntry, judgment: JudgmentMemory
    ) -> Dict[str, Any]:
        """피드백 영향 분석"""
        impact_analysis = {
            "impact_level": "low",
            "learning_potential": 0.0,
            "adaptation_needed": False,
            "key_insights": [],
        }

        # 피드백 타입에 따른 영향 분석
        if feedback.feedback_type == FeedbackType.NEGATIVE:
            impact_analysis["impact_level"] = "high"
            impact_analysis["learning_potential"] = 0.8
            impact_analysis["adaptation_needed"] = True
            impact_analysis["key_insights"].append("부정적 피드백으로 인한 개선 필요")

        elif feedback.feedback_type == FeedbackType.CORRECTIVE:
            impact_analysis["impact_level"] = "medium"
            impact_analysis["learning_potential"] = 0.6
            impact_analysis["adaptation_needed"] = True
            impact_analysis["key_insights"].append("수정적 피드백으로 인한 조정 필요")

        elif feedback.feedback_type == FeedbackType.ENHANCING:
            impact_analysis["impact_level"] = "medium"
            impact_analysis["learning_potential"] = 0.5
            impact_analysis["adaptation_needed"] = False
            impact_analysis["key_insights"].append("향상적 피드백으로 인한 개선 기회")

        # 신뢰도와 피드백의 관계 분석
        if judgment.confidence_score > 0.8 and feedback.impact_score > 0.7:
            impact_analysis["key_insights"].append(
                "높은 신뢰도에도 불구하고 피드백이 있음 - 재검토 필요"
            )

        return impact_analysis

    async def _update_learning_pattern(
        self, judgment: JudgmentMemory, feedback: FeedbackEntry
    ) -> LearningPattern:
        """학습 패턴 업데이트"""
        pattern_id = f"pattern_{judgment.judgment_type.value}_{feedback.feedback_type.value}"

        # 기존 패턴 조회 또는 새로 생성
        try:
            conn = sqlite3.connect(self.memory_system.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM learning_patterns WHERE pattern_id = ?
            """,
                (pattern_id,),
            )

            result = cursor.fetchone()

            if result:
                # 기존 패턴 업데이트
                frequency = result[2] + 1
                success_rate = (result[3] * (frequency - 1) + feedback.impact_score) / frequency

                cursor.execute(
                    """
                    UPDATE learning_patterns
                    SET frequency = ?, success_rate = ?, last_occurrence = ?
                    WHERE pattern_id = ?
                """,
                    (frequency, success_rate, datetime.now().isoformat(), pattern_id),
                )
            else:
                # 새 패턴 생성
                cursor.execute(
                    """
                    INSERT INTO learning_patterns VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        pattern_id,
                        f"{judgment.judgment_type.value}_{feedback.feedback_type.value}",
                        1,
                        feedback.impact_score,
                        datetime.now().isoformat(),
                        json.dumps([]),
                    ),
                )

            conn.commit()
            conn.close()

            return LearningPattern(
                pattern_id=pattern_id,
                pattern_type=f"{judgment.judgment_type.value}_{feedback.feedback_type.value}",
                frequency=result[2] + 1 if result else 1,
                success_rate=success_rate if result else feedback.impact_score,
                last_occurrence=datetime.now(),
                improvement_suggestions=[],
            )

        except Exception as e:
            logger.error(f"학습 패턴 업데이트 실패: {e}")
            return LearningPattern(
                pattern_id=pattern_id,
                pattern_type="unknown",
                frequency=1,
                success_rate=0.0,
                last_occurrence=datetime.now(),
                improvement_suggestions=[],
            )

    def _generate_adaptation_suggestions(
        self, feedback_analysis: Dict[str, Any], learning_pattern: LearningPattern
    ) -> List[str]:
        """적응 제안 생성"""
        suggestions = []

        if feedback_analysis["adaptation_needed"]:
            suggestions.append("피드백을 반영하여 판단 기준을 조정하세요")
            suggestions.append("유사한 상황에서 더 신중한 분석을 수행하세요")

        if learning_pattern.success_rate < 0.5:
            suggestions.append("해당 패턴의 성공률이 낮으므로 접근 방식을 재검토하세요")

        if learning_pattern.frequency > 5:
            suggestions.append("반복되는 패턴이므로 체계적인 개선이 필요합니다")

        return suggestions


async def test_learning_feedback_system():
    """학습 피드백 시스템 테스트"""
    print("=== 학습 피드백 시스템 테스트 시작 (Day 6) ===")

    # 시스템 초기화
    memory_system = JudgmentMemorySystem()
    improvement_system = SelfImprovementSystem(memory_system)
    learning_engine = AdaptiveLearningEngine(memory_system, improvement_system)

    # 테스트 판단 저장
    test_judgment = JudgmentMemory(
        judgment_id="test_judgment_001",
        situation="거짓말을 해야 하는 상황",
        judgment_type=JudgmentType.ETHICAL,
        reasoning_process={
            "semantic_analysis": {"situation_type": "ethical_dilemma"},
            "philosophical_analysis": {"kantian": "금지", "utilitarian": "금지"},
        },
        conclusion="거짓말은 도덕적으로 허용되지 않는다",
        confidence_score=0.8,
        timestamp=datetime.now(),
        context_metadata={"complexity": "high", "urgency": "medium"},
    )

    await memory_system.store_judgment(test_judgment)

    # 테스트 피드백 추가
    test_feedback = FeedbackEntry(
        feedback_id="test_feedback_001",
        judgment_id="test_judgment_001",
        feedback_type=FeedbackType.CORRECTIVE,
        content="상황의 맥락을 더 고려해야 한다",
        source="human_expert",
        impact_score=0.7,
        timestamp=datetime.now(),
        metadata={"expertise_level": "high"},
    )

    await memory_system.add_feedback(test_feedback)

    # 학습 진행도 분석
    learning_progress = await improvement_system.analyze_learning_progress()

    print(f"\n📊 학습 진행도 분석:")
    print(f"  • 전체 개선도: {learning_progress['learning_metrics']['overall_improvement']:.2f}")
    print(f"  • 신뢰도 트렌드: {learning_progress['learning_metrics']['confidence_trend']:.2f}")
    print(f"  • 일관성 점수: {learning_progress['learning_metrics']['consistency_score']:.2f}")
    print(f"  • 적응률: {learning_progress['learning_metrics']['adaptation_rate']:.2f}")
    print(
        f"  • 피드백 효과성: {learning_progress['learning_metrics']['feedback_effectiveness']:.2f}"
    )

    print(f"\n🔍 개선 패턴:")
    for pattern in learning_progress["improvement_patterns"]:
        print(f"  • {pattern['pattern_type']}: {pattern['description']}")

    print(f"\n💡 개선 제안:")
    for suggestion in learning_progress["improvement_suggestions"]:
        print(f"  • {suggestion}")

    # 피드백 적응 테스트
    adaptation_result = await learning_engine.adapt_to_feedback("test_judgment_001", test_feedback)

    print(f"\n🔄 피드백 적응 결과:")
    print(f"  • 성공: {adaptation_result['success']}")
    print(f"  • 영향 수준: {adaptation_result['feedback_analysis']['impact_level']}")
    print(f"  • 학습 잠재력: {adaptation_result['feedback_analysis']['learning_potential']:.2f}")
    print(f"  • 적응 필요: {adaptation_result['feedback_analysis']['adaptation_needed']}")

    print(f"\n📝 적응 제안:")
    for suggestion in adaptation_result["adaptation_suggestions"]:
        print(f"  • {suggestion}")

    print(f"\n{'='*70}")
    print("=== 학습 피드백 시스템 테스트 완료 (Day 6) ===")
    print("✅ Day 6 목표 달성: 일회성 판단 → 지속적 개선")
    print("✅ 판단 기억 시스템 및 자기 개선 시스템 구현")
    print("✅ 적응적 학습 엔진 및 피드백 통합 시스템 구현")


if __name__ == "__main__":
    asyncio.run(test_learning_feedback_system())
