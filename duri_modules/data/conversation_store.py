#!/usr/bin/env python3
"""
실제 대화 데이터 수집 및 저장 시스템
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List

DATA_PATH = "/tmp/duri_conversations"
os.makedirs(DATA_PATH, exist_ok=True)


class ConversationStore:
    """실제 대화 데이터 저장 및 관리 시스템"""

    def __init__(self):
        self.data_path = DATA_PATH
        self.conversation_history = []
        self.learning_patterns = []

    def store_conversation(
        self, user_input: str, duri_response: str, metadata: Dict[str, Any] = None
    ) -> str:
        """대화 데이터 저장"""

        timestamp = datetime.now()
        conversation_id = self._generate_conversation_id(user_input, timestamp)

        conversation_data = {
            "conversation_id": conversation_id,
            "timestamp": timestamp.isoformat(),
            "user_input": user_input,
            "duri_response": duri_response,
            "metadata": metadata or {},
            "learning_value": self._calculate_learning_value(user_input, duri_response),
            "conversation_length": len(user_input) + len(duri_response),
            "response_time": metadata.get("response_time", 0) if metadata else 0,
        }

        # 파일에 저장
        filename = f"{self.data_path}/conversation_{conversation_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)

        # 메모리에 저장
        self.conversation_history.append(conversation_data)

        print(f"💾 대화 저장 완료: {conversation_id}")
        print(f"   📝 사용자 입력: {len(user_input)}자")
        print(f"   🤖 DuRi 응답: {len(duri_response)}자")
        print(f"   📊 학습 가치: {conversation_data['learning_value']:.2f}")

        return conversation_id

    def _generate_conversation_id(self, user_input: str, timestamp: datetime) -> str:
        """대화 ID 생성"""
        content_hash = hashlib.md5(f"{user_input}{timestamp}".encode()).hexdigest()[:8]
        return f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{content_hash}"

    def _calculate_learning_value(self, user_input: str, duri_response: str) -> float:
        """학습 가치 계산"""
        # 입력 복잡도
        input_complexity = len(user_input.split()) / 10.0

        # 응답 품질
        response_quality = len(duri_response.split()) / 20.0

        # 기술적 키워드 포함 여부
        tech_keywords = [
            "API",
            "HTTP",
            "JSON",
            "async",
            "await",
            "FastAPI",
            "Flask",
            "Python",
            "코드",
            "구현",
        ]
        tech_score = sum(
            1 for keyword in tech_keywords if keyword.lower() in duri_response.lower()
        ) / len(tech_keywords)

        # 종합 학습 가치
        learning_value = (input_complexity + response_quality + tech_score) / 3.0
        return min(learning_value, 1.0)

    def get_conversation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """대화 기록 조회"""
        return sorted(self.conversation_history, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_learning_statistics(self) -> Dict[str, Any]:
        """학습 통계 생성"""
        if not self.conversation_history:
            return {"total_conversations": 0, "avg_learning_value": 0.0}

        total_conversations = len(self.conversation_history)
        avg_learning_value = (
            sum(conv["learning_value"] for conv in self.conversation_history) / total_conversations
        )
        total_response_time = sum(
            conv.get("response_time", 0) for conv in self.conversation_history
        )
        avg_response_time = (
            total_response_time / total_conversations if total_conversations > 0 else 0
        )

        return {
            "total_conversations": total_conversations,
            "avg_learning_value": avg_learning_value,
            "avg_response_time": avg_response_time,
            "total_conversation_length": sum(
                conv["conversation_length"] for conv in self.conversation_history
            ),
            "high_value_conversations": len(
                [conv for conv in self.conversation_history if conv["learning_value"] > 0.7]
            ),
        }

    def extract_learning_patterns(self) -> List[Dict[str, Any]]:
        """학습 패턴 추출"""
        patterns = []

        # 자주 나오는 키워드 패턴
        keyword_patterns = {}
        for conv in self.conversation_history:
            user_words = set(conv["user_input"].lower().split())
            for word in user_words:
                if len(word) > 3:  # 3글자 이상만
                    keyword_patterns[word] = keyword_patterns.get(word, 0) + 1

        # 상위 키워드
        top_keywords = sorted(keyword_patterns.items(), key=lambda x: x[1], reverse=True)[:10]

        # 응답 길이 패턴
        response_lengths = [conv["conversation_length"] for conv in self.conversation_history]
        avg_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0

        patterns.append(
            {
                "type": "keyword_patterns",
                "data": top_keywords,
                "description": "자주 언급되는 키워드 패턴",
            }
        )

        patterns.append(
            {
                "type": "response_length_pattern",
                "data": {
                    "average_length": avg_length,
                    "total_conversations": len(response_lengths),
                },
                "description": "응답 길이 패턴",
            }
        )

        return patterns

    def get_conversation_by_id(self, conversation_id: str) -> Dict[str, Any]:
        """특정 대화 조회"""
        for conv in self.conversation_history:
            if conv["conversation_id"] == conversation_id:
                return conv
        return {}

    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        try:
            learning_stats = self.get_learning_statistics()
            patterns = self.extract_learning_patterns()

            return {
                "learning_statistics": learning_stats,
                "learning_patterns": patterns,
                "total_conversations": len(self.conversation_history),
                "recent_conversations": (
                    len(self.conversation_history[-10:]) if self.conversation_history else 0
                ),
            }
        except Exception as e:
            print(f"통계 생성 오류: {e}")
            return {"error": str(e)}

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 대화 기록 반환"""
        return self.get_conversation_history(limit)


# 모듈 인스턴스 생성
conversation_store = ConversationStore()
