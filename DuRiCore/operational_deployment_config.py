from DuRiCore.trace import emit_trace
"""
운영 배포 설정
롤백 포인트 + 캐너리 배포 전략
"""
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class DeploymentPhase(Enum):
    """배포 단계"""
    CANARY_5 = 'canary_5_percent'
    CANARY_25 = 'canary_25_percent'
    FULL_DEPLOY = 'full_deploy'
    ROLLBACK = 'rollback'

class RollbackReason(Enum):
    """롤백 사유"""
    CRITICAL_ERROR = 'critical_error'
    PERFORMANCE_DEGRADATION = 'performance_degradation'
    SAFETY_VIOLATION = 'safety_violation'
    USER_REQUEST = 'user_request'
    AUTOMATIC_DETECTION = 'automatic_detection'

@dataclass
class RollbackPoint:
    """롤백 포인트 정의"""
    version: str
    tag: str
    commit_hash: str
    timestamp: str
    description: str
    safety_score: float
    equivalence_score: float
    test_results: Dict[str, Any]
    backup_path: str

@dataclass
class CanaryConfig:
    """캐너리 배포 설정"""
    phase: DeploymentPhase
    traffic_percentage: int
    duration_minutes: int
    health_check_interval: int
    success_criteria: Dict[str, Any]
    rollback_threshold: Dict[str, Any]

class OperationalDeploymentConfig:
    """운영 배포 설정 관리"""

    def __init__(self):
        self.rollback_points = self._setup_rollback_points()
        self.canary_configs = self._setup_canary_configs()
        self.deployment_history = []

    def _setup_rollback_points(self) -> Dict[str, RollbackPoint]:
        """롤백 포인트 설정"""
        return {'v1.0.0-control-final': RollbackPoint(version='v1.0.0', tag='v1.0.0-control-final', commit_hash='abc123...', timestamp='2025-08-01 10:00:00', description='안전성 시스템 통합 전 최종 안정 버전', safety_score=0.85, equivalence_score=0.92, test_results={'scenarios_passed': 6, 'total_scenarios': 8, 'success_rate': '75%', 'execution_time': 3.2}, backup_path='/backups/v1.0.0-control-final'), 'v1.1.0-safety-stabilized': RollbackPoint(version='v1.1.0', tag='v1.1.0-safety-stabilized', commit_hash='def456...', timestamp='2025-08-10 15:30:00', description='8/8 시나리오 성공률 달성, 안전성 시스템 안정화', safety_score=0.95, equivalence_score=0.999, test_results={'scenarios_passed': 8, 'total_scenarios': 8, 'success_rate': '100%', 'execution_time': 2.8}, backup_path='/backups/v1.1.0-safety-stabilized')}

    def _setup_canary_configs(self) -> List[CanaryConfig]:
        """캐너리 배포 설정"""
        return [CanaryConfig(phase=DeploymentPhase.CANARY_5, traffic_percentage=5, duration_minutes=15, health_check_interval=30, success_criteria={'error_rate': 0.01, 'response_time': 2.0, 'safety_score': 0.9, 'equivalence_score': 0.99}, rollback_threshold={'error_rate': 0.05, 'response_time': 5.0, 'safety_score': 0.7, 'equivalence_score': 0.95}), CanaryConfig(phase=DeploymentPhase.CANARY_25, traffic_percentage=25, duration_minutes=30, health_check_interval=60, success_criteria={'error_rate': 0.005, 'response_time': 1.5, 'safety_score': 0.92, 'equivalence_score': 0.995}, rollback_threshold={'error_rate': 0.03, 'response_time': 4.0, 'safety_score': 0.75, 'equivalence_score': 0.97}), CanaryConfig(phase=DeploymentPhase.FULL_DEPLOY, traffic_percentage=100, duration_minutes=60, health_check_interval=120, success_criteria={'error_rate': 0.001, 'response_time': 1.0, 'safety_score': 0.95, 'equivalence_score': 0.998}, rollback_threshold={'error_rate': 0.02, 'response_time': 3.0, 'safety_score': 0.8, 'equivalence_score': 0.98})]

    def get_rollback_point(self, version: str) -> Optional[RollbackPoint]:
        """버전별 롤백 포인트 조회"""
        return self.rollback_points.get(version)

    def get_latest_rollback_point(self) -> Optional[RollbackPoint]:
        """최신 롤백 포인트 조회"""
        if not self.rollback_points:
            return None
        latest = max(self.rollback_points.values(), key=lambda x: time.strptime(x.timestamp, '%Y-%m-%d %H:%M:%S'))
        return latest

    def get_canary_config(self, phase: DeploymentPhase) -> Optional[CanaryConfig]:
        """배포 단계별 캐너리 설정 조회"""
        for config in self.canary_configs:
            if config.phase == phase:
                return config
        return None

    def should_rollback(self, phase: DeploymentPhase, metrics: Dict[str, Any]) -> tuple[bool, RollbackReason, str]:
        """롤백 필요 여부 판단"""
        config = self.get_canary_config(phase)
        if not config:
            return (False, None, '캐너리 설정을 찾을 수 없음')
        for (metric, threshold) in config.rollback_threshold.items():
            if metric in metrics:
                current_value = metrics[metric]
                if metric == 'error_rate' and current_value >= threshold:
                    return (True, RollbackReason.CRITICAL_ERROR, f'에러율 임계값 초과: {current_value} >= {threshold}')
                elif metric == 'response_time' and current_value >= threshold:
                    return (True, RollbackReason.PERFORMANCE_DEGRADATION, f'응답시간 임계값 초과: {current_value} >= {threshold}')
                elif metric == 'safety_score' and current_value <= threshold:
                    return (True, RollbackReason.SAFETY_VIOLATION, f'안전성 점수 임계값 미달: {current_value} <= {threshold}')
                elif metric == 'equivalence_score' and current_value <= threshold:
                    return (True, RollbackReason.SAFETY_VIOLATION, f'동등성 점수 임계값 미달: {current_value} <= {threshold}')
        return (False, None, '모든 메트릭이 정상 범위 내')

    def record_deployment(self, phase: DeploymentPhase, success: bool, metrics: Dict[str, Any], duration_seconds: int, notes: str=''):
        """배포 기록"""
        deployment_record = {'phase': phase.value, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'success': success, 'metrics': metrics, 'duration_seconds': duration_seconds, 'notes': notes}
        self.deployment_history.append(deployment_record)
        if len(self.deployment_history) > 100:
            self.deployment_history = self.deployment_history[-100:]

    def get_deployment_stats(self) -> Dict[str, Any]:
        """배포 통계 조회"""
        if not self.deployment_history:
            return {'total': 0, 'success': 0, 'failure': 0, 'success_rate': '0%'}
        total = len(self.deployment_history)
        success = sum((1 for record in self.deployment_history if record['success']))
        failure = total - success
        success_rate = f'{success / total * 100:.1f}%'
        return {'total': total, 'success': success, 'failure': failure, 'success_rate': success_rate, 'recent_deployments': self.deployment_history[-10:]}

    def export_config(self) -> Dict[str, Any]:
        """설정 내보내기"""
        return {'version': '1.0.0', 'last_updated': '2025-08-10', 'rollback_points': {version: {'version': point.version, 'tag': point.tag, 'commit_hash': point.commit_hash, 'timestamp': point.timestamp, 'description': point.description, 'safety_score': point.safety_score, 'equivalence_score': point.equivalence_score, 'test_results': point.test_results, 'backup_path': point.backup_path} for (version, point) in self.rollback_points.items()}, 'canary_configs': [{'phase': config.phase.value, 'traffic_percentage': config.traffic_percentage, 'duration_minutes': config.duration_minutes, 'health_check_interval': config.health_check_interval, 'success_criteria': config.success_criteria, 'rollback_threshold': config.rollback_threshold} for config in self.canary_configs], 'deployment_stats': self.get_deployment_stats()}
