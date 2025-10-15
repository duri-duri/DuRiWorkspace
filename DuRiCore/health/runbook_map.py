#!/usr/bin/env python3
"""
DuRi Runbook Map - Day 75 실패 사유 → 런북 매핑 테이블
"""

import re
from typing import List, Dict, Any
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("runbook_map")

# Day 75: 실패 사유 → 런북 매핑 테이블
RUNBOOKS = [
    {
        "pattern": re.compile(r"p95 latency .* >"),
        "id": "INC-001-PERF",
        "title": "High Latency Performance Issue",
        "url": "https://runbook.company.com/incidents/latency-high",
        "severity": "high",
        "action_hint": "scale-out",
        "description": "P95 latency exceeds threshold. Consider scaling out or investigating performance bottlenecks."
    },
    {
        "pattern": re.compile(r"error rate .* >"),
        "id": "INC-002-ERRORS",
        "title": "High Error Rate Issue",
        "url": "https://runbook.company.com/incidents/error-rate-high",
        "severity": "high",
        "action_hint": "rollback",
        "description": "Error rate exceeds threshold. Consider rolling back recent deployment or investigating error sources."
    },
    {
        "pattern": re.compile(r"readiness fail rate .* >"),
        "id": "INC-003-READINESS",
        "title": "Readiness Probe Failures",
        "url": "https://runbook.company.com/incidents/readiness-failures",
        "severity": "medium",
        "action_hint": "restart-pod",
        "description": "Readiness probe failures detected. Consider restarting pods or investigating health check issues."
    },
    {
        "pattern": re.compile(r"integrity: .* modified"),
        "id": "INC-004-INTEGRITY",
        "title": "File Integrity Violation",
        "url": "https://runbook.company.com/incidents/integrity-modified",
        "severity": "critical",
        "action_hint": "rollback",
        "description": "Modified files detected in deployment. Critical integrity violation - immediate rollback recommended."
    },
    {
        "pattern": re.compile(r"ignore snapshot mismatch"),
        "id": "INC-005-INTEGRITY-IGNORE",
        "title": "Ignore Snapshot Mismatch",
        "url": "https://runbook.company.com/incidents/ignore-mismatch",
        "severity": "low",
        "action_hint": "rebuild-manifest",
        "description": "Ignore snapshot mismatch detected. Consider rebuilding deployment manifest."
    },
    {
        "pattern": re.compile(r"check failure:"),
        "id": "INC-006-SYSTEM",
        "title": "System Check Failure",
        "url": "https://runbook.company.com/incidents/system-check-failure",
        "severity": "critical",
        "action_hint": "investigate",
        "description": "System check failure detected. Investigate system health and dependencies."
    }
]

def map_runbooks(failure_reasons: List[str]) -> List[Dict[str, Any]]:
    """
    Day 75: 실패 사유를 런북으로 매핑
    
    Args:
        failure_reasons: 실패 이유 리스트
        
    Returns:
        매핑된 런북 리스트 (중복 제거됨)
    """
    if not failure_reasons:
        return []
    
    seen_runbooks = {}
    
    for reason in failure_reasons:
        for runbook in RUNBOOKS:
            pattern = runbook["pattern"]
            if pattern.search(reason):
                runbook_id = runbook["id"]
                if runbook_id not in seen_runbooks:
                    seen_runbooks[runbook_id] = runbook.copy()
                    logger.debug(f"런북 매핑: '{reason}' -> {runbook_id}")
    
    result = list(seen_runbooks.values())
    logger.info(f"런북 매핑 완료: {len(failure_reasons)}개 사유 -> {len(result)}개 런북")
    
    return result

def get_runbook_by_id(runbook_id: str) -> Dict[str, Any]:
    """
    ID로 런북 가져오기
    
    Args:
        runbook_id: 런북 ID
        
    Returns:
        런북 정보 또는 None
    """
    for runbook in RUNBOOKS:
        if runbook["id"] == runbook_id:
            return runbook
    return None

def get_all_runbooks() -> List[Dict[str, Any]]:
    """모든 런북 가져오기"""
    return RUNBOOKS.copy()

def get_runbooks_by_severity(severity: str) -> List[Dict[str, Any]]:
    """
    심각도별 런북 가져오기
    
    Args:
        severity: 심각도 (critical, high, medium, low)
        
    Returns:
        해당 심각도의 런북 리스트
    """
    return [runbook for runbook in RUNBOOKS if runbook["severity"] == severity]

def get_action_hints(runbooks: List[Dict[str, Any]]) -> List[str]:
    """
    런북 리스트에서 액션 힌트 추출
    
    Args:
        runbooks: 런북 리스트
        
    Returns:
        액션 힌트 리스트
    """
    return [runbook["action_hint"] for runbook in runbooks if runbook.get("action_hint")]

def format_action_commands(action_hints: List[str]) -> Dict[str, str]:
    """
    Day 75: 액션 힌트를 실제 명령어로 변환
    
    Args:
        action_hints: 액션 힌트 리스트
        
    Returns:
        액션별 명령어 매핑
    """
    commands = {
        "scale-out": "kubectl scale deployment duri-app --replicas=5",
        "rollback": "kubectl rollout undo deployment/duri-app",
        "restart-pod": "kubectl delete pods -l app=duri-app",
        "rebuild-manifest": "python3 -c \"from DuRiCore.deployment.deployment_integrity import deployment_integrity; deployment_integrity.create_deployment_metadata('1.0.0')\"",
        "investigate": "kubectl logs -l app=duri-app --tail=100",
        "check-dependencies": "kubectl get pods -l app=duri-app -o wide"
    }
    
    result = {}
    for hint in action_hints:
        if hint in commands:
            result[hint] = commands[hint]
        else:
            result[hint] = f"Unknown action: {hint}"
    
    return result

def generate_runbook_summary(failure_reasons: List[str]) -> Dict[str, Any]:
    """
    Day 75: 실패 사유에 대한 런북 요약 생성
    
    Args:
        failure_reasons: 실패 이유 리스트
        
    Returns:
        런북 요약 정보
    """
    runbooks = map_runbooks(failure_reasons)
    action_hints = get_action_hints(runbooks)
    action_commands = format_action_commands(action_hints)
    
    # 심각도별 분류
    severity_counts = {}
    for runbook in runbooks:
        severity = runbook["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # 최고 심각도 결정
    severity_order = ["critical", "high", "medium", "low"]
    max_severity = None
    for severity in severity_order:
        if severity in severity_counts:
            max_severity = severity
            break
    
    return {
        "runbooks": runbooks,
        "action_hints": action_hints,
        "action_commands": action_commands,
        "severity_counts": severity_counts,
        "max_severity": max_severity,
        "total_runbooks": len(runbooks),
        "recommended_actions": list(action_commands.keys())
    }
