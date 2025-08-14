"""
🎓 학습 기반 추천 시스템 (Learning-Based Recommender)
사용자 행동 패턴을 학습하고 개인화된 모듈 추천을 제공하는 고급 시스템

주요 기능:
• 사용자 행동 패턴 학습 및 분석
• 개인화된 모듈 추천 시스템
• 예측적 모듈 로딩 구현
• 적응형 성능 최적화 제공
• 머신러닝 기반 추천 알고리즘
"""

import logging
import time
import json
import pickle
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import threading
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import hashlib

logger = logging.getLogger(__name__)

class UserBehaviorType(Enum):
    """사용자 행동 유형 정의"""
    MODULE_ACCESS = "module_access"      # 모듈 접근
    PERFORMANCE_QUERY = "performance_query"  # 성능 조회
    BACKUP_OPERATION = "backup_operation"    # 백업 작업
    ANALYSIS_REQUEST = "analysis_request"     # 분석 요청
    INTEGRATION_TASK = "integration_task"    # 통합 작업
    SYSTEM_MAINTENANCE = "system_maintenance" # 시스템 유지보수

class RecommendationType(Enum):
    """추천 유형 정의"""
    MODULE_LOADING = "module_loading"    # 모듈 로딩
    PERFORMANCE_OPTIMIZATION = "performance_optimization"  # 성능 최적화
    RESOURCE_MANAGEMENT = "resource_management"  # 리소스 관리
    WORKFLOW_SUGGESTION = "workflow_suggestion"  # 워크플로우 제안
    MAINTENANCE_ALERT = "maintenance_alert"  # 유지보수 알림

@dataclass
class UserBehavior:
    """사용자 행동 데이터 클래스"""
    timestamp: datetime
    user_id: str
    behavior_type: UserBehaviorType
    module_name: str
    action: str
    parameters: Dict[str, Any]
    session_duration: float
    success: bool
    performance_impact: float
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['behavior_type'] = self.behavior_type.value
        return data

@dataclass
class UserProfile:
    """사용자 프로필 데이터 클래스"""
    user_id: str
    created_at: datetime
    last_updated: datetime
    total_sessions: int
    preferred_modules: List[str]
    usage_patterns: Dict[str, float]
    performance_preferences: Dict[str, float]
    skill_level: str  # beginner, intermediate, advanced
    workload_type: str  # light, moderate, heavy
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data

@dataclass
class PersonalizedRecommendation:
    """개인화된 추천 데이터 클래스"""
    timestamp: datetime
    user_id: str
    recommendation_type: RecommendationType
    title: str
    description: str
    confidence_score: float
    expected_benefit: str
    implementation_steps: List[str]
    priority: str
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['recommendation_type'] = self.recommendation_type.value
        return data

@dataclass
class LearningModel:
    """학습 모델 데이터 클래스"""
    model_id: str
    model_type: str
    created_at: datetime
    last_trained: datetime
    accuracy_score: float
    training_samples: int
    features: List[str]
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_trained'] = self.last_trained.isoformat()
        return data

