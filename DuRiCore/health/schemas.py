#!/usr/bin/env python3
"""
DuRi Health Schemas - Day 75 확장
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class IntegritySummary(BaseModel):
    """무결성 요약 정보"""
    status: str
    summary: Dict[str, Any]
    deployment_id: Optional[str] = None
    modified_files: List[str] = Field(default_factory=list)
    missing_files: List[str] = Field(default_factory=list)

class RunbookInfo(BaseModel):
    """Day 75: 런북 정보"""
    id: str
    title: str
    url: str
    severity: str
    action_hint: str
    description: str

class CanaryResponse(BaseModel):
    """카나리 체크 응답 - Day 75 확장"""
    timestamp: datetime
    canary_ok: bool
    recommendation: str
    rollback_required: bool
    failure_reasons: List[str] = Field(default_factory=list)
    metrics: Dict[str, float]
    thresholds: Dict[str, float]
    checks: Dict[str, bool]
    slo_status: str
    integrity: IntegritySummary
    deployment_info: Dict[str, Any]
    runbooks: Optional[List[RunbookInfo]] = None  # Day 75 추가

class CanaryStatusResponse(BaseModel):
    """카나리 상태 응답"""
    timestamp: datetime
    status: str
    deployment_id: Optional[str] = None
    version: Optional[str] = None
    git_sha: Optional[str] = None
    canary_ok: bool
    recommendation: str
    rollback_required: bool
    failure_reasons: List[str] = Field(default_factory=list)
    integrity_details: Dict[str, Any]