if __name__ == '__main__':
    config = OperationalDeploymentConfig()
    emit_trace('info', ' '.join(map(str, ['🚀 운영 배포 설정'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    emit_trace('info', ' '.join(map(str, [f'🔒 롤백 포인트: {len(config.rollback_points)}개'])))
    for (version, point) in config.rollback_points.items():
        emit_trace('info', ' '.join(map(str, [f'  - {version}: {point.description}'])))
    emit_trace('info', ' '.join(map(str, [f'\n📊 캐너리 배포 단계: {len(config.canary_configs)}개'])))
    for config_item in config.canary_configs:
        emit_trace('info', ' '.join(map(str, [f'  - {config_item.phase.value}: {config_item.traffic_percentage}% 트래픽, {config_item.duration_minutes}분'])))
    config_data = config.export_config()
    emit_trace('info', ' '.join(map(str, [f"\n💾 설정 내보내기 완료: v{config_data['version']}"])))
    emit_trace('info', ' '.join(map(str, ['\n🧪 롤백 시뮬레이션:'])))
    test_metrics = {'error_rate': 0.06, 'response_time': 2.5, 'safety_score': 0.85, 'equivalence_score': 0.97}
    (should_rollback, reason, message) = config.should_rollback(DeploymentPhase.CANARY_5, test_metrics)
    if should_rollback:
        emit_trace('info', ' '.join(map(str, [f'  ❌ 롤백 필요: {reason.value} - {message}'])))
    else:
        emit_trace('info', ' '.join(map(str, [f'  ✅ 롤백 불필요: {message}'])))