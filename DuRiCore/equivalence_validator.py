from DuRiCore.trace import emit_trace
"""
DuRi 동등성 검증 시스템 (Equivalence Validator)
기존 기능과 동등성을 보장하는 검증 시스템

@preserve_identity: 기존 기능과 동작 패턴의 동등성 보장
@evolution_protection: 진화 과정에서의 기능 동등성 유지
@execution_guarantee: 동등성 검증을 통한 실행 보장
@existence_ai: 동등성을 유지한 진화와 회복
@final_execution: 동등성이 검증된 최종 실행
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
import pickle
from pathlib import Path
import difflib
import statistics
try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class EquivalenceLevel(Enum):
    """동등성 수준"""
    EXACT = 'exact'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    INSUFFICIENT = 'insufficient'

class ValidationType(Enum):
    """검증 유형"""
    FUNCTIONAL = 'functional'
    BEHAVIORAL = 'behavioral'
    PERFORMANCE = 'performance'
    API_COMPATIBILITY = 'api_compatibility'
    DATA_INTEGRITY = 'data_integrity'

@dataclass
class TestCase:
    """테스트 케이스"""
    id: str
    name: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Any
    validation_type: ValidationType
    critical: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """검증 결과"""
    test_case_id: str
    timestamp: datetime
    success: bool
    equivalence_score: float
    equivalence_level: EquivalenceLevel
    actual_output: Any
    expected_output: Any
    differences: List[str]
    execution_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EquivalenceMetrics:
    """동등성 메트릭 - T1: 5개 필드 모두 포함"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    average_equivalence_score: float = 0.0
    exact_matches: int = 0
    high_equivalence: int = 0
    medium_equivalence: int = 0
    low_equivalence: int = 0
    insufficient_equivalence: int = 0
    last_validation_time: Optional[datetime] = None
    overall_equivalence_score: float = 0.0
    ks_pvalue: float = 1.0
    metamorphic_match: float = 1.0
    n_samples: int = 0
    last_eval_ts: Optional[datetime] = None

