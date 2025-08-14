from DuRiCore.trace import emit_trace
"""
모니터링 대시보드 설정
핵심 메트릭 카드 + 경보 규칙 정의
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class AlertSeverity(Enum):
    """경보 심각도"""
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'

@dataclass
class MetricCard:
    """메트릭 카드 정의"""
    name: str
    key: str
    description: str
    unit: str = ''
    threshold_warning: float = None
    threshold_critical: float = None
    refresh_interval: int = 30

@dataclass
class AlertRule:
    """경보 규칙 정의"""
    name: str
    condition: str
    severity: AlertSeverity
    description: str
    cooldown: int = 300

class MonitoringDashboardConfig:
    """모니터링 대시보드 설정"""

    def __init__(self):
        self.metric_cards = self._setup_metric_cards()
        self.alert_rules = self._setup_alert_rules()

    def _setup_metric_cards(self) -> List[MetricCard]:
        """핵심 메트릭 카드 설정"""
        return [MetricCard(name='전체 동등성 점수', key='overall_equivalence_score', description='시스템 동작의 예상 결과와의 일치도', unit='점수', threshold_warning=0.995, threshold_critical=0.99, refresh_interval=15), MetricCard(name='KS p-value', key='ks_pvalue', description='Kolmogorov-Smirnov 검정 p-value', unit='p-value', threshold_warning=0.05, threshold_critical=0.01, refresh_interval=30), MetricCard(name='메타모픽 매치율', key='metamorphic_match', description='메타모픽 테스트 통과율', unit='%', threshold_warning=95.0, threshold_critical=90.0, refresh_interval=20), MetricCard(name='현재 WIP', key='current_wip', description='현재 진행 중인 작업 항목 수', unit='개', threshold_warning=80, threshold_critical=95, refresh_interval=10), MetricCard(name='안전성 점수', key='safety_score', description='전체 시스템 안전성 점수', unit='점수', threshold_warning=0.8, threshold_critical=0.6, refresh_interval=15), MetricCard(name='통합 상태', key='integration_status', description='시스템 통합 상태', unit='상태', refresh_interval=5), MetricCard(name='E-stop 상태', key='emergency_stop_status', description='비상 정지 활성화 상태', unit='상태', refresh_interval=5), MetricCard(name='웜업 윈도우', key='warmup_window_status', description='E-stop 웜업 윈도우 상태', unit='초', refresh_interval=10)]

    def _setup_alert_rules(self) -> List[AlertRule]:
        """경보 규칙 설정"""
        return [AlertRule(name='동등성 점수 저하', condition='overall_equivalence_score < 0.995', severity=AlertSeverity.WARNING, description='동등성 점수가 0.995 미만으로 저하됨', cooldown=600), AlertRule(name='동등성 점수 위험', condition='overall_equivalence_score < 0.990', severity=AlertSeverity.CRITICAL, description='동등성 점수가 0.990 미만으로 위험 수준', cooldown=300), AlertRule(name='WIP 메트릭 누락', condition="current_wip is None or current_wip == 'missing'", severity=AlertSeverity.WARNING, description='current_wip 메트릭이 누락되거나 None임 (비-E-stop 상황)', cooldown=180), AlertRule(name='E-stop 연속 발생', condition='emergency_stop_count >= 2 in 10min', severity=AlertSeverity.CRITICAL, description='10분 내 E-stop이 2회 이상 연속 발생', cooldown=600), AlertRule(name='안전성 점수 저하', condition='safety_score < 0.8', severity=AlertSeverity.WARNING, description='안전성 점수가 0.8 미만으로 저하됨', cooldown=300), AlertRule(name='시스템 상태 이상', condition="integration_status not in ['ready', 'initializing']", severity=AlertSeverity.WARNING, description='시스템이 정상 상태가 아님', cooldown=120)]

    def get_metric_card_by_key(self, key: str) -> MetricCard:
        """키로 메트릭 카드 조회"""
        for card in self.metric_cards:
            if card.key == key:
                return card
        return None

    def get_alert_rules_by_severity(self, severity: AlertSeverity) -> List[AlertRule]:
        """심각도별 경보 규칙 조회"""
        return [rule for rule in self.alert_rules if rule.severity == severity]

    def validate_metric_value(self, key: str, value: Any) -> Dict[str, Any]:
        """메트릭 값 검증 및 경보 상태 반환"""
        card = self.get_metric_card_by_key(key)
        if not card:
            return {'valid': False, 'alert': None, 'message': '알 수 없는 메트릭'}
        if value is None:
            return {'valid': False, 'alert': 'WARNING', 'message': f'{card.name} 값이 None입니다'}
        if isinstance(value, (int, float)) and card.threshold_warning is not None:
            if card.threshold_critical is not None and value <= card.threshold_critical:
                return {'valid': False, 'alert': 'CRITICAL', 'message': f'{card.name}이(가) 위험 수준입니다: {value}'}
            elif value <= card.threshold_warning:
                return {'valid': False, 'alert': 'WARNING', 'message': f'{card.name}이(가) 경고 수준입니다: {value}'}
        return {'valid': True, 'alert': None, 'message': f'{card.name} 정상: {value}'}

    def export_config(self) -> Dict[str, Any]:
        """설정 내보내기"""
        return {'version': '1.0.0', 'last_updated': '2025-08-10', 'metric_cards': [{'name': card.name, 'key': card.key, 'description': card.description, 'unit': card.unit, 'threshold_warning': card.threshold_warning, 'threshold_critical': card.threshold_critical, 'refresh_interval': card.refresh_interval} for card in self.metric_cards], 'alert_rules': [{'name': rule.name, 'condition': rule.condition, 'severity': rule.severity.value, 'description': rule.description, 'cooldown': rule.cooldown} for rule in self.alert_rules]}
if __name__ == '__main__':
    config = MonitoringDashboardConfig()
    emit_trace('info', ' '.join(map(str, ['🎯 모니터링 대시보드 설정'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    emit_trace('info', ' '.join(map(str, [f'📊 메트릭 카드: {len(config.metric_cards)}개'])))
    for card in config.metric_cards:
        emit_trace('info', ' '.join(map(str, [f'  - {card.name} ({card.key})'])))
    emit_trace('info', ' '.join(map(str, [f'\n🚨 경보 규칙: {len(config.alert_rules)}개'])))
    for rule in config.alert_rules:
        emit_trace('info', ' '.join(map(str, [f'  - {rule.name} [{rule.severity.value.upper()}]'])))
    config_data = config.export_config()
    emit_trace('info', ' '.join(map(str, [f"\n💾 설정 내보내기 완료: v{config_data['version']}"])))