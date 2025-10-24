#!/usr/bin/env python3
"""
대화 로그 수집 및 분석 시스템 - DuRi의 실제 학습 데이터 수집
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ConversationEntry:
    """대화 엔트리"""

    timestamp: str
    user_input: str
    duri_response: str
    response_time: float
    success: bool
    learning_patterns: List[str]
    improvement_areas: List[str]
    evolution_metrics: Dict[str, float]


@dataclass
class EvolutionLog:
    """진화 로그"""

    conversation_id: str
    start_time: str
    end_time: str
    total_exchanges: int
    average_response_time: float
    learning_efficiency: float
    problem_solving_score: float
    autonomy_level: float
    evolution_patterns: List[str]
    key_insights: List[str]


class ConversationLogger:
    """대화 로그 수집 및 분석 시스템"""

    def __init__(self, log_dir: str = "conversation_logs"):
        self.log_dir = log_dir
        self.current_conversation = []
        self.conversation_history = []
        self.evolution_logs = []

        # 로그 디렉토리 생성
        os.makedirs(log_dir, exist_ok=True)

        # 기존 로그 로드
        self._load_existing_logs()

        logger.info("🧠 대화 로그 수집 시스템 초기화 완료")

    def start_conversation(self, conversation_id: str = None) -> str:
        """새로운 대화 시작"""
        if not conversation_id:
            conversation_id = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_conversation = []
        self.current_conversation_id = conversation_id

        logger.info(f"🔄 대화 시작: {conversation_id}")
        return conversation_id

    def log_exchange(
        self,
        user_input: str,
        duri_response: str,
        response_time: float,
        success: bool = True,
        learning_patterns: List[str] = None,
        improvement_areas: List[str] = None,
        evolution_metrics: Dict[str, float] = None,
    ):
        """대화 교환 로그"""
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            duri_response=duri_response,
            response_time=response_time,
            success=success,
            learning_patterns=learning_patterns or [],
            improvement_areas=improvement_areas or [],
            evolution_metrics=evolution_metrics or {},
        )

        self.current_conversation.append(entry)

        # 실시간 분석
        self._analyze_exchange(entry)

        logger.info(
            f"📝 대화 교환 로그: {response_time:.3f}초 ({'성공' if success else '실패'})"
        )

    def end_conversation(self) -> EvolutionLog:
        """대화 종료 및 진화 로그 생성"""
        if not self.current_conversation:
            return None

        # 대화 요약 생성
        evolution_log = self._create_evolution_log()

        # 로그 저장
        self._save_conversation_log()
        self._save_evolution_log(evolution_log)

        # 히스토리에 추가
        self.conversation_history.append(self.current_conversation)
        self.evolution_logs.append(evolution_log)

        logger.info(
            f"🏁 대화 종료: {evolution_log.total_exchanges}교환, 효율성 {evolution_log.learning_efficiency:.3f}"
        )

        return evolution_log

    def get_conversation_statistics(self) -> Dict[str, Any]:
        """대화 통계 반환"""
        if not self.evolution_logs:
            return {"status": "no_data"}

        total_conversations = len(self.evolution_logs)
        total_exchanges = sum(log.total_exchanges for log in self.evolution_logs)
        avg_response_time = (
            sum(log.average_response_time for log in self.evolution_logs)
            / total_conversations
        )
        avg_learning_efficiency = (
            sum(log.learning_efficiency for log in self.evolution_logs)
            / total_conversations
        )
        avg_problem_solving = (
            sum(log.problem_solving_score for log in self.evolution_logs)
            / total_conversations
        )
        avg_autonomy = (
            sum(log.autonomy_level for log in self.evolution_logs) / total_conversations
        )

        # 진화 패턴 분석
        evolution_patterns = self._analyze_evolution_patterns()

        return {
            "status": "success",
            "total_conversations": total_conversations,
            "total_exchanges": total_exchanges,
            "average_response_time": avg_response_time,
            "average_learning_efficiency": avg_learning_efficiency,
            "average_problem_solving": avg_problem_solving,
            "average_autonomy": avg_autonomy,
            "evolution_patterns": evolution_patterns,
            "recent_trends": self._analyze_recent_trends(),
        }

    def extract_learning_patterns(self) -> List[Dict[str, Any]]:
        """학습 패턴 추출"""
        patterns = []

        for conversation in self.conversation_history:
            for entry in conversation:
                if entry.learning_patterns:
                    for pattern in entry.learning_patterns:
                        patterns.append(
                            {
                                "timestamp": entry.timestamp,
                                "pattern": pattern,
                                "context": (
                                    entry.user_input[:100] + "..."
                                    if len(entry.user_input) > 100
                                    else entry.user_input
                                ),
                            }
                        )

        return patterns

    def get_improvement_suggestions(self) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        # 응답 시간 분석
        response_times = [
            entry.response_time for conv in self.conversation_history for entry in conv
        ]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            if avg_response_time > 2.0:
                suggestions.append(
                    "응답 시간이 2초를 초과합니다. 성능 최적화가 필요합니다."
                )

        # 학습 효율성 분석
        learning_efficiencies = [log.learning_efficiency for log in self.evolution_logs]
        if learning_efficiencies:
            avg_efficiency = sum(learning_efficiencies) / len(learning_efficiencies)
            if avg_efficiency < 0.6:
                suggestions.append(
                    "학습 효율성이 낮습니다. 학습 방법 개선이 필요합니다."
                )

        # 자율성 분석
        autonomy_levels = [log.autonomy_level for log in self.evolution_logs]
        if autonomy_levels:
            avg_autonomy = sum(autonomy_levels) / len(autonomy_levels)
            if avg_autonomy < 0.5:
                suggestions.append(
                    "자율성이 낮습니다. 자율적 의사결정 능력 향상이 필요합니다."
                )

        return suggestions

    def _analyze_exchange(self, entry: ConversationEntry):
        """교환 분석"""
        # 학습 패턴 자동 감지
        if "개선" in entry.user_input or "수정" in entry.user_input:
            entry.learning_patterns.append("feedback_learning")

        if "왜" in entry.user_input or "어떻게" in entry.user_input:
            entry.learning_patterns.append("explanation_seeking")

        if "예시" in entry.user_input or "예를 들어" in entry.user_input:
            entry.learning_patterns.append("example_based_learning")

        # 진화 메트릭 계산
        entry.evolution_metrics = {
            "response_quality": (
                min(1.0, 1.0 / entry.response_time) if entry.response_time > 0 else 0.0
            ),
            "learning_depth": len(entry.learning_patterns) / 10.0,
            "problem_solving": 1.0 if entry.success else 0.5,
        }

    def _create_evolution_log(self) -> EvolutionLog:
        """진화 로그 생성"""
        if not self.current_conversation:
            return None

        start_time = self.current_conversation[0].timestamp
        end_time = self.current_conversation[-1].timestamp

        # 평균 응답 시간
        response_times = [entry.response_time for entry in self.current_conversation]
        avg_response_time = sum(response_times) / len(response_times)

        # 학습 효율성 계산
        learning_patterns = [
            pattern
            for entry in self.current_conversation
            for pattern in entry.learning_patterns
        ]
        learning_efficiency = min(
            1.0, len(learning_patterns) / len(self.current_conversation)
        )

        # 문제 해결 점수
        success_count = sum(1 for entry in self.current_conversation if entry.success)
        problem_solving_score = success_count / len(self.current_conversation)

        # 자율성 레벨 (사용자 개입 최소화)
        autonomous_responses = sum(
            1 for entry in self.current_conversation if len(entry.learning_patterns) > 0
        )
        autonomy_level = autonomous_responses / len(self.current_conversation)

        # 진화 패턴 분석
        evolution_patterns = self._extract_conversation_patterns()

        # 핵심 인사이트
        key_insights = self._extract_key_insights()

        return EvolutionLog(
            conversation_id=self.current_conversation_id,
            start_time=start_time,
            end_time=end_time,
            total_exchanges=len(self.current_conversation),
            average_response_time=avg_response_time,
            learning_efficiency=learning_efficiency,
            problem_solving_score=problem_solving_score,
            autonomy_level=autonomy_level,
            evolution_patterns=evolution_patterns,
            key_insights=key_insights,
        )

    def _extract_conversation_patterns(self) -> List[str]:
        """대화 패턴 추출"""
        patterns = []

        # 응답 시간 패턴
        response_times = [entry.response_time for entry in self.current_conversation]
        if len(response_times) > 1:
            if all(t2 >= t1 for t1, t2 in zip(response_times[:-1], response_times[1:])):
                patterns.append("response_time_increasing")
            elif all(
                t2 <= t1 for t1, t2 in zip(response_times[:-1], response_times[1:])
            ):
                patterns.append("response_time_decreasing")

        # 학습 패턴
        learning_counts = [
            len(entry.learning_patterns) for entry in self.current_conversation
        ]
        if any(count > 0 for count in learning_counts):
            patterns.append("active_learning")

        # 성공 패턴
        success_rate = sum(
            1 for entry in self.current_conversation if entry.success
        ) / len(self.current_conversation)
        if success_rate > 0.8:
            patterns.append("high_success_rate")
        elif success_rate < 0.5:
            patterns.append("low_success_rate")

        return patterns

    def _extract_key_insights(self) -> List[str]:
        """핵심 인사이트 추출"""
        insights = []

        # 가장 긴 응답 시간
        max_response_time = max(
            entry.response_time for entry in self.current_conversation
        )
        if max_response_time > 3.0:
            insights.append(f"최대 응답 시간: {max_response_time:.2f}초 (개선 필요)")

        # 학습 패턴
        total_learning_patterns = sum(
            len(entry.learning_patterns) for entry in self.current_conversation
        )
        if total_learning_patterns > 0:
            insights.append(f"학습 패턴 {total_learning_patterns}개 감지됨")

        # 성공률
        success_rate = sum(
            1 for entry in self.current_conversation if entry.success
        ) / len(self.current_conversation)
        insights.append(f"성공률: {success_rate:.1%}")

        return insights

    def _analyze_evolution_patterns(self) -> Dict[str, Any]:
        """진화 패턴 분석"""
        if not self.evolution_logs:
            return {}

        patterns = {}
        for log in self.evolution_logs:
            for pattern in log.evolution_patterns:
                patterns[pattern] = patterns.get(pattern, 0) + 1

        return patterns

    def _analyze_recent_trends(self) -> Dict[str, Any]:
        """최근 트렌드 분석"""
        if len(self.evolution_logs) < 2:
            return {}

        recent_logs = self.evolution_logs[-5:]  # 최근 5개 대화

        trends = {
            "response_time_trend": "stable",
            "learning_efficiency_trend": "stable",
            "problem_solving_trend": "stable",
            "autonomy_trend": "stable",
        }

        # 응답 시간 트렌드
        response_times = [log.average_response_time for log in recent_logs]
        if len(response_times) >= 2:
            if response_times[-1] < response_times[0]:
                trends["response_time_trend"] = "improving"
            elif response_times[-1] > response_times[0]:
                trends["response_time_trend"] = "declining"

        # 학습 효율성 트렌드
        efficiencies = [log.learning_efficiency for log in recent_logs]
        if len(efficiencies) >= 2:
            if efficiencies[-1] > efficiencies[0]:
                trends["learning_efficiency_trend"] = "improving"
            elif efficiencies[-1] < efficiencies[0]:
                trends["learning_efficiency_trend"] = "declining"

        return trends

    def _save_conversation_log(self):
        """대화 로그 저장"""
        if not self.current_conversation:
            return

        log_file = os.path.join(self.log_dir, f"{self.current_conversation_id}.json")

        conversation_data = {
            "conversation_id": self.current_conversation_id,
            "entries": [asdict(entry) for entry in self.current_conversation],
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)

    def _save_evolution_log(self, evolution_log: EvolutionLog):
        """진화 로그 저장"""
        if not evolution_log:
            return

        log_file = os.path.join(
            self.log_dir, f"evolution_{evolution_log.conversation_id}.json"
        )

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(asdict(evolution_log), f, ensure_ascii=False, indent=2)

    def _load_existing_logs(self):
        """기존 로그 로드"""
        try:
            # 진화 로그 파일들 로드
            for filename in os.listdir(self.log_dir):
                if filename.startswith("evolution_") and filename.endswith(".json"):
                    filepath = os.path.join(self.log_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        log_data = json.load(f)
                        evolution_log = EvolutionLog(**log_data)
                        self.evolution_logs.append(evolution_log)

            logger.info(f"📚 기존 진화 로그 {len(self.evolution_logs)}개 로드 완료")
        except Exception as e:
            logger.error(f"기존 로그 로드 오류: {e}")


# 전역 인스턴스 생성
conversation_logger = ConversationLogger()
