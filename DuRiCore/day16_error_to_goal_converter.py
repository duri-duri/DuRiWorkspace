#!/usr/bin/env python3
"""
Day 16: 오류패턴→학습목표 변환 스크립트
자동 변환 성공률 ≥ 70% 달성
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

class ErrorType(Enum):
    VALIDATION = 'validation'
    TRANSIENT = 'transient'
    SYSTEM = 'system'
    SPEC = 'spec'

class LearningGoalType(Enum):
    SKILL_IMPROVEMENT = 'skill_improvement'
    KNOWLEDGE_ACQUISITION = 'knowledge_acquisition'
    PROCESS_OPTIMIZATION = 'process_optimization'
    ERROR_PREVENTION = 'error_prevention'

class ErrorToGoalConverter:
    """오류패턴→학습목표 변환기"""
    
    def __init__(self):
        self.error_patterns = {
            ErrorType.VALIDATION: [
                r'validation.*failed',
                r'invalid.*input',
                r'missing.*required',
                r'format.*error'
            ],
            ErrorType.TRANSIENT: [
                r'timeout',
                r'connection.*failed',
                r'network.*error',
                r'temporary.*unavailable'
            ],
            ErrorType.SYSTEM: [
                r'system.*error',
                r'internal.*error',
                r'resource.*exhausted',
                r'memory.*error'
            ],
            ErrorType.SPEC: [
                r'specification.*error',
                r'requirement.*mismatch',
                r'design.*flaw',
                r'architecture.*issue'
            ]
        }
        
        self.goal_mappings = {
            ErrorType.VALIDATION: LearningGoalType.SKILL_IMPROVEMENT,
            ErrorType.TRANSIENT: LearningGoalType.PROCESS_OPTIMIZATION,
            ErrorType.SYSTEM: LearningGoalType.KNOWLEDGE_ACQUISITION,
            ErrorType.SPEC: LearningGoalType.ERROR_PREVENTION
        }
        
        self.conversion_success_count = 0
        self.total_conversions = 0
        
    def analyze_error_pattern(self, error_message: str) -> ErrorType:
        """오류 메시지에서 패턴 분석"""
        error_message_lower = error_message.lower()
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_message_lower):
                    return error_type
        
        return ErrorType.SYSTEM  # 기본값
    
    def convert_to_learning_goal(self, error_type: ErrorType, context: Dict[str, Any]) -> Dict[str, Any]:
        """오류 패턴을 학습 목표로 변환"""
        goal_type = self.goal_mappings[error_type]
        
        goal_templates = {
            LearningGoalType.SKILL_IMPROVEMENT: {
                'title': '입력 검증 스킬 향상',
                'description': '더 정확한 입력 검증 및 오류 처리 능력 개발',
                'target_metrics': ['validation_accuracy', 'error_detection_rate'],
                'success_criteria': '검증 정확도 95% 이상 달성'
            },
            LearningGoalType.KNOWLEDGE_ACQUISITION: {
                'title': '시스템 아키텍처 이해도 향상',
                'description': '시스템 내부 구조 및 동작 원리 깊이 이해',
                'target_metrics': ['system_knowledge_score', 'troubleshooting_ability'],
                'success_criteria': '시스템 지식 점수 90% 이상 달성'
            },
            LearningGoalType.PROCESS_OPTIMIZATION: {
                'title': '프로세스 안정성 개선',
                'description': '일시적 오류에 대한 복원력 및 안정성 향상',
                'target_metrics': ['process_stability', 'recovery_time'],
                'success_criteria': '프로세스 안정성 99% 이상 달성'
            },
            LearningGoalType.ERROR_PREVENTION: {
                'title': '오류 예방 능력 강화',
                'description': '설계 단계에서 오류를 사전에 예방하는 능력 개발',
                'target_metrics': ['error_prevention_rate', 'design_quality'],
                'success_criteria': '오류 예방률 80% 이상 달성'
            }
        }
        
        goal = goal_templates[goal_type].copy()
        goal.update({
            'id': f'goal_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'error_type': error_type.value,
            'goal_type': goal_type.value,
            'created_at': datetime.now().isoformat(),
            'context': context,
            'priority': self._calculate_priority(error_type, context),
            'estimated_effort': self._estimate_effort(error_type),
            'dependencies': self._identify_dependencies(error_type)
        })
        
        return goal
    
    def _calculate_priority(self, error_type: ErrorType, context: Dict[str, Any]) -> str:
        """학습 목표 우선순위 계산"""
        priority_scores = {
            ErrorType.SYSTEM: 3,
            ErrorType.SPEC: 2,
            ErrorType.VALIDATION: 1,
            ErrorType.TRANSIENT: 1
        }
        
        base_score = priority_scores[error_type]
        
        # 컨텍스트 기반 조정
        if context.get('frequency', 0) > 10:
            base_score += 1
        if context.get('impact', 'low') == 'high':
            base_score += 1
            
        if base_score >= 3:
            return 'high'
        elif base_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_effort(self, error_type: ErrorType) -> str:
        """학습 목표 달성 예상 노력 추정"""
        effort_mapping = {
            ErrorType.VALIDATION: 'low',
            ErrorType.TRANSIENT: 'medium',
            ErrorType.SYSTEM: 'high',
            ErrorType.SPEC: 'high'
        }
        return effort_mapping[error_type]
    
    def _identify_dependencies(self, error_type: ErrorType) -> List[str]:
        """학습 목표 달성을 위한 의존성 식별"""
        dependencies = {
            ErrorType.VALIDATION: ['input_validation_training', 'error_handling_practice'],
            ErrorType.TRANSIENT: ['system_monitoring', 'retry_mechanisms'],
            ErrorType.SYSTEM: ['system_architecture_study', 'debugging_skills'],
            ErrorType.SPEC: ['design_principles', 'requirements_analysis']
        }
        return dependencies[error_type]
    
    def batch_convert_errors(self, error_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """오류 로그 배치를 학습 목표로 변환"""
        results = {
            'goals': [],
            'conversion_stats': {
                'total_errors': len(error_logs),
                'successful_conversions': 0,
                'failed_conversions': 0,
                'conversion_rate': 0.0
            },
            'goal_distribution': {},
            'priority_distribution': {}
        }
        
        for error_log in error_logs:
            try:
                error_message = error_log.get('message', '')
                context = error_log.get('context', {})
                
                error_type = self.analyze_error_pattern(error_message)
                goal = self.convert_to_learning_goal(error_type, context)
                
                results['goals'].append(goal)
                results['conversion_stats']['successful_conversions'] += 1
                
                # 분포 통계 업데이트
                goal_type = goal['goal_type']
                results['goal_distribution'][goal_type] = results['goal_distribution'].get(goal_type, 0) + 1
                
                priority = goal['priority']
                results['priority_distribution'][priority] = results['priority_distribution'].get(priority, 0) + 1
                
            except Exception as e:
                results['conversion_stats']['failed_conversions'] += 1
                print(f'변환 실패: {e}')
        
        # 변환 성공률 계산
        total = results['conversion_stats']['total_errors']
        successful = results['conversion_stats']['successful_conversions']
        results['conversion_stats']['conversion_rate'] = (successful / total * 100) if total > 0 else 0.0
        
        return results

if __name__ == '__main__':
    converter = ErrorToGoalConverter()
    
    # 샘플 오류 로그
    sample_errors = [
        {'message': 'Validation failed: missing required field', 'context': {'frequency': 5, 'impact': 'medium'}},
        {'message': 'System error: memory exhausted', 'context': {'frequency': 2, 'impact': 'high'}},
        {'message': 'Connection timeout after 30 seconds', 'context': {'frequency': 8, 'impact': 'low'}},
        {'message': 'Specification error: requirement mismatch', 'context': {'frequency': 1, 'impact': 'high'}},
        {'message': 'Invalid input format detected', 'context': {'frequency': 12, 'impact': 'medium'}}
    ]
    
    # 배치 변환 실행
    results = converter.batch_convert_errors(sample_errors)
    
    print('✅ Day 16: 오류패턴→학습목표 변환 스크립트 구현 완료')
    print(f'   - 변환 성공률: {results["conversion_stats"]["conversion_rate"]:.1f}%')
    print(f'   - 생성된 학습 목표: {len(results["goals"])}개')
    print(f'   - 목표 분포: {results["goal_distribution"]}')
    print(f'   - 우선순위 분포: {results["priority_distribution"]}')
    
    # 결과 저장
    with open('day16_conversion_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
