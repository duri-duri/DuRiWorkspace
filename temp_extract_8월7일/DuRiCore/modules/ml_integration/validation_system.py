"""
검증 시스템 모듈
ML 통합 과정의 각 단계를 검증하고 품질을 보장합니다.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    """검증 상태 열거형"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

class ValidationLevel(Enum):
    """검증 수준 열거형"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    CUSTOM = "custom"

@dataclass
class ValidationResult:
    """검증 결과 데이터 클래스"""
    test_name: str
    status: ValidationStatus
    score: float
    message: str
    details: Dict[str, Any]
    timestamp: float
    execution_time: float
    metadata: Dict[str, Any]

class ValidationRule:
    """검증 규칙 기본 클래스"""
    
    def __init__(self, name: str, description: str, weight: float = 1.0):
        self.name = name
        self.description = description
        self.weight = weight
        self.enabled = True
    
    def validate(self, data: Any) -> Tuple[bool, str, Dict[str, Any]]:
        """검증 수행 - 하위 클래스에서 구현"""
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")
    
    def __str__(self):
        return f"ValidationRule({self.name}, weight={self.weight})"

class DataQualityValidator(ValidationRule):
    """데이터 품질 검증기"""
    
    def __init__(self):
        super().__init__("DataQuality", "데이터 품질 검증", weight=1.5)
    
    def validate(self, data: Any) -> Tuple[bool, str, Dict[str, Any]]:
        """데이터 품질 검증"""
        try:
            if data is None:
                return False, "데이터가 None입니다", {"error": "null_data"}
            
            if hasattr(data, '__len__') and len(data) == 0:
                return False, "데이터가 비어있습니다", {"error": "empty_data"}
            
            # 기본 데이터 타입 검증
            if not isinstance(data, (dict, list, str, int, float)):
                return False, f"지원하지 않는 데이터 타입: {type(data)}", {"error": "unsupported_type"}
            
            return True, "데이터 품질 검증 통과", {"data_type": str(type(data)), "data_size": len(data) if hasattr(data, '__len__') else "N/A"}
        
        except Exception as e:
            return False, f"데이터 품질 검증 중 오류: {str(e)}", {"error": str(e)}

class ModelPerformanceValidator(ValidationRule):
    """모델 성능 검증기"""
    
    def __init__(self, min_accuracy: float = 0.7, min_f1: float = 0.6):
        super().__init__("ModelPerformance", "모델 성능 검증", weight=2.0)
        self.min_accuracy = min_accuracy
        self.min_f1 = min_f1
    
    def validate(self, data: Any) -> Tuple[bool, str, Dict[str, Any]]:
        """모델 성능 검증"""
        try:
            if not isinstance(data, dict):
                return False, "모델 성능 데이터가 딕셔너리가 아닙니다", {"error": "invalid_format"}
            
            # 필수 메트릭 확인
            required_metrics = ['accuracy', 'f1_score', 'precision', 'recall']
            missing_metrics = [metric for metric in required_metrics if metric not in data]
            
            if missing_metrics:
                return False, f"필수 메트릭이 누락되었습니다: {missing_metrics}", {"missing_metrics": missing_metrics}
            
            # 성능 임계값 검증
            accuracy = data.get('accuracy', 0)
            f1_score = data.get('f1_score', 0)
            
            if accuracy < self.min_accuracy:
                return False, f"정확도가 임계값({self.min_accuracy}) 미만입니다: {accuracy}", {"metric": "accuracy", "value": accuracy, "threshold": self.min_accuracy}
            
            if f1_score < self.min_f1:
                return False, f"F1 점수가 임계값({self.min_f1}) 미만입니다: {f1_score}", {"metric": "f1_score", "value": f1_score, "threshold": self.min_f1}
            
            return True, "모델 성능 검증 통과", {
                "accuracy": accuracy,
                "f1_score": f1_score,
                "precision": data.get('precision'),
                "recall": data.get('recall')
            }
        
        except Exception as e:
            return False, f"모델 성능 검증 중 오류: {str(e)}", {"error": str(e)}

class IntegrationConsistencyValidator(ValidationRule):
    """통합 일관성 검증기"""
    
    def __init__(self):
        super().__init__("IntegrationConsistency", "통합 일관성 검증", weight=1.8)
    
    def validate(self, data: Any) -> Tuple[bool, str, Dict[str, Any]]:
        """통합 일관성 검증"""
        try:
            if not isinstance(data, dict):
                return False, "통합 데이터가 딕셔너리가 아닙니다", {"error": "invalid_format"}
            
            # 필수 키 확인
            required_keys = ['phase1_status', 'phase2_status', 'integration_status']
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                return False, f"필수 키가 누락되었습니다: {missing_keys}", {"missing_keys": missing_keys}
            
            # 상태 일관성 검증
            phase1_status = data.get('phase1_status')
            phase2_status = data.get('phase2_status')
            integration_status = data.get('integration_status')
            
            # Phase 1이 완료되지 않았는데 Phase 2가 진행된 경우
            if phase1_status != 'completed' and phase2_status in ['in_progress', 'completed']:
                return False, "Phase 1이 완료되지 않았는데 Phase 2가 진행되었습니다", {
                    "phase1_status": phase1_status,
                    "phase2_status": phase2_status
                }
            
            # 통합 상태와 개별 단계 상태 불일치
            if integration_status == 'completed' and (phase1_status != 'completed' or phase2_status != 'completed'):
                return False, "통합 상태가 완료되었는데 개별 단계가 완료되지 않았습니다", {
                    "integration_status": integration_status,
                    "phase1_status": phase1_status,
                    "phase2_status": phase2_status
                }
            
            return True, "통합 일관성 검증 통과", {
                "phase1_status": phase1_status,
                "phase2_status": phase2_status,
                "integration_status": integration_status
            }
        
        except Exception as e:
            return False, f"통합 일관성 검증 중 오류: {str(e)}", {"error": str(e)}

class ValidationSystem:
    """검증 시스템 메인 클래스"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.validation_level = validation_level
        self.validators: List[ValidationRule] = []
        self.validation_history: List[ValidationResult] = []
        self.custom_rules: Dict[str, ValidationRule] = {}
        
        # 기본 검증기 등록
        self._register_default_validators()
        
        # 검증 수준에 따른 규칙 조정
        self._adjust_rules_by_level()
    
    def _register_default_validators(self):
        """기본 검증기 등록"""
        self.validators.extend([
            DataQualityValidator(),
            ModelPerformanceValidator(),
            IntegrationConsistencyValidator()
        ])
    
    def _adjust_rules_by_level(self):
        """검증 수준에 따른 규칙 조정"""
        if self.validation_level == ValidationLevel.STRICT:
            # 엄격한 검증을 위한 임계값 조정
            for validator in self.validators:
                if isinstance(validator, ModelPerformanceValidator):
                    validator.min_accuracy = 0.8
                    validator.min_f1 = 0.7
        elif self.validation_level == ValidationLevel.BASIC:
            # 기본 검증을 위한 임계값 완화
            for validator in self.validators:
                if isinstance(validator, ModelPerformanceValidator):
                    validator.min_accuracy = 0.6
                    validator.min_f1 = 0.5
    
    def add_custom_rule(self, rule: ValidationRule):
        """사용자 정의 검증 규칙 추가"""
        self.custom_rules[rule.name] = rule
        self.validators.append(rule)
        logger.info(f"사용자 정의 검증 규칙 추가: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """검증 규칙 제거"""
        self.validators = [v for v in self.validators if v.name != rule_name]
        if rule_name in self.custom_rules:
            del self.custom_rules[rule_name]
        logger.info(f"검증 규칙 제거: {rule_name}")
    
    def validate_data(self, data: Any, context: str = "general") -> ValidationResult:
        """데이터 검증 수행"""
        start_time = time.time()
        logger.info(f"데이터 검증 시작: {context}")
        
        # 전체 검증 결과 집계
        total_score = 0.0
        total_weight = 0.0
        validation_details = {}
        all_passed = True
        messages = []
        
        for validator in self.validators:
            if not validator.enabled:
                continue
            
            try:
                passed, message, details = validator.validate(data)
                validation_details[validator.name] = {
                    "passed": passed,
                    "message": message,
                    "details": details,
                    "weight": validator.weight
                }
                
                if passed:
                    total_score += validator.weight
                    messages.append(f"✓ {validator.name}: {message}")
                else:
                    all_passed = False
                    messages.append(f"✗ {validator.name}: {message}")
                
                total_weight += validator.weight
                
            except Exception as e:
                logger.error(f"검증기 {validator.name} 실행 중 오류: {str(e)}")
                validation_details[validator.name] = {
                    "passed": False,
                    "message": f"검증 중 오류 발생: {str(e)}",
                    "details": {"error": str(e)},
                    "weight": validator.weight
                }
                all_passed = False
                total_weight += validator.weight
        
        # 최종 점수 계산
        final_score = (total_score / total_weight) * 100 if total_weight > 0 else 0
        
        # 상태 결정
        if all_passed:
            status = ValidationStatus.PASSED
        elif final_score >= 70:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.FAILED
        
        execution_time = time.time() - start_time
        
        # 검증 결과 생성
        result = ValidationResult(
            test_name=f"Validation_{context}",
            status=status,
            score=final_score,
            message="\n".join(messages),
            details=validation_details,
            timestamp=time.time(),
            execution_time=execution_time,
            metadata={
                "validation_level": self.validation_level.value,
                "total_validators": len(self.validators),
                "context": context
            }
        )
        
        # 검증 히스토리에 추가
        self.validation_history.append(result)
        
        logger.info(f"데이터 검증 완료: {context} - 점수: {final_score:.2f}, 상태: {status.value}")
        
        return result
    
    def validate_integration_workflow(self, workflow_data: Dict[str, Any]) -> List[ValidationResult]:
        """통합 워크플로우 검증"""
        results = []
        
        # 1. 데이터 품질 검증
        data_quality_result = self.validate_data(workflow_data, "DataQuality")
        results.append(data_quality_result)
        
        # 2. 모델 성능 검증 (성능 데이터가 있는 경우)
        if 'model_performance' in workflow_data:
            performance_result = self.validate_data(workflow_data['model_performance'], "ModelPerformance")
            results.append(performance_result)
        
        # 3. 통합 일관성 검증
        consistency_result = self.validate_data(workflow_data, "IntegrationConsistency")
        results.append(consistency_result)
        
        return results
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """검증 요약 정보 반환"""
        if not self.validation_history:
            return {"message": "검증 히스토리가 없습니다"}
        
        total_validations = len(self.validation_history)
        passed_count = sum(1 for r in self.validation_history if r.status == ValidationStatus.PASSED)
        failed_count = sum(1 for r in self.validation_history if r.status == ValidationStatus.FAILED)
        warning_count = sum(1 for r in self.validation_history if r.status == ValidationStatus.WARNING)
        
        avg_score = sum(r.score for r in self.validation_history) / total_validations
        avg_execution_time = sum(r.execution_time for r in self.validation_history) / total_validations
        
        return {
            "total_validations": total_validations,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "warning_count": warning_count,
            "success_rate": (passed_count / total_validations) * 100,
            "average_score": avg_score,
            "average_execution_time": avg_execution_time,
            "validation_level": self.validation_level.value,
            "active_validators": len([v for v in self.validators if v.enabled])
        }
    
    def export_validation_report(self, filepath: str = None) -> str:
        """검증 보고서 내보내기"""
        if not filepath:
            timestamp = int(time.time())
            filepath = f"validation_report_{timestamp}.json"
        
        report_data = {
            "validation_summary": self.get_validation_summary(),
            "validation_history": [
                {
                    "test_name": result.test_name,
                    "status": result.status.value,
                    "score": result.score,
                    "message": result.message,
                    "timestamp": result.timestamp,
                    "execution_time": result.execution_time,
                    "metadata": result.metadata
                }
                for result in self.validation_history
            ],
            "export_timestamp": time.time()
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"검증 보고서 내보내기 완료: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"검증 보고서 내보내기 실패: {str(e)}")
            raise
    
    def clear_history(self):
        """검증 히스토리 초기화"""
        self.validation_history.clear()
        logger.info("검증 히스토리가 초기화되었습니다")
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """상세한 검증 통계 반환"""
        if not self.validation_history:
            return {"message": "검증 데이터가 없습니다"}
        
        # 상태별 통계
        status_stats = {}
        for status in ValidationStatus:
            count = sum(1 for r in self.validation_history if r.status == status)
            status_stats[status.value] = count
        
        # 점수 분포
        score_ranges = {
            "excellent": (90, 100),
            "good": (80, 89),
            "fair": (70, 79),
            "poor": (60, 69),
            "very_poor": (0, 59)
        }
        
        score_distribution = {}
        for range_name, (min_score, max_score) in score_ranges.items():
            count = sum(1 for r in self.validation_history if min_score <= r.score <= max_score)
            score_distribution[range_name] = count
        
        return {
            "status_statistics": status_stats,
            "score_distribution": score_distribution,
            "performance_metrics": {
                "total_execution_time": sum(r.execution_time for r in self.validation_history),
                "average_execution_time": sum(r.execution_time for r in self.validation_history) / len(self.validation_history),
                "fastest_validation": min(r.execution_time for r in self.validation_history),
                "slowest_validation": max(r.execution_time for r in self.validation_history)
            }
        }

# 사용 예시
if __name__ == "__main__":
    # 검증 시스템 인스턴스 생성
    validator = ValidationSystem(ValidationLevel.STANDARD)
    
    # 샘플 데이터로 검증 테스트
    sample_data = {
        "phase1_status": "completed",
        "phase2_status": "in_progress",
        "integration_status": "in_progress",
        "model_performance": {
            "accuracy": 0.85,
            "f1_score": 0.82,
            "precision": 0.83,
            "recall": 0.81
        }
    }
    
    # 통합 워크플로우 검증
    results = validator.validate_integration_workflow(sample_data)
    
    # 결과 출력
    for result in results:
        print(f"\n=== {result.test_name} ===")
        print(f"상태: {result.status.value}")
        print(f"점수: {result.score:.2f}")
        print(f"메시지: {result.message}")
        print(f"실행 시간: {result.execution_time:.4f}초")
    
    # 검증 요약 출력
    summary = validator.get_validation_summary()
    print(f"\n=== 검증 요약 ===")
    print(f"총 검증 수: {summary['total_validations']}")
    print(f"성공률: {summary['success_rate']:.2f}%")
    print(f"평균 점수: {summary['average_score']:.2f}")
    print(f"평균 실행 시간: {summary['average_execution_time']:.4f}초")
    
    # 상세 통계 출력
    stats = validator.get_validation_statistics()
    print(f"\n=== 상세 통계 ===")
    print(f"상태별 통계: {stats['status_statistics']}")
    print(f"점수 분포: {stats['score_distribution']}")
    
    print("\n검증 시스템 테스트 완료!")
