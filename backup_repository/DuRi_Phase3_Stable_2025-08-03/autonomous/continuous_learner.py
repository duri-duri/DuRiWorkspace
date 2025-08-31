#!/usr/bin/env python3
"""
DuRi 24/7 자동 학습 시스템
백그라운드에서 지속적으로 학습하고, 문제 발생 시에만 사용자에게 보고
"""
import asyncio
import time
import threading
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('duri_autonomous_learning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LearningSession:
    """학습 세션 정보"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    learning_cycles: int = 0
    problems_detected: int = 0
    decisions_made: int = 0
    status: str = "active"

class AutonomousLearner:
    def __init__(self):
        self.is_running = False
        self.learning_thread = None
        self.current_session = None
        self.learning_interval = 300  # 5분마다 학습
        self.problem_threshold = 0.3  # 문제 감지 임계값
        self.decision_threshold = 0.7  # 결정 필요 임계값
        self.last_report_time = datetime.now()
        self.report_interval = 3600  # 1시간마다 상태 보고
        
        # 학습 통계
        self.total_learning_cycles = 0
        self.total_problems_detected = 0
        self.total_decisions_made = 0
        self.learning_history = []
        
        # 문제 감지 패턴
        self.problem_patterns = {
            "error_rate_high": {"threshold": 0.1, "description": "오류율이 높음"},
            "response_time_slow": {"threshold": 2.0, "description": "응답 시간이 느림"},
            "learning_stagnation": {"threshold": 0.1, "description": "학습 진전이 없음"},
            "memory_usage_high": {"threshold": 0.8, "description": "메모리 사용량이 높음"},
            "cpu_usage_high": {"threshold": 0.9, "description": "CPU 사용량이 높음"}
        }
        
        # 자동 결정 규칙
        self.decision_rules = {
            "restart_service": {"condition": "error_rate > 0.2", "action": "서비스 재시작"},
            "optimize_memory": {"condition": "memory_usage > 0.9", "action": "메모리 최적화"},
            "adjust_learning_rate": {"condition": "learning_stagnation > 0.3", "action": "학습률 조정"},
            "backup_data": {"condition": "session_duration > 3600", "action": "데이터 백업"}
        }

    def start_autonomous_learning(self):
        """자동 학습 시작"""
        if self.is_running:
            logger.warning("자동 학습이 이미 실행 중입니다.")
            return False
            
        self.is_running = True
        self.current_session = LearningSession(
            session_id=f"session_{int(time.time())}",
            start_time=datetime.now()
        )
        
        self.learning_thread = threading.Thread(target=self._learning_loop)
        self.learning_thread.daemon = True
        self.learning_thread.start()
        
        logger.info("🚀 DuRi 24/7 자동 학습 시스템 시작")
        return True

    def stop_autonomous_learning(self):
        """자동 학습 중지"""
        if not self.is_running:
            logger.warning("자동 학습이 실행 중이 아닙니다.")
            return False
            
        self.is_running = False
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.status = "completed"
            
        logger.info("🛑 DuRi 자동 학습 시스템 중지")
        return True

    def _learning_loop(self):
        """메인 학습 루프"""
        while self.is_running:
            try:
                # 학습 사이클 실행
                self._execute_learning_cycle()
                
                # 문제 감지
                problems = self._detect_problems()
                if problems:
                    self._handle_problems(problems)
                
                # 자동 결정 실행
                decisions = self._make_automatic_decisions()
                if decisions:
                    self._execute_decisions(decisions)
                
                # 정기 보고
                self._check_reporting_needs()
                
                # 대기
                time.sleep(self.learning_interval)
                
            except Exception as e:
                logger.error(f"학습 루프 오류: {e}")
                self._report_problem("learning_loop_error", str(e))

    def _execute_learning_cycle(self):
        """단일 학습 사이클 실행"""
        try:
            # 학습 데이터 수집
            learning_data = self._collect_learning_data()
            
            # 학습 메트릭 계산
            metrics = self._calculate_learning_metrics(learning_data)
            
            # 학습 진전 평가
            progress = self._evaluate_learning_progress(metrics)
            
            # 학습 기록 저장
            self._save_learning_record(metrics, progress)
            
            self.total_learning_cycles += 1
            if self.current_session:
                self.current_session.learning_cycles += 1
                
            logger.debug(f"학습 사이클 완료: {self.total_learning_cycles}")
            
        except Exception as e:
            logger.error(f"학습 사이클 오류: {e}")

    def _collect_learning_data(self) -> Dict[str, Any]:
        """학습 데이터 수집"""
        # 실제 구현에서는 시스템 메트릭, 대화 데이터 등을 수집
        return {
            "timestamp": datetime.now().isoformat(),
            "memory_usage": self._get_memory_usage(),
            "cpu_usage": self._get_cpu_usage(),
            "error_count": self._get_error_count(),
            "response_time": self._get_average_response_time(),
            "learning_patterns": self._get_learning_patterns()
        }

    def _calculate_learning_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """학습 메트릭 계산"""
        return {
            "error_rate": data.get("error_count", 0) / max(self.total_learning_cycles, 1),
            "avg_response_time": data.get("response_time", 0.0),
            "memory_efficiency": 1.0 - data.get("memory_usage", 0.0),
            "learning_progress": self._calculate_progress_score(data),
            "system_health": self._calculate_health_score(data)
        }

    def _detect_problems(self) -> List[Dict[str, Any]]:
        """문제 감지"""
        problems = []
        current_metrics = self._get_current_metrics()
        
        for problem_name, pattern in self.problem_patterns.items():
            if self._check_problem_condition(problem_name, current_metrics, pattern):
                problems.append({
                    "type": problem_name,
                    "description": pattern["description"],
                    "severity": self._calculate_severity(current_metrics, pattern),
                    "timestamp": datetime.now().isoformat()
                })
                
        return problems

    def _make_automatic_decisions(self) -> List[Dict[str, Any]]:
        """자동 결정 생성"""
        decisions = []
        current_metrics = self._get_current_metrics()
        
        for rule_name, rule in self.decision_rules.items():
            if self._evaluate_decision_rule(rule_name, current_metrics, rule):
                decisions.append({
                    "rule": rule_name,
                    "action": rule["action"],
                    "reason": self._get_decision_reason(rule_name, current_metrics),
                    "timestamp": datetime.now().isoformat()
                })
                
        return decisions

    def _handle_problems(self, problems: List[Dict[str, Any]]):
        """문제 처리"""
        for problem in problems:
            self.total_problems_detected += 1
            if self.current_session:
                self.current_session.problems_detected += 1
                
            # 심각한 문제는 즉시 보고
            if problem["severity"] > 0.7:
                self._report_problem(problem["type"], problem["description"])
            else:
                logger.warning(f"문제 감지: {problem['description']} (심각도: {problem['severity']:.2f})")

    def _execute_decisions(self, decisions: List[Dict[str, Any]]):
        """자동 결정 실행"""
        for decision in decisions:
            self.total_decisions_made += 1
            if self.current_session:
                self.current_session.decisions_made += 1
                
            logger.info(f"자동 결정 실행: {decision['action']} - {decision['reason']}")
            
            # 실제 액션 실행
            self._execute_action(decision["action"])

    def _check_reporting_needs(self):
        """보고 필요성 확인"""
        now = datetime.now()
        if (now - self.last_report_time).total_seconds() > self.report_interval:
            self._generate_status_report()
            self.last_report_time = now

    def _report_problem(self, problem_type: str, description: str):
        """문제 보고"""
        report = {
            "type": "problem_report",
            "problem_type": problem_type,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session.session_id if self.current_session else None,
            "total_cycles": self.total_learning_cycles,
            "total_problems": self.total_problems_detected
        }
        
        # 파일에 저장
        self._save_report(report)
        logger.error(f"🚨 문제 보고: {description}")

    def _generate_status_report(self):
        """상태 보고서 생성"""
        if not self.current_session:
            return
            
        report = {
            "type": "status_report",
            "session_id": self.current_session.session_id,
            "session_duration": (datetime.now() - self.current_session.start_time).total_seconds(),
            "learning_cycles": self.current_session.learning_cycles,
            "problems_detected": self.current_session.problems_detected,
            "decisions_made": self.current_session.decisions_made,
            "total_learning_cycles": self.total_learning_cycles,
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_report(report)
        logger.info(f"📊 상태 보고: {self.current_session.learning_cycles} 사이클, {self.current_session.problems_detected} 문제, {self.current_session.decisions_made} 결정")

    def _save_report(self, report: Dict[str, Any]):
        """보고서 저장"""
        os.makedirs("reports", exist_ok=True)
        filename = f"reports/autonomous_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    def _save_learning_record(self, metrics: Dict[str, float], progress: float):
        """학습 기록 저장"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "progress": progress,
            "session_id": self.current_session.session_id if self.current_session else None
        }
        
        self.learning_history.append(record)
        
        # 최근 1000개만 유지
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-1000:]

    # 헬퍼 메서드들 (실제 구현에서는 시스템 메트릭을 가져옴)
    def _get_memory_usage(self) -> float:
        """메모리 사용량 반환 (0.0 ~ 1.0)"""
        try:
            import psutil
            return psutil.virtual_memory().percent / 100.0
        except ImportError:
            return 0.5  # 기본값

    def _get_cpu_usage(self) -> float:
        """CPU 사용량 반환 (0.0 ~ 1.0)"""
        try:
            import psutil
            return psutil.cpu_percent() / 100.0
        except ImportError:
            return 0.3  # 기본값

    def _get_error_count(self) -> int:
        """오류 수 반환"""
        return 0  # 실제 구현에서는 로그에서 오류 수를 계산

    def _get_average_response_time(self) -> float:
        """평균 응답 시간 반환"""
        return 0.5  # 기본값

    def _get_learning_patterns(self) -> Dict[str, Any]:
        """학습 패턴 반환"""
        return {
            "pattern_count": len(self.learning_history),
            "recent_progress": self._calculate_recent_progress()
        }

    def _get_current_metrics(self) -> Dict[str, float]:
        """현재 메트릭 반환"""
        return {
            "error_rate": self._get_error_count() / max(self.total_learning_cycles, 1),
            "memory_usage": self._get_memory_usage(),
            "cpu_usage": self._get_cpu_usage(),
            "response_time": self._get_average_response_time(),
            "learning_progress": self._calculate_recent_progress()
        }

    def _check_problem_condition(self, problem_name: str, metrics: Dict[str, float], pattern: Dict[str, Any]) -> bool:
        """문제 조건 확인"""
        threshold = pattern["threshold"]
        
        if problem_name == "error_rate_high":
            return metrics["error_rate"] > threshold
        elif problem_name == "response_time_slow":
            return metrics["response_time"] > threshold
        elif problem_name == "memory_usage_high":
            return metrics["memory_usage"] > threshold
        elif problem_name == "cpu_usage_high":
            return metrics["cpu_usage"] > threshold
        elif problem_name == "learning_stagnation":
            return metrics["learning_progress"] < threshold
            
        return False

    def _calculate_severity(self, metrics: Dict[str, float], pattern: Dict[str, Any]) -> float:
        """문제 심각도 계산"""
        threshold = pattern["threshold"]
        
        if "error_rate" in pattern.get("metric", ""):
            return min(metrics["error_rate"] / threshold, 1.0)
        elif "memory_usage" in pattern.get("metric", ""):
            return min(metrics["memory_usage"] / threshold, 1.0)
        elif "cpu_usage" in pattern.get("metric", ""):
            return min(metrics["cpu_usage"] / threshold, 1.0)
        elif "response_time" in pattern.get("metric", ""):
            return min(metrics["response_time"] / threshold, 1.0)
            
        return 0.5

    def _evaluate_decision_rule(self, rule_name: str, metrics: Dict[str, float], rule: Dict[str, Any]) -> bool:
        """결정 규칙 평가"""
        condition = rule["condition"]
        
        if rule_name == "restart_service":
            return metrics["error_rate"] > 0.2
        elif rule_name == "optimize_memory":
            return metrics["memory_usage"] > 0.9
        elif rule_name == "adjust_learning_rate":
            return metrics["learning_progress"] < 0.1
        elif rule_name == "backup_data":
            if self.current_session:
                duration = (datetime.now() - self.current_session.start_time).total_seconds()
                return duration > 3600
                
        return False

    def _get_decision_reason(self, rule_name: str, metrics: Dict[str, float]) -> str:
        """결정 이유 반환"""
        reasons = {
            "restart_service": f"오류율이 {metrics['error_rate']:.2%}로 높음",
            "optimize_memory": f"메모리 사용량이 {metrics['memory_usage']:.2%}로 높음",
            "adjust_learning_rate": f"학습 진전이 {metrics['learning_progress']:.2%}로 낮음",
            "backup_data": "세션 지속 시간이 1시간을 초과함"
        }
        return reasons.get(rule_name, "자동 결정")

    def _execute_action(self, action: str):
        """액션 실행"""
        if action == "서비스 재시작":
            logger.info("🔄 서비스 재시작 액션 실행")
            # 실제 구현에서는 서비스 재시작 로직
        elif action == "메모리 최적화":
            logger.info("🧹 메모리 최적화 액션 실행")
            # 실제 구현에서는 메모리 정리 로직
        elif action == "학습률 조정":
            logger.info("⚙️ 학습률 조정 액션 실행")
            # 실제 구현에서는 학습률 조정 로직
        elif action == "데이터 백업":
            logger.info("💾 데이터 백업 액션 실행")
            # 실제 구현에서는 백업 로직

    def _calculate_progress_score(self, data: Dict[str, Any]) -> float:
        """진전 점수 계산"""
        # 실제 구현에서는 학습 진전을 계산
        return 0.5

    def _calculate_health_score(self, data: Dict[str, Any]) -> float:
        """시스템 건강도 계산"""
        memory_score = 1.0 - data.get("memory_usage", 0.5)
        cpu_score = 1.0 - data.get("cpu_usage", 0.3)
        error_score = 1.0 - data.get("error_count", 0) / max(self.total_learning_cycles, 1)
        
        return (memory_score + cpu_score + error_score) / 3.0

    def _evaluate_learning_progress(self, metrics: Dict[str, float]) -> float:
        """학습 진전 평가"""
        # 실제 구현에서는 학습 진전을 계산
        # 현재는 기본값 반환
        return 0.5

    def _calculate_recent_progress(self) -> float:
        """최근 진전 계산"""
        if len(self.learning_history) < 2:
            return 0.0
            
        recent = self.learning_history[-10:]  # 최근 10개 기록
        if len(recent) < 2:
            return 0.0
            
        first_progress = recent[0].get("progress", 0.0)
        last_progress = recent[-1].get("progress", 0.0)
        
        return last_progress - first_progress

    def process_learning_question(self, learning_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """학습 질문 처리 및 자율 학습 결과 생성"""
        try:
            logger.info("🧠 자율 학습 질문 처리 시작")
            
            # 현재 학습 상태 분석
            current_status = self.get_status()
            
            # 학습 메트릭 기반 개선 방향 결정
            improvement_direction = self._determine_improvement_direction(learning_metrics)
            
            # 자율 학습 실행
            learning_result = {
                "timestamp": datetime.now().isoformat(),
                "learning_metrics": learning_metrics,
                "current_status": current_status,
                "improvement_direction": improvement_direction,
                "autonomous_actions": [],
                "learning_score": 0.0,
                "confidence": 0.0
            }
            
            # 자율 학습 액션 실행
            if improvement_direction.get("needs_optimization"):
                optimization_result = self._execute_optimization_actions(learning_metrics)
                learning_result["autonomous_actions"].append(optimization_result)
                
            if improvement_direction.get("needs_adaptation"):
                adaptation_result = self._execute_adaptation_actions(learning_metrics)
                learning_result["autonomous_actions"].append(adaptation_result)
                
            if improvement_direction.get("needs_restructuring"):
                restructuring_result = self._execute_restructuring_actions(learning_metrics)
                learning_result["autonomous_actions"].append(restructuring_result)
            
            # 학습 점수 계산
            learning_result["learning_score"] = self._calculate_learning_score(learning_result)
            learning_result["confidence"] = self._calculate_confidence_score(learning_result)
            
            logger.info(f"✅ 자율 학습 질문 처리 완료 - 점수: {learning_result['learning_score']:.3f}")
            return learning_result
            
        except Exception as e:
            logger.error(f"❌ 자율 학습 질문 처리 오류: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "learning_score": 0.0,
                "confidence": 0.0
            }

    def _determine_improvement_direction(self, learning_metrics: Dict[str, Any]) -> Dict[str, bool]:
        """학습 메트릭 기반 개선 방향 결정"""
        direction = {
            "needs_optimization": False,
            "needs_adaptation": False,
            "needs_restructuring": False
        }
        
        # 성능 기반 판단
        if learning_metrics.get("performance_score", 0.0) < 0.5:
            direction["needs_optimization"] = True
            
        # 적응성 기반 판단
        if learning_metrics.get("adaptability_score", 0.0) < 0.4:
            direction["needs_adaptation"] = True
            
        # 구조적 문제 기반 판단
        if learning_metrics.get("structural_score", 0.0) < 0.3:
            direction["needs_restructuring"] = True
            
        return direction

    def _execute_optimization_actions(self, learning_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """최적화 액션 실행"""
        return {
            "action_type": "optimization",
            "description": "성능 최적화 실행",
            "actions": [
                "메모리 사용량 최적화",
                "응답 시간 개선",
                "학습 알고리즘 튜닝"
            ],
            "impact_score": 0.7
        }

    def _execute_adaptation_actions(self, learning_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """적응성 액션 실행"""
        return {
            "action_type": "adaptation",
            "description": "학습 방식 적응",
            "actions": [
                "학습 패턴 분석",
                "새로운 전략 적용",
                "유연한 접근 방식 도입"
            ],
            "impact_score": 0.8
        }

    def _execute_restructuring_actions(self, learning_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """구조 개선 액션 실행"""
        return {
            "action_type": "restructuring",
            "description": "학습 구조 개선",
            "actions": [
                "학습 모듈 재구성",
                "데이터 흐름 최적화",
                "새로운 학습 프레임워크 도입"
            ],
            "impact_score": 0.9
        }

    def _calculate_learning_score(self, learning_result: Dict[str, Any]) -> float:
        """학습 점수 계산"""
        base_score = learning_result.get("learning_metrics", {}).get("overall_score", 0.0)
        action_bonus = len(learning_result.get("autonomous_actions", [])) * 0.1
        return min(1.0, base_score + action_bonus)

    def _calculate_confidence_score(self, learning_result: Dict[str, Any]) -> float:
        """신뢰도 점수 계산"""
        actions = learning_result.get("autonomous_actions", [])
        if not actions:
            return 0.5
            
        impact_scores = [action.get("impact_score", 0.0) for action in actions]
        return sum(impact_scores) / len(impact_scores)

    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            "is_running": self.is_running,
            "session_id": self.current_session.session_id if self.current_session else None,
            "session_duration": (datetime.now() - self.current_session.start_time).total_seconds() if self.current_session else 0,
            "total_learning_cycles": self.total_learning_cycles,
            "total_problems_detected": self.total_problems_detected,
            "total_decisions_made": self.total_decisions_made,
            "learning_interval": self.learning_interval,
            "last_report_time": self.last_report_time.isoformat(),
            "current_metrics": self._get_current_metrics()
        }

# 전역 인스턴스
autonomous_learner = AutonomousLearner() 