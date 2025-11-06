#!/usr/bin/env python3
"""
EvolutionSession 스키마 및 로그 관리
목적: inputs/config→candidates→eval→decision 로그 일원화
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from enum import Enum


class EvolutionPhase(Enum):
    """진화 단계"""
    PLAN = "plan"
    EXECUTE = "execute"
    EVALUATE = "evaluate"
    DECIDE = "decide"
    PROMOTE = "promote"
    ROLLBACK = "rollback"


class TaskType(Enum):
    """태스크 유형"""
    OBS_RULE_TUNE = "obs_rule_tune"
    DOC_TO_PR = "doc_to_pr"
    CONFIG_PATCH = "config_patch"


@dataclass
class EvolutionSession:
    """진화 세션 스키마"""
    session_id: str
    timestamp: str
    phase: str
    task_type: str
    config: Dict[str, Any]
    inputs: Dict[str, Any]
    candidates: Optional[List[Dict[str, Any]]] = None
    evaluation: Optional[Dict[str, Any]] = None
    decision: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None
    artifacts: Optional[List[str]] = None
    tag: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvolutionSession':
        """딕셔너리에서 생성"""
        return cls(**data)


class EvolutionSessionManager:
    """진화 세션 관리자"""
    
    def __init__(self, base_dir: Path = Path('var/evolution')):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_file = self.base_dir / 'sessions.jsonl'
        self.db_file = self.base_dir / 'sessions.db'
        self._init_db()
    
    def _init_db(self):
        """SQLite 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                phase TEXT NOT NULL,
                task_type TEXT NOT NULL,
                config TEXT,
                inputs TEXT,
                candidates TEXT,
                evaluation TEXT,
                decision TEXT,
                metrics TEXT,
                artifacts TEXT,
                tag TEXT,
                error TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, task_type: TaskType, config: Dict[str, Any], 
                      inputs: Dict[str, Any]) -> EvolutionSession:
        """새 세션 생성"""
        session_id = f"EV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        session = EvolutionSession(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            phase=EvolutionPhase.PLAN.value,
            task_type=task_type.value,
            config=config,
            inputs=inputs,
        )
        
        self.save_session(session)
        return session
    
    def save_session(self, session: EvolutionSession):
        """세션 저장 (JSONL + SQLite)"""
        # JSONL 저장
        with open(self.jsonl_file, 'a') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False)
            f.write('\n')
        
        # SQLite 저장
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.session_id,
            session.timestamp,
            session.phase,
            session.task_type,
            json.dumps(session.config),
            json.dumps(session.inputs),
            json.dumps(session.candidates) if session.candidates else None,
            json.dumps(session.evaluation) if session.evaluation else None,
            session.decision,
            json.dumps(session.metrics) if session.metrics else None,
            json.dumps(session.artifacts) if session.artifacts else None,
            session.tag,
            session.error,
        ))
        
        conn.commit()
        conn.close()
    
    def update_session(self, session_id: str, **kwargs):
        """세션 업데이트"""
        session = self.get_session(session_id)
        if not session:
            return
        
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        self.save_session(session)
    
    def get_session(self, session_id: str) -> Optional[EvolutionSession]:
        """세션 조회"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return EvolutionSession(
            session_id=row[0],
            timestamp=row[1],
            phase=row[2],
            task_type=row[3],
            config=json.loads(row[4]) if row[4] else {},
            inputs=json.loads(row[5]) if row[5] else {},
            candidates=json.loads(row[6]) if row[6] else None,
            evaluation=json.loads(row[7]) if row[7] else None,
            decision=row[8],
            metrics=json.loads(row[9]) if row[9] else None,
            artifacts=json.loads(row[10]) if row[10] else None,
            tag=row[11],
            error=row[12],
        )
    
    def list_sessions(self, task_type: Optional[TaskType] = None, 
                     phase: Optional[EvolutionPhase] = None, 
                     limit: int = 100) -> List[EvolutionSession]:
        """세션 목록 조회"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM sessions WHERE 1=1'
        params = []
        
        if task_type:
            query += ' AND task_type = ?'
            params.append(task_type.value)
        
        if phase:
            query += ' AND phase = ?'
            params.append(phase.value)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append(EvolutionSession(
                session_id=row[0],
                timestamp=row[1],
                phase=row[2],
                task_type=row[3],
                config=json.loads(row[4]) if row[4] else {},
                inputs=json.loads(row[5]) if row[5] else {},
                candidates=json.loads(row[6]) if row[6] else None,
                evaluation=json.loads(row[7]) if row[7] else None,
                decision=row[8],
                metrics=json.loads(row[9]) if row[9] else None,
                artifacts=json.loads(row[10]) if row[10] else None,
                tag=row[11],
                error=row[12],
            ))
        
        return sessions


if __name__ == '__main__':
    # 테스트
    manager = EvolutionSessionManager()
    
    session = manager.create_session(
        TaskType.OBS_RULE_TUNE,
        config={'threshold_delta': 0.05},
        inputs={'rule_file': 'prometheus/rules/alerts.yml'}
    )
    
    print(f"세션 생성: {session.session_id}")
    
    manager.update_session(session.session_id, phase=EvolutionPhase.EXECUTE.value)
    
    session_loaded = manager.get_session(session.session_id)
    print(f"세션 조회: {session_loaded.phase}")

