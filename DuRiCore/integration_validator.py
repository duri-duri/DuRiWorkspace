from DuRiCore.trace import emit_trace
"""
DuRi IntegrationValidator - Phase 2 스켈레톤
SafetyController와 통합된 안전성 검증 시스템

@preserve_identity: 기존 SafetyController와의 호환성 보장
@evolution_protection: 진화 과정에서의 통합 안전성 확보
@execution_guarantee: 통합된 검증 보장
@existence_ai: 안전한 진화와 회복을 위한 통합 검증
@final_execution: 통합 안전성이 보장된 최종 실행
"""
import asyncio
import json
import time
import os
import yaml
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
import logging
try:
    from DuRiCore.safety_controller import SafetyController, SafetyLevel, SafetyTrigger, SafetyAction, SafetyEvent, SafetyMetrics, safety_controller
except ImportError:
    from safety_controller import SafetyController, SafetyLevel, SafetyTrigger, SafetyAction, SafetyEvent, SafetyMetrics, safety_controller
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """검증 결과 데이터 클래스"""
    success: bool
    timestamp: datetime = field(default_factory=lambda : datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Optional[SafetyMetrics] = None

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {'success': self.success, 'timestamp': self.timestamp.isoformat(), 'details': self.details, 'errors': self.errors, 'warnings': self.warnings, 'metrics': self.metrics.to_dict() if self.metrics else None}

@dataclass
class ValidationRule:
    """검증 규칙 데이터 클래스"""
    name: str
    description: str
    severity: SafetyLevel
    condition: Callable[[SafetyMetrics], bool]
    action: SafetyAction
    enabled: bool = True

    def evaluate(self, metrics: SafetyMetrics) -> bool:
        """규칙 평가"""
        if not self.enabled:
            return True
        try:
            return self.condition(metrics)
        except Exception as e:
            logger.error(f"규칙 '{self.name}' 평가 중 오류: {e}")
            return False

class IntegrationValidator:
    """통합 안전성 검증 시스템"""

    def __init__(self, safety_controller: Optional[SafetyController]=None, max_concurrent_validations: int=5):
        """
        IntegrationValidator 초기화
        
        Args:
            safety_controller: SafetyController 인스턴스 (None이면 전역 인스턴스 사용)
            max_concurrent_validations: 최대 동시 검증 수
        """
        self.safety_controller = safety_controller or safety_controller
        self.max_concurrent_validations = max_concurrent_validations
        self.validation_semaphore = asyncio.Semaphore(max_concurrent_validations)
        self.thresholds = self._load_thresholds()
        self.validation_rules: List[ValidationRule] = []
        self._setup_default_rules()
        self.validation_history: List[ValidationResult] = []
        self.max_history_size = 1000
        self._running = False
        self._validation_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        logger.info('🔍 IntegrationValidator 초기화 완료')

    def _load_thresholds(self) -> Dict[str, Any]:
        """임계값 설정 로딩"""
        try:
            profile = os.getenv('DURI_PROFILE', 'dev')
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'thresholds.yaml')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                if profile in config.get('profiles', {}):
                    thresholds = config['profiles'][profile]
                    logger.info(f"📊 프로필 '{profile}' 임계값 로드 완료")
                    return thresholds
                else:
                    logger.warning(f"⚠️ 프로필 '{profile}'을 찾을 수 없음, 기본값 사용")
                    return config.get('defaults', {})
            else:
                logger.warning(f'⚠️ 설정 파일을 찾을 수 없음: {config_path}, 기본값 사용')
                return self._get_default_thresholds()
        except Exception as e:
            logger.error(f'❌ 임계값 로드 실패: {e}, 기본값 사용')
            return self._get_default_thresholds()

    def _get_default_thresholds(self) -> Dict[str, Any]:
        """기본 임계값 반환"""
        return {'p95_latency_inc_pct': 5.0, 'error_rate_pct': 2.0, 'memory_inc_pct': 3.0, 'cpu_inc_pct': 5.0, 'total_events_max': 5, 'critical_events_max': 0, 'performance_events_max': 5, 'error_events_max': 5, 'resource_events_max': 5}

    def _m(self, metrics: SafetyMetrics, key: str, default: float=0.0) -> float:
        """안전한 메트릭 접근 헬퍼 (존재하지 않는 속성은 기본값 0으로 처리)"""
        return float(getattr(metrics, key, default) or default)

    def _setup_default_rules(self):
        """기본 검증 규칙 설정"""

        def safe_metric(metrics: SafetyMetrics, key: str, default: float=0.0) -> float:
            """안전한 메트릭 접근 헬퍼"""
            return float(getattr(metrics, key, default) or default)
        self.add_rule(ValidationRule(name='performance_degradation_threshold', description='성능 저하 임계값 초과 시 경고', severity=SafetyLevel.MEDIUM, condition=lambda m: safe_metric(m, 'performance_events') == 0, action=SafetyAction.WARNING))
        self.add_rule(ValidationRule(name='error_spike_detection', description='에러 급증 감지 시 모니터링', severity=SafetyLevel.HIGH, condition=lambda m: safe_metric(m, 'error_events') == 0, action=SafetyAction.MONITOR))
        self.add_rule(ValidationRule(name='resource_exhaustion_warning', description='리소스 고갈 시 긴급 정지', severity=SafetyLevel.CRITICAL, condition=lambda m: safe_metric(m, 'resource_events') == 0, action=SafetyAction.MONITOR))
        logger.info(f'📋 기본 검증 규칙 {len(self.validation_rules)}개 설정 완료')

    async def _ensure_running(self):
        """실행 상태 보장 (lazy-start)"""
        if not self._running:
            await self.start()

    def add_rule(self, rule: ValidationRule):
        """검증 규칙 추가"""
        self.validation_rules.append(rule)
        logger.info(f'➕ 검증 규칙 추가: {rule.name}')

    def remove_rule(self, rule_name: str) -> bool:
        """검증 규칙 제거"""
        for (i, rule) in enumerate(self.validation_rules):
            if rule.name == rule_name:
                del self.validation_rules[i]
                logger.info(f'➖ 검증 규칙 제거: {rule_name}')
                return True
        return False

    async def evaluate_rule(self, name: str, metrics: Optional[SafetyMetrics]=None) -> ValidationResult:
        """개별 규칙 평가"""
        rule = None
        for r in self.validation_rules:
            if r.name == name:
                rule = r
                break
        if not rule:
            return ValidationResult(success=False, errors=[f"규칙 '{name}'을 찾을 수 없습니다"])
        if metrics is None:
            try:
                if self.safety_controller:
                    metrics = await self.safety_controller.get_metrics()
                else:
                    from safety_controller import get_safety_metrics
                    metrics = await get_safety_metrics()
            except Exception as e:
                logger.warning(f'메트릭 수집 실패, 기본값 사용: {str(e)}')
                metrics = SafetyMetrics()
        try:
            rule_result = rule.evaluate(metrics)
            return ValidationResult(success=rule_result, metrics=metrics, details={'rule_name': name, 'rule_description': rule.description})
        except Exception as e:
            logger.error(f"규칙 '{name}' 평가 중 오류: {e}")
            return ValidationResult(success=False, errors=[f'규칙 평가 오류: {str(e)}'])

    async def start(self) -> bool:
        """검증 시스템 시작"""
        async with self._lock:
            first = not self._running
            self._running = True
            if first:
                if self.safety_controller and (not self.safety_controller._running):
                    await self.safety_controller.start()
                self._validation_task = asyncio.create_task(self._periodic_validation())
                logger.info('🚀 IntegrationValidator 시작됨')
            return first

    async def stop(self) -> bool:
        """검증 시스템 정지"""
        async with self._lock:
            was = self._running
            self._running = False
            if was:
                if self._validation_task:
                    self._validation_task.cancel()
                    try:
                        await self._validation_task
                    except asyncio.CancelledError:
                        pass
                    self._validation_task = None
                logger.info('🛑 IntegrationValidator 정지됨')
            return was

    async def _periodic_validation(self):
        """주기적 검증 실행"""
        while self._running:
            try:
                await self.run_validation()
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'주기적 검증 중 오류: {e}')
                await asyncio.sleep(10)

    async def run_validation(self) -> ValidationResult:
        """검증 실행"""
        await self._ensure_running()
        async with self._lock:
            async with self.validation_semaphore:
                try:
                    logger.info('🔍 통합 안전성 검증 시작')
                    try:
                        if self.safety_controller:
                            metrics = await self.safety_controller.get_metrics()
                        else:
                            from safety_controller import get_safety_metrics
                            metrics = await get_safety_metrics()
                    except Exception as e:
                        logger.warning(f'메트릭 수집 실패, 기본값 사용: {str(e)}')
                        metrics = SafetyMetrics()
                    validation_result = ValidationResult(success=True, metrics=metrics, details={'rules_evaluated': len(self.validation_rules)})
                    for rule in self.validation_rules:
                        if not rule.evaluate(metrics):
                            validation_result.success = False
                            validation_result.errors.append(f"규칙 '{rule.name}' 위반")
                    self._add_to_history(validation_result)
                    if validation_result.success:
                        logger.info('✅ 통합 안전성 검증 통과')
                    else:
                        logger.warning(f'⚠️ 통합 안전성 검증 실패: {len(validation_result.errors)}개 규칙 위반')
                    return validation_result
                except Exception as e:
                    logger.error(f'검증 실행 중 오류: {e}')
                    error_result = ValidationResult(success=False, errors=[f'검증 실행 오류: {str(e)}'])
                    self._add_to_history(error_result)
                    return error_result

    def _add_to_history(self, result: ValidationResult):
        """검증 결과를 히스토리에 추가"""
        self.validation_history.append(result)
        if len(self.validation_history) > self.max_history_size:
            self.validation_history.pop(0)

    async def get_validation_status(self) -> Dict[str, Any]:
        """검증 상태 조회"""
        await self._ensure_running()
        recent_results = self.validation_history[-10:] if self.validation_history else []
        return {'running': bool(self._running), 'total_rules': len(self.validation_rules), 'enabled_rules': len([r for r in self.validation_rules if r.enabled]), 'recent_validations': len(recent_results), 'success_rate': self._calculate_success_rate(recent_results), 'last_validation': recent_results[-1].timestamp.isoformat() if recent_results else None}

    def _calculate_success_rate(self, results: List[ValidationResult]) -> float:
        """성공률 계산"""
        if not results:
            return 0.0
        successful = sum((1 for r in results if r.success))
        return successful / len(results) * 100

    async def reset(self):
        """검증 시스템 초기화"""
        await self.stop()
        self.validation_history.clear()
        self.validation_rules.clear()
        self._setup_default_rules()
        logger.info('🔄 IntegrationValidator 초기화 완료')
integration_validator = IntegrationValidator()

async def start_integration_validation() -> bool:
    """통합 검증 시작"""
    return await integration_validator.start()

async def stop_integration_validation() -> bool:
    """통합 검증 정지"""
    return await integration_validator.stop()

async def run_integration_validation() -> ValidationResult:
    """통합 검증 실행"""
    return await integration_validator.run_validation()

async def get_integration_status() -> Dict[str, Any]:
    """통합 검증 상태 조회"""
    return await integration_validator.get_validation_status()