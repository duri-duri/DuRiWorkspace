"""
ML 통합 모듈 통합 인터페이스 (개선된 선택적 로딩 버전)
기능별로 분리된 모듈들을 필요할 때만 로드하여 메모리 효율성을 높입니다.

🚀 빠른 시작:
    # 가벼운 사용 (핵심 기능만)
    manager = create_manager("lightweight")
    
    # 표준 사용 (권장)
    manager = create_manager("standard")
    
    # 전체 기능
    manager = create_manager("full")
    
    # 사용자 정의 설정
    manager = create_custom_manager(["core", "performance", "backup"])

📚 주요 기능:
    • 지연 로딩: 필요할 때만 모듈 로드
    • 선택적 로딩: 원하는 기능만 선택
    • 메모리 효율성: 초기 0KB → 필요시에만 증가
    • 자동 통합: 백그라운드에서 자동 처리
    • 성능 모니터링: 실시간 성능 추적
    • 백업 관리: 자동 백업 및 복구
    • 고급 분석: AI 기반 인사이트 제공
"""

from typing import Dict, Any, List, Optional, Union
import logging
import importlib
import sys

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LazyModuleLoader:
    """
    지연 로딩을 위한 모듈 로더
    실제 사용할 때만 모듈을 import합니다.
    """
    
    def __init__(self, module_name: str, class_name: str):
        self.module_name = module_name
        self.class_name = class_name
        self._module = None
        self._class = None
        self._loaded = False
    
    def _load_module(self):
        """모듈을 실제로 로드"""
        if not self._loaded:
            try:
                # 동적 import - 현재 디렉토리에서 직접 import
                module = importlib.import_module(self.module_name)
                self._class = getattr(module, self.class_name)
                self._loaded = True
                logger.info(f"모듈 로드 완료: {self.module_name}.{self.class_name}")
            except ImportError as e:
                logger.error(f"모듈 로드 실패: {self.module_name}.{self.class_name} - {e}")
                raise
    
    def get_instance(self, *args, **kwargs):
        """모듈 인스턴스 반환 (지연 로딩)"""
        self._load_module()
        return self._class(*args, **kwargs)
    
    def is_loaded(self) -> bool:
        """모듈이 로드되었는지 확인"""
        return self._loaded

