#!/usr/bin/env python3
"""
DuRi 판단 전략 적용 시스템 - judgment_advice_database.json을 기반으로 판단 전략을 동적으로 적용
"""

from datetime import datetime
import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JudgmentStrategyApplier:
    """판단 전략 적용 시스템"""

    def __init__(self, database_path: str = None):
        if database_path is None:
            # 현재 파일의 디렉토리를 기준으로 상대 경로 설정
            current_dir = os.path.dirname(os.path.abspath(__file__))
            database_path = os.path.join(current_dir, "judgment_advice_database.json")
        self.database_path = database_path
        self.strategies = self._load_strategies()

    def _load_strategies(self) -> Dict[str, Any]:
        """판단 전략 데이터베이스 로드"""
        try:
            if os.path.exists(self.database_path):
                with open(self.database_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(
                        f"판단 전략 데이터베이스 로드 완료: {len(data.get('judgment_strategies', []))}개 전략"
                    )
                    return data
            else:
                logger.warning(
                    f"판단 전략 데이터베이스가 존재하지 않음: {self.database_path}"
                )
                return {"judgment_strategies": [], "metadata": {}}
        except Exception as e:
            logger.error(f"판단 전략 데이터베이스 로드 실패: {e}")
            return {"judgment_strategies": [], "metadata": {}}

    def find_matching_strategy(
        self, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        컨텍스트와 일치하는 판단 전략 찾기

        Args:
            context: 판단 대상 상황

        Returns:
            Optional[Dict[str, Any]]: 일치하는 전략 (없으면 None)
        """
        try:
            # 컨텍스트를 문자열로 변환하여 패턴 매칭
            context_str = self._context_to_string(context)

            best_match = None
            best_score = 0.0

            for strategy in self.strategies.get("judgment_strategies", []):
                pattern = strategy.get("context_pattern", "")
                if pattern:
                    # 간단한 키워드 매칭 (향후 더 정교한 매칭으로 개선 가능)
                    score = self._calculate_match_score(context_str, pattern)
                    if score > best_score and score > 0.3:  # 최소 매칭 점수
                        best_score = score
                        best_match = strategy

            if best_match:
                logger.info(
                    f"판단 전략 매칭 성공: {best_match['id']} (점수: {best_score:.2f})"
                )
                return best_match
            else:
                logger.debug("일치하는 판단 전략 없음")
                return None

        except Exception as e:
            logger.error(f"판단 전략 매칭 실패: {e}")
            return None

    def _context_to_string(self, context: Dict[str, Any]) -> str:
        """컨텍스트를 문자열로 변환"""
        if isinstance(context, dict):
            # 주요 키들을 문자열로 결합
            key_fields = ["content", "situation", "context", "type", "description"]
            context_parts = []

            for field in key_fields:
                if field in context:
                    value = context[field]
                    if isinstance(value, str):
                        context_parts.append(value)
                    elif isinstance(value, (list, dict)):
                        context_parts.append(str(value))

            return " ".join(context_parts)
        else:
            return str(context)

    def _calculate_match_score(self, context_str: str, pattern: str) -> float:
        """매칭 점수 계산 (간단한 키워드 기반)"""
        try:
            context_lower = context_str.lower()
            pattern_lower = pattern.lower()

            # 키워드 매칭
            pattern_keywords = pattern_lower.split()
            matched_keywords = 0

            for keyword in pattern_keywords:
                if keyword in context_lower:
                    matched_keywords += 1

            if pattern_keywords:
                return matched_keywords / len(pattern_keywords)
            else:
                return 0.0

        except Exception as e:
            logger.warning(f"매칭 점수 계산 실패: {e}")
            return 0.0

    def apply_strategy(
        self, context: Dict[str, Any], judgment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        판단 전략을 적용하여 판단 결과를 개선

        Args:
            context: 판단 대상 상황
            judgment_result: 원본 판단 결과

        Returns:
            Dict[str, Any]: 전략이 적용된 판단 결과
        """
        try:
            # 일치하는 전략 찾기
            strategy = self.find_matching_strategy(context)

            if strategy:
                # 전략 적용
                improved_result = judgment_result.copy()
                improved_result["applied_strategy"] = strategy["improvement"]
                improved_result["strategy_source"] = "judgment_advice_database"
                improved_result["strategy_id"] = strategy["id"]
                improved_result["strategy_success_rate"] = strategy["success_rate"]

                logger.info(
                    f"판단 전략 적용: {strategy['id']} - {strategy['improvement']}"
                )

                # 전략 사용 횟수 업데이트 (향후 구현)
                self._update_strategy_usage(strategy["id"])

                return improved_result
            else:
                # 전략이 없는 경우 원본 결과 반환
                judgment_result["applied_strategy"] = None
                judgment_result["strategy_source"] = None
                return judgment_result

        except Exception as e:
            logger.error(f"판단 전략 적용 실패: {e}")
            return judgment_result

    def _update_strategy_usage(self, strategy_id: str) -> None:
        """전략 사용 횟수 업데이트 (향후 구현)"""
        try:
            # TODO: 전략 사용 횟수 및 성공률 추적 구현
            pass
        except Exception as e:
            logger.warning(f"전략 사용 횟수 업데이트 실패: {e}")
