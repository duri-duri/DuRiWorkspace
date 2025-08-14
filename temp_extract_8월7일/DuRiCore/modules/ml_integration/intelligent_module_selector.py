"""
🧠 지능형 모듈 선택 시스템 (Intelligent Module Selector)
사용 패턴을 분석하고 자동으로 최적의 모듈을 선택하는 고급 시스템

주요 기능:
• 사용 패턴 분석 및 학습
• 성능 기반 모듈 권장
• 자동 모듈 로딩/언로딩 최적화
• 스마트 모듈 조합 생성
• 메모리 효율성 극대화
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

class ModulePriority(Enum):
    """모듈 우선순위 정의"""
    CRITICAL = "critical"      # 반드시 필요한 핵심 모듈
    HIGH = "high"              # 높은 우선순위
    MEDIUM = "medium"          # 중간 우선순위
    LOW = "low"                # 낮은 우선순위
    OPTIONAL = "optional"      # 선택적 모듈

class ModuleCategory(Enum):
    """모듈 카테고리 정의"""
    CORE = "core"              # 핵심 기능
    PERFORMANCE = "performance" # 성능 관련
    STORAGE = "storage"        # 저장소 관련
    AUTOMATION = "automation"  # 자동화 관련
    ANALYTICS = "analytics"    # 분석 관련
    VALIDATION = "validation"  # 검증 관련

@dataclass
class ModuleUsagePattern:
    """모듈 사용 패턴 데이터 클래스"""
    module_name: str
    access_count: int
    last_access_time: datetime
    average_session_duration: float
    peak_usage_hours: List[int]
    dependency_modules: Set[str]
    performance_impact: float
    memory_usage: float
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['last_access_time'] = self.last_access_time.isoformat()
        data['dependency_modules'] = list(self.dependency_modules)
        return data

@dataclass
class ModuleRecommendation:
    """모듈 권장사항 데이터 클래스"""
    timestamp: datetime
    module_name: str
    priority: ModulePriority
    category: ModuleCategory
    reason: str
    expected_benefit: str
    confidence_score: float
    alternative_modules: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['priority'] = self.priority.value
        data['category'] = self.category.value
        return data

@dataclass
class ModuleCombination:
    """모듈 조합 데이터 클래스"""
    combination_id: str
    modules: List[str]
    total_memory_usage: float
    performance_score: float
    coverage_score: float
    efficiency_score: float
    recommended_for: str
    estimated_cost: str
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)

class IntelligentModuleSelector:
    """지능형 모듈 선택 시스템"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        지능형 모듈 선택 시스템 초기화
        
        Args:
            config: 설정 정보
        """
        self.config = config or {}
        
        # 모듈 정보 및 메타데이터
        self.module_metadata = {
            'core': {
                'name': 'Core Integration',
                'category': ModuleCategory.CORE,
                'priority': ModulePriority.CRITICAL,
                'base_memory_mb': 2.0,
                'dependencies': set(),
                'performance_impact': 0.1,
                'essential': True
            },
            'performance': {
                'name': 'Performance Monitor',
                'category': ModuleCategory.PERFORMANCE,
                'priority': ModulePriority.HIGH,
                'base_memory_mb': 1.5,
                'dependencies': {'core'},
                'performance_impact': 0.05,
                'essential': False
            },
            'backup': {
                'name': 'Backup Manager',
                'category': ModuleCategory.STORAGE,
                'priority': ModulePriority.MEDIUM,
                'base_memory_mb': 3.0,
                'dependencies': {'core'},
                'performance_impact': 0.08,
                'essential': False
            },
            'auto': {
                'name': 'Auto Integration',
                'category': ModuleCategory.AUTOMATION,
                'priority': ModulePriority.MEDIUM,
                'base_memory_mb': 4.0,
                'dependencies': {'core', 'performance'},
                'performance_impact': 0.15,
                'essential': False
            },
            'analytics': {
                'name': 'Advanced Analytics',
                'category': ModuleCategory.ANALYTICS,
                'priority': ModulePriority.LOW,
                'base_memory_mb': 6.0,
                'dependencies': {'core', 'performance'},
                'performance_impact': 0.12,
                'essential': False
            },
            'validation': {
                'name': 'Validation System',
                'category': ModuleCategory.VALIDATION,
                'priority': ModulePriority.LOW,
                'base_memory_mb': 2.5,
                'dependencies': {'core'},
                'performance_impact': 0.06,
                'essential': False
            }
        }
        
        # 사용 패턴 분석 데이터
        self.usage_patterns: Dict[str, ModuleUsagePattern] = {}
        self.access_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.session_data: Dict[str, List[float]] = defaultdict(list)
        
        # 모듈 조합 데이터
        self.module_combinations: Dict[str, ModuleCombination] = {}
        self.recommendation_history: List[ModuleRecommendation] = []
        
        # 학습 및 최적화 설정
        self.learning_enabled = self.config.get('learning_enabled', True)
        self.auto_optimization = self.config.get('auto_optimization', True)
        self.memory_threshold = self.config.get('memory_threshold', 80.0)  # MB
        
        # 통계 정보
        self.stats = {
            'total_recommendations': 0,
            'successful_predictions': 0,
            'memory_savings_mb': 0.0,
            'performance_improvements': 0.0,
            'last_optimization_time': None
        }
        
        # 백그라운드 최적화 스레드
        self.optimization_thread = None
        self.optimization_active = False
        
        logger.info("🧠 지능형 모듈 선택 시스템 초기화 완료")
    
    def record_module_access(self, module_name: str, access_type: str = "read"):
        """
        모듈 접근 기록
        
        Args:
            module_name: 접근한 모듈명
            access_type: 접근 유형 (read, write, execute)
        """
        try:
            current_time = datetime.now()
            
            # 접근 이력 기록
            self.access_history[module_name].append({
                'timestamp': current_time,
                'type': access_type,
                'memory_usage': self._get_current_memory_usage()
            })
            
            # 사용 패턴 업데이트
            if module_name not in self.usage_patterns:
                self.usage_patterns[module_name] = ModuleUsagePattern(
                    module_name=module_name,
                    access_count=0,
                    last_access_time=current_time,
                    average_session_duration=0.0,
                    peak_usage_hours=[],
                    dependency_modules=set(),
                    performance_impact=0.0,
                    memory_usage=0.0
                )
            
            pattern = self.usage_patterns[module_name]
            pattern.access_count += 1
            pattern.last_access_time = current_time
            
            # 피크 사용 시간 분석
            hour = current_time.hour
            if hour not in pattern.peak_usage_hours:
                pattern.peak_usage_hours.append(hour)
                pattern.peak_usage_hours.sort()
            
            # 메모리 사용량 업데이트
            pattern.memory_usage = self._get_current_memory_usage()
            
            logger.debug(f"📊 모듈 접근 기록: {module_name} ({access_type})")
            
        except Exception as e:
            logger.error(f"모듈 접근 기록 실패: {e}")
    
    def start_session_tracking(self, module_name: str):
        """세션 추적 시작"""
        try:
            self.session_data[module_name].append(time.time())
            logger.debug(f"🕐 세션 추적 시작: {module_name}")
        except Exception as e:
            logger.error(f"세션 추적 시작 실패: {e}")
    
    def end_session_tracking(self, module_name: str):
        """세션 추적 종료"""
        try:
            if module_name in self.session_data and self.session_data[module_name]:
                start_time = self.session_data[module_name].pop()
                duration = time.time() - start_time
                
                if module_name in self.usage_patterns:
                    pattern = self.usage_patterns[module_name]
                    # 평균 세션 시간 업데이트 (이동 평균)
                    if pattern.average_session_duration == 0:
                        pattern.average_session_duration = duration
                    else:
                        pattern.average_session_duration = (
                            pattern.average_session_duration * 0.9 + duration * 0.1
                        )
                
                logger.debug(f"🕐 세션 추적 종료: {module_name}, 지속시간: {duration:.2f}초")
                
        except Exception as e:
            logger.error(f"세션 추적 종료 실패: {e}")
    
    def analyze_usage_patterns(self) -> Dict[str, Any]:
        """사용 패턴 분석"""
        try:
            analysis = {
                'total_modules': len(self.usage_patterns),
                'most_used_modules': [],
                'least_used_modules': [],
                'peak_usage_hours': [],
                'memory_efficiency': 0.0,
                'performance_insights': []
            }
            
            if not self.usage_patterns:
                return analysis
            
            # 가장 많이 사용된 모듈
            sorted_by_usage = sorted(
                self.usage_patterns.items(),
                key=lambda x: x[1].access_count,
                reverse=True
            )
            
            analysis['most_used_modules'] = [
                {'name': name, 'access_count': pattern.access_count}
                for name, pattern in sorted_by_usage[:3]
            ]
            
            analysis['least_used_modules'] = [
                {'name': name, 'access_count': pattern.access_count}
                for name, pattern in sorted_by_usage[-3:]
            ]
            
            # 피크 사용 시간 분석
            all_hours = []
            for pattern in self.usage_patterns.values():
                all_hours.extend(pattern.peak_usage_hours)
            
            if all_hours:
                hour_counts = defaultdict(int)
                for hour in all_hours:
                    hour_counts[hour] += 1
                
                peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
                analysis['peak_usage_hours'] = [
                    {'hour': hour, 'count': count}
                    for hour, count in peak_hours[:5]
                ]
            
            # 메모리 효율성 계산
            total_memory = sum(pattern.memory_usage for pattern in self.usage_patterns.values())
            if total_memory > 0:
                analysis['memory_efficiency'] = (
                    sum(pattern.access_count for pattern in self.usage_patterns.values()) / total_memory
                )
            
            # 성능 인사이트
            for name, pattern in self.usage_patterns.items():
                if pattern.performance_impact > 0.1:  # 성능 영향이 큰 모듈
                    analysis['performance_insights'].append({
                        'module': name,
                        'impact': pattern.performance_impact,
                        'recommendation': '성능 최적화 고려'
                    })
            
            logger.info(f"📊 사용 패턴 분석 완료: {len(self.usage_patterns)}개 모듈")
            return analysis
            
        except Exception as e:
            logger.error(f"사용 패턴 분석 실패: {e}")
            return {'error': str(e)}
    
    def generate_module_recommendations(self, 
                                      current_modules: List[str],
                                      target_performance: float = 0.8,
                                      max_memory_mb: float = 50.0) -> List[ModuleRecommendation]:
        """
        모듈 권장사항 생성
        
        Args:
            current_modules: 현재 로드된 모듈 목록
            target_performance: 목표 성능 점수
            max_memory_mb: 최대 메모리 사용량 (MB)
        
        Returns:
            List[ModuleRecommendation]: 모듈 권장사항 목록
        """
        try:
            recommendations = []
            current_memory = sum(
                self.module_metadata[module]['base_memory_mb']
                for module in current_modules
                if module in self.module_metadata
            )
            
            # 현재 성능 점수 계산
            current_performance = self._calculate_current_performance(current_modules)
            
            # 성능 개선이 필요한 경우
            if current_performance < target_performance:
                # 성능 향상 모듈 추천
                for module_name, metadata in self.module_metadata.items():
                    if module_name not in current_modules:
                        # 의존성 확인
                        if self._can_add_module(module_name, current_modules):
                            benefit = self._estimate_performance_benefit(module_name, current_modules)
                            
                            if benefit > 0.1:  # 의미있는 성능 향상
                                recommendation = ModuleRecommendation(
                                    timestamp=datetime.now(),
                                    module_name=module_name,
                                    priority=metadata['priority'],
                                    category=metadata['category'],
                                    reason=f"성능 향상: {benefit:.2f}점 개선 예상",
                                    expected_benefit=f"성능 점수 {benefit:.2f}점 향상",
                                    confidence_score=min(0.9, benefit * 2),
                                    alternative_modules=self._find_alternatives(module_name)
                                )
                                recommendations.append(recommendation)
            
            # 메모리 최적화 권장사항
            if current_memory > max_memory_mb * 0.8:  # 메모리 사용량이 높은 경우
                for module_name in current_modules:
                    if not self.module_metadata[module_name]['essential']:
                        usage_frequency = self.usage_patterns.get(module_name, None)
                        
                        if usage_frequency and usage_frequency.access_count < 5:  # 사용 빈도가 낮은 경우
                            recommendation = ModuleRecommendation(
                                timestamp=datetime.now(),
                                module_name=module_name,
                                priority=ModulePriority.LOW,
                                category=self.module_metadata[module_name]['category'],
                                reason="메모리 최적화: 사용 빈도가 낮음",
                                expected_benefit=f"메모리 {self.module_metadata[module_name]['base_memory_mb']:.1f}MB 절약",
                                confidence_score=0.7,
                                alternative_modules=[]
                            )
                            recommendations.append(recommendation)
            
            # 사용 패턴 기반 권장사항
            for module_name, pattern in self.usage_patterns.items():
                if module_name not in current_modules:
                    # 자주 사용되는 모듈 자동 로딩 권장
                    if pattern.access_count > 10 and pattern.last_access_time > datetime.now() - timedelta(hours=1):
                        recommendation = ModuleRecommendation(
                            timestamp=datetime.now(),
                            module_name=module_name,
                            priority=ModulePriority.MEDIUM,
                            category=self.module_metadata[module_name]['category'],
                            reason="사용 패턴: 자주 사용되는 모듈",
                            expected_benefit="사용자 경험 향상",
                            confidence_score=0.8,
                            alternative_modules=[]
                        )
                        recommendations.append(recommendation)
            
            # 우선순위별 정렬
            recommendations.sort(key=lambda x: self._get_priority_score(x.priority), reverse=True)
            
            # 권장사항 저장
            self.recommendation_history.extend(recommendations)
            self.stats['total_recommendations'] += len(recommendations)
            
            logger.info(f"💡 모듈 권장사항 생성 완료: {len(recommendations)}개")
            return recommendations
            
        except Exception as e:
            logger.error(f"모듈 권장사항 생성 실패: {e}")
            return []
    
    def create_optimal_module_combination(self, 
                                        requirements: Dict[str, Any],
                                        constraints: Dict[str, Any]) -> ModuleCombination:
        """
        최적의 모듈 조합 생성
        
        Args:
            requirements: 요구사항 (성능, 기능 등)
            constraints: 제약사항 (메모리, 시간 등)
        
        Returns:
            ModuleCombination: 최적 모듈 조합
        """
        try:
            # 기본 핵심 모듈
            base_modules = ['core']
            
            # 요구사항에 따른 모듈 추가
            if requirements.get('performance_monitoring', False):
                base_modules.append('performance')
            
            if requirements.get('data_backup', False):
                base_modules.append('backup')
            
            if requirements.get('automation', False):
                base_modules.append('auto')
            
            if requirements.get('advanced_analysis', False):
                base_modules.append('analytics')
            
            if requirements.get('validation', False):
                base_modules.append('validation')
            
            # 메모리 제약 확인 및 최적화
            total_memory = sum(
                self.module_metadata[module]['base_memory_mb']
                for module in base_modules
            )
            
            if total_memory > constraints.get('max_memory_mb', 50.0):
                # 메모리 제약에 맞춰 모듈 제거
                non_essential = [m for m in base_modules if not self.module_metadata[m]['essential']]
                for module in reversed(non_essential):
                    if total_memory > constraints.get('max_memory_mb', 50.0):
                        base_modules.remove(module)
                        total_memory -= self.module_metadata[module]['base_memory_mb']
            
            # 성능 점수 계산
            performance_score = self._calculate_performance_score(base_modules)
            coverage_score = self._calculate_coverage_score(base_modules, requirements)
            efficiency_score = self._calculate_efficiency_score(base_modules, total_memory)
            
            combination = ModuleCombination(
                combination_id=f"opt_{int(time.time())}",
                modules=base_modules,
                total_memory_usage=total_memory,
                performance_score=performance_score,
                coverage_score=coverage_score,
                efficiency_score=efficiency_score,
                recommended_for=requirements.get('purpose', 'general'),
                estimated_cost=f"{total_memory:.1f}MB 메모리"
            )
            
            # 조합 저장
            self.module_combinations[combination.combination_id] = combination
            
            logger.info(f"🎯 최적 모듈 조합 생성: {len(base_modules)}개 모듈, {total_memory:.1f}MB")
            return combination
            
        except Exception as e:
            logger.error(f"최적 모듈 조합 생성 실패: {e}")
            return None
    
    def start_auto_optimization(self, interval_seconds: int = 300):
        """자동 최적화 시작"""
        try:
            if self.optimization_active:
                logger.warning("자동 최적화가 이미 실행 중입니다")
                return True
            
            self.optimization_active = True
            self.optimization_thread = threading.Thread(
                target=self._optimization_loop,
                args=(interval_seconds,),
                daemon=True,
                name="ModuleOptimizer"
            )
            self.optimization_thread.start()
            
            logger.info(f"🚀 자동 모듈 최적화 시작 (간격: {interval_seconds}초)")
            return True
            
        except Exception as e:
            logger.error(f"자동 최적화 시작 실패: {e}")
            self.optimization_active = False
            return False
    
    def stop_auto_optimization(self):
        """자동 최적화 중지"""
        try:
            self.optimization_active = False
            
            if self.optimization_thread and self.optimization_thread.is_alive():
                self.optimization_thread.join(timeout=5)
            
            logger.info("🛑 자동 모듈 최적화 중지")
            return True
            
        except Exception as e:
            logger.error(f"자동 최적화 중지 실패: {e}")
            return False
    
    def _optimization_loop(self, interval_seconds: int):
        """최적화 루프"""
        logger.info("🔄 자동 최적화 루프 시작")
        
        while self.optimization_active:
            try:
                # 사용 패턴 분석
                analysis = self.analyze_usage_patterns()
                
                # 모듈 조합 최적화
                self._optimize_module_combinations()
                
                # 메모리 사용량 최적화
                self._optimize_memory_usage()
                
                # 통계 업데이트
                self.stats['last_optimization_time'] = datetime.now()
                
                logger.debug("🔄 자동 최적화 완료")
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"자동 최적화 루프 오류: {e}")
                time.sleep(60)  # 오류 발생시 1분 대기
        
        logger.info("🔄 자동 최적화 루프 종료")
    
    def _optimize_module_combinations(self):
        """모듈 조합 최적화"""
        try:
            # 사용 빈도가 낮은 조합 제거
            old_combinations = [
                combo_id for combo_id, combo in self.module_combinations.items()
                if combo_id.startswith('opt_') and 
                int(combo_id.split('_')[1]) < time.time() - 3600  # 1시간 이상 된 조합
            ]
            
            for combo_id in old_combinations:
                del self.module_combinations[combo_id]
            
            if old_combinations:
                logger.debug(f"🗑️ 오래된 모듈 조합 정리: {len(old_combinations)}개")
                
        except Exception as e:
            logger.error(f"모듈 조합 최적화 실패: {e}")
    
    def _optimize_memory_usage(self):
        """메모리 사용량 최적화"""
        try:
            current_memory = sum(
                pattern.memory_usage for pattern in self.usage_patterns.values()
            )
            
            if current_memory > self.memory_threshold:
                # 메모리 사용량이 높은 경우 최적화 제안
                logger.info(f"💾 메모리 최적화 필요: {current_memory:.1f}MB > {self.memory_threshold}MB")
                
        except Exception as e:
            logger.error(f"메모리 사용량 최적화 실패: {e}")
    
    def _get_current_memory_usage(self) -> float:
        """현재 메모리 사용량 반환 (시뮬레이션)"""
        try:
            # 실제 구현에서는 실제 메모리 사용량을 측정
            import random
            return random.uniform(1.0, 10.0)
        except:
            return 5.0
    
    def _calculate_current_performance(self, modules: List[str]) -> float:
        """현재 성능 점수 계산"""
        try:
            if not modules:
                return 0.0
            
            total_score = 0.0
            for module in modules:
                if module in self.module_metadata:
                    metadata = self.module_metadata[module]
                    # 우선순위에 따른 점수
                    priority_score = self._get_priority_score(metadata['priority'])
                    # 성능 영향 고려
                    performance_score = 1.0 - metadata['performance_impact']
                    total_score += priority_score * performance_score
            
            return total_score / len(modules)
            
        except Exception as e:
            logger.error(f"현재 성능 점수 계산 실패: {e}")
            return 0.5
    
    def _estimate_performance_benefit(self, module_name: str, current_modules: List[str]) -> float:
        """모듈 추가 시 성능 향상 예상치"""
        try:
            if module_name not in self.module_metadata:
                return 0.0
            
            metadata = self.module_metadata[module_name]
            current_performance = self._calculate_current_performance(current_modules)
            
            # 모듈의 성능 영향과 우선순위 고려
            benefit = metadata['performance_impact'] * self._get_priority_score(metadata['priority'])
            
            return min(0.3, benefit)  # 최대 0.3점 향상
            
        except Exception as e:
            logger.error(f"성능 향상 예상치 계산 실패: {e}")
            return 0.0
    
    def _can_add_module(self, module_name: str, current_modules: List[str]) -> bool:
        """모듈 추가 가능 여부 확인"""
        try:
            if module_name not in self.module_metadata:
                return False
            
            metadata = self.module_metadata[module_name]
            dependencies = metadata['dependencies']
            
            # 의존성 확인
            return all(dep in current_modules for dep in dependencies)
            
        except Exception as e:
            logger.error(f"모듈 추가 가능 여부 확인 실패: {e}")
            return False
    
    def _find_alternatives(self, module_name: str) -> List[str]:
        """대안 모듈 찾기"""
        try:
            alternatives = []
            target_category = self.module_metadata[module_name]['category']
            
            for name, metadata in self.module_metadata.items():
                if (name != module_name and 
                    metadata['category'] == target_category and
                    metadata['priority'] == self.module_metadata[module_name]['priority']):
                    alternatives.append(name)
            
            return alternatives[:3]  # 최대 3개
            
        except Exception as e:
            logger.error(f"대안 모듈 찾기 실패: {e}")
            return []
    
    def _get_priority_score(self, priority: ModulePriority) -> float:
        """우선순위 점수 반환"""
        priority_scores = {
            ModulePriority.CRITICAL: 1.0,
            ModulePriority.HIGH: 0.8,
            ModulePriority.MEDIUM: 0.6,
            ModulePriority.LOW: 0.4,
            ModulePriority.OPTIONAL: 0.2
        }
        return priority_scores.get(priority, 0.5)
    
    def _calculate_performance_score(self, modules: List[str]) -> float:
        """모듈 조합의 성능 점수 계산"""
        try:
            if not modules:
                return 0.0
            
            total_score = 0.0
            for module in modules:
                if module in self.module_metadata:
                    metadata = self.module_metadata[module]
                    priority_score = self._get_priority_score(metadata['priority'])
                    performance_score = 1.0 - metadata['performance_impact']
                    total_score += priority_score * performance_score
            
            return total_score / len(modules)
            
        except Exception as e:
            logger.error(f"성능 점수 계산 실패: {e}")
            return 0.5
    
    def _calculate_coverage_score(self, modules: List[str], requirements: Dict[str, Any]) -> float:
        """요구사항 커버리지 점수 계산"""
        try:
            if not requirements:
                return 0.5
            
            covered_requirements = 0
            total_requirements = len(requirements)
            
            for req_name, req_value in requirements.items():
                if req_value:  # 요구사항이 활성화된 경우
                    # 해당 요구사항을 만족하는 모듈이 있는지 확인
                    if self._requirement_satisfied(req_name, modules):
                        covered_requirements += 1
            
            return covered_requirements / total_requirements if total_requirements > 0 else 0.0
            
        except Exception as e:
            logger.error(f"커버리지 점수 계산 실패: {e}")
            return 0.5
    
    def _requirement_satisfied(self, requirement: str, modules: List[str]) -> bool:
        """요구사항 만족 여부 확인"""
        requirement_mapping = {
            'performance_monitoring': 'performance',
            'data_backup': 'backup',
            'automation': 'auto',
            'advanced_analysis': 'analytics',
            'validation': 'validation'
        }
        
        required_module = requirement_mapping.get(requirement)
        return required_module in modules if required_module else False
    
    def _calculate_efficiency_score(self, modules: List[str], memory_usage: float) -> float:
        """효율성 점수 계산"""
        try:
            if memory_usage <= 0:
                return 0.0
            
            # 메모리 사용량이 낮을수록 높은 점수
            memory_score = max(0, 1 - (memory_usage / 100))  # 100MB 기준
            
            # 모듈 수가 적을수록 높은 점수 (단순성)
            simplicity_score = max(0, 1 - (len(modules) / 10))  # 10개 기준
            
            return (memory_score + simplicity_score) / 2
            
        except Exception as e:
            logger.error(f"효율성 점수 계산 실패: {e}")
            return 0.5
    
    def get_selector_summary(self) -> Dict[str, Any]:
        """선택기 요약 정보 반환"""
        try:
            summary = {
                'total_modules': len(self.module_metadata),
                'usage_patterns': len(self.usage_patterns),
                'module_combinations': len(self.module_combinations),
                'total_recommendations': self.stats['total_recommendations'],
                'auto_optimization_active': self.optimization_active,
                'last_optimization_time': self.stats['last_optimization_time'].isoformat() if self.stats['last_optimization_time'] else None,
                'memory_threshold_mb': self.memory_threshold,
                'learning_enabled': self.learning_enabled
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"선택기 요약 생성 실패: {e}")
            return {'error': str(e)}
    
    def export_learning_data(self, format_type: str = 'json') -> str:
        """학습 데이터 내보내기"""
        try:
            if format_type == 'json':
                export_data = {
                    'export_time': datetime.now().isoformat(),
                    'usage_patterns': {name: pattern.to_dict() for name, pattern in self.usage_patterns.items()},
                    'module_combinations': {combo_id: combo.to_dict() for combo_id, combo in self.module_combinations.items()},
                    'recommendation_history': [rec.to_dict() for rec in self.recommendation_history],
                    'stats': self.stats,
                    'module_metadata': self.module_metadata
                }
                
                filename = f"intelligent_selector_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"📤 학습 데이터 내보내기 완료: {filename}")
                return filename
            
            else:
                raise ValueError(f"지원하지 않는 형식: {format_type}")
                
        except Exception as e:
            logger.error(f"학습 데이터 내보내기 실패: {e}")
            return ""

# 기존 호환성을 위한 별칭
ModuleSelector = IntelligentModuleSelector