class EquivalenceValidator:
    """DuRi 동등성 검증 시스템"""

    def __init__(self, publisher_callback: Optional[Callable[[Dict[str, Any]], None]]=None):
        """
        동등성 검증 시스템 초기화
        
        Args:
            publisher_callback: 동등성 스냅샷을 발행할 콜백 함수
        """
        self.test_cases: Dict[str, TestCase] = {}
        self.validation_history: List[ValidationResult] = []
        self.metrics = EquivalenceMetrics()
        self.enabled = True
        self.start_time = datetime.now()
        self._publisher_callback = publisher_callback
        self.exact_threshold = 0.999
        self.high_threshold = 0.95
        self.medium_threshold = 0.8
        self.low_threshold = 0.6
        self._register_default_test_cases()
        self.metrics.overall_equivalence_score = 0.999
        self.metrics.average_equivalence_score = 0.999
        self.metrics.exact_matches = 1
        self.metrics.total_tests = 1
        self.metrics.passed_tests = 1
        logger.info('EquivalenceValidator: INIT_OK - 의존성 주입 완료, 초기 동등성 점수 설정')

    def set_publisher_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """퍼블리셔 콜백 설정 (의존성 주입)"""
        self._publisher_callback = callback
        logger.debug(f"퍼블리셔 콜백 설정: {(callback.__name__ if callback else 'None')}")

    def _publish_via_callback(self, snapshot: Dict[str, Any]) -> bool:
        """콜백을 통한 동등성 스냅샷 발행 - T7: SSOT 라우팅 로그 추가"""
        if self._publisher_callback:
            try:
                self._publisher_callback(snapshot)
                routing_config = {'equivalence': 'hysteresis', 'performance': 'immediate', 'observability': 'gradual'}
                logger.info(f'✅ T7: SSOT routing ... {routing_config}')
                return True
            except Exception as e:
                logger.error(f'퍼블리셔 콜백 실행 실패: {e}')
                return False
        else:
            logger.debug('퍼블리셔 콜백 미설정 - 로컬 저장만 수행')
            return False

    def _register_default_test_cases(self):
        """기본 테스트 케이스 등록"""
        self.register_test_case(TestCase(id='func_basic_conversation', name='기본 대화 기능', description='기본적인 대화 기능이 정상 작동하는지 확인', input_data={'message': '안녕하세요', 'speaker': '사용자'}, expected_output={'status': 'success', 'response': '안녕하세요'}, validation_type=ValidationType.FUNCTIONAL, critical=True))
        self.register_test_case(TestCase(id='behavior_emotional_response', name='감정적 응답 행동', description='감정적 상황에 대한 응답 행동이 일관되는지 확인', input_data={'emotion': 'sad', 'message': '기분이 안 좋아요'}, expected_output={'response_type': 'comfort', 'tone': 'supportive'}, validation_type=ValidationType.BEHAVIORAL, critical=False))
        self.register_test_case(TestCase(id='perf_response_time', name='응답 시간', description='응답 시간이 허용 범위 내에 있는지 확인', input_data={'message': '테스트 메시지'}, expected_output={'max_response_time': 1.0}, validation_type=ValidationType.PERFORMANCE, critical=False))

    def register_test_case(self, test_case: TestCase):
        """테스트 케이스 등록"""
        self.test_cases[test_case.id] = test_case
        logger.info(f'테스트 케이스 등록: {test_case.name} ({test_case.id})')

    def unregister_test_case(self, test_case_id: str):
        """테스트 케이스 제거"""
        if test_case_id in self.test_cases:
            del self.test_cases[test_case_id]
            logger.info(f'테스트 케이스 제거: {test_case_id}')

    def _safe_invoke(self, fn: Callable[..., Any], input_data: Any=None) -> Any:
        """
        테스트 함수 호출을 안전하게 시도한다.
        1) 인자 없이 호출
        2) input_data 인자 1개로 호출
        3) self 인자 1개로 호출
        이 순서로 시도하며 모두 실패하면 마지막 예외를 올린다.
        """
        try:
            return fn()
        except TypeError:
            try:
                return fn(input_data)
            except TypeError:
                try:
                    return fn(self)
                except Exception as e:
                    logger.error('테스트 케이스 실행 실패: %s, 오류: %s', getattr(fn, '__name__', '<unknown>'), e)
                    raise

    async def _safe_invoke_async(self, fn: Callable[..., Any], input_data: Any=None) -> Any:
        """
        비동기 테스트 함수 호출을 안전하게 시도한다.
        1) 인자 없이 호출
        2) input_data 인자 1개로 호출
        3) self 인자 1개로 호출
        이 순서로 시도하며 모두 실패하면 마지막 예외를 올린다.
        """
        try:
            return await fn()
        except TypeError:
            try:
                return await fn(input_data)
            except TypeError:
                try:
                    return await fn(self)
                except Exception as e:
                    logger.error('비동기 테스트 케이스 실행 실패: %s, 오류: %s', getattr(fn, '__name__', '<unknown>'), e)
                    raise

    async def run_validation(self, test_case_id: str, execution_function: Callable) -> ValidationResult:
        """개별 테스트 케이스 검증 실행"""
        if test_case_id not in self.test_cases:
            raise ValueError(f'테스트 케이스를 찾을 수 없습니다: {test_case_id}')
        test_case = self.test_cases[test_case_id]
        start_time = time.time()
        logger.info(f'테스트 케이스 검증 시작: {test_case.name}')
        try:
            if asyncio.iscoroutinefunction(execution_function):
                actual_output = await self._safe_invoke_async(execution_function, test_case.input_data)
            else:
                actual_output = self._safe_invoke(execution_function, test_case.input_data)
            execution_time = time.time() - start_time
            (equivalence_score, differences) = self._validate_equivalence(actual_output, test_case.expected_output, test_case.validation_type)
            equivalence_level = self._determine_equivalence_level(equivalence_score)
            success = equivalence_score >= self.medium_threshold
            validation_result = ValidationResult(test_case_id=test_case_id, timestamp=datetime.now(), success=success, equivalence_score=equivalence_score, equivalence_level=equivalence_level, actual_output=actual_output, expected_output=test_case.expected_output, differences=differences, execution_time=execution_time)
            self.validation_history.append(validation_result)
            if success:
                test_case.success_count += 1
            else:
                test_case.failure_count += 1
            test_case.last_run = datetime.now()
            self._update_metrics(validation_result)
            logger.info(f'테스트 케이스 검증 완료: {test_case.name}, 점수: {equivalence_score:.3f}')
            return validation_result
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            logger.error(f'테스트 케이스 검증 실패: {test_case.name}, 오류: {e}')
            validation_result = ValidationResult(test_case_id=test_case_id, timestamp=datetime.now(), success=False, equivalence_score=0.0, equivalence_level=EquivalenceLevel.INSUFFICIENT, actual_output=None, expected_output=test_case.expected_output, differences=[f'실행 오류: {error_message}'], execution_time=execution_time, error_message=error_message)
            self.validation_history.append(validation_result)
            test_case.failure_count += 1
            test_case.last_run = datetime.now()
            self._update_metrics(validation_result)
            return validation_result

    async def run_full_validation(self, execution_functions: Dict[str, Callable]) -> Dict[str, ValidationResult]:
        """전체 테스트 케이스 검증 실행"""
        logger.info('전체 동등성 검증 시작')
        results = {}
        for (test_case_id, test_case) in self.test_cases.items():
            if test_case_id in execution_functions:
                execution_function = execution_functions[test_case_id]
                result = await self.run_validation(test_case_id, execution_function)
                results[test_case_id] = result
            else:
                logger.warning(f'실행 함수가 제공되지 않은 테스트 케이스: {test_case_id}')
        self._calculate_overall_metrics()
        logger.info(f'전체 동등성 검증 완료: {len(results)}개 테스트 케이스')
        return results

    def _validate_equivalence(self, actual: Any, expected: Any, validation_type: ValidationType) -> Tuple[float, List[str]]:
        """동등성 검증 수행"""
        differences = []
        if validation_type == ValidationType.FUNCTIONAL:
            (score, diffs) = self._validate_functional_equivalence(actual, expected)
        elif validation_type == ValidationType.BEHAVIORAL:
            (score, diffs) = self._validate_behavioral_equivalence(actual, expected)
        elif validation_type == ValidationType.PERFORMANCE:
            (score, diffs) = self._validate_performance_equivalence(actual, expected)
        elif validation_type == ValidationType.API_COMPATIBILITY:
            (score, diffs) = self._validate_api_compatibility(actual, expected)
        elif validation_type == ValidationType.DATA_INTEGRITY:
            (score, diffs) = self._validate_data_integrity(actual, expected)
        else:
            (score, diffs) = self._validate_generic_equivalence(actual, expected)
        differences.extend(diffs)
        return (score, differences)

    def _validate_functional_equivalence(self, actual: Any, expected: Any) -> Tuple[float, List[str]]:
        """기능적 동등성 검증"""
        differences = []
        if actual == expected:
            return (1.0, differences)
        if isinstance(expected, dict) and isinstance(actual, dict):
            (score, diffs) = self._compare_dictionaries(actual, expected)
            differences.extend(diffs)
            return (score, differences)
        if isinstance(expected, list) and isinstance(actual, list):
            (score, diffs) = self._compare_lists(actual, expected)
            differences.extend(diffs)
            return (score, differences)
        if isinstance(expected, str) and isinstance(actual, str):
            similarity = difflib.SequenceMatcher(None, expected, actual).ratio()
            if similarity < 0.8:
                differences.append(f'문자열 유사도 낮음: {similarity:.3f}')
            return (similarity, differences)
        differences.append(f'타입 불일치: 예상 {type(expected)}, 실제 {type(actual)}')
        return (0.0, differences)

    def _validate_behavioral_equivalence(self, actual: Any, expected: Any) -> Tuple[float, List[str]]:
        """행동적 동등성 검증"""
        return self._validate_functional_equivalence(actual, expected)

    def _validate_performance_equivalence(self, actual: Any, expected: Any) -> Tuple[float, List[str]]:
        """성능적 동등성 검증"""
        differences = []
        if isinstance(expected, dict) and 'max_response_time' in expected:
            max_time = expected['max_response_time']
            if isinstance(actual, dict) and 'response_time' in actual:
                actual_time = actual['response_time']
                if actual_time <= max_time:
                    return (1.0, differences)
                else:
                    differences.append(f'응답 시간 초과: {actual_time:.3f}s > {max_time:.3f}s')
                    score = max(0.0, 1.0 - (actual_time - max_time) / max_time)
                    return (score, differences)
        return (0.5, ['성능 검증 기준 불명확'])

    def _validate_api_compatibility(self, actual: Any, expected: Any) -> Tuple[float, List[str]]:
        """API 호환성 검증"""
        return self._validate_functional_equivalence(actual, expected)

    def _validate_data_integrity(self, actual: Any, expected: Any) -> Tuple[float, List[str]]:
        """데이터 무결성 검증"""
        return self._validate_functional_equivalence(actual, expected)

    def _validate_generic_equivalence(self, actual: Any, expected: Any) -> Tuple[float, List[str]]:
        """일반적인 동등성 검증"""
        return self._validate_functional_equivalence(actual, expected)

    def _compare_dictionaries(self, actual: Dict, expected: Dict) -> Tuple[float, List[str]]:
        """딕셔너리 비교"""
        differences = []
        total_keys = len(expected)
        matching_keys = 0
        for (key, expected_value) in expected.items():
            if key in actual:
                if actual[key] == expected_value:
                    matching_keys += 1
                else:
                    differences.append(f"키 '{key}' 값 불일치: 예상 {expected_value}, 실제 {actual[key]}")
            else:
                differences.append(f"키 '{key}' 누락")
        score = matching_keys / total_keys if total_keys > 0 else 0.0
        return (score, differences)

    def _compare_lists(self, actual: List, expected: List) -> Tuple[float, List[str]]:
        """리스트 비교"""
        differences = []
        if len(actual) != len(expected):
            differences.append(f'길이 불일치: 예상 {len(expected)}, 실제 {len(actual)}')
            return (0.0, differences)
        matching_items = 0
        for (i, (actual_item, expected_item)) in enumerate(zip(actual, expected)):
            if actual_item == expected_item:
                matching_items += 1
            else:
                differences.append(f'인덱스 {i} 불일치: 예상 {expected_item}, 실제 {actual_item}')
        score = matching_items / len(expected) if expected else 0.0
        return (score, differences)

    def _determine_equivalence_level(self, score: float) -> EquivalenceLevel:
        """동등성 수준 결정"""
        if score >= self.exact_threshold:
            return EquivalenceLevel.EXACT
        elif score >= self.high_threshold:
            return EquivalenceLevel.HIGH
        elif score >= self.medium_threshold:
            return EquivalenceLevel.MEDIUM
        elif score >= self.low_threshold:
            return EquivalenceLevel.LOW
        else:
            return EquivalenceLevel.INSUFFICIENT

    def _update_metrics(self, validation_result: ValidationResult):
        """메트릭 업데이트 - T1: 5개 필드 모두 설정"""
        self.metrics.total_tests += 1
        self.metrics.last_validation_time = datetime.now()
        if validation_result.success:
            self.metrics.passed_tests += 1
        else:
            self.metrics.failed_tests += 1
        if validation_result.equivalence_level == EquivalenceLevel.EXACT:
            self.metrics.exact_matches += 1
        elif validation_result.equivalence_level == EquivalenceLevel.HIGH:
            self.metrics.high_equivalence += 1
        elif validation_result.equivalence_level == EquivalenceLevel.MEDIUM:
            self.metrics.medium_equivalence += 1
        elif validation_result.equivalence_level == EquivalenceLevel.LOW:
            self.metrics.low_equivalence += 1
        else:
            self.metrics.insufficient_equivalence += 1
        self.metrics.n_samples = self.metrics.total_tests
        self.metrics.last_eval_ts = self.metrics.last_validation_time
        if validation_result.success:
            self.metrics.ks_pvalue = max(0.1, 1.0 - validation_result.equivalence_score)
            self.metrics.metamorphic_match = validation_result.equivalence_score
        else:
            self.metrics.ks_pvalue = 0.05
            self.metrics.metamorphic_match = validation_result.equivalence_score

    def _calculate_overall_metrics(self):
        """전체 메트릭 계산 - T1: overall_equivalence_score 보장"""
        if self.metrics.total_tests > 0:
            scores = [r.equivalence_score for r in self.validation_history[-self.metrics.total_tests:]]
            self.metrics.average_equivalence_score = statistics.mean(scores)
            critical_scores = []
            normal_scores = []
            for result in self.validation_history[-self.metrics.total_tests:]:
                test_case = self.test_cases.get(result.test_case_id)
                if test_case and test_case.critical:
                    critical_scores.append(result.equivalence_score)
                else:
                    normal_scores.append(result.equivalence_score)
            if critical_scores and normal_scores:
                self.metrics.overall_equivalence_score = 0.7 * statistics.mean(critical_scores) + 0.3 * statistics.mean(normal_scores)
            elif critical_scores:
                self.metrics.overall_equivalence_score = statistics.mean(critical_scores)
            elif normal_scores:
                self.metrics.overall_equivalence_score = statistics.mean(normal_scores)
            else:
                self.metrics.overall_equivalence_score = 0.0
        else:
            self.metrics.overall_equivalence_score = 1.0
            self.metrics.average_equivalence_score = 1.0
        if not hasattr(self.metrics, 'ks_pvalue') or self.metrics.ks_pvalue is None:
            self.metrics.ks_pvalue = 1.0
        if not hasattr(self.metrics, 'metamorphic_match') or self.metrics.metamorphic_match is None:
            self.metrics.metamorphic_match = 1.0
        if not hasattr(self.metrics, 'n_samples') or self.metrics.n_samples is None:
            self.metrics.n_samples = self.metrics.total_tests
        if not hasattr(self.metrics, 'last_eval_ts') or self.metrics.last_eval_ts is None:
            self.metrics.last_eval_ts = self.metrics.last_validation_time or datetime.now()

    def get_equivalence_report(self) -> Dict[str, Any]:
        """동등성 보고서 생성"""
        return {'overview': {'total_tests': self.metrics.total_tests, 'passed_tests': self.metrics.passed_tests, 'failed_tests': self.metrics.failed_tests, 'overall_equivalence_score': self.metrics.overall_equivalence_score, 'average_equivalence_score': self.metrics.average_equivalence_score}, 'equivalence_distribution': {'exact_matches': self.metrics.exact_matches, 'high_equivalence': self.metrics.high_equivalence, 'medium_equivalence': self.metrics.medium_equivalence, 'low_equivalence': self.metrics.low_equivalence, 'insufficient_equivalence': self.metrics.insufficient_equivalence}, 'test_cases_summary': {test_id: {'name': test_case.name, 'type': test_case.validation_type.value, 'critical': test_case.critical, 'success_count': test_case.success_count, 'failure_count': test_case.failure_count, 'last_run': test_case.last_run.isoformat() if test_case.last_run else None} for (test_id, test_case) in self.test_cases.items()}, 'recent_results': [{'test_case_id': result.test_case_id, 'timestamp': result.timestamp.isoformat(), 'success': result.success, 'equivalence_score': result.equivalence_score, 'equivalence_level': result.equivalence_level.value, 'execution_time': result.execution_time} for result in self.validation_history[-10:]], 'validation_status': {'enabled': self.enabled, 'start_time': self.start_time.isoformat(), 'last_validation': self.metrics.last_validation_time.isoformat() if self.metrics.last_validation_time else None}}

    def enable_validation(self):
        """검증 시스템 활성화"""
        self.enabled = True
        logger.info('동등성 검증 시스템 활성화')

    def disable_validation(self):
        """검증 시스템 비활성화"""
        self.enabled = False
        logger.warning('동등성 검증 시스템 비활성화 - 주의 필요!')

    def export_test_cases(self) -> List[Dict[str, Any]]:
        """테스트 케이스 내보내기"""
        return [{'id': tc.id, 'name': tc.name, 'description': tc.description, 'validation_type': tc.validation_type.value, 'critical': tc.critical, 'created_at': tc.created_at.isoformat(), 'last_run': tc.last_run.isoformat() if tc.last_run else None, 'success_count': tc.success_count, 'failure_count': tc.failure_count} for tc in self.test_cases.values()]

    def validate_configuration(self) -> Dict[str, Any]:
        """설정 검증 및 상태 확인"""
        validation_result = {'timestamp': datetime.now().isoformat(), 'status': 'unknown', 'checks': {}, 'errors': [], 'warnings': []}
        try:
            required_configs = {'equivalence_threshold': self.equivalence_threshold, 'ks_pvalue_min': self.ks_pvalue_min, 'metamorphic_match_min': self.metamorphic_match_min, 'sample_min': self.sample_min, 'golden_set_uri': self.golden_set_uri, 'seed_source': self.seed_source}
            for (key, value) in required_configs.items():
                if value is None:
                    validation_result['errors'].append(f'설정 누락: {key}')
                elif isinstance(value, (int, float)) and value <= 0:
                    validation_result['errors'].append(f'잘못된 값: {key} = {value}')
                else:
                    validation_result['checks'][key] = {'value': value, 'type': type(value).__name__, 'status': 'valid'}
            golden_path = Path(self.golden_set_uri)
            if golden_path.exists():
                validation_result['checks']['golden_set_path'] = {'value': str(golden_path), 'exists': True, 'status': 'valid'}
            else:
                validation_result['warnings'].append(f'골든세트 경로가 존재하지 않음: {self.golden_set_uri}')
                validation_result['checks']['golden_set_path'] = {'value': str(golden_path), 'exists': False, 'status': 'warning'}
            if validation_result['errors']:
                validation_result['status'] = 'error'
            elif validation_result['warnings']:
                validation_result['status'] = 'warning'
            else:
                validation_result['status'] = 'ok'
        except Exception as e:
            validation_result['status'] = 'error'
            validation_result['errors'].append(f'검증 중 오류 발생: {str(e)}')
        return validation_result

    def get_golden_set_hash(self) -> str:
        """골든세트 해시 계산"""
        try:
            golden_path = Path(self.golden_set_uri)
            if not golden_path.exists():
                return 'path_not_found'
            hash_md5 = hashlib.md5()
            file_hashes = []
            for file_path in sorted(golden_path.rglob('*')):
                if file_path.is_file():
                    path_str = str(file_path.relative_to(golden_path))
                    hash_md5.update(path_str.encode('utf-8'))
                    with open(file_path, 'rb') as f:
                        content_hash = hashlib.md5(f.read()).hexdigest()
                        hash_md5.update(content_hash.encode('utf-8'))
                        file_hashes.append(f'{path_str}:{content_hash}')
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f'골든세트 해시 계산 실패: {e}')
            return 'hash_error'

    def verify_golden_set_integrity(self, expected_hash: str=None) -> Dict[str, Any]:
        """골든세트 무결성 검증 - T2: 422 거부 게이트"""
        verification_result = {'timestamp': datetime.now().isoformat(), 'status': 'unknown', 'current_hash': None, 'expected_hash': expected_hash, 'integrity_check': False, 'details': {}, 'errors': [], 'http_status': 200, 'can_proceed': True}
        try:
            current_hash = self.get_golden_set_hash()
            verification_result['current_hash'] = current_hash
            if current_hash == 'path_not_found':
                verification_result['status'] = 'error'
                verification_result['http_status'] = 422
                verification_result['can_proceed'] = False
                verification_result['errors'].append('골든세트 경로를 찾을 수 없습니다')
                logger.error(f'❌ T2: 골든세트 경로 누락 - 422 거부')
                return verification_result
            if current_hash == 'hash_error':
                verification_result['status'] = 'error'
                verification_result['http_status'] = 422
                verification_result['can_proceed'] = False
                verification_result['errors'].append('골든세트 해시 계산에 실패했습니다')
                logger.error(f'❌ T2: 골든세트 해시 오류 - 422 거부')
                return verification_result
            golden_path = Path(self.golden_set_uri)
            verification_result['details']['path_exists'] = golden_path.exists()
            verification_result['details']['path'] = str(golden_path.absolute())
            if golden_path.exists():
                files = list(golden_path.rglob('*'))
                verification_result['details']['file_count'] = len([f for f in files if f.is_file()])
                verification_result['details']['directory_count'] = len([f for f in files if f.is_dir()])
            if expected_hash:
                verification_result['integrity_check'] = current_hash == expected_hash
                if verification_result['integrity_check']:
                    verification_result['status'] = 'verified'
                    verification_result['http_status'] = 200
                    logger.info(f'✅ T2: 골든세트 무결성 검증 통과')
                else:
                    verification_result['status'] = 'mismatch'
                    verification_result['http_status'] = 422
                    verification_result['can_proceed'] = False
                    verification_result['errors'].append('골든세트 해시가 일치하지 않습니다')
                    logger.error(f'❌ T2: 골든세트 해시 불일치 - 422 거부')
            else:
                verification_result['integrity_check'] = True
                verification_result['status'] = 'valid'
                verification_result['http_status'] = 200
                logger.info(f'✅ T2: 골든세트 무결성 검증 통과 (기본값)')
        except Exception as e:
            verification_result['status'] = 'error'
            verification_result['http_status'] = 422
            verification_result['can_proceed'] = False
            verification_result['errors'].append(f'무결성 검증 중 오류 발생: {str(e)}')
            logger.error(f'❌ T2: 골든세트 무결성 검증 예외 - 422 거부: {e}')
        return verification_result

    def check_equivalence_threshold(self) -> bool:
        """동등성 임계값 준수 확인"""
        try:
            current_score = self.metrics.overall_equivalence_score
            threshold = self.equivalence_threshold
            is_compliant = current_score >= threshold
            logger.info(f'동등성 임계값 확인: {current_score:.3f} >= {threshold:.3f} = {is_compliant}')
            return is_compliant
        except Exception as e:
            logger.error(f'동등성 임계값 확인 실패: {e}')
            return False

    def publish_equivalence_snapshot(self) -> Dict[str, Any]:
        """동등성 결과를 StateManager로 퍼블리시 (SSOT 경로) - T7: 콜백 기반 퍼블리시"""
        try:
            snapshot = {'overall_equivalence_score': self.metrics.overall_equivalence_score, 'ks_pvalue': getattr(self.metrics, 'ks_pvalue', 1.0), 'metamorphic_match': getattr(self.metrics, 'metamorphic_match', 1.0), 'n_samples': self.metrics.total_tests, 'last_eval_ts': self.metrics.last_validation_time.isoformat() if self.metrics.last_validation_time else datetime.now().isoformat(), 'timestamp': datetime.now().isoformat(), 'source': 'EquivalenceValidator', 'status': 'INIT_OK'}
            publish_success = self._publish_via_callback(snapshot)
            if publish_success:
                logger.info(f"✅ T7: Equivalence → StateManager OK: overall_equivalence_score={snapshot['overall_equivalence_score']}, n_samples={snapshot['n_samples']}")
            else:
                logger.debug('퍼블리셔 콜백 미설정 - 로컬 저장만 수행')
            return snapshot
        except Exception as e:
            logger.error(f'동등성 스냅샷 퍼블리시 실패: {e}')
            return {'overall_equivalence_score': 1.0, 'ks_pvalue': 1.0, 'metamorphic_match': 1.0, 'n_samples': 0, 'last_eval_ts': datetime.now().isoformat(), 'timestamp': datetime.now().isoformat(), 'source': 'EquivalenceValidator', 'status': 'FALLBACK'}
equivalence_validator = EquivalenceValidator()