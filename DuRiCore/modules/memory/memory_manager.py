#!/usr/bin/env python3
"""
DuRi 메모리 관리 시스템
장기 기억과 단기 기억을 관리하는 시스템
"""

from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional


class MemoryManager:
    """DuRi 메모리 관리 시스템"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.long_term_memory = {}
            self.short_term_memory = {}
            self.memory_file = "DuRiCore/memory/du_ri_memory.json"
            self.initialized = True
            self._load_memory()

    def _load_memory(self):
        """메모리 파일에서 데이터를 로드합니다."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.long_term_memory = data.get("long_term", {})
                    self.short_term_memory = data.get("short_term", {})
        except Exception as e:
            print(f"메모리 로드 실패: {e}")

    def _save_memory(self):
        """메모리 데이터를 파일에 저장합니다."""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            data = {
                "long_term": self.long_term_memory,
                "short_term": self.short_term_memory,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"메모리 저장 실패: {e}")

    def store_long_term(self, key: str, data: Any):
        """
        장기 기억에 데이터를 저장합니다.
        """
        self.long_term_memory[key] = {
            "data": data,
            "stored_at": datetime.now().isoformat(),
            "access_count": 0,
        }
        self._save_memory()
        return True

    def retrieve_long_term(self, key: str) -> Optional[Any]:
        """
        장기 기억에서 데이터를 검색합니다.
        """
        if key in self.long_term_memory:
            self.long_term_memory[key]["access_count"] += 1
            self._save_memory()
            return self.long_term_memory[key]["data"]
        return None

    def store_short_term(self, key: str, data: Any):
        """
        단기 기억에 데이터를 저장합니다.
        """
        self.short_term_memory[key] = {
            "data": data,
            "stored_at": datetime.now().isoformat(),
        }
        return True

    def retrieve_short_term(self, key: str) -> Optional[Any]:
        """
        단기 기억에서 데이터를 검색합니다.
        """
        return self.short_term_memory.get(key, {}).get("data")

    def get_memory_summary(self) -> Dict:
        """
        메모리 요약 정보를 반환합니다.
        """
        return {
            "long_term_count": len(self.long_term_memory),
            "short_term_count": len(self.short_term_memory),
            "total_memory": len(self.long_term_memory) + len(self.short_term_memory),
            "last_updated": datetime.now().isoformat(),
        }
