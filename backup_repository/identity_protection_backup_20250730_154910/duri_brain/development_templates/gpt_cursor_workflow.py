#!/usr/bin/env python3
"""
GPT/Cursor Workflow System - Phase 12+
GPT/커서 주도 실행-수정 루프 시스템

목적:
- GPT가 먼저 구조 제안 → 인간이 선택/수정
- 디버깅 로그 기반 리팩토링 추천 루틴
- 구조화된 개발 워크플로우
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStage(Enum):
    """워크플로우 단계"""
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    REVIEW = "review"
    REFACTORING = "refactoring"
    DEPLOYMENT = "deployment"

class RefactoringType(Enum):
    """리팩토링 유형"""
    CODE_STRUCTURE = "code_structure"
    PERFORMANCE = "performance"
    READABILITY = "readability"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"

@dataclass
class GPTRecommendation:
    """GPT 추천사항"""
    id: str
    stage: WorkflowStage
    recommendation_type: str
    description: str
    code_suggestion: str
    reasoning: str
    priority: str
    estimated_effort: str
    timestamp: datetime

@dataclass
class CodeAnalysis:
    """코드 분석"""
    id: str
    file_path: str
    analysis_type: str
    issues_found: List[str]
    suggestions: List[str]
    complexity_score: float
    maintainability_score: float
    performance_score: float
    timestamp: datetime

@dataclass
class RefactoringTask:
    """리팩토링 작업"""
    id: str
    refactoring_type: RefactoringType
    target_file: str
    current_issues: List[str]
    proposed_solutions: List[str]
    estimated_impact: str
    priority: str
    status: str  # "pending", "in_progress", "completed", "cancelled"
    timestamp: datetime

class GPTCursorWorkflow:
    """GPT/커서 주도 워크플로우 시스템"""
    
    def __init__(self):
        self.recommendations: List[GPTRecommendation] = []
        self.code_analyses: List[CodeAnalysis] = []
        self.refactoring_tasks: List[RefactoringTask] = []
        self.workflow_history: List[Dict[str, Any]] = []
        
        logger.info("GPTCursorWorkflow 초기화 완료")
    
    def generate_gpt_recommendation(self, stage: WorkflowStage, context: Dict[str, Any]) -> GPTRecommendation:
        """GPT 추천사항 생성"""
        recommendation_id = f"gpt_recommendation_{len(self.recommendations) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 단계별 추천사항 템플릿
        stage_recommendations = {
            WorkflowStage.DESIGN: {
                "recommendation_type": "architecture_design",
                "description": "시스템 아키텍처 설계 제안",
                "code_suggestion": "# 시스템 설계 템플릿\nclass SystemDesign:\n    def __init__(self):\n        pass",
                "reasoning": "확장 가능하고 유지보수하기 쉬운 구조가 필요합니다.",
                "priority": "high",
                "estimated_effort": "2-3시간"
            },
            WorkflowStage.IMPLEMENTATION: {
                "recommendation_type": "implementation_pattern",
                "description": "구현 패턴 및 모범 사례 제안",
                "code_suggestion": "# 구현 패턴\nclass ImplementationPattern:\n    def __init__(self):\n        self.logger = logging.getLogger(__name__)",
                "reasoning": "일관된 코딩 스타일과 로깅이 필요합니다.",
                "priority": "medium",
                "estimated_effort": "1-2시간"
            },
            WorkflowStage.TESTING: {
                "recommendation_type": "test_strategy",
                "description": "테스트 전략 및 테스트 케이스 제안",
                "code_suggestion": "# 테스트 전략\n@pytest.fixture\ndef test_system():\n    return TestSystem()",
                "reasoning": "포괄적인 테스트 커버리지가 필요합니다.",
                "priority": "high",
                "estimated_effort": "2-4시간"
            },
            WorkflowStage.REVIEW: {
                "recommendation_type": "code_review",
                "description": "코드 리뷰 및 개선 제안",
                "code_suggestion": "# 코드 개선\n# TODO: 성능 최적화 필요\n# TODO: 에러 처리 강화 필요",
                "reasoning": "코드 품질과 성능 개선이 필요합니다.",
                "priority": "medium",
                "estimated_effort": "1-3시간"
            },
            WorkflowStage.REFACTORING: {
                "recommendation_type": "refactoring_plan",
                "description": "리팩토링 계획 및 실행 제안",
                "code_suggestion": "# 리팩토링 계획\n# 1. 메서드 분리\n# 2. 클래스 추출\n# 3. 중복 제거",
                "reasoning": "코드 중복과 복잡성을 줄여야 합니다.",
                "priority": "high",
                "estimated_effort": "3-5시간"
            },
            WorkflowStage.DEPLOYMENT: {
                "recommendation_type": "deployment_strategy",
                "description": "배포 전략 및 환경 설정 제안",
                "code_suggestion": "# 배포 설정\nDEPLOYMENT_CONFIG = {\n    'environment': 'production',\n    'version': '1.0.0'\n}",
                "reasoning": "안정적인 배포와 모니터링이 필요합니다.",
                "priority": "critical",
                "estimated_effort": "4-6시간"
            }
        }
        
        template = stage_recommendations.get(stage, {})
        
        recommendation = GPTRecommendation(
            id=recommendation_id,
            stage=stage,
            recommendation_type=template.get("recommendation_type", "general"),
            description=template.get("description", "일반적인 추천사항"),
            code_suggestion=template.get("code_suggestion", "# 기본 코드 템플릿"),
            reasoning=template.get("reasoning", "일반적인 개선이 필요합니다."),
            priority=template.get("priority", "medium"),
            estimated_effort=template.get("estimated_effort", "1-2시간"),
            timestamp=datetime.now()
        )
        
        self.recommendations.append(recommendation)
        logger.info(f"GPT 추천사항 생성: {recommendation_id}")
        
        return recommendation
    
    def analyze_code_quality(self, file_path: str, code_content: str) -> CodeAnalysis:
        """코드 품질 분석"""
        analysis_id = f"code_analysis_{len(self.code_analyses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 코드 분석 수행
        issues_found = self._identify_code_issues(code_content)
        suggestions = self._generate_code_suggestions(issues_found)
        complexity_score = self._calculate_complexity_score(code_content)
        maintainability_score = self._calculate_maintainability_score(code_content)
        performance_score = self._calculate_performance_score(code_content)
        
        analysis = CodeAnalysis(
            id=analysis_id,
            file_path=file_path,
            analysis_type="quality_assessment",
            issues_found=issues_found,
            suggestions=suggestions,
            complexity_score=complexity_score,
            maintainability_score=maintainability_score,
            performance_score=performance_score,
            timestamp=datetime.now()
        )
        
        self.code_analyses.append(analysis)
        logger.info(f"코드 품질 분석 완료: {analysis_id}")
        
        return analysis
    
    def _identify_code_issues(self, code_content: str) -> List[str]:
        """코드 이슈 식별"""
        issues = []
        
        # 긴 함수 체크
        if len(code_content.split('\n')) > 50:
            issues.append("함수가 너무 깁니다. 분리가 필요합니다.")
        
        # 중복 코드 체크
        if code_content.count('def ') > 10:
            issues.append("중복된 함수가 있을 수 있습니다.")
        
        # 예외 처리 체크
        if 'try:' not in code_content and 'except' not in code_content:
            issues.append("예외 처리가 부족합니다.")
        
        # 로깅 체크
        if 'logging' not in code_content and 'print(' in code_content:
            issues.append("print 대신 logging을 사용하는 것이 좋습니다.")
        
        # 타입 힌트 체크
        if 'typing' not in code_content and 'def ' in code_content:
            issues.append("타입 힌트를 추가하는 것이 좋습니다.")
        
        return issues if issues else ["특별한 이슈가 발견되지 않았습니다."]
    
    def _generate_code_suggestions(self, issues: List[str]) -> List[str]:
        """코드 개선 제안 생성"""
        suggestions = []
        
        for issue in issues:
            if "함수가 너무 깁니다" in issue:
                suggestions.append("함수를 더 작은 단위로 분리하세요.")
            elif "중복된 함수" in issue:
                suggestions.append("공통 기능을 별도 함수로 추출하세요.")
            elif "예외 처리가 부족" in issue:
                suggestions.append("try-except 블록을 추가하여 예외를 처리하세요.")
            elif "print 대신 logging" in issue:
                suggestions.append("logging 모듈을 사용하여 로그를 관리하세요.")
            elif "타입 힌트" in issue:
                suggestions.append("함수 매개변수와 반환값에 타입 힌트를 추가하세요.")
        
        return suggestions if suggestions else ["코드가 전반적으로 양호합니다."]
    
    def _calculate_complexity_score(self, code_content: str) -> float:
        """복잡도 점수 계산"""
        base_score = 0.5
        
        # 함수 개수에 따른 복잡도
        function_count = code_content.count('def ')
        if function_count > 10:
            base_score += 0.3
        elif function_count > 5:
            base_score += 0.2
        else:
            base_score += 0.1
        
        # 중첩 레벨에 따른 복잡도
        nested_levels = max([len(line) - len(line.lstrip()) for line in code_content.split('\n') if line.strip()])
        if nested_levels > 8:
            base_score += 0.3
        elif nested_levels > 4:
            base_score += 0.2
        else:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _calculate_maintainability_score(self, code_content: str) -> float:
        """유지보수성 점수 계산"""
        base_score = 0.7
        
        # 주석 비율
        comment_lines = len([line for line in code_content.split('\n') if line.strip().startswith('#')])
        total_lines = len([line for line in code_content.split('\n') if line.strip()])
        
        if total_lines > 0:
            comment_ratio = comment_lines / total_lines
            if comment_ratio > 0.2:
                base_score += 0.2
            elif comment_ratio > 0.1:
                base_score += 0.1
        
        # 함수 길이
        if len(code_content.split('\n')) < 30:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _calculate_performance_score(self, code_content: str) -> float:
        """성능 점수 계산"""
        base_score = 0.8
        
        # 비효율적인 패턴 체크
        if 'for ' in code_content and ' in ' in code_content:
            base_score += 0.1
        
        if 'list(' in code_content and 'map(' in code_content:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def create_refactoring_task(self, analysis: CodeAnalysis, refactoring_type: RefactoringType) -> RefactoringTask:
        """리팩토링 작업 생성"""
        task_id = f"refactoring_task_{len(self.refactoring_tasks) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 리팩토링 유형별 해결책
        solutions_map = {
            RefactoringType.CODE_STRUCTURE: [
                "함수 분리 및 모듈화",
                "클래스 구조 개선",
                "코드 중복 제거"
            ],
            RefactoringType.PERFORMANCE: [
                "알고리즘 최적화",
                "메모리 사용량 개선",
                "캐싱 전략 적용"
            ],
            RefactoringType.READABILITY: [
                "변수명 및 함수명 개선",
                "주석 추가 및 개선",
                "코드 포맷팅 개선"
            ],
            RefactoringType.MAINTAINABILITY: [
                "의존성 분리",
                "설정 외부화",
                "테스트 코드 추가"
            ],
            RefactoringType.SECURITY: [
                "입력 검증 강화",
                "보안 취약점 수정",
                "권한 검사 추가"
            ]
        }
        
        proposed_solutions = solutions_map.get(refactoring_type, ["일반적인 개선"])
        
        # 영향도 평가
        impact_levels = {
            RefactoringType.CODE_STRUCTURE: "중간",
            RefactoringType.PERFORMANCE: "높음",
            RefactoringType.READABILITY: "낮음",
            RefactoringType.MAINTAINABILITY: "중간",
            RefactoringType.SECURITY: "높음"
        }
        
        estimated_impact = impact_levels.get(refactoring_type, "중간")
        
        # 우선순위 결정
        priority_levels = {
            RefactoringType.SECURITY: "critical",
            RefactoringType.PERFORMANCE: "high",
            RefactoringType.CODE_STRUCTURE: "medium",
            RefactoringType.MAINTAINABILITY: "medium",
            RefactoringType.READABILITY: "low"
        }
        
        priority = priority_levels.get(refactoring_type, "medium")
        
        task = RefactoringTask(
            id=task_id,
            refactoring_type=refactoring_type,
            target_file=analysis.file_path,
            current_issues=analysis.issues_found,
            proposed_solutions=proposed_solutions,
            estimated_impact=estimated_impact,
            priority=priority,
            status="pending",
            timestamp=datetime.now()
        )
        
        self.refactoring_tasks.append(task)
        logger.info(f"리팩토링 작업 생성: {task_id}")
        
        return task
    
    def execute_workflow_stage(self, stage: WorkflowStage, context: Dict[str, Any]) -> Dict[str, Any]:
        """워크플로우 단계 실행"""
        stage_id = f"workflow_stage_{stage.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # GPT 추천사항 생성
        recommendation = self.generate_gpt_recommendation(stage, context)
        
        # 단계별 특별 처리
        stage_results = {
            WorkflowStage.DESIGN: self._execute_design_stage,
            WorkflowStage.IMPLEMENTATION: self._execute_implementation_stage,
            WorkflowStage.TESTING: self._execute_testing_stage,
            WorkflowStage.REVIEW: self._execute_review_stage,
            WorkflowStage.REFACTORING: self._execute_refactoring_stage,
            WorkflowStage.DEPLOYMENT: self._execute_deployment_stage
        }
        
        stage_executor = stage_results.get(stage, self._execute_general_stage)
        stage_result = stage_executor(context, recommendation)
        
        # 워크플로우 히스토리 기록
        workflow_entry = {
            "stage_id": stage_id,
            "stage": stage.value,
            "recommendation": asdict(recommendation),
            "result": stage_result,
            "timestamp": datetime.now().isoformat()
        }
        
        self.workflow_history.append(workflow_entry)
        
        logger.info(f"워크플로우 단계 실행 완료: {stage.value}")
        
        return {
            "stage": stage.value,
            "recommendation": asdict(recommendation),
            "result": stage_result,
            "workflow_entry": workflow_entry
        }
    
    def _execute_design_stage(self, context: Dict[str, Any], recommendation: GPTRecommendation) -> Dict[str, Any]:
        """설계 단계 실행"""
        return {
            "status": "completed",
            "design_artifacts": ["시스템 아키텍처", "클래스 다이어그램", "데이터 흐름"],
            "next_steps": ["구현 계획 수립", "기술 스택 선택", "프로토타입 개발"]
        }
    
    def _execute_implementation_stage(self, context: Dict[str, Any], recommendation: GPTRecommendation) -> Dict[str, Any]:
        """구현 단계 실행"""
        return {
            "status": "completed",
            "implementation_artifacts": ["코드 구현", "단위 테스트", "문서화"],
            "next_steps": ["코드 리뷰", "통합 테스트", "성능 테스트"]
        }
    
    def _execute_testing_stage(self, context: Dict[str, Any], recommendation: GPTRecommendation) -> Dict[str, Any]:
        """테스트 단계 실행"""
        return {
            "status": "completed",
            "testing_artifacts": ["테스트 케이스", "테스트 결과", "버그 리포트"],
            "next_steps": ["버그 수정", "테스트 커버리지 개선", "성능 최적화"]
        }
    
    def _execute_review_stage(self, context: Dict[str, Any], recommendation: GPTRecommendation) -> Dict[str, Any]:
        """리뷰 단계 실행"""
        return {
            "status": "completed",
            "review_artifacts": ["코드 리뷰 결과", "개선 제안", "품질 메트릭"],
            "next_steps": ["리팩토링", "문서 업데이트", "팀 피드백"]
        }
    
    def _execute_refactoring_stage(self, context: Dict[str, Any], recommendation: GPTRecommendation) -> Dict[str, Any]:
        """리팩토링 단계 실행"""
        return {
            "status": "completed",
            "refactoring_artifacts": ["리팩토링 계획", "코드 변경사항", "성능 개선"],
            "next_steps": ["리팩토링 검증", "테스트 재실행", "문서 업데이트"]
        }
    
    def _execute_deployment_stage(self, context: Dict[str, Any], recommendation: GPTRecommendation) -> Dict[str, Any]:
        """배포 단계 실행"""
        return {
            "status": "completed",
            "deployment_artifacts": ["배포 스크립트", "환경 설정", "모니터링 도구"],
            "next_steps": ["배포 검증", "성능 모니터링", "사용자 피드백"]
        }
    
    def _execute_general_stage(self, context: Dict[str, Any], recommendation: GPTRecommendation) -> Dict[str, Any]:
        """일반 단계 실행"""
        return {
            "status": "completed",
            "artifacts": ["일반 작업 결과"],
            "next_steps": ["다음 단계 진행"]
        }
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """워크플로우 통계 제공"""
        total_recommendations = len(self.recommendations)
        total_analyses = len(self.code_analyses)
        total_tasks = len(self.refactoring_tasks)
        total_history = len(self.workflow_history)
        
        # 단계별 통계
        stage_stats = {}
        for stage in WorkflowStage:
            stage_recommendations = [r for r in self.recommendations if r.stage == stage]
            stage_stats[stage.value] = len(stage_recommendations)
        
        # 우선순위별 통계
        priority_stats = {}
        for recommendation in self.recommendations:
            priority = recommendation.priority
            if priority not in priority_stats:
                priority_stats[priority] = 0
            priority_stats[priority] += 1
        
        statistics = {
            'total_recommendations': total_recommendations,
            'total_analyses': total_analyses,
            'total_tasks': total_tasks,
            'total_history': total_history,
            'stage_statistics': stage_stats,
            'priority_statistics': priority_stats,
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info("워크플로우 통계 생성 완료")
        return statistics
    
    def export_workflow_data(self) -> Dict[str, Any]:
        """워크플로우 데이터 내보내기"""
        return {
            'recommendations': [asdict(r) for r in self.recommendations],
            'code_analyses': [asdict(a) for a in self.code_analyses],
            'refactoring_tasks': [asdict(t) for t in self.refactoring_tasks],
            'workflow_history': self.workflow_history,
            'export_date': datetime.now().isoformat()
        }

# 테스트 함수
def test_gpt_cursor_workflow():
    """GPT/커서 워크플로우 시스템 테스트"""
    print("🔄 GPTCursorWorkflow 테스트 시작...")
    
    workflow = GPTCursorWorkflow()
    
    # 1. GPT 추천사항 생성
    context = {"system_name": "TestSystem", "stage": "design"}
    recommendation = workflow.generate_gpt_recommendation(WorkflowStage.DESIGN, context)
    print(f"✅ GPT 추천사항 생성: {recommendation.recommendation_type}")
    print(f"   우선순위: {recommendation.priority}")
    print(f"   예상 노력: {recommendation.estimated_effort}")
    
    # 2. 코드 품질 분석
    sample_code = '''
def long_function():
    # 긴 함수 예시
    result = []
    for i in range(100):
        if i % 2 == 0:
            result.append(i)
    return result

def another_function():
    print("테스트")
    return True
'''
    
    analysis = workflow.analyze_code_quality("test_file.py", sample_code)
    print(f"✅ 코드 품질 분석: {len(analysis.issues_found)}개 이슈 발견")
    print(f"   복잡도 점수: {analysis.complexity_score:.2f}")
    print(f"   유지보수성 점수: {analysis.maintainability_score:.2f}")
    print(f"   성능 점수: {analysis.performance_score:.2f}")
    
    # 3. 리팩토링 작업 생성
    refactoring_task = workflow.create_refactoring_task(analysis, RefactoringType.CODE_STRUCTURE)
    print(f"✅ 리팩토링 작업 생성: {refactoring_task.refactoring_type.value}")
    print(f"   우선순위: {refactoring_task.priority}")
    print(f"   예상 영향: {refactoring_task.estimated_impact}")
    
    # 4. 워크플로우 단계 실행
    workflow_result = workflow.execute_workflow_stage(WorkflowStage.IMPLEMENTATION, context)
    print(f"✅ 워크플로우 단계 실행: {workflow_result['stage']}")
    print(f"   상태: {workflow_result['result']['status']}")
    
    # 5. 통계
    statistics = workflow.get_workflow_statistics()
    print(f"✅ 워크플로우 통계: {statistics['total_recommendations']}개 추천사항")
    print(f"   단계별 통계: {statistics['stage_statistics']}")
    print(f"   우선순위별 통계: {statistics['priority_statistics']}")
    
    # 6. 데이터 내보내기
    export_data = workflow.export_workflow_data()
    print(f"✅ 워크플로우 데이터 내보내기: {len(export_data['recommendations'])}개 추천사항")
    
    print("🎉 GPTCursorWorkflow 테스트 완료!")

if __name__ == "__main__":
    test_gpt_cursor_workflow() 