#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 1-3 Week 3 Day 10: 시스템 검증 엔진

이 모듈은 시스템 품질 보증 및 검증을 수행하는 엔진입니다.
시스템 검증, 품질 보증, 최종 검증을 제공합니다.

주요 기능:
- 시스템 검증 엔진
- 품질 보증 시스템
- 최종 검증 시스템
"""

import asyncio
import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ValidationType(Enum):
    """검증 유형 열거형"""

    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"
    INTEGRATION = "integration"
    QUALITY = "quality"


class ValidationStatus(Enum):
    """검증 상태 열거형"""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class QualityLevel(Enum):
    """품질 수준 열거형"""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class ValidationRule:
    """검증 규칙 데이터 클래스"""

    name: str
    validation_type: ValidationType
    description: str
    criteria: Dict[str, Any]
    weight: float = 1.0
    required: bool = True
    timeout: int = 300


@dataclass
class ValidationResult:
    """검증 결과 데이터 클래스"""

    rule: ValidationRule
    status: ValidationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """품질 보고서 데이터 클래스"""

    timestamp: datetime
    overall_quality: QualityLevel
    quality_score: float
    validation_results: List[ValidationResult]
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SystemValidation:
    """시스템 검증 데이터 클래스"""

    system_name: str
    validation_type: ValidationType
    validation_results: List[ValidationResult]
    overall_score: float
    quality_level: QualityLevel
    validation_time: float


class SystemValidationEngine:
    """
    시스템 검증 엔진

    시스템 품질 보증 및 검증을 수행하는 엔진입니다.
    """

    def __init__(self):
        """초기화"""
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validation_results: List[ValidationResult] = []
        self.quality_reports: List[QualityReport] = []
        self.system_validations: List[SystemValidation] = []
        self.is_running = False
        self.start_time = None

        # 기본 검증 규칙 등록
        self._register_default_validation_rules()

    def _register_default_validation_rules(self):
        """기본 검증 규칙 등록"""
        # 기능적 검증 규칙
        functional_rules = [
            ValidationRule(
                name="시스템 응답성 검증",
                validation_type=ValidationType.FUNCTIONAL,
                description="시스템이 요청에 적절히 응답하는지 검증",
                criteria={"response_time": 0.1, "success_rate": 0.95},
                weight=1.0,
                required=True,
            ),
            ValidationRule(
                name="기능 완성도 검증",
                validation_type=ValidationType.FUNCTIONAL,
                description="모든 필수 기능이 구현되었는지 검증",
                criteria={"feature_completeness": 0.9, "implementation_rate": 0.95},
                weight=1.0,
                required=True,
            ),
            ValidationRule(
                name="오류 처리 검증",
                validation_type=ValidationType.FUNCTIONAL,
                description="오류 상황에 대한 적절한 처리가 이루어지는지 검증",
                criteria={"error_handling_rate": 0.9, "recovery_success_rate": 0.8},
                weight=0.8,
                required=True,
            ),
        ]

        # 성능 검증 규칙
        performance_rules = [
            ValidationRule(
                name="응답 시간 검증",
                validation_type=ValidationType.PERFORMANCE,
                description="시스템의 응답 시간이 기준을 만족하는지 검증",
                criteria={"max_response_time": 0.05, "avg_response_time": 0.03},
                weight=1.0,
                required=True,
            ),
            ValidationRule(
                name="처리량 검증",
                validation_type=ValidationType.PERFORMANCE,
                description="시스템의 처리량이 기준을 만족하는지 검증",
                criteria={"min_throughput": 1000, "target_throughput": 2000},
                weight=1.0,
                required=True,
            ),
            ValidationRule(
                name="리소스 사용량 검증",
                validation_type=ValidationType.PERFORMANCE,
                description="시스템의 리소스 사용량이 적절한지 검증",
                criteria={"max_memory_usage": 0.8, "max_cpu_usage": 0.7},
                weight=0.8,
                required=False,
            ),
        ]

        # 보안 검증 규칙
        security_rules = [
            ValidationRule(
                name="인증 검증",
                validation_type=ValidationType.SECURITY,
                description="시스템의 인증 메커니즘이 적절한지 검증",
                criteria={
                    "authentication_strength": 0.8,
                    "authentication_success_rate": 0.95,
                },
                weight=1.0,
                required=True,
            ),
            ValidationRule(
                name="권한 검증",
                validation_type=ValidationType.SECURITY,
                description="시스템의 권한 관리가 적절한지 검증",
                criteria={"authorization_accuracy": 0.9, "permission_check_rate": 1.0},
                weight=1.0,
                required=True,
            ),
            ValidationRule(
                name="데이터 보안 검증",
                validation_type=ValidationType.SECURITY,
                description="시스템의 데이터 보안이 적절한지 검증",
                criteria={"data_encryption_rate": 0.9, "data_integrity_rate": 0.95},
                weight=0.9,
                required=True,
            ),
        ]

        # 호환성 검증 규칙
        compatibility_rules = [
            ValidationRule(
                name="시스템 호환성 검증",
                validation_type=ValidationType.COMPATIBILITY,
                description="시스템 간 호환성이 적절한지 검증",
                criteria={"compatibility_score": 0.9, "integration_success_rate": 0.95},
                weight=1.0,
                required=True,
            ),
            ValidationRule(
                name="버전 호환성 검증",
                validation_type=ValidationType.COMPATIBILITY,
                description="버전 간 호환성이 적절한지 검증",
                criteria={"version_compatibility": 0.9, "backward_compatibility": 0.8},
                weight=0.8,
                required=False,
            ),
        ]

        # 통합 검증 규칙
        integration_rules = [
            ValidationRule(
                name="시스템 통합 검증",
                validation_type=ValidationType.INTEGRATION,
                description="시스템 통합이 적절한지 검증",
                criteria={
                    "integration_success_rate": 0.95,
                    "system_interaction_rate": 0.9,
                },
                weight=1.0,
                required=True,
            ),
            ValidationRule(
                name="데이터 흐름 검증",
                validation_type=ValidationType.INTEGRATION,
                description="시스템 간 데이터 흐름이 적절한지 검증",
                criteria={"data_flow_success_rate": 0.95, "data_consistency_rate": 0.9},
                weight=1.0,
                required=True,
            ),
        ]

        # 모든 규칙 등록
        all_rules = functional_rules + performance_rules + security_rules + compatibility_rules + integration_rules
        for rule in all_rules:
            self.validation_rules[rule.name] = rule

    async def validate_system(self, system_name: str, validation_data: Dict[str, Any]) -> SystemValidation:
        """
        시스템 검증 수행

        Args:
            system_name: 시스템 이름
            validation_data: 검증 데이터

        Returns:
            SystemValidation: 시스템 검증 결과
        """
        start_time = time.time()

        try:
            logger.info(f"시작: 시스템 검증 - {system_name}")

            # 검증 규칙 선택
            validation_types = validation_data.get("validation_types", [ValidationType.FUNCTIONAL])
            selected_rules = []

            for rule in self.validation_rules.values():
                if rule.validation_type in validation_types:
                    selected_rules.append(rule)

            # 검증 실행
            validation_results = await self._execute_validations(selected_rules, validation_data)

            # 전체 점수 계산
            overall_score = await self._calculate_overall_score(validation_results)

            # 품질 수준 결정
            quality_level = await self._determine_quality_level(overall_score)

            validation_time = time.time() - start_time

            validation = SystemValidation(
                system_name=system_name,
                validation_type=ValidationType.INTEGRATION,
                validation_results=validation_results,
                overall_score=overall_score,
                quality_level=quality_level,
                validation_time=validation_time,
            )

            self.system_validations.append(validation)
            logger.info(f"시스템 검증 완료: {system_name} - 점수 {overall_score:.2f}, 품질 {quality_level.value}")

            return validation

        except Exception as e:
            error_msg = f"시스템 검증 실패 {system_name}: {str(e)}"
            logger.error(error_msg)
            return SystemValidation(
                system_name=system_name,
                validation_type=ValidationType.INTEGRATION,
                validation_results=[],
                overall_score=0.0,
                quality_level=QualityLevel.CRITICAL,
                validation_time=time.time() - start_time,
            )

    async def _execute_validations(
        self, rules: List[ValidationRule], validation_data: Dict[str, Any]
    ) -> List[ValidationResult]:
        """검증 실행"""
        validation_results = []

        for rule in rules:
            try:
                result = await self._execute_single_validation(rule, validation_data)
                validation_results.append(result)
            except Exception as e:
                error_msg = f"검증 실행 실패 {rule.name}: {str(e)}"
                logger.error(error_msg)

                error_result = ValidationResult(
                    rule=rule,
                    status=ValidationStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration=0.0,
                    score=0.0,
                    errors=[error_msg],
                )
                validation_results.append(error_result)

        return validation_results

    async def _execute_single_validation(
        self, rule: ValidationRule, validation_data: Dict[str, Any]
    ) -> ValidationResult:
        """단일 검증 실행"""
        start_time = datetime.now()
        result = ValidationResult(rule=rule, status=ValidationStatus.RUNNING, start_time=start_time)

        try:
            logger.info(f"검증 실행: {rule.name}")

            # 검증 타입에 따른 실행
            if rule.validation_type == ValidationType.FUNCTIONAL:
                details = await self._execute_functional_validation(rule, validation_data)
            elif rule.validation_type == ValidationType.PERFORMANCE:
                details = await self._execute_performance_validation(rule, validation_data)
            elif rule.validation_type == ValidationType.SECURITY:
                details = await self._execute_security_validation(rule, validation_data)
            elif rule.validation_type == ValidationType.COMPATIBILITY:
                details = await self._execute_compatibility_validation(rule, validation_data)
            elif rule.validation_type == ValidationType.INTEGRATION:
                details = await self._execute_integration_validation(rule, validation_data)
            else:
                details = await self._execute_general_validation(rule, validation_data)

            # 결과 검증
            score = await self._calculate_validation_score(rule, details)
            status = await self._determine_validation_status(rule, score)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            result.status = status
            result.end_time = end_time
            result.duration = duration
            result.score = score
            result.details = details

            if status == ValidationStatus.FAILED:
                result.errors.append(f"검증 실패: 점수 {score:.2f} (기준: {rule.criteria})")
            elif status == ValidationStatus.WARNING:
                result.warnings.append(f"검증 경고: 점수 {score:.2f} (기준: {rule.criteria})")

            logger.info(f"검증 완료: {rule.name} - {status.value} (점수: {score:.2f})")

        except Exception as e:
            error_msg = f"검증 실행 중 오류: {str(e)}"
            logger.error(error_msg)
            result.status = ValidationStatus.FAILED
            result.end_time = datetime.now()
            result.duration = (result.end_time - start_time).total_seconds()
            result.score = 0.0
            result.errors.append(error_msg)

        return result

    async def _execute_functional_validation(
        self, rule: ValidationRule, validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """기능적 검증 실행"""
        if "시스템 응답성" in rule.name:
            response_time = await self._measure_response_time()
            success_rate = await self._measure_success_rate()
            return {"response_time": response_time, "success_rate": success_rate}

        elif "기능 완성도" in rule.name:
            feature_completeness = await self._measure_feature_completeness()
            implementation_rate = await self._measure_implementation_rate()
            return {
                "feature_completeness": feature_completeness,
                "implementation_rate": implementation_rate,
            }

        elif "오류 처리" in rule.name:
            error_handling_rate = await self._measure_error_handling_rate()
            recovery_success_rate = await self._measure_recovery_success_rate()
            return {
                "error_handling_rate": error_handling_rate,
                "recovery_success_rate": recovery_success_rate,
            }

        else:
            return {"error": "알 수 없는 기능적 검증"}

    async def _execute_performance_validation(
        self, rule: ValidationRule, validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """성능 검증 실행"""
        if "응답 시간" in rule.name:
            max_response_time = await self._measure_max_response_time()
            avg_response_time = await self._measure_avg_response_time()
            return {
                "max_response_time": max_response_time,
                "avg_response_time": avg_response_time,
            }

        elif "처리량" in rule.name:
            min_throughput = await self._measure_min_throughput()
            target_throughput = await self._measure_target_throughput()
            return {
                "min_throughput": min_throughput,
                "target_throughput": target_throughput,
            }

        elif "리소스 사용량" in rule.name:
            max_memory_usage = await self._measure_max_memory_usage()
            max_cpu_usage = await self._measure_max_cpu_usage()
            return {
                "max_memory_usage": max_memory_usage,
                "max_cpu_usage": max_cpu_usage,
            }

        else:
            return {"error": "알 수 없는 성능 검증"}

    async def _execute_security_validation(
        self, rule: ValidationRule, validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """보안 검증 실행"""
        if "인증" in rule.name:
            authentication_strength = await self._measure_authentication_strength()
            authentication_success_rate = await self._measure_authentication_success_rate()
            return {
                "authentication_strength": authentication_strength,
                "authentication_success_rate": authentication_success_rate,
            }

        elif "권한" in rule.name:
            authorization_accuracy = await self._measure_authorization_accuracy()
            permission_check_rate = await self._measure_permission_check_rate()
            return {
                "authorization_accuracy": authorization_accuracy,
                "permission_check_rate": permission_check_rate,
            }

        elif "데이터 보안" in rule.name:
            data_encryption_rate = await self._measure_data_encryption_rate()
            data_integrity_rate = await self._measure_data_integrity_rate()
            return {
                "data_encryption_rate": data_encryption_rate,
                "data_integrity_rate": data_integrity_rate,
            }

        else:
            return {"error": "알 수 없는 보안 검증"}

    async def _execute_compatibility_validation(
        self, rule: ValidationRule, validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """호환성 검증 실행"""
        if "시스템 호환성" in rule.name:
            compatibility_score = await self._measure_compatibility_score()
            integration_success_rate = await self._measure_integration_success_rate()
            return {
                "compatibility_score": compatibility_score,
                "integration_success_rate": integration_success_rate,
            }

        elif "버전 호환성" in rule.name:
            version_compatibility = await self._measure_version_compatibility()
            backward_compatibility = await self._measure_backward_compatibility()
            return {
                "version_compatibility": version_compatibility,
                "backward_compatibility": backward_compatibility,
            }

        else:
            return {"error": "알 수 없는 호환성 검증"}

    async def _execute_integration_validation(
        self, rule: ValidationRule, validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통합 검증 실행"""
        if "시스템 통합" in rule.name:
            integration_success_rate = await self._measure_integration_success_rate()
            system_interaction_rate = await self._measure_system_interaction_rate()
            return {
                "integration_success_rate": integration_success_rate,
                "system_interaction_rate": system_interaction_rate,
            }

        elif "데이터 흐름" in rule.name:
            data_flow_success_rate = await self._measure_data_flow_success_rate()
            data_consistency_rate = await self._measure_data_consistency_rate()
            return {
                "data_flow_success_rate": data_flow_success_rate,
                "data_consistency_rate": data_consistency_rate,
            }

        else:
            return {"error": "알 수 없는 통합 검증"}

    async def _execute_general_validation(
        self, rule: ValidationRule, validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """일반 검증 실행"""
        # 기본 검증 (시뮬레이션)
        await asyncio.sleep(0.1)
        return {"general_validation": True, "score": 0.8}

    async def _calculate_validation_score(self, rule: ValidationRule, details: Dict[str, Any]) -> float:
        """검증 점수 계산"""
        if "error" in details:
            return 0.0

        score = 0.0
        total_weight = 0.0

        for key, expected_value in rule.criteria.items():
            if key in details:
                actual_value = details[key]

                # 수치 비교
                if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                    if key in [
                        "response_time",
                        "max_response_time",
                        "avg_response_time",
                        "max_memory_usage",
                        "max_cpu_usage",
                    ]:
                        # 낮을수록 좋은 지표
                        if actual_value <= expected_value:
                            score += 1.0
                        else:
                            score += max(
                                0.0,
                                1.0 - (actual_value - expected_value) / expected_value,
                            )
                    elif key in [
                        "success_rate",
                        "feature_completeness",
                        "implementation_rate",
                        "error_handling_rate",
                        "recovery_success_rate",
                        "min_throughput",
                        "target_throughput",
                        "authentication_strength",
                        "authentication_success_rate",
                        "authorization_accuracy",
                        "permission_check_rate",
                        "data_encryption_rate",
                        "data_integrity_rate",
                        "compatibility_score",
                        "integration_success_rate",
                        "version_compatibility",
                        "backward_compatibility",
                        "system_interaction_rate",
                        "data_flow_success_rate",
                        "data_consistency_rate",
                    ]:
                        # 높을수록 좋은 지표
                        if actual_value >= expected_value:
                            score += 1.0
                        else:
                            score += max(0.0, actual_value / expected_value)
                    else:
                        # 기타 비교
                        if actual_value == expected_value:
                            score += 1.0
                        else:
                            score += 0.5
                else:
                    # 기타 비교
                    if actual_value == expected_value:
                        score += 1.0
                    else:
                        score += 0.5

                total_weight += 1.0

        return score / total_weight if total_weight > 0 else 0.0

    async def _determine_validation_status(self, rule: ValidationRule, score: float) -> ValidationStatus:
        """검증 상태 결정"""
        if score >= 0.9:
            return ValidationStatus.PASSED
        elif score >= 0.7:
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.FAILED

    async def _calculate_overall_score(self, validation_results: List[ValidationResult]) -> float:
        """전체 점수 계산"""
        if not validation_results:
            return 0.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for result in validation_results:
            weight = result.rule.weight
            total_weighted_score += result.score * weight
            total_weight += weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    async def _determine_quality_level(self, score: float) -> QualityLevel:
        """품질 수준 결정"""
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.8:
            return QualityLevel.GOOD
        elif score >= 0.7:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.5:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL

    # 측정 메서드들 (시뮬레이션)
    async def _measure_response_time(self) -> float:
        return 0.03

    async def _measure_success_rate(self) -> float:
        return 0.95

    async def _measure_feature_completeness(self) -> float:
        return 0.92

    async def _measure_implementation_rate(self) -> float:
        return 0.95

    async def _measure_error_handling_rate(self) -> float:
        return 0.90

    async def _measure_recovery_success_rate(self) -> float:
        return 0.85

    async def _measure_max_response_time(self) -> float:
        return 0.04

    async def _measure_avg_response_time(self) -> float:
        return 0.025

    async def _measure_min_throughput(self) -> float:
        return 1200

    async def _measure_target_throughput(self) -> float:
        return 2200

    async def _measure_max_memory_usage(self) -> float:
        return 0.75

    async def _measure_max_cpu_usage(self) -> float:
        return 0.65

    async def _measure_authentication_strength(self) -> float:
        return 0.85

    async def _measure_authentication_success_rate(self) -> float:
        return 0.95

    async def _measure_authorization_accuracy(self) -> float:
        return 0.92

    async def _measure_permission_check_rate(self) -> float:
        return 1.0

    async def _measure_data_encryption_rate(self) -> float:
        return 0.90

    async def _measure_data_integrity_rate(self) -> float:
        return 0.95

    async def _measure_compatibility_score(self) -> float:
        return 0.88

    async def _measure_integration_success_rate(self) -> float:
        return 0.93

    async def _measure_version_compatibility(self) -> float:
        return 0.85

    async def _measure_backward_compatibility(self) -> float:
        return 0.80

    async def _measure_system_interaction_rate(self) -> float:
        return 0.90

    async def _measure_data_flow_success_rate(self) -> float:
        return 0.94

    async def _measure_data_consistency_rate(self) -> float:
        return 0.91

    async def generate_quality_report(self, validation_data: Dict[str, Any]) -> QualityReport:
        """
        품질 보고서 생성

        Args:
            validation_data: 검증 데이터

        Returns:
            QualityReport: 품질 보고서
        """
        try:
            logger.info("시작: 품질 보고서 생성")

            # 최근 검증 결과 수집
            recent_validations = self.system_validations[-10:] if self.system_validations else []

            if not recent_validations:
                return QualityReport(
                    timestamp=datetime.now(),
                    overall_quality=QualityLevel.CRITICAL,
                    quality_score=0.0,
                    validation_results=[],
                    summary={},
                    recommendations=["검증 데이터가 없습니다."],
                )

            # 전체 품질 점수 계산
            total_score = sum(v.overall_score for v in recent_validations)
            average_score = total_score / len(recent_validations)

            # 전체 품질 수준 결정
            overall_quality = await self._determine_quality_level(average_score)

            # 검증 결과 수집
            all_validation_results = []
            for validation in recent_validations:
                all_validation_results.extend(validation.validation_results)

            # 요약 생성
            summary = await self._generate_quality_summary(recent_validations, all_validation_results)

            # 권장사항 생성
            recommendations = await self._generate_quality_recommendations(recent_validations, all_validation_results)

            report = QualityReport(
                timestamp=datetime.now(),
                overall_quality=overall_quality,
                quality_score=average_score,
                validation_results=all_validation_results,
                summary=summary,
                recommendations=recommendations,
            )

            self.quality_reports.append(report)
            logger.info(f"품질 보고서 생성 완료: 전체 품질 {overall_quality.value}, 점수 {average_score:.2f}")

            return report

        except Exception as e:
            error_msg = f"품질 보고서 생성 실패: {str(e)}"
            logger.error(error_msg)
            return QualityReport(
                timestamp=datetime.now(),
                overall_quality=QualityLevel.CRITICAL,
                quality_score=0.0,
                validation_results=[],
                summary={"error": error_msg},
                recommendations=[error_msg],
            )

    async def _generate_quality_summary(
        self,
        validations: List[SystemValidation],
        validation_results: List[ValidationResult],
    ) -> Dict[str, Any]:
        """품질 요약 생성"""
        summary = {
            "total_validations": len(validations),
            "total_validation_results": len(validation_results),
            "quality_distribution": {},
            "validation_type_distribution": {},
            "system_performance": {},
        }

        # 품질 수준별 분포
        quality_counts = {}
        for validation in validations:
            quality = validation.quality_level.value
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        summary["quality_distribution"] = quality_counts

        # 검증 타입별 분포
        type_counts = {}
        for result in validation_results:
            validation_type = result.rule.validation_type.value
            type_counts[validation_type] = type_counts.get(validation_type, 0) + 1

        summary["validation_type_distribution"] = type_counts

        # 시스템별 성능
        for validation in validations:
            summary["system_performance"][validation.system_name] = {
                "score": validation.overall_score,
                "quality_level": validation.quality_level.value,
                "validation_time": validation.validation_time,
            }

        return summary

    async def _generate_quality_recommendations(
        self,
        validations: List[SystemValidation],
        validation_results: List[ValidationResult],
    ) -> List[str]:
        """품질 권장사항 생성"""
        recommendations = []

        # 전체 품질 기반 권장사항
        avg_score = sum(v.overall_score for v in validations) / len(validations) if validations else 0.0
        if avg_score < 0.8:
            recommendations.append("전체 시스템 품질이 낮습니다. 종합적인 개선이 필요합니다.")

        # 실패한 검증 기반 권장사항
        failed_results = [r for r in validation_results if r.status == ValidationStatus.FAILED]
        if failed_results:
            failed_types = {}
            for result in failed_results:
                validation_type = result.rule.validation_type.value
                failed_types[validation_type] = failed_types.get(validation_type, 0) + 1

            most_failed_type = max(failed_types.items(), key=lambda x: x[1])[0]
            recommendations.append(f"{most_failed_type} 검증 실패율이 높습니다. 해당 영역 개선이 필요합니다.")

        # 경고 검증 기반 권장사항
        warning_results = [r for r in validation_results if r.status == ValidationStatus.WARNING]
        if warning_results:
            recommendations.append("일부 검증에서 경고가 발생했습니다. 해당 영역 모니터링이 필요합니다.")

        # 시스템별 권장사항
        for validation in validations:
            if validation.overall_score < 0.7:
                recommendations.append(f"{validation.system_name} 시스템의 품질이 낮습니다. 개선이 필요합니다.")

        return recommendations

    async def start(self):
        """엔진 시작"""
        if not self.is_running:
            self.is_running = True
            self.start_time = datetime.now()
            logger.info("시스템 검증 엔진 시작")

    async def stop(self):
        """엔진 중지"""
        if self.is_running:
            self.is_running = False
            logger.info("시스템 검증 엔진 중지")

    def get_status(self) -> Dict[str, Any]:
        """엔진 상태 조회"""
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "validation_rules_count": len(self.validation_rules),
            "validation_results_count": len(self.validation_results),
            "quality_reports_count": len(self.quality_reports),
            "system_validations_count": len(self.system_validations),
        }


async def main():
    """메인 함수"""
    # 시스템 검증 엔진 생성
    validation_engine = SystemValidationEngine()

    # 엔진 시작
    await validation_engine.start()

    try:
        # 시스템 검증
        system_validation = await validation_engine.validate_system(
            "test_system",
            {
                "validation_types": [
                    ValidationType.FUNCTIONAL,
                    ValidationType.PERFORMANCE,
                ]
            },
        )
        print(
            f"시스템 검증 결과: 점수 {system_validation.overall_score:.2f}, 품질 {system_validation.quality_level.value}"  # noqa: E501
        )

        # 품질 보고서 생성
        quality_report = await validation_engine.generate_quality_report({})
        print(f"품질 보고서: 전체 품질 {quality_report.overall_quality.value}, 점수 {quality_report.quality_score:.2f}")

        # 엔진 상태 출력
        status = validation_engine.get_status()
        print(f"엔진 상태: {status}")

    except Exception as e:
        logger.error(f"메인 실행 중 오류: {str(e)}")
        traceback.print_exc()

    finally:
        # 엔진 중지
        await validation_engine.stop()


if __name__ == "__main__":
    asyncio.run(main())
