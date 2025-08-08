"""
DuRi Memory System - MemoryEntry Model
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class MemoryEntry(Base):
    """Memory Entry Model - DuRi의 기억을 저장하는 기본 단위"""
    
    __tablename__ = "memory_entries"
    
    # 기본 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 기억의 종류 (decision, input, log, event, error, success 등)
    type = Column(String(50), nullable=False, index=True)
    
    # 기억의 맥락 (어떤 상황에서 생성됨)
    context = Column(String(200), nullable=False)
    
    # 핵심 요약 내용
    content = Column(Text, nullable=False)
    
    # 상세 데이터 (JSON 형태)
    raw_data = Column(JSON, nullable=True)
    
    # 이 기억을 만든 주체 (cursor_ai, user, brain, system 등)
    source = Column(String(50), nullable=False, index=True)
    
    # 관련 키워드들 (JSON 배열)
    tags = Column(JSONB(astext_type=Text()), nullable=True)
    
    # 중요도 점수 (0-100)
    importance_score = Column(Integer, default=50)
    
    # 기억 레벨 (short/medium/truth)
    memory_level = Column(String(20), default='short', nullable=False, index=True)
    
    # 만료 시간 (단기 기억용)
    expires_at = Column(DateTime, nullable=True, index=True)
    
    # 승격 횟수 (중기 기억 승격 추적용)
    promotion_count = Column(Integer, default=0, index=True)
    
    # 생성 시간
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 수정 시간
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_memory_type_source', 'type', 'source'),
        Index('idx_memory_created_at', 'created_at'),
        Index('idx_memory_importance', 'importance_score'),
        Index('idx_memory_level_created', 'memory_level', 'created_at'),
        Index('idx_memory_level_importance', 'memory_level', 'importance_score'),
    )
    
    def __repr__(self):
        return f"<MemoryEntry(id={self.id}, type='{self.type}', context='{self.context}', source='{self.source}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """MemoryEntry를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'type': self.type,
            'context': self.context,
            'content': self.content,
            'raw_data': self.raw_data,
            'source': self.source,
            'tags': self.tags,
            'importance_score': self.importance_score,
            'memory_level': self.memory_level,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'promotion_count': self.promotion_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """딕셔너리로부터 MemoryEntry 생성"""
        memory_level = data.get('memory_level', 'short')
        expires_at = None
        
        # 단기 기억인 경우 만료 시간 설정
        if memory_level == 'short':
            expires_at = datetime.utcnow() + timedelta(hours=24)
        
        return cls(
            type=data.get('type'),
            context=data.get('context'),
            content=data.get('content'),
            raw_data=data.get('raw_data'),
            source=data.get('source'),
            tags=data.get('tags'),
            importance_score=data.get('importance_score', 50),
            memory_level=memory_level,
            expires_at=expires_at,
            promotion_count=data.get('promotion_count', 0)
        ) 