#!/usr/bin/env python3
"""
DuRi 사고 흐름 관리 시스템
사고의 흐름을 추적하고 관리하는 시스템
"""

from datetime import datetime
import json
from typing import Any, Dict, List, Optional


class DuRiThoughtFlow:
    """DuRi 사고 흐름 관리 시스템"""

    _instance = None
    _streams = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DuRiThoughtFlow, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.streams = {}
            self.thought_history = []
            self.initialized = True

    @classmethod
    def register_stream(cls, stream_name: str, data: Any):
        """
        사고 흐름 스트림에 데이터를 등록합니다.
        """
        if cls._instance is None:
            cls._instance = cls()

        if stream_name not in cls._instance.streams:
            cls._instance.streams[stream_name] = []

        stream_entry = {
            "timestamp": datetime.now().isoformat(),
            "stream_name": stream_name,
            "data": data,
        }

        cls._instance.streams[stream_name].append(stream_entry)
        cls._instance.thought_history.append(stream_entry)

        return stream_entry

    def get_stream(self, stream_name: str) -> List[Dict]:
        """
        특정 스트림의 데이터를 반환합니다.
        """
        return self.streams.get(stream_name, [])

    def get_all_streams(self) -> Dict[str, List]:
        """
        모든 스트림 데이터를 반환합니다.
        """
        return self.streams

    def get_thought_history(self) -> List[Dict]:
        """
        전체 사고 히스토리를 반환합니다.
        """
        return self.thought_history

    def export_thought_flow(self) -> Dict:
        """
        사고 흐름 데이터를 JSON 형태로 내보냅니다.
        """
        return {
            "total_streams": len(self.streams),
            "total_thoughts": len(self.thought_history),
            "streams": self.streams,
            "thought_history": self.thought_history,
            "exported_at": datetime.now().isoformat(),
        }
