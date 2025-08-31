#!/usr/bin/env python3
"""
🗄️ DuRi 데이터베이스 모델 정의
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, JSON, Boolean, func
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
import os

Base = declarative_base()

# -----------------------------
# 🔹 공통 Base Mixin
# -----------------------------

class BaseModelMixin:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


# -----------------------------
# 🔹 감정 기록 모델
# -----------------------------

class EmotionRecord(Base, BaseModelMixin):
    __tablename__ = "emotion_records"

    emotion_type = Column(String(50), nullable=False, index=True)
    intensity = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    meta_info = Column(JSON, nullable=True)
    processed = Column(Boolean, default=False)


# -----------------------------
# 🔹 시스템 로그 모델
# -----------------------------

class SystemLog(Base, BaseModelMixin):
    __tablename__ = "system_logs"

    level = Column(String(20), nullable=False, index=True)  # e.g., INFO, ERROR
    module = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# -----------------------------
# 🔹 모듈 상태 모델
# -----------------------------

class ModuleStatus(Base, BaseModelMixin):
    __tablename__ = "module_status"

    module_name = Column(String(50), nullable=False, unique=True, index=True)
    status = Column(String(50), nullable=False, default="unknown")
    version = Column(String(20), nullable=True)
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
    meta_info = Column(JSON, nullable=True)


# -----------------------------
# 🔹 DB 유틸 함수
# -----------------------------

def get_database_url() -> str:
    """환경변수 기반 DB URL 구성"""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "duri_db")
    db_user = os.getenv("DB_USER", "duri_user")
    db_password = os.getenv("DB_PASSWORD", "duri_password")
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def create_tables(engine):
    """모든 테이블 생성"""
    Base.metadata.create_all(bind=engine)

def drop_tables(engine):
    """모든 테이블 삭제"""
    Base.metadata.drop_all(bind=engine)
