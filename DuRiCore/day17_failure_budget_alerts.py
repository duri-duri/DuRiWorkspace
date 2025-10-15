#!/usr/bin/env python3
"""
Day 17: 실패 예산 경고 자동화
0.5% 초과 시 기능 동결하는 경고 시스템
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

class AlertSeverity(Enum):
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'
    EMERGENCY = 'emergency'

class FeatureStatus(Enum):
    ACTIVE = 'active'
    WARNING = 'warning'
    FROZEN = 'frozen'
    DISABLED = 'disabled'

@dataclass
class FailureBudget:
    total_requests: int
    failed_requests: int
    failure_rate: float
    budget_threshold: float
    burn_rate: float
    remaining_budget: float
    time_window: str

@dataclass
class Alert:
    id: str
    severity: AlertSeverity
    message: str
    feature: str
    failure_rate: float
    threshold: float
    timestamp: datetime
    actions_taken: List[str]

class FailureBudgetAlertSystem:
    """실패 예산 경고 자동화 시스템"""
    
    def __init__(self):
        self.budget_threshold = 0.005  # 0.5% 임계값
        self.critical_threshold = 0.01  # 1.0% 긴급 임계값
        self.frozen_features = set()
        self.alert_history = []
        self.feature_status = {}
        
        # 기존 시스템과 통합
        self.prometheus_rules = []
        self.alertmanager_config = {}
        
    def calculate_failure_budget(self, metrics: Dict[str, Any]) -> FailureBudget:
        """실패 예산 계산"""
        total_requests = metrics.get('total_requests', 0)
        failed_requests = metrics.get('failed_requests', 0)
        
        failure_rate = failed_requests / max(total_requests, 1)
        
        # 버닝 레이트 계산 (시간당)
        time_window_hours = metrics.get('time_window_hours', 1)
        burn_rate = failure_rate / time_window_hours
        
        # 남은 예산 계산
        remaining_budget = max(0, self.budget_threshold - failure_rate)
        
        return FailureBudget(
            total_requests=total_requests,
            failed_requests=failed_requests,
            failure_rate=failure_rate,
            budget_threshold=self.budget_threshold,
            burn_rate=burn_rate,
            remaining_budget=remaining_budget,
            time_window=f'{time_window_hours}h'
        )
    
    def check_budget_threshold(self, budget: FailureBudget, feature: str) -> Optional[Alert]:
        """예산 임계값 확인 및 알림 생성"""
        if budget.failure_rate <= self.budget_threshold:
            return None
        
        # 심각도 결정
        if budget.failure_rate >= self.critical_threshold:
            severity = AlertSeverity.EMERGENCY
        elif budget.failure_rate >= self.budget_threshold * 2:
            severity = AlertSeverity.CRITICAL
        else:
            severity = AlertSeverity.WARNING
        
        # 알림 메시지 생성
        message = f'실패 예산 초과: {budget.failure_rate:.3%} > {self.budget_threshold:.2%}'
        
        alert = Alert(
            id=f'alert_{int(time.time())}',
            severity=severity,
            message=message,
            feature=feature,
            failure_rate=budget.failure_rate,
            threshold=self.budget_threshold,
            timestamp=datetime.now(),
            actions_taken=[]
        )
        
        return alert
    
    def execute_alert_actions(self, alert: Alert) -> List[str]:
        """알림에 따른 액션 실행"""
        actions = []
        
        if alert.severity == AlertSeverity.EMERGENCY:
            # 긴급: 기능 즉시 동결
            actions.append('freeze_feature')
            actions.append('send_emergency_notification')
            actions.append('trigger_rollback')
            self.frozen_features.add(alert.feature)
            self.feature_status[alert.feature] = FeatureStatus.FROZEN
            
        elif alert.severity == AlertSeverity.CRITICAL:
            # 위험: 기능 동결 및 알림
            actions.append('freeze_feature')
            actions.append('send_critical_notification')
            self.frozen_features.add(alert.feature)
            self.feature_status[alert.feature] = FeatureStatus.FROZEN
            
        elif alert.severity == AlertSeverity.WARNING:
            # 경고: 모니터링 강화
            actions.append('increase_monitoring')
            actions.append('send_warning_notification')
            self.feature_status[alert.feature] = FeatureStatus.WARNING
        
        alert.actions_taken = actions
        return actions
    
    def generate_prometheus_rules(self) -> List[Dict[str, Any]]:
        """Prometheus 알림 규칙 생성"""
        rules = [
            {
                'alert': 'FailureBudgetExceeded',
                'expr': f'duri_failure_rate > {self.budget_threshold}',
                'for': '5m',
                'labels': {
                    'severity': 'warning',
                    'team': 'duri',
                    'component': 'failure_budget'
                },
                'annotations': {
                    'summary': '실패 예산 초과',
                    'description': '실패율이 {{  | printf "%.3f" }}%로 임계값 {{ .threshold }}%를 초과했습니다.'
                }
            },
            {
                'alert': 'FailureBudgetCritical',
                'expr': f'duri_failure_rate > {self.critical_threshold}',
                'for': '2m',
                'labels': {
                    'severity': 'critical',
                    'team': 'duri',
                    'component': 'failure_budget'
                },
                'annotations': {
                    'summary': '실패 예산 긴급 초과',
                    'description': '실패율이 {{  | printf "%.3f" }}%로 긴급 임계값을 초과했습니다. 기능 동결 필요.'
                }
            }
        ]
        
        return rules
    
    def generate_alertmanager_config(self) -> Dict[str, Any]:
        """Alertmanager 설정 생성"""
        config = {
            'route': {
                'group_by': ['alertname', 'cluster', 'service'],
                'group_wait': '10s',
                'group_interval': '10s',
                'repeat_interval': '1h',
                'receiver': 'duri-alerts'
            },
            'receivers': [
                {
                    'name': 'duri-alerts',
                    'webhook_configs': [
                        {
                            'url': 'http://duri-alert-handler:9093/webhook',
                            'send_resolved': True
                        }
                    ]
                }
            ],
            'inhibit_rules': [
                {
                    'source_match': {
                        'severity': 'critical'
                    },
                    'target_match': {
                        'severity': 'warning'
                    },
                    'equal': ['alertname', 'cluster', 'service']
                }
            ]
        }
        
        return config
    
    def monitor_features(self, feature_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """기능별 실패 예산 모니터링"""
        results = {
            'alerts': [],
            'frozen_features': list(self.frozen_features),
            'feature_status': self.feature_status.copy(),
            'monitoring_stats': {
                'total_features': len(feature_metrics),
                'frozen_count': len(self.frozen_features),
                'warning_count': 0,
                'active_count': 0
            }
        }
        
        for feature, metrics in feature_metrics.items():
            # 실패 예산 계산
            budget = self.calculate_failure_budget(metrics)
            
            # 임계값 확인
            alert = self.check_budget_threshold(budget, feature)
            
            if alert:
                # 액션 실행
                actions = self.execute_alert_actions(alert)
                results['alerts'].append({
                    'alert': alert.__dict__,
                    'actions': actions,
                    'budget': budget.__dict__
                })
            
            # 상태 통계 업데이트
            status = self.feature_status.get(feature, FeatureStatus.ACTIVE)
            if status == FeatureStatus.WARNING:
                results['monitoring_stats']['warning_count'] += 1
            elif status == FeatureStatus.ACTIVE:
                results['monitoring_stats']['active_count'] += 1
        
        return results

if __name__ == '__main__':
    alert_system = FailureBudgetAlertSystem()
    
    # 샘플 기능 메트릭
    sample_metrics = {
        'duri-search': {
            'total_requests': 1000,
            'failed_requests': 8,  # 0.8% > 0.5%
            'time_window_hours': 1
        },
        'duri-recommendation': {
            'total_requests': 500,
            'failed_requests': 1,  # 0.2% < 0.5%
            'time_window_hours': 1
        },
        'duri-analysis': {
            'total_requests': 200,
            'failed_requests': 5,  # 2.5% > 1.0% (긴급)
            'time_window_hours': 1
        }
    }
    
    # 모니터링 실행
    results = alert_system.monitor_features(sample_metrics)
    
    print('✅ Day 17: 실패 예산 경고 자동화 구현 완료')
    print(f'   - 생성된 알림: {len(results["alerts"])}개')
    print(f'   - 동결된 기능: {len(results["frozen_features"])}개')
    print(f'   - 기능 상태: {results["feature_status"]}')
    print(f'   - 모니터링 통계: {results["monitoring_stats"]}')
    
    # 결과 저장
    with open('day17_failure_budget_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