class IntegrationManager:
    """
    통합 관리자 - 지연 로딩으로 필요한 모듈만 로드
    
    이 클래스는 기능별로 분리된 모듈들을 필요할 때만 로드하여
    메모리 효율성을 높이는 통합 인터페이스를 제공합니다.
    
    🎯 권장 사용법:
        # 간단한 사용 (권장)
        manager = create_manager("standard")
        
        # 직접 설정
        manager = IntegrationManager(modules=['core', 'performance'])
        
        # 모든 기능
        manager = IntegrationManager(modules=['core', 'performance', 'backup', 'auto', 'analytics'])
    
    💡 팁: create_manager() 함수를 사용하면 더 간단하게 설정할 수 있습니다.
    """
    
    def __init__(self, modules: Optional[List[str]] = None, config: Optional[Dict[str, Any]] = None):
        """
        통합 관리자 초기화
        
        Args:
            modules: 사용할 모듈 목록. None이면 모든 모듈 사용
            config: 모듈별 설정 정보
        """
        self.config = config or {}
        self.modules = modules or ['core', 'performance', 'backup', 'auto', 'analytics', 'validation']
        
        # 모듈 로더 초기화 (실제 로딩은 하지 않음)
        self._module_loaders = {}
        self._module_instances = {}
        self.active_modules = []
        
        # 모듈 로더 설정
        self._setup_module_loaders()
        
        # 지능형 모듈 선택 시스템 초기화
        self.intelligent_selector = None
        if config and config.get('enable_intelligent_selection', True):
            try:
                from intelligent_module_selector import IntelligentModuleSelector
                self.intelligent_selector = IntelligentModuleSelector(config.get('selector_config', {}))
                logger.info("🧠 지능형 모듈 선택 시스템 초기화 완료")
            except ImportError as e:
                logger.warning(f"지능형 모듈 선택 시스템 초기화 실패: {e}")
        
        # 학습 기반 추천 시스템 초기화
        self.learning_recommender = None
        if config and config.get('enable_learning_recommendations', True):
            try:
                from learning_based_recommender import LearningBasedRecommender
                self.learning_recommender = LearningBasedRecommender(config.get('learning_config', {}))
                logger.info("🎓 학습 기반 추천 시스템 초기화 완료")
            except ImportError as e:
                logger.warning(f"학습 기반 추천 시스템 초기화 실패: {e}")
        
        logger.info(f"IntegrationManager 초기화 완료. 설정된 모듈: {self.modules}")
    
    def _setup_module_loaders(self):
        """모듈 로더 설정 (실제 로딩은 하지 않음)"""
        module_configs = {
            'core': ('core_integration', 'CoreIntegrationManager'),
            'performance': ('performance_monitor', 'PerformanceMonitor'),
            'backup': ('backup_manager', 'BackupManager'),
            'auto': ('auto_integration', 'AutoIntegrationManager'),
            'analytics': ('advanced_analytics', 'AdvancedAnalyticsEngine'),
            'validation': ('validation_system', 'ValidationSystem')
        }
        
        for module_name in self.modules:
            if module_name in module_configs:
                file_name, class_name = module_configs[module_name]
                self._module_loaders[module_name] = LazyModuleLoader(file_name, class_name)
                self.active_modules.append(module_name)
                logger.info(f"모듈 로더 설정 완료: {module_name}")
    
    def _get_module_instance(self, module_name: str):
        """모듈 인스턴스 반환 (지연 로딩)"""
        if module_name not in self._module_loaders:
            raise ValueError(f"알 수 없는 모듈: {module_name}")
        
        if module_name not in self._module_instances:
            # 실제 사용할 때만 모듈 로드
            config = self.config.get(module_name, {})
            self._module_instances[module_name] = self._module_loaders[module_name].get_instance(**config)
            logger.info(f"모듈 인스턴스 생성 완료: {module_name}")
            
            # 지능형 모듈 선택 시스템에 모듈 접근 기록
            if self.intelligent_selector:
                try:
                    self.intelligent_selector.record_module_access(module_name, 'load')
                    self.intelligent_selector.start_session_tracking(module_name)
                except Exception as e:
                    logger.debug(f"지능형 선택기 기록 실패: {e}")
        
        # 지능형 모듈 선택 시스템에 모듈 접근 기록
        if self.intelligent_selector:
            try:
                self.intelligent_selector.record_module_access(module_name, 'access')
            except Exception as e:
                logger.debug(f"지능형 선택기 기록 실패: {e}")
        
        return self._module_instances[module_name]
    
    @property
    def core(self):
        """핵심 통합 모듈 (지연 로딩)"""
        if 'core' in self.modules:
            return self._get_module_instance('core')
        return None
    
    @property
    def performance_monitor(self):
        """성능 모니터링 모듈 (지연 로딩)"""
        if 'performance' in self.modules:
            return self._get_module_instance('performance')
        return None
    
    @property
    def backup_manager(self):
        """백업 관리 모듈 (지연 로딩)"""
        if 'backup' in self.modules:
            return self._get_module_instance('backup')
        return None
    
    @property
    def auto_integration(self):
        """자동 통합 모듈 (지연 로딩)"""
        if 'auto' in self.modules:
            return self._get_module_instance('auto')
        return None
    
    @property
    def analytics_engine(self):
        """고급 분석 모듈 (지연 로딩)"""
        if 'analytics' in self.modules:
            return self._get_module_instance('analytics')
        return None
    
    @property
    def validation_system(self):
        """검증 시스템 모듈 (지연 로딩)"""
        if 'validation' in self.modules:
            return self._get_module_instance('validation')
        return None
    
    def get_module_status(self) -> Dict[str, Any]:
        """모듈 상태 정보 반환"""
        status = {
            "configured_modules": self.modules,
            "active_modules": self.active_modules,
            "loaded_modules": list(self._module_instances.keys()),
            "module_details": {}
        }
        
        # 각 모듈의 상태 정보
        for module_name in self.modules:
            is_loaded = module_name in self._module_instances
            loader = self._module_loaders.get(module_name)
            
            status["module_details"][module_name] = {
                "status": "loaded" if is_loaded else "configured",
                "loaded": is_loaded,
                "loader_ready": loader is not None
            }
        
        return status
    
    def perform_integration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """통합 수행"""
        try:
            if not self.core:
                raise RuntimeError(
                    "핵심 통합 모듈이 필요합니다. "
                    "다음 중 하나를 사용하여 'core' 모듈을 포함한 관리자를 생성해주세요:\n"
                    "• create_manager('lightweight') - 가벼운 사용\n"
                    "• create_manager('standard') - 표준 사용 (권장)\n"
                    "• create_manager('full') - 전체 기능"
                )
            
            logger.info("통합 수행 시작")
            
            # 핵심 통합 실행
            integration_result = self.core.perform_integration()
            
            # 성능 모니터링 (활성화된 경우)
            if self.performance_monitor:
                performance_data = self.performance_monitor.monitor_integration_performance()
                integration_result['performance_monitoring'] = performance_data
            
            # 백업 생성 (활성화된 경우)
            if self.backup_manager:
                backup_info = self.backup_manager.create_backup(
                    data=integration_result,
                    description="통합 결과 백업",
                    backup_type="integration_result"
                )
                if backup_info:
                    # backup_info가 딕셔너리인지 객체인지 확인
                    if isinstance(backup_info, dict):
                        backup_id = backup_info.get('backup_id', 'unknown')
                        timestamp = backup_info.get('timestamp', 'unknown')
                    else:
                        # 객체인 경우 속성으로 접근
                        backup_id = getattr(backup_info, 'backup_id', 'unknown')
                        timestamp = getattr(backup_info, 'timestamp', 'unknown')
                    
                    integration_result['backup_info'] = {
                        'backup_id': backup_id,
                        'timestamp': timestamp
                    }
            
            # 고급 분석 (활성화된 경우)
            if self.analytics_engine:
                try:
                    # run_comprehensive_analysis 메서드가 있는지 확인
                    if hasattr(self.analytics_engine, 'run_comprehensive_analysis'):
                        analysis_results = self.analytics_engine.run_comprehensive_analysis(integration_result)
                    else:
                        # 대체 메서드 사용
                        analysis_results = self.analytics_engine.run_analysis('comprehensive', integration_result)
                    
                    integration_result['analytics'] = analysis_results
                except Exception as e:
                    logger.warning(f"고급 분석 실행 실패: {e}")
                    integration_result['analytics'] = {'error': str(e)}
            
            logger.info("통합 수행 완료")
            return integration_result
        
        except Exception as e:
            logger.error(f"통합 수행 실패: {str(e)}")
            raise
    
    def start_auto_integration(self) -> bool:
        """자동 통합 시작"""
        try:
            if not self.auto_integration:
                logger.warning(
                    "자동 통합 모듈이 설정되지 않았습니다. "
                    "다음 중 하나를 사용하여 'auto' 모듈을 포함한 관리자를 생성해주세요:\n"
                    "• create_manager('full') - 전체 기능 (권장)\n"
                    "• create_custom_manager(['core', 'auto']) - 사용자 정의 설정"
                )
                return False
            
            self.auto_integration.start_auto_integration()
            logger.info("자동 통합이 시작되었습니다")
            return True
        
        except Exception as e:
            logger.error(f"자동 통합 시작 실패: {str(e)}")
            return False
    
    def stop_auto_integration(self) -> bool:
        """자동 통합 중지"""
        try:
            if not self.auto_integration:
                logger.warning(
                    "자동 통합 모듈이 설정되지 않았습니다. "
                    "다음 중 하나를 사용하여 'auto' 모듈을 포함한 관리자를 생성해주세요:\n"
                    "• create_manager('full') - 전체 기능 (권장)\n"
                    "• create_custom_manager(['core', 'auto']) - 사용자 정의 설정"
                )
                return False
            
            self.auto_integration.stop_auto_integration()
            logger.info("자동 통합이 중지되었습니다")
            return True
        
        except Exception as e:
            logger.error(f"자동 통합 중지 실패: {str(e)}")
            return False
    
    def get_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """성능 메트릭 반환"""
        try:
            if not self.performance_monitor:
                logger.warning(
                    "성능 모니터링 모듈이 설정되지 않았습니다. "
                    "다음 중 하나를 사용하여 'performance' 모듈을 포함한 관리자를 생성해주세요:\n"
                    "• create_manager('standard') - 표준 기능 (권장)\n"
                    "• create_manager('full') - 전체 기능"
                )
                return None
            
            return self.performance_monitor.get_performance_summary()
        
        except Exception as e:
            logger.error(f"성능 메트릭 조회 실패: {str(e)}")
            return None
    
    def get_performance_dashboard(self) -> Optional[Dict[str, Any]]:
        """성능 대시보드 반환"""
        try:
            if not self.performance_monitor:
                logger.warning(
                    "성능 모니터링 모듈이 설정되지 않았습니다. "
                    "다음 중 하나를 사용하여 'performance' 모듈을 포함한 관리자를 생성해주세요:\n"
                    "• create_manager('standard') - 표준 기능 (권장)\n"
                    "• create_manager('full') - 전체 기능"
                )
                return None
            
            return self.performance_monitor.get_performance_dashboard()
        
        except Exception as e:
            logger.error(f"성능 대시보드 조회 실패: {str(e)}")
            return None
    
    def start_performance_monitoring(self, background: bool = True) -> bool:
        """성능 모니터링 시작"""
        try:
            if not self.performance_monitor:
                logger.warning(
                    "성능 모니터링 모듈이 설정되지 않았습니다. "
                    "다음 중 하나를 사용하여 'performance' 모듈을 포함한 관리자를 생성해주세요:\n"
                    "• create_manager('standard') - 표준 기능 (권장)\n"
                    "• create_manager('full') - 전체 기능"
                )
                return False
            
            return self.performance_monitor.start_monitoring(background=background)
        
        except Exception as e:
            logger.error(f"성능 모니터링 시작 실패: {str(e)}")
            return False
    
    def stop_performance_monitoring(self) -> bool:
        """성능 모니터링 중지"""
        try:
            if not self.performance_monitor:
                logger.warning(
                    "성능 모니터링 모듈이 설정되지 않았습니다. "
                    "다음 중 하나를 사용하여 'performance' 모듈을 포함한 관리자를 생성해주세요:\n"
                    "• create_manager('standard') - 표준 기능 (권장)\n"
                    "• create_manager('full') - 전체 기능"
                )
                return False
            
            return self.performance_monitor.stop_monitoring()
        
        except Exception as e:
            logger.error(f"성능 모니터링 중지 실패: {str(e)}")
            return False
    
    # 지능형 모듈 선택 시스템 메서드들
    def get_intelligent_recommendations(self, target_performance: float = 0.8, max_memory_mb: float = 50.0) -> Optional[List[Dict[str, Any]]]:
        """지능형 모듈 권장사항 조회"""
        try:
            if not self.intelligent_selector:
                logger.warning(
                    "지능형 모듈 선택 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_intelligent_selection': True}를 설정해주세요."
                )
                return None
            
            # 현재 로드된 모듈 목록
            current_modules = list(self._module_instances.keys())
            
            # 권장사항 생성
            recommendations = self.intelligent_selector.generate_module_recommendations(
                current_modules, target_performance, max_memory_mb
            )
            
            # 딕셔너리로 변환
            return [rec.to_dict() for rec in recommendations]
        
        except Exception as e:
            logger.error(f"지능형 모듈 권장사항 조회 실패: {str(e)}")
            return None
    
    def create_optimal_combination(self, requirements: Dict[str, Any], constraints: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """최적 모듈 조합 생성"""
        try:
            if not self.intelligent_selector:
                logger.warning(
                    "지능형 모듈 선택 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_intelligent_selection': True}를 설정해주세요."
                )
                return None
            
            combination = self.intelligent_selector.create_optimal_module_combination(requirements, constraints)
            
            if combination:
                return combination.to_dict()
            return None
        
        except Exception as e:
            logger.error(f"최적 모듈 조합 생성 실패: {str(e)}")
            return None
    
    def analyze_usage_patterns(self) -> Optional[Dict[str, Any]]:
        """사용 패턴 분석"""
        try:
            if not self.intelligent_selector:
                logger.warning(
                    "지능형 모듈 선택 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_intelligent_selection': True}를 설정해주세요."
                )
                return None
            
            return self.intelligent_selector.analyze_usage_patterns()
        
        except Exception as e:
            logger.error(f"사용 패턴 분석 실패: {str(e)}")
            return None
    
    def start_intelligent_optimization(self, interval_seconds: int = 300) -> bool:
        """지능형 최적화 시작"""
        try:
            if not self.intelligent_selector:
                logger.warning(
                    "지능형 모듈 선택 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_intelligent_selection': True}를 설정해주세요."
                )
                return False
            
            return self.intelligent_selector.start_auto_optimization(interval_seconds)
        
        except Exception as e:
            logger.error(f"지능형 최적화 시작 실패: {str(e)}")
            return False
    
    def stop_intelligent_optimization(self) -> bool:
        """지능형 최적화 중지"""
        try:
            if not self.intelligent_selector:
                logger.warning(
                    "지능형 모듈 선택 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_intelligent_selection': True}를 설정해주세요."
                )
                return False
            
            return self.intelligent_selector.stop_auto_optimization()
        
        except Exception as e:
            logger.error(f"지능형 최적화 중지 실패: {str(e)}")
            return False
    
    def get_intelligent_summary(self) -> Optional[Dict[str, Any]]:
        """지능형 선택기 요약 정보"""
        try:
            if not self.intelligent_selector:
                logger.warning(
                    "지능형 모듈 선택 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_intelligent_selection': True}를 설정해주세요."
                )
                return None
            
            return self.intelligent_selector.get_selector_summary()
        
        except Exception as e:
            logger.error(f"지능형 선택기 요약 조회 실패: {str(e)}")
            return None
    
    # 학습 기반 추천 시스템 메서드들
    def record_user_behavior(self, 
                           user_id: str,
                           behavior_type: str,
                           module_name: str,
                           action: str,
                           parameters: Dict[str, Any] = None,
                           session_duration: float = 0.0,
                           success: bool = True,
                           performance_impact: float = 0.0):
        """사용자 행동 기록"""
        try:
            if not self.learning_recommender:
                logger.warning(
                    "학습 기반 추천 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_learning_recommendations': True}를 설정해주세요."
                )
                return False
            
            from learning_based_recommender import UserBehaviorType
            
            # 문자열을 UserBehaviorType으로 변환
            behavior_enum = None
            for behavior in UserBehaviorType:
                if behavior.value == behavior_type:
                    behavior_enum = behavior
                    break
            
            if behavior_enum is None:
                logger.warning(f"알 수 없는 행동 유형: {behavior_type}")
                return False
            
            self.learning_recommender.record_user_behavior(
                user_id=user_id,
                behavior_type=behavior_enum,
                module_name=module_name,
                action=action,
                parameters=parameters,
                session_duration=session_duration,
                success=success,
                performance_impact=performance_impact
            )
            
            return True
        
        except Exception as e:
            logger.error(f"사용자 행동 기록 실패: {str(e)}")
            return False
    
    def analyze_user_patterns(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 패턴 분석"""
        try:
            if not self.learning_recommender:
                logger.warning(
                    "학습 기반 추천 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_learning_recommendations': True}를 설정해주세요."
                )
                return None
            
            return self.learning_recommender.analyze_user_patterns(user_id)
        
        except Exception as e:
            logger.error(f"사용자 패턴 분석 실패: {str(e)}")
            return None
    
    def get_personalized_recommendations(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """개인화된 추천 조회"""
        try:
            if not self.learning_recommender:
                logger.warning(
                    "학습 기반 추천 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_learning_recommendations': True}를 설정해주세요."
                )
                return None
            
            recommendations = self.learning_recommender.generate_personalized_recommendations(user_id)
            return [rec.to_dict() for rec in recommendations]
        
        except Exception as e:
            logger.error(f"개인화된 추천 조회 실패: {str(e)}")
            return None
    
    def start_learning_recommendations(self, interval_seconds: int = 3600) -> bool:
        """학습 기반 추천 시작"""
        try:
            if not self.learning_recommender:
                logger.warning(
                    "학습 기반 추천 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_learning_recommendations': True}를 설정해주세요."
                )
                return False
            
            return self.learning_recommender.start_learning(interval_seconds)
        
        except Exception as e:
            logger.error(f"학습 기반 추천 시작 실패: {str(e)}")
            return False
    
    def stop_learning_recommendations(self) -> bool:
        """학습 기반 추천 중지"""
        try:
            if not self.learning_recommender:
                logger.warning(
                    "학습 기반 추천 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_learning_recommendations': True}를 설정해주세요."
                )
                return False
            
            return self.learning_recommender.stop_learning()
        
        except Exception as e:
            logger.error(f"학습 기반 추천 중지 실패: {str(e)}")
            return False
    
    def get_learning_summary(self) -> Optional[Dict[str, Any]]:
        """학습 기반 추천 시스템 요약 정보"""
        try:
            if not self.learning_recommender:
                logger.warning(
                    "학습 기반 추천 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_learning_recommendations': True}를 설정해주세요."
                )
                return None
            
            return self.learning_recommender.get_recommender_summary()
        
        except Exception as e:
            logger.error(f"학습 기반 추천 시스템 요약 조회 실패: {str(e)}")
            return None
    
    def predict_next_modules(self, user_id: str, time_window_hours: int = 24) -> Optional[List[str]]:
        """사용자의 다음 사용할 모듈 예측"""
        try:
            if not self.learning_recommender:
                logger.warning(
                    "학습 기반 추천 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_learning_recommendations': True}를 설정해주세요."
                )
                return None
            
            return self.learning_recommender.predict_next_modules(user_id, time_window_hours)
        
        except Exception as e:
            logger.error(f"모듈 예측 실패: {str(e)}")
            return None
    
    def get_adaptive_optimization_suggestions(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """적응형 성능 최적화 제안 조회"""
        try:
            if not self.learning_recommender:
                logger.warning(
                    "학습 기반 추천 시스템이 활성화되지 않았습니다. "
                    "create_manager() 호출 시 config={'enable_learning_recommendations': True}를 설정해주세요."
                )
                return None
            
            return self.learning_recommender.get_adaptive_optimization_suggestions(user_id)
        
        except Exception as e:
            logger.error(f"적응형 최적화 제안 조회 실패: {str(e)}")
            return None
    
    def create_backup(self, data: Any, description: str = "", backup_type: str = "data") -> Optional[Dict[str, Any]]:
        """백업 생성"""
        try:
            if not self.backup_manager:
                logger.warning(
                    "백업 관리 모듈이 설정되지 않았습니다. "
                    "다음 중 하나를 사용하여 'backup' 모듈을 포함한 관리자를 생성해주세요:\n"
                    "• create_manager('full') - 전체 기능 (권장)\n"
                    "• create_custom_manager(['core', 'backup']) - 사용자 정의 설정"
                )
                return None
            
            backup_info = self.backup_manager.create_backup(
                data=data,
                description=description,
                backup_type=backup_type
            )
            
            if backup_info:
                return {
                    'backup_id': backup_info.backup_id,
                    'timestamp': backup_info.timestamp,
                    'description': backup_info.description,
                    'size_bytes': backup_info.size_bytes,
                    'checksum': backup_info.checksum
                }
            
            return None
        
        except Exception as e:
            logger.error(f"백업 생성 실패: {str(e)}")
            return None
    
    def run_analysis(self, analysis_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """분석 실행"""
        try:
            if not self.analytics_engine:
                logger.warning(
                    "고급 분석 모듈이 설정되지 않았습니다. "
                    "다음 중 하나를 사용하여 'analytics' 모듈을 포함한 관리자를 생성해주세요:\n"
                    "• create_manager('full') - 전체 기능 (권장)\n"
                    "• create_custom_manager(['core', 'analytics']) - 사용자 정의 설정"
                )
                return None
            
            result = self.analytics_engine.run_analysis(analysis_type, data)
            
            if result:
                return {
                    'analysis_id': result.analysis_id,
                    'analysis_type': result.analysis_type,
                    'timestamp': result.timestamp.isoformat(),
                    'confidence_score': result.confidence_score,
                    'summary': result.summary,
                    'recommendations': result.recommendations
                }
            
            return None
        
        except Exception as e:
            logger.error(f"분석 실행 실패: {str(e)}")
            return None
    
    def get_system_health(self) -> Dict[str, Any]:
        """시스템 상태 정보 반환"""
        health_info = {
            "status": "healthy",
            "configured_modules": len(self.modules),
            "loaded_modules": len(self._module_instances),
            "module_status": {}
        }
        
        try:
            # 각 모듈의 상태 확인
            for module_name in self.modules:
                is_loaded = module_name in self._module_instances
                health_info["module_status"][module_name] = {
                    "status": "loaded" if is_loaded else "configured",
                    "loaded": is_loaded
                }
            
            # 전체 상태 결정
            if len(self._module_instances) == 0:
                health_info["status"] = "configured"
            elif len(self._module_instances) < len(self.modules):
                health_info["status"] = "partially_loaded"
            else:
                health_info["status"] = "fully_loaded"
            
            return health_info
        
        except Exception as e:
            logger.error(f"시스템 상태 확인 실패: {str(e)}")
            health_info["status"] = "error"
            health_info["error"] = str(e)
            return health_info
    
    def preload_module(self, module_name: str) -> bool:
        """특정 모듈을 미리 로드"""
        try:
            if module_name in self.modules and module_name not in self._module_instances:
                self._get_module_instance(module_name)
                logger.info(f"모듈 미리 로드 완료: {module_name}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"모듈 미리 로드 실패: {module_name} - {str(e)}")
            return False
    
    def unload_module(self, module_name: str) -> bool:
        """특정 모듈을 메모리에서 제거"""
        try:
            if module_name in self._module_instances:
                del self._module_instances[module_name]
                logger.info(f"모듈 메모리 제거 완료: {module_name}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"모듈 메모리 제거 실패: {module_name} - {str(e)}")
            return False
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """메모리 사용량 정보 반환"""
        import sys
        
        memory_info = {
            "loaded_modules": len(self._module_instances),
            "configured_modules": len(self.modules),
            "memory_efficiency": f"{(len(self._module_instances) / len(self.modules)) * 100:.1f}%"
        }
        
        # 실제 메모리 사용량 (대략적)
        try:
            memory_info["estimated_memory_mb"] = len(self._module_instances) * 2  # 모듈당 약 2MB 추정
        except:
            memory_info["estimated_memory_mb"] = "unknown"
        
        return memory_info

# 편의 함수들 (지연 로딩 지원)
def create_manager(manager_type: str = "standard", config: Optional[Dict[str, Any]] = None) -> IntegrationManager:
    """
    통합 관리자 생성 (가장 간단한 방법!)
    
    🎯 관리자 유형:
        • "lightweight": 핵심 기능만 (가장 가벼움, 메모리 절약)
        • "standard": 핵심 + 성능 모니터링 (권장, 균형잡힌 기능)
        • "full": 모든 기능 (전체 기능 필요시, 최대 성능)
        • "intelligent": 지능형 선택 + 표준 기능 (AI 기반 최적화)
    
    📝 매개변수:
        manager_type: 관리자 유형 (기본값: "standard")
        config: 모듈별 설정 정보 (선택사항)
    
    🔄 반환값:
        IntegrationManager: 설정된 통합 관리자
    
    🚀 사용 예시:
        # 가벼운 사용 (메모리 절약)
        manager = create_manager("lightweight")
        
        # 표준 사용 (권장)
        manager = create_manager("standard")
        
        # 전체 기능 (최대 성능)
        manager = create_manager("full")
        
        # 지능형 선택 (AI 기반 최적화)
        manager = create_manager("intelligent")
        
        # 사용자 정의 설정
        manager = create_manager("custom", {"performance": {"interval": 5}})
        
        # 지능형 선택 + 사용자 정의
        manager = create_manager("intelligent", {
            "selector_config": {"memory_threshold": 100.0}
        })
    """
    manager_configs = {
        "lightweight": ['core'],
        "standard": ['core', 'performance'],
        "full": ['core', 'performance', 'backup', 'auto', 'analytics', 'validation'],
        "intelligent": ['core', 'performance']  # 지능형 선택은 표준 모듈 + AI 최적화
    }
    
    if manager_type not in manager_configs:
        available_types = list(manager_configs.keys())
        raise ValueError(
            f"알 수 없는 관리자 유형: '{manager_type}'. "
            f"사용 가능한 유형: {available_types}\n"
            f"사용 예시:\n"
            f"• create_manager('lightweight') - 가벼운 사용\n"
            f"• create_manager('standard') - 표준 사용 (권장)\n"
            f"• create_manager('full') - 전체 기능"
        )
    
    modules = manager_configs[manager_type]
    
    # 지능형 선택이 활성화된 경우 설정 추가
    if manager_type == "intelligent":
            if config is None:
                config = {}
            config['enable_intelligent_selection'] = True
            config['enable_learning_recommendations'] = True
            if 'selector_config' not in config:
                config['selector_config'] = {
                    'learning_enabled': True,
                    'auto_optimization': True,
                    'memory_threshold': 80.0
                }
            if 'learning_config' not in config:
                config['learning_config'] = {
                    'learning_enabled': True,
                    'auto_training': True,
                    'min_training_samples': 50,
                    'training_interval': 1800  # 30분
                }
    
    return IntegrationManager(modules=modules, config=config)

# 기존 함수들과의 호환성을 위한 별칭
def create_lightweight_manager() -> IntegrationManager:
    """가벼운 통합 관리자 생성 (핵심 기능만) - 호환성 유지"""
    return create_manager("lightweight")

def create_standard_manager() -> IntegrationManager:
    """표준 통합 관리자 생성 (핵심 + 성능 모니터링) - 호환성 유지"""
    return create_manager("standard")

def create_full_featured_manager() -> IntegrationManager:
    """전체 기능 통합 관리자 생성 (모든 모듈) - 호환성 유지"""
    return create_manager("full")

def create_custom_manager(modules: List[str], config: Optional[Dict[str, Any]] = None) -> IntegrationManager:
    """
    사용자 정의 통합 관리자 생성
    
    🎯 사용 시기:
        • 특정 모듈만 필요한 경우
        • 기본 제공 유형으로는 부족한 경우
        • 세밀한 제어가 필요한 경우
    
    📝 매개변수:
        modules: 사용할 모듈 목록 (예: ['core', 'performance', 'backup'])
        config: 모듈별 설정 정보 (선택사항)
    
    🚀 사용 예시:
        # 핵심 + 성능 모니터링만
        manager = create_custom_manager(['core', 'performance'])
        
        # 핵심 + 백업 + 분석
        manager = create_custom_manager(['core', 'backup', 'analytics'])
        
        # 설정과 함께
        manager = create_custom_manager(
            ['core', 'performance'], 
            {'performance': {'interval': 10}}
        )
    """
    return IntegrationManager(modules=modules, config=config)

# 버전 정보
__version__ = "2.0.0"
__author__ = "DuRi Core Team"
__description__ = "ML 통합 모듈 통합 인터페이스 (지연 로딩 지원)"

# 사용 예시
if __name__ == "__main__":
    print("🚀 === ML 통합 모듈 통합 인터페이스 (지연 로딩 지원) ===")
    print(f"📋 버전: {__version__}")
    print(f"📖 설명: {__description__}")
    
    print("\n" + "="*60)
    print("🎯 1단계: 가벼운 통합 관리자 생성 (메모리 절약)")
    print("="*60)
    light_manager = create_manager("lightweight")
    print(f"✅ 설정된 모듈: {light_manager.modules}")
    print(f"💾 로드된 모듈: {list(light_manager._module_instances.keys())}")
    print(f"💡 메모리 효율성: 초기 0KB (모듈 접근시에만 로드)")
    
    print("\n" + "="*60)
    print("🎯 2단계: 표준 통합 관리자 생성 (권장)")
    print("="*60)
    standard_manager = create_manager("standard")
    print(f"✅ 설정된 모듈: {standard_manager.modules}")
    print(f"💾 로드된 모듈: {list(standard_manager._module_instances.keys())}")
    print(f"💡 성능 모니터링 포함으로 안정적인 운영 가능")
    
    print("\n" + "="*60)
    print("🎯 3단계: 전체 기능 통합 관리자 생성 (최대 성능)")
    print("="*60)
    full_manager = create_manager("full")
    print(f"✅ 설정된 모듈: {full_manager.modules}")
    print(f"💾 로드된 모듈: {list(full_manager._module_instances.keys())}")
    print(f"💡 모든 기능 사용 가능 (자동 통합, 백업, 분석 등)")
    
    print("\n" + "="*60)
    print("🎯 4단계: 지연 로딩 테스트 (실시간 모듈 로딩)")
    print("="*60)
    print("📊 백업 모듈 접근 전:", list(full_manager._module_instances.keys()))
    
    # 백업 모듈에 접근하면 자동으로 로드됨
    backup_status = full_manager.backup_manager is not None
    print("📊 백업 모듈 접근 후:", list(full_manager._module_instances.keys()))
    print(f"✅ 백업 모듈 상태: {backup_status}")
    print(f"💡 지연 로딩 작동 확인: 필요할 때만 모듈 로드")
    
    print("\n" + "="*60)
    print("🎯 5단계: 시스템 상태 확인")
    print("="*60)
    health = full_manager.get_system_health()
    print(f"🏥 상태: {health['status']}")
    print(f"⚙️ 설정된 모듈: {health['configured_modules']}")
    print(f"💾 로드된 모듈: {health['loaded_modules']}")
    
    print("\n" + "="*60)
    print("🎯 6단계: 메모리 사용량 확인")
    print("="*60)
    memory = full_manager.get_memory_usage()
    print(f"💾 로드된 모듈: {memory['loaded_modules']}")
    print(f"📊 메모리 효율성: {memory['memory_efficiency']}")
    print(f"💡 지연 로딩으로 메모리 효율성 극대화")
    
    print("\n" + "="*60)
    print("🎉 지연 로딩 시스템 테스트 완료!")
    print("="*60)
    print("💡 주요 장점:")
    print("   • 초기 메모리 사용량: 0KB")
    print("   • 필요시에만 모듈 로드")
    print("   • 선택적 기능 사용")
    print("   • 자동 성능 최적화")
    print("="*60)
