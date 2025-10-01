"""
DuRi 성능 히스토리 관리 시스템

성능 데이터를 수집, 저장, 분석하여 리팩터링 예측에 활용합니다.
"""

import json
import logging
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """성능 지표 유형"""

    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    LEARNING_CYCLE_TIME = "learning_cycle_time"
    MEMORY_GROWTH_RATE = "memory_growth_rate"
    SYSTEM_COMPLEXITY = "system_complexity"


@dataclass
class PerformanceSnapshot:
    """성능 스냅샷"""

    timestamp: datetime
    metrics: Dict[str, float]
    module_name: str
    operation_type: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class PerformanceTrend:
    """성능 경향"""

    metric_name: str
    start_time: datetime
    end_time: datetime
    initial_value: float
    final_value: float
    change_rate: float  # 변화율 (%)
    trend_direction: str  # "improving", "degrading", "stable"
    confidence: float  # 신뢰도 (0.0 ~ 1.0)


class PerformanceHistory:
    """DuRi 성능 히스토리 관리 시스템"""

    def __init__(self, db_path: str = "duri_performance.db"):
        """PerformanceHistory 초기화"""
        self.db_path = db_path
        self.snapshots: List[PerformanceSnapshot] = []
        self.trends: List[PerformanceTrend] = []
        self.is_collecting = False
        self.collection_thread: Optional[threading.Thread] = None

        # 데이터베이스 초기화
        self._init_database()

        # 수집 설정
        self.collection_interval = 30  # 30초마다 수집
        self.max_history_days = 30  # 30일간 보관
        self.trend_analysis_window = 24  # 24시간 윈도우로 경향 분석

        logger.info("PerformanceHistory 초기화 완료")

    def _init_database(self):
        """데이터베이스를 초기화합니다."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 성능 스냅샷 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    module_name TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    success INTEGER NOT NULL,
                    error_message TEXT,
                    metrics TEXT NOT NULL
                )
            """
            )

            # 성능 경향 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    initial_value REAL NOT NULL,
                    final_value REAL NOT NULL,
                    change_rate REAL NOT NULL,
                    trend_direction TEXT NOT NULL,
                    confidence REAL NOT NULL
                )
            """
            )

            conn.commit()
            conn.close()
            logger.info("성능 데이터베이스 초기화 완료")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")

    def start_collection(self):
        """성능 데이터 수집을 시작합니다."""
        if self.is_collecting:
            logger.warning("이미 수집 중입니다.")
            return

        self.is_collecting = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop, daemon=True
        )
        self.collection_thread.start()
        logger.info("성능 데이터 수집 시작")

    def stop_collection(self):
        """성능 데이터 수집을 중지합니다."""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("성능 데이터 수집 중지")

    def _collection_loop(self):
        """성능 데이터 수집 루프"""
        while self.is_collecting:
            try:
                # 현재 성능 상태 수집
                current_metrics = self._collect_current_metrics()

                # 스냅샷 생성
                snapshot = PerformanceSnapshot(
                    timestamp=datetime.now(),
                    metrics=current_metrics,
                    module_name="system_overview",
                    operation_type="periodic_collection",
                    duration_ms=0.0,
                    success=True,
                )

                # 데이터베이스에 저장
                self._save_snapshot(snapshot)

                # 경향 분석 (24시간마다)
                if self._should_analyze_trends():
                    self._analyze_performance_trends()

                # 오래된 데이터 정리 (7일마다)
                if self._should_cleanup_old_data():
                    self._cleanup_old_data()

                time.sleep(self.collection_interval)

            except Exception as e:
                logger.error(f"성능 데이터 수집 중 오류: {e}")
                time.sleep(5)  # 오류 시 잠시 대기

    def _collect_current_metrics(self) -> Dict[str, float]:
        """현재 성능 지표를 수집합니다."""
        import psutil

        try:
            # 시스템 메트릭
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # DuRi 특화 메트릭 (시뮬레이션)
            learning_cycle_time = self._get_learning_cycle_time()
            error_rate = self._get_error_rate()
            memory_growth_rate = self._get_memory_growth_rate()
            system_complexity = self._get_system_complexity()

            return {
                PerformanceMetric.CPU_USAGE.value: cpu_percent,
                PerformanceMetric.MEMORY_USAGE.value: memory_percent,
                PerformanceMetric.LEARNING_CYCLE_TIME.value: learning_cycle_time,
                PerformanceMetric.ERROR_RATE.value: error_rate,
                PerformanceMetric.MEMORY_GROWTH_RATE.value: memory_growth_rate,
                PerformanceMetric.SYSTEM_COMPLEXITY.value: system_complexity,
            }

        except Exception as e:
            logger.error(f"성능 지표 수집 실패: {e}")
            return {}

    def _get_learning_cycle_time(self) -> float:
        """학습 사이클 시간을 측정합니다."""
        # 실제 구현에서는 LearningLoopManager에서 가져옴
        return 2.5  # 시뮬레이션 값

    def _get_error_rate(self) -> float:
        """오류율을 계산합니다."""
        # 실제 구현에서는 로그 분석을 통해 계산
        return 0.02  # 2% 시뮬레이션

    def _get_memory_growth_rate(self) -> float:
        """메모리 성장률을 계산합니다."""
        # 실제 구현에서는 메모리 사용량 변화율 계산
        return 0.05  # 5% 시뮬레이션

    def _get_system_complexity(self) -> float:
        """시스템 복잡도를 계산합니다."""
        # 실제 구현에서는 모듈 수, 함수 수 등을 기반으로 계산
        return 0.75  # 75% 시뮬레이션

    def _save_snapshot(self, snapshot: PerformanceSnapshot):
        """성능 스냅샷을 데이터베이스에 저장합니다."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO performance_snapshots
                (timestamp, module_name, operation_type, duration_ms, success, error_message, metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    snapshot.timestamp.isoformat(),
                    snapshot.module_name,
                    snapshot.operation_type,
                    snapshot.duration_ms,
                    1 if snapshot.success else 0,
                    snapshot.error_message,
                    json.dumps(snapshot.metrics),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"스냅샷 저장 실패: {e}")

    def _should_analyze_trends(self) -> bool:
        """경향 분석이 필요한지 확인합니다."""
        # 24시간마다 분석
        return True  # 시뮬레이션을 위해 항상 True

    def _should_cleanup_old_data(self) -> bool:
        """오래된 데이터 정리가 필요한지 확인합니다."""
        # 7일마다 정리
        return False  # 시뮬레이션을 위해 False

    def _analyze_performance_trends(self):
        """성능 경향을 분석합니다."""
        try:
            # 최근 24시간 데이터 조회
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=self.trend_analysis_window)

            trends = self._calculate_trends(start_time, end_time)

            # 경향 저장
            for trend in trends:
                self._save_trend(trend)

            logger.info(f"성능 경향 분석 완료: {len(trends)}개 지표")

        except Exception as e:
            logger.error(f"경향 분석 실패: {e}")

    def _calculate_trends(
        self, start_time: datetime, end_time: datetime
    ) -> List[PerformanceTrend]:
        """특정 기간의 성능 경향을 계산합니다."""
        trends = []

        # 각 성능 지표별로 경향 계산
        for metric in PerformanceMetric:
            try:
                trend = self._calculate_metric_trend(metric.value, start_time, end_time)
                if trend:
                    trends.append(trend)
            except Exception as e:
                logger.error(f"{metric.value} 경향 계산 실패: {e}")

        return trends

    def _calculate_metric_trend(
        self, metric_name: str, start_time: datetime, end_time: datetime
    ) -> Optional[PerformanceTrend]:
        """특정 지표의 경향을 계산합니다."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 시작과 끝 값 조회
            cursor.execute(
                """
                SELECT metrics FROM performance_snapshots
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """,
                (start_time.isoformat(), end_time.isoformat()),
            )

            rows = cursor.fetchall()
            if len(rows) < 2:
                return None

            # 첫 번째와 마지막 값 추출
            first_metrics = json.loads(rows[0][0])
            last_metrics = json.loads(rows[-1][0])

            initial_value = first_metrics.get(metric_name, 0.0)
            final_value = last_metrics.get(metric_name, 0.0)

            # 변화율 계산
            if initial_value != 0:
                change_rate = ((final_value - initial_value) / initial_value) * 100
            else:
                change_rate = 0.0

            # 경향 방향 결정
            if change_rate > 5:
                trend_direction = "degrading"
            elif change_rate < -5:
                trend_direction = "improving"
            else:
                trend_direction = "stable"

            # 신뢰도 계산 (데이터 포인트 수 기반)
            confidence = min(len(rows) / 100.0, 1.0)

            conn.close()

            return PerformanceTrend(
                metric_name=metric_name,
                start_time=start_time,
                end_time=end_time,
                initial_value=initial_value,
                final_value=final_value,
                change_rate=change_rate,
                trend_direction=trend_direction,
                confidence=confidence,
            )

        except Exception as e:
            logger.error(f"{metric_name} 경향 계산 실패: {e}")
            return None

    def _save_trend(self, trend: PerformanceTrend):
        """성능 경향을 데이터베이스에 저장합니다."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO performance_trends
                (metric_name, start_time, end_time, initial_value, final_value,
                 change_rate, trend_direction, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    trend.metric_name,
                    trend.start_time.isoformat(),
                    trend.end_time.isoformat(),
                    trend.initial_value,
                    trend.final_value,
                    trend.change_rate,
                    trend.trend_direction,
                    trend.confidence,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"경향 저장 실패: {e}")

    def get_recent_trends(self, hours: int = 24) -> List[PerformanceTrend]:
        """최근 경향을 조회합니다."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)

            cursor.execute(
                """
                SELECT metric_name, start_time, end_time, initial_value, final_value,
                       change_rate, trend_direction, confidence
                FROM performance_trends
                WHERE end_time >= ?
                ORDER BY end_time DESC
            """,
                (start_time.isoformat(),),
            )

            trends = []
            for row in cursor.fetchall():
                trend = PerformanceTrend(
                    metric_name=row[0],
                    start_time=datetime.fromisoformat(row[1]),
                    end_time=datetime.fromisoformat(row[2]),
                    initial_value=row[3],
                    final_value=row[4],
                    change_rate=row[5],
                    trend_direction=row[6],
                    confidence=row[7],
                )
                trends.append(trend)

            conn.close()
            return trends

        except Exception as e:
            logger.error(f"최근 경향 조회 실패: {e}")
            return []

    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약을 반환합니다."""
        try:
            recent_trends = self.get_recent_trends(24)

            # 경고 지표 식별
            warning_metrics = [
                trend
                for trend in recent_trends
                if trend.trend_direction == "degrading" and trend.confidence > 0.7
            ]

            # 개선 지표 식별
            improving_metrics = [
                trend
                for trend in recent_trends
                if trend.trend_direction == "improving" and trend.confidence > 0.7
            ]

            return {
                "total_trends": len(recent_trends),
                "warning_metrics": len(warning_metrics),
                "improving_metrics": len(improving_metrics),
                "warning_details": [
                    {
                        "metric": trend.metric_name,
                        "change_rate": f"{trend.change_rate:.1f}%",
                        "confidence": f"{trend.confidence:.1f}",
                    }
                    for trend in warning_metrics
                ],
                "improving_details": [
                    {
                        "metric": trend.metric_name,
                        "change_rate": f"{trend.change_rate:.1f}%",
                        "confidence": f"{trend.confidence:.1f}",
                    }
                    for trend in improving_metrics
                ],
            }

        except Exception as e:
            logger.error(f"성능 요약 생성 실패: {e}")
            return {}


# 전역 인스턴스
_performance_history: Optional[PerformanceHistory] = None


def get_performance_history() -> PerformanceHistory:
    """PerformanceHistory 인스턴스를 반환합니다."""
    global _performance_history
    if _performance_history is None:
        _performance_history = PerformanceHistory()
    return _performance_history


if __name__ == "__main__":
    # 테스트
    history = get_performance_history()
    history.start_collection()

    print("📊 성능 히스토리 시스템 테스트 시작")
    print("⏰ 30초간 데이터 수집 중...")

    time.sleep(30)

    summary = history.get_performance_summary()
    print(f"📈 성능 요약: {summary}")

    history.stop_collection()
    print("✅ 테스트 완료")
