"""
DuRi Brain Memory Models
"""

from datetime import datetime

from sqlalchemy import ARRAY, JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MemoryEntry(Base):
    """메모리 엔트리 모델"""

    __tablename__ = "memory_entries"

    id = Column(Integer, primary_key=True, index=True)
    memory_type = Column(String(50), nullable=False)
    context = Column(Text)
    content = Column(Text, nullable=False)
    raw_data = Column(JSON)
    source = Column(String(100))
    tags = Column(ARRAY(String))
    importance_score = Column(Integer, default=1)
    memory_level = Column(String(20), default="short_term")
    expires_at = Column(DateTime)
    promotion_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