class LearningBasedRecommender:
    """학습 기반 추천 시스템"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        학습 기반 추천 시스템 초기화
        
        Args:
            config: 설정 정보
        """
        self.config = config or {}
        
        # 사용자 데이터 저장소
        self.user_behaviors: List[UserBehavior] = []
        self.user_profiles: Dict[str, UserProfile] = {}
        self.personalized_recommendations: List[PersonalizedRecommendation] = []
        
        # 학습 모델 관련
        self.learning_models: Dict[str, LearningModel] = {}
        self.scaler = StandardScaler()
        self.clustering_model = None
        
        # 학습 및 추천 설정
        self.learning_enabled = self.config.get('learning_enabled', True)
        self.auto_training = self.config.get('auto_training', True)
        self.min_training_samples = self.config.get('min_training_samples', 100)
        self.training_interval = self.config.get('training_interval', 3600)  # 1시간
        
        # 사용자 행동 분석 설정
        self.behavior_window_hours = self.config.get('behavior_window_hours', 24)
        self.pattern_threshold = self.config.get('pattern_threshold', 0.7)
        
        # 백그라운드 학습 스레드
        self.learning_thread = None
        self.learning_active = False
        
        # 통계 정보
        self.stats = {
            'total_behaviors_collected': 0,
            'total_recommendations_generated': 0,
            'total_users_profiled': 0,
            'model_accuracy_improvements': 0.0,
            'last_training_time': None,
            'last_recommendation_time': None
        }
        
        # 초기 학습 모델 생성
        self._initialize_learning_models()
        
        logger.info("🎓 학습 기반 추천 시스템 초기화 완료")
    
    def _initialize_learning_models(self):
        """초기 학습 모델 생성"""
        try:
            # 사용자 행동 클러스터링 모델
            clustering_model = LearningModel(
                model_id="user_behavior_clustering",
                model_type="kmeans_clustering",
                created_at=datetime.now(),
                last_trained=datetime.now(),
                accuracy_score=0.0,
                training_samples=0,
                features=['session_duration', 'performance_impact', 'success_rate'],
                parameters={'n_clusters': 3, 'random_state': 42}
            )
            self.learning_models["user_behavior_clustering"] = clustering_model
            
            # 모듈 사용 패턴 모델
            pattern_model = LearningModel(
                model_id="module_usage_pattern",
                model_type="pattern_analysis",
                created_at=datetime.now(),
                last_trained=datetime.now(),
                accuracy_score=0.0,
                training_samples=0,
                features=['access_frequency', 'session_length', 'performance_impact'],
                parameters={'pattern_threshold': self.pattern_threshold}
            )
            self.learning_models["module_usage_pattern"] = pattern_model
            
            logger.info("🧠 초기 학습 모델 생성 완료")
            
        except Exception as e:
            logger.error(f"초기 학습 모델 생성 실패: {e}")
    
    def record_user_behavior(self, 
                           user_id: str,
                           behavior_type: UserBehaviorType,
                           module_name: str,
                           action: str,
                           parameters: Dict[str, Any] = None,
                           session_duration: float = 0.0,
                           success: bool = True,
                           performance_impact: float = 0.0):
        """
        사용자 행동 기록
        
        Args:
            user_id: 사용자 ID
            behavior_type: 행동 유형
            module_name: 모듈명
            action: 수행한 작업
            parameters: 작업 매개변수
            session_duration: 세션 지속시간
            success: 성공 여부
            performance_impact: 성능 영향도
        """
        try:
            behavior = UserBehavior(
                timestamp=datetime.now(),
                user_id=user_id,
                behavior_type=behavior_type,
                module_name=module_name,
                action=action,
                parameters=parameters or {},
                session_duration=session_duration,
                success=success,
                performance_impact=performance_impact
            )
            
            self.user_behaviors.append(behavior)
            self.stats['total_behaviors_collected'] += 1
            
            # 사용자 프로필 업데이트
            self._update_user_profile(user_id, behavior)
            
            logger.debug(f"📊 사용자 행동 기록: {user_id} - {behavior_type.value} - {module_name}")
            
        except Exception as e:
            logger.error(f"사용자 행동 기록 실패: {e}")
    
    def _update_user_profile(self, user_id: str, behavior: UserBehavior):
        """사용자 프로필 업데이트"""
        try:
            if user_id not in self.user_profiles:
                # 새 사용자 프로필 생성
                self.user_profiles[user_id] = UserProfile(
                    user_id=user_id,
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    total_sessions=0,
                    preferred_modules=[],
                    usage_patterns={},
                    performance_preferences={},
                    skill_level='beginner',
                    workload_type='light'
                )
                self.stats['total_users_profiled'] += 1
            
            profile = self.user_profiles[user_id]
            profile.last_updated = datetime.now()
            
            # 모듈 사용 패턴 업데이트
            if behavior.module_name not in profile.usage_patterns:
                profile.usage_patterns[behavior.module_name] = 0.0
            
            profile.usage_patterns[behavior.module_name] += 1.0
            
            # 성능 선호도 업데이트
            if behavior.performance_impact > 0:
                if 'performance_impact' not in profile.performance_preferences:
                    profile.performance_preferences['performance_impact'] = 0.0
                
                profile.performance_preferences['performance_impact'] = (
                    profile.performance_preferences['performance_impact'] * 0.9 + 
                    behavior.performance_impact * 0.1
                )
            
            # 세션 수 업데이트
            if behavior.session_duration > 0:
                profile.total_sessions += 1
            
            # 선호 모듈 업데이트
            self._update_preferred_modules(profile)
            
            # 기술 수준 및 워크로드 유형 업데이트
            self._update_user_classification(profile)
            
        except Exception as e:
            logger.error(f"사용자 프로필 업데이트 실패: {e}")
    
    def _update_preferred_modules(self, profile: UserProfile):
        """선호 모듈 업데이트"""
        try:
            # 사용 빈도 기반으로 선호 모듈 정렬
            sorted_modules = sorted(
                profile.usage_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # 상위 5개 모듈을 선호 모듈로 설정
            profile.preferred_modules = [module for module, _ in sorted_modules[:5]]
            
        except Exception as e:
            logger.error(f"선호 모듈 업데이트 실패: {e}")
    
    def _update_user_classification(self, profile: UserProfile):
        """사용자 분류 업데이트"""
        try:
            # 기술 수준 분류
            total_usage = sum(profile.usage_patterns.values())
            if total_usage > 100:
                profile.skill_level = 'advanced'
            elif total_usage > 50:
                profile.skill_level = 'intermediate'
            else:
                profile.skill_level = 'beginner'
            
            # 워크로드 유형 분류
            avg_session_duration = profile.performance_preferences.get('performance_impact', 0)
            if avg_session_duration > 0.8:
                profile.workload_type = 'heavy'
            elif avg_session_duration > 0.4:
                profile.workload_type = 'moderate'
            else:
                profile.workload_type = 'light'
                
        except Exception as e:
            logger.error(f"사용자 분류 업데이트 실패: {e}")
    
    def analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """사용자 패턴 분석"""
        try:
            if user_id not in self.user_profiles:
                return {'error': '사용자 프로필이 없습니다'}
            
            profile = self.user_profiles[user_id]
            
            # 사용자별 행동 데이터 필터링
            user_behaviors = [
                b for b in self.user_behaviors 
                if b.user_id == user_id and 
                b.timestamp > datetime.now() - timedelta(hours=self.behavior_window_hours)
            ]
            
            if not user_behaviors:
                return {'message': '분석할 행동 데이터가 부족합니다'}
            
            # 행동 유형별 분석
            behavior_analysis = defaultdict(list)
            for behavior in user_behaviors:
                behavior_analysis[behavior.behavior_type.value].append(behavior)
            
            # 성공률 분석
            success_rate = sum(1 for b in user_behaviors if b.success) / len(user_behaviors)
            
            # 성능 영향도 분석
            performance_impacts = [b.performance_impact for b in user_behaviors if b.performance_impact > 0]
            avg_performance_impact = np.mean(performance_impacts) if performance_impacts else 0.0
            
            # 세션 패턴 분석
            session_durations = [b.session_duration for b in user_behaviors if b.session_duration > 0]
            avg_session_duration = np.mean(session_durations) if session_durations else 0.0
            
            analysis = {
                'user_id': user_id,
                'analysis_period_hours': self.behavior_window_hours,
                'total_behaviors': len(user_behaviors),
                'success_rate': success_rate,
                'average_performance_impact': avg_performance_impact,
                'average_session_duration': avg_session_duration,
                'behavior_distribution': {
                    behavior_type: len(behaviors)
                    for behavior_type, behaviors in behavior_analysis.items()
                },
                'preferred_modules': profile.preferred_modules,
                'skill_level': profile.skill_level,
                'workload_type': profile.workload_type,
                'usage_patterns': profile.usage_patterns,
                'performance_preferences': profile.performance_preferences
            }
            
            logger.info(f"📊 사용자 패턴 분석 완료: {user_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"사용자 패턴 분석 실패: {e}")
            return {'error': str(e)}
    
    def generate_personalized_recommendations(self, user_id: str) -> List[PersonalizedRecommendation]:
        """개인화된 추천 생성"""
        try:
            if user_id not in self.user_profiles:
                logger.warning(f"사용자 프로필이 없습니다: {user_id}")
                return []
            
            profile = self.user_profiles[user_id]
            recommendations = []
            
            # 기술 수준 기반 추천
            if profile.skill_level == 'beginner':
                recommendations.extend(self._generate_beginner_recommendations(profile))
            elif profile.skill_level == 'intermediate':
                recommendations.extend(self._generate_intermediate_recommendations(profile))
            else:  # advanced
                recommendations.extend(self._generate_advanced_recommendations(profile))
            
            # 워크로드 유형 기반 추천
            if profile.workload_type == 'heavy':
                recommendations.extend(self._generate_heavy_workload_recommendations(profile))
            elif profile.workload_type == 'moderate':
                recommendations.extend(self._generate_moderate_workload_recommendations(profile))
            
            # 사용 패턴 기반 추천
            recommendations.extend(self._generate_pattern_based_recommendations(profile))
            
            # 성능 최적화 추천
            recommendations.extend(self._generate_performance_recommendations(profile))
            
            # 중복 제거 및 우선순위 정렬
            unique_recommendations = self._deduplicate_recommendations(recommendations)
            unique_recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # 추천 저장
            self.personalized_recommendations.extend(unique_recommendations)
            self.stats['total_recommendations_generated'] += len(unique_recommendations)
            self.stats['last_recommendation_time'] = datetime.now()
            
            logger.info(f"💡 개인화된 추천 생성 완료: {user_id} - {len(unique_recommendations)}개")
            return unique_recommendations
            
        except Exception as e:
            logger.error(f"개인화된 추천 생성 실패: {e}")
            return []
    
    def _generate_beginner_recommendations(self, profile: UserProfile) -> List[PersonalizedRecommendation]:
        """초보자용 추천 생성"""
        recommendations = []
        
        # 기본 모듈 사용법 추천
        if 'core' not in profile.preferred_modules:
            recommendations.append(PersonalizedRecommendation(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                recommendation_type=RecommendationType.MODULE_LOADING,
                title="핵심 모듈 활용 시작",
                description="시스템의 기본 기능을 익히기 위해 핵심 모듈 사용을 권장합니다",
                confidence_score=0.9,
                expected_benefit="시스템 이해도 향상 및 기본 작업 수행 능력 확보",
                implementation_steps=[
                    "핵심 모듈 로드 및 기본 기능 테스트",
                    "간단한 통합 작업 수행",
                    "기본 성능 모니터링 확인"
                ],
                priority="high",
                context={'skill_level': 'beginner', 'module': 'core'}
            ))
        
        return recommendations
    
    def _generate_intermediate_recommendations(self, profile: UserProfile) -> List[PersonalizedRecommendation]:
        """중급자용 추천 생성"""
        recommendations = []
        
        # 성능 모니터링 추천
        if 'performance' not in profile.preferred_modules:
            recommendations.append(PersonalizedRecommendation(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                recommendation_type=RecommendationType.PERFORMANCE_OPTIMIZATION,
                title="성능 모니터링 활성화",
                description="시스템 성능을 체계적으로 관리하기 위해 성능 모니터링을 권장합니다",
                confidence_score=0.8,
                expected_benefit="성능 병목 지점 식별 및 시스템 최적화",
                implementation_steps=[
                    "성능 모니터링 모듈 활성화",
                    "성능 지표 설정 및 임계값 조정",
                    "정기적인 성능 분석 수행"
                ],
                priority="medium",
                context={'skill_level': 'intermediate', 'module': 'performance'}
            ))
        
        return recommendations
    
    def _generate_advanced_recommendations(self, profile: UserProfile) -> List[PersonalizedRecommendation]:
        """고급자용 추천 생성"""
        recommendations = []
        
        # 고급 분석 모듈 추천
        if 'analytics' not in profile.preferred_modules:
            recommendations.append(PersonalizedRecommendation(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                recommendation_type=RecommendationType.WORKFLOW_SUGGESTION,
                title="고급 분석 모듈 활용",
                description="데이터 기반 인사이트를 얻기 위해 고급 분석 모듈을 권장합니다",
                confidence_score=0.85,
                expected_benefit="데이터 기반 의사결정 및 시스템 최적화",
                implementation_steps=[
                    "고급 분석 모듈 활성화",
                    "분석 워크플로우 설계",
                    "자동화된 분석 파이프라인 구축"
                ],
                priority="medium",
                context={'skill_level': 'advanced', 'module': 'analytics'}
            ))
        
        return recommendations
    
    def _generate_heavy_workload_recommendations(self, profile: UserProfile) -> List[PersonalizedRecommendation]:
        """높은 워크로드용 추천 생성"""
        recommendations = []
        
        # 자동화 모듈 추천
        if 'auto' not in profile.preferred_modules:
            recommendations.append(PersonalizedRecommendation(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                recommendation_type=RecommendationType.WORKFLOW_SUGGESTION,
                title="자동화 모듈 활성화",
                description="높은 워크로드를 효율적으로 관리하기 위해 자동화 모듈을 권장합니다",
                confidence_score=0.9,
                expected_benefit="작업 자동화 및 효율성 향상",
                implementation_steps=[
                    "자동화 모듈 활성화",
                    "반복 작업 자동화 설정",
                    "자동화 규칙 및 예외 처리 구성"
                ],
                priority="high",
                context={'workload_type': 'heavy', 'module': 'auto'}
            ))
        
        return recommendations
    
    def _generate_moderate_workload_recommendations(self, profile: UserProfile) -> List[PersonalizedRecommendation]:
        """보통 워크로드용 추천 생성"""
        recommendations = []
        
        # 백업 관리 모듈 추천
        if 'backup' not in profile.preferred_modules:
            recommendations.append(PersonalizedRecommendation(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                recommendation_type=RecommendationType.RESOURCE_MANAGEMENT,
                title="백업 관리 모듈 활용",
                description="데이터 안전성을 위해 백업 관리 모듈을 권장합니다",
                confidence_score=0.8,
                expected_benefit="데이터 보호 및 복구 능력 향상",
                implementation_steps=[
                    "백업 관리 모듈 활성화",
                    "백업 스케줄 및 정책 설정",
                    "정기적인 백업 테스트 수행"
                ],
                priority="medium",
                context={'workload_type': 'moderate', 'module': 'backup'}
            ))
        
        return recommendations
    
    def _generate_pattern_based_recommendations(self, profile: UserProfile) -> List[PersonalizedRecommendation]:
        """사용 패턴 기반 추천 생성"""
        recommendations = []
        
        # 자주 사용하는 모듈의 고급 기능 추천
        for module_name, usage_count in profile.usage_patterns.items():
            if usage_count > 20:  # 자주 사용하는 모듈
                if module_name == 'core':
                    recommendations.append(PersonalizedRecommendation(
                        timestamp=datetime.now(),
                        user_id=profile.user_id,
                        recommendation_type=RecommendationType.PERFORMANCE_OPTIMIZATION,
                        title="핵심 모듈 고급 설정",
                        description="자주 사용하는 핵심 모듈의 성능을 최적화하세요",
                        confidence_score=0.85,
                        expected_benefit="핵심 모듈 성능 향상 및 응답 시간 단축",
                        implementation_steps=[
                            "핵심 모듈 설정 최적화",
                            "캐싱 및 메모리 관리 개선",
                            "성능 모니터링 강화"
                        ],
                        priority="medium",
                        context={'pattern_based': True, 'module': module_name}
                    ))
        
        return recommendations
    
    def _generate_performance_recommendations(self, profile: UserProfile) -> List[PersonalizedRecommendation]:
        """성능 최적화 추천 생성"""
        recommendations = []
        
        # 성능 선호도 기반 추천
        if profile.performance_preferences.get('performance_impact', 0) > 0.7:
            recommendations.append(PersonalizedRecommendation(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                recommendation_type=RecommendationType.PERFORMANCE_OPTIMIZATION,
                title="성능 최적화 설정",
                description="높은 성능을 요구하는 작업을 위해 최적화 설정을 권장합니다",
                confidence_score=0.9,
                expected_benefit="전체 시스템 성능 향상 및 응답 시간 단축",
                implementation_steps=[
                    "성능 모니터링 강화",
                    "리소스 사용량 최적화",
                    "병목 지점 분석 및 개선"
                ],
                priority="high",
                context={'performance_focused': True}
            ))
        
        return recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[PersonalizedRecommendation]) -> List[PersonalizedRecommendation]:
        """중복 추천 제거"""
        try:
            unique_recommendations = []
            seen_titles = set()
            
            for rec in recommendations:
                title_hash = hashlib.md5(rec.title.encode()).hexdigest()
                if title_hash not in seen_titles:
                    unique_recommendations.append(rec)
                    seen_titles.add(title_hash)
            
            return unique_recommendations
            
        except Exception as e:
            logger.error(f"중복 추천 제거 실패: {e}")
            return recommendations
    
    def start_learning(self, interval_seconds: int = 3600):
        """학습 시작"""
        try:
            if self.learning_active:
                logger.warning("학습이 이미 실행 중입니다")
                return True
            
            self.learning_active = True
            self.learning_thread = threading.Thread(
                target=self._learning_loop,
                args=(interval_seconds,),
                daemon=True,
                name="LearningRecommender"
            )
            self.learning_thread.start()
            
            logger.info(f"🎓 학습 기반 추천 시스템 학습 시작 (간격: {interval_seconds}초)")
            return True
            
        except Exception as e:
            logger.error(f"학습 시작 실패: {e}")
            self.learning_active = False
            return False
    
    def stop_learning(self):
        """학습 중지"""
        try:
            self.learning_active = False
            
            if self.learning_thread and self.learning_thread.is_alive():
                self.learning_thread.join(timeout=5)
            
            logger.info("🛑 학습 기반 추천 시스템 학습 중지")
            return True
            
        except Exception as e:
            logger.error(f"학습 중지 실패: {e}")
            return False
    
    def _learning_loop(self, interval_seconds: int):
        """학습 루프"""
        logger.info("🔄 학습 루프 시작")
        
        while self.learning_active:
            try:
                # 충분한 데이터가 있는 경우 모델 학습
                if len(self.user_behaviors) >= self.min_training_samples:
                    self._train_learning_models()
                
                # 사용자 프로필 업데이트
                self._update_all_user_profiles()
                
                # 통계 업데이트
                self.stats['last_training_time'] = datetime.now()
                
                logger.debug("🔄 학습 루프 완료")
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"학습 루프 오류: {e}")
                time.sleep(300)  # 오류 발생시 5분 대기
        
        logger.info("🔄 학습 루프 종료")
    
    def _train_learning_models(self):
        """학습 모델 훈련"""
        try:
            if len(self.user_behaviors) < self.min_training_samples:
                logger.debug("훈련 데이터가 부족합니다")
                return
            
            # 사용자 행동 데이터 전처리
            features = self._extract_behavior_features()
            
            if len(features) < 2:
                logger.debug("특성 추출에 실패했습니다")
                return
            
            # 클러스터링 모델 훈련
            self._train_clustering_model(features)
            
            # 패턴 분석 모델 업데이트
            self._update_pattern_analysis_model()
            
            logger.info("🧠 학습 모델 훈련 완료")
            
        except Exception as e:
            logger.error(f"학습 모델 훈련 실패: {e}")
    
    def _extract_behavior_features(self) -> List[List[float]]:
        """행동 특성 추출"""
        try:
            features = []
            
            for behavior in self.user_behaviors[-self.min_training_samples:]:
                feature_vector = [
                    behavior.session_duration,
                    behavior.performance_impact,
                    1.0 if behavior.success else 0.0,
                    float(hash(behavior.module_name) % 100) / 100.0  # 모듈 해시 정규화
                ]
                features.append(feature_vector)
            
            return features
            
        except Exception as e:
            logger.error(f"행동 특성 추출 실패: {e}")
            return []
    
    def _train_clustering_model(self, features: List[List[float]]):
        """클러스터링 모델 훈련"""
        try:
            if not features:
                return
            
            # 특성 정규화
            features_array = np.array(features)
            features_scaled = self.scaler.fit_transform(features_array)
            
            # K-means 클러스터링
            n_clusters = min(3, len(features) // 10)
            if n_clusters < 2:
                n_clusters = 2
            
            self.clustering_model = KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10
            )
            
            # 모델 훈련
            cluster_labels = self.clustering_model.fit_predict(features_scaled)
            
            # 정확도 점수 계산 (간단한 실루엣 점수 대체)
            accuracy = 1.0 - (np.std(cluster_labels) / n_clusters)
            
            # 모델 정보 업데이트
            if "user_behavior_clustering" in self.learning_models:
                model = self.learning_models["user_behavior_clustering"]
                model.last_trained = datetime.now()
                model.accuracy_score = max(0.0, min(1.0, accuracy))
                model.training_samples = len(features)
                model.parameters['n_clusters'] = n_clusters
            
            logger.info(f"🎯 클러스터링 모델 훈련 완료: {n_clusters}개 클러스터, 정확도: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"클러스터링 모델 훈련 실패: {e}")
    
    def _update_pattern_analysis_model(self):
        """패턴 분석 모델 업데이트"""
        try:
            if "module_usage_pattern" in self.learning_models:
                model = self.learning_models["module_usage_pattern"]
                model.last_trained = datetime.now()
                model.training_samples = len(self.user_behaviors)
                
                # 패턴 임계값 동적 조정
                if len(self.user_behaviors) > 100:
                    # 사용 패턴의 표준편차를 기반으로 임계값 조정
                    module_usage_counts = defaultdict(int)
                    for behavior in self.user_behaviors:
                        module_usage_counts[behavior.module_name] += 1
                    
                    if module_usage_counts:
                        usage_std = np.std(list(module_usage_counts.values()))
                        model.parameters['pattern_threshold'] = max(0.5, min(0.9, 0.7 + usage_std / 100))
                
                logger.debug("📊 패턴 분석 모델 업데이트 완료")
                
        except Exception as e:
            logger.error(f"패턴 분석 모델 업데이트 실패: {e}")
    
    def _update_all_user_profiles(self):
        """모든 사용자 프로필 업데이트"""
        try:
            for user_id in list(self.user_profiles.keys()):
                try:
                    # 사용자별 행동 데이터로 프로필 업데이트
                    user_behaviors = [b for b in self.user_behaviors if b.user_id == user_id]
                    if user_behaviors:
                        for behavior in user_behaviors[-10:]:  # 최근 10개 행동만
                            self._update_user_profile(user_id, behavior)
                except Exception as e:
                    logger.debug(f"사용자 프로필 업데이트 실패: {user_id} - {e}")
            
        except Exception as e:
            logger.error(f"전체 사용자 프로필 업데이트 실패: {e}")
    
    def get_recommender_summary(self) -> Dict[str, Any]:
        """추천 시스템 요약 정보 반환"""
        try:
            summary = {
                'total_behaviors_collected': self.stats['total_behaviors_collected'],
                'total_recommendations_generated': self.stats['total_recommendations_generated'],
                'total_users_profiled': self.stats['total_users_profiled'],
                'learning_active': self.learning_active,
                'learning_models': len(self.learning_models),
                'last_training_time': self.stats['last_training_time'].isoformat() if self.stats['last_training_time'] else None,
                'last_recommendation_time': self.stats['last_recommendation_time'].isoformat() if self.stats['last_recommendation_time'] else None,
                'model_accuracy_improvements': self.stats['model_accuracy_improvements']
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"추천 시스템 요약 생성 실패: {e}")
            return {'error': str(e)}
    
    def predict_next_modules(self, user_id: str, time_window_hours: int = 24) -> List[str]:
        """사용자의 다음 사용할 모듈 예측"""
        try:
            if user_id not in self.user_profiles:
                return []
            
            profile = self.user_profiles[user_id]
            
            # 시간대별 사용 패턴 분석
            current_hour = datetime.now().hour
            time_based_patterns = self._analyze_time_based_patterns(user_id, current_hour)
            
            # 사용 빈도 기반 예측
            frequency_based = self._predict_by_frequency(profile)
            
            # 컨텍스트 기반 예측
            context_based = self._predict_by_context(user_id, time_window_hours)
            
            # 예측 점수 계산 및 정렬
            predictions = []
            for module_name in set(frequency_based + context_based + time_based_patterns):
                score = self._calculate_prediction_score(module_name, user_id, profile)
                predictions.append((module_name, score))
            
            # 점수 순으로 정렬하고 상위 모듈 반환
            predictions.sort(key=lambda x: x[1], reverse=True)
            predicted_modules = [module for module, score in predictions[:5]]
            
            logger.info(f"🔮 모듈 예측 완료: {user_id} - {predicted_modules}")
            return predicted_modules
            
        except Exception as e:
            logger.error(f"모듈 예측 실패: {e}")
            return []
    
    def _analyze_time_based_patterns(self, user_id: str, current_hour: int) -> List[str]:
        """시간대별 사용 패턴 분석"""
        try:
            time_patterns = defaultdict(int)
            
            for behavior in self.user_behaviors:
                if behavior.user_id == user_id:
                    behavior_hour = behavior.timestamp.hour
                    # 현재 시간과 비슷한 시간대의 사용 패턴 분석
                    if abs(behavior_hour - current_hour) <= 2:
                        time_patterns[behavior.module_name] += 1
            
            # 사용 빈도 순으로 정렬
            sorted_patterns = sorted(time_patterns.items(), key=lambda x: x[1], reverse=True)
            return [module for module, _ in sorted_patterns[:3]]
            
        except Exception as e:
            logger.error(f"시간대별 패턴 분석 실패: {e}")
            return []
    
    def _predict_by_frequency(self, profile: UserProfile) -> List[str]:
        """사용 빈도 기반 예측"""
        try:
            # 선호 모듈 중에서 사용 빈도가 높은 순으로 반환
            return profile.preferred_modules[:3]
            
        except Exception as e:
            logger.error(f"빈도 기반 예측 실패: {e}")
            return []
    
    def _predict_by_context(self, user_id: str, time_window_hours: int) -> List[str]:
        """컨텍스트 기반 예측"""
        try:
            recent_behaviors = [
                b for b in self.user_behaviors 
                if b.user_id == user_id and 
                b.timestamp > datetime.now() - timedelta(hours=time_window_hours)
            ]
            
            if not recent_behaviors:
                return []
            
            # 최근 사용한 모듈과 연관된 모듈 예측
            context_modules = set()
            for behavior in recent_behaviors[-3:]:  # 최근 3개 행동
                related_modules = self._get_related_modules(behavior.module_name)
                context_modules.update(related_modules)
            
            return list(context_modules)[:3]
            
        except Exception as e:
            logger.error(f"컨텍스트 기반 예측 실패: {e}")
            return []
    
    def _get_related_modules(self, module_name: str) -> List[str]:
        """연관 모듈 조회"""
        try:
            # 모듈 간 연관성 정의
            module_relations = {
                'core': ['performance', 'validation'],
                'performance': ['core', 'analytics'],
                'backup': ['core', 'validation'],
                'auto': ['core', 'performance'],
                'analytics': ['performance', 'core'],
                'validation': ['core', 'backup']
            }
            
            return module_relations.get(module_name, [])
            
        except Exception as e:
            logger.error(f"연관 모듈 조회 실패: {e}")
            return []
    
    def _calculate_prediction_score(self, module_name: str, user_id: str, profile: UserProfile) -> float:
        """예측 점수 계산"""
        try:
            score = 0.0
            
            # 사용 빈도 점수 (40%)
            usage_count = profile.usage_patterns.get(module_name, 0)
            frequency_score = min(usage_count / 10.0, 1.0)  # 최대 10회 사용시 1.0점
            score += frequency_score * 0.4
            
            # 최근 사용 점수 (30%)
            recent_usage = self._get_recent_usage_score(module_name, user_id)
            score += recent_usage * 0.3
            
            # 시간대 적합성 점수 (20%)
            time_score = self._get_time_suitability_score(module_name, user_id)
            score += time_score * 0.2
            
            # 성능 영향도 점수 (10%)
            performance_score = profile.performance_preferences.get('performance_impact', 0)
            score += performance_score * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"예측 점수 계산 실패: {e}")
            return 0.0
    
    def _get_recent_usage_score(self, module_name: str, user_id: str) -> float:
        """최근 사용 점수 계산"""
        try:
            recent_behaviors = [
                b for b in self.user_behaviors 
                if b.user_id == user_id and b.module_name == module_name
            ]
            
            if not recent_behaviors:
                return 0.0
            
            # 최근 사용 시간 계산
            latest_usage = max(b.timestamp for b in recent_behaviors)
            hours_since_usage = (datetime.now() - latest_usage).total_seconds() / 3600
            
            # 24시간 이내 사용시 높은 점수
            if hours_since_usage <= 24:
                return 1.0
            elif hours_since_usage <= 72:
                return 0.7
            elif hours_since_usage <= 168:  # 1주일
                return 0.4
            else:
                return 0.1
                
        except Exception as e:
            logger.error(f"최근 사용 점수 계산 실패: {e}")
            return 0.0
    
    def _get_time_suitability_score(self, module_name: str, user_id: str) -> float:
        """시간대 적합성 점수 계산"""
        try:
            current_hour = datetime.now().hour
            
            # 모듈별 최적 사용 시간대 정의
            optimal_times = {
                'core': (9, 17),      # 업무 시간
                'performance': (10, 16), # 성능 모니터링 시간
                'backup': (2, 6),      # 새벽 시간
                'auto': (0, 24),       # 언제든지
                'analytics': (14, 18),  # 오후 분석 시간
                'validation': (9, 18)   # 업무 시간
            }
            
            if module_name not in optimal_times:
                return 0.5
            
            start_hour, end_hour = optimal_times[module_name]
            
            # 현재 시간이 최적 시간대에 포함되는지 확인
            if start_hour <= current_hour <= end_hour:
                return 1.0
            elif start_hour > end_hour:  # 자정을 넘는 경우
                if current_hour >= start_hour or current_hour <= end_hour:
                    return 1.0
                else:
                    return 0.3
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"시간대 적합성 점수 계산 실패: {e}")
            return 0.5
    
    def get_adaptive_optimization_suggestions(self, user_id: str) -> List[Dict[str, Any]]:
        """적응형 성능 최적화 제안"""
        try:
            if user_id not in self.user_profiles:
                return []
            
            profile = self.user_profiles[user_id]
            suggestions = []
            
            # 성능 기반 최적화 제안
            if profile.performance_preferences.get('performance_impact', 0) > 0.7:
                suggestions.append({
                    'type': 'performance_optimization',
                    'title': '고성능 모드 활성화',
                    'description': '높은 성능을 요구하는 작업을 위해 최적화 설정을 권장합니다',
                    'priority': 'high',
                    'estimated_benefit': '성능 20-30% 향상',
                    'implementation': [
                        '성능 모니터링 강화',
                        '리소스 사용량 최적화',
                        '병목 지점 분석 및 개선'
                    ]
                })
            
            # 메모리 사용량 기반 제안
            total_usage = sum(profile.usage_patterns.values())
            if total_usage > 100:
                suggestions.append({
                    'type': 'memory_optimization',
                    'title': '메모리 사용량 최적화',
                    'description': '높은 메모리 사용량을 보이는 모듈들의 최적화를 권장합니다',
                    'priority': 'medium',
                    'estimated_benefit': '메모리 사용량 15-25% 감소',
                    'implementation': [
                        '사용하지 않는 모듈 언로드',
                        '메모리 캐싱 전략 최적화',
                        '가비지 컬렉션 주기 조정'
                    ]
                })
            
            # 워크플로우 최적화 제안
            if profile.workload_type == 'heavy':
                suggestions.append({
                    'type': 'workflow_optimization',
                    'title': '워크플로우 자동화',
                    'description': '높은 워크로드를 효율적으로 관리하기 위해 자동화를 권장합니다',
                    'priority': 'high',
                    'estimated_benefit': '작업 효율성 30-40% 향상',
                    'implementation': [
                        '자동화 모듈 활성화',
                        '반복 작업 자동화 설정',
                        '자동화 규칙 및 예외 처리 구성'
                    ]
                })
            
            # 학습 기반 개인화 제안
            if profile.skill_level == 'advanced':
                suggestions.append({
                    'type': 'personalization',
                    'title': '고급 개인화 설정',
                    'description': '고급 사용자를 위한 맞춤형 설정을 권장합니다',
                    'priority': 'medium',
                    'estimated_benefit': '사용자 경험 25-35% 향상',
                    'implementation': [
                        '고급 분석 모듈 활용',
                        '커스텀 워크플로우 구성',
                        '고급 성능 튜닝 설정'
                    ]
                })
            
            logger.info(f"🔧 적응형 최적화 제안 생성 완료: {user_id} - {len(suggestions)}개")
            return suggestions
            
        except Exception as e:
            logger.error(f"적응형 최적화 제안 생성 실패: {e}")
            return []
    
    def export_learning_data(self, format_type: str = 'json') -> str:
        """학습 데이터 내보내기"""
        try:
            if format_type == 'json':
                export_data = {
                    'export_time': datetime.now().isoformat(),
                    'user_behaviors': [behavior.to_dict() for behavior in self.user_behaviors],
                    'user_profiles': {user_id: profile.to_dict() for user_id, profile in self.user_profiles.items()},
                    'personalized_recommendations': [rec.to_dict() for rec in self.personalized_recommendations],
                    'learning_models': {model_id: model.to_dict() for model_id, model in self.learning_models.items()},
                    'stats': self.stats
                }
                
                filename = f"learning_recommender_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"📤 학습 데이터 내보내기 완료: {filename}")
                return filename
            
            elif format_type == 'pickle':
                export_data = {
                    'user_behaviors': self.user_behaviors,
                    'user_profiles': self.user_profiles,
                    'personalized_recommendations': self.personalized_recommendations,
                    'learning_models': self.learning_models,
                    'stats': self.stats,
                    'clustering_model': self.clustering_model,
                    'scaler': self.scaler
                }
                
                filename = f"learning_recommender_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
                with open(filename, 'wb') as f:
                    pickle.dump(export_data, f)
                
                logger.info(f"📤 학습 데이터 내보내기 완료: {filename}")
                return filename
            
            else:
                raise ValueError(f"지원하지 않는 형식: {format_type}")
                
        except Exception as e:
            logger.error(f"학습 데이터 내보내기 실패: {e}")
            return ""

# 기존 호환성을 위한 별칭
LearningRecommender = LearningBasedRecommender
