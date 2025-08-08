"""
DuRi의 전략 묘지 시스템

실패한 전략을 기록하고 관리합니다.
동일한 실패 조건의 반복을 방지하고 실패 패턴을 분석합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class FailedStrategy:
    """실패한 전략"""
    strategy_id: str
    failure_date: datetime
    failure_reason: str
    context: Dict[str, Any]
    emotion_trend: List[str]
    performance_history: List[float]
    modification_count: int
    strategy_age_days: int
    failure_pattern_hash: str

@dataclass
class FailurePattern:
    """실패 패턴"""
    pattern_hash: str
    failure_count: int
    common_context: Dict[str, Any]
    common_reasons: List[str]
    first_failure_date: datetime
    last_failure_date: datetime

class StrategyGraveyard:
    """
    DuRi의 전략 묘지 시스템
    
    실패한 전략을 기록하고 관리합니다.
    """
    
    def __init__(self, storage_path: str = "strategy_graveyard.json"):
        """StrategyGraveyard 초기화"""
        self.storage_path = storage_path
        self.failed_strategies: Dict[str, FailedStrategy] = {}
        self.failure_patterns: Dict[str, FailurePattern] = {}
        self.context_blacklist: Set[str] = set()  # 반복 방지용 컨텍스트 블랙리스트
        
        # 저장된 데이터 로드
        self._load_graveyard_data()
        
        logger.info("StrategyGraveyard 초기화 완료")
    
    def bury_strategy(self, strategy_id: str, failure_reason: str, 
                     context: Dict[str, Any], emotion_trend: List[str],
                     performance_history: List[float], modification_count: int,
                     strategy_age_days: int) -> bool:
        """
        실패한 전략을 묘지에 안장합니다.
        
        Args:
            strategy_id: 전략 ID
            failure_reason: 실패 이유
            context: 실패 당시 컨텍스트
            emotion_trend: 감정 변화 추이
            performance_history: 성과 히스토리
            modification_count: 수정 횟수
            strategy_age_days: 전략 사용 일수
            
        Returns:
            bool: 안장 성공 여부
        """
        try:
            # 실패 패턴 해시 생성
            failure_pattern_hash = self._generate_failure_pattern_hash(context, failure_reason)
            
            # 실패한 전략 기록
            failed_strategy = FailedStrategy(
                strategy_id=strategy_id,
                failure_date=datetime.now(),
                failure_reason=failure_reason,
                context=context,
                emotion_trend=emotion_trend,
                performance_history=performance_history,
                modification_count=modification_count,
                strategy_age_days=strategy_age_days,
                failure_pattern_hash=failure_pattern_hash
            )
            
            self.failed_strategies[strategy_id] = failed_strategy
            
            # 실패 패턴 업데이트
            self._update_failure_pattern(failure_pattern_hash, context, failure_reason)
            
            # 컨텍스트 블랙리스트 업데이트
            self._update_context_blacklist(context, failure_reason)
            
            # 데이터 저장
            self._save_graveyard_data()
            
            logger.info(f"전략 {strategy_id} 안장 완료: {failure_reason}")
            return True
            
        except Exception as e:
            logger.error(f"전략 안장 실패: {e}")
            return False
    
    def _generate_failure_pattern_hash(self, context: Dict[str, Any], failure_reason: str) -> str:
        """실패 패턴 해시를 생성합니다."""
        # 컨텍스트와 실패 이유를 기반으로 해시 생성
        pattern_data = {
            'context_keys': sorted(context.keys()),
            'context_values': sorted([str(v) for v in context.values()]),
            'failure_reason': failure_reason
        }
        
        pattern_string = json.dumps(pattern_data, sort_keys=True)
        return hashlib.md5(pattern_string.encode()).hexdigest()
    
    def _update_failure_pattern(self, pattern_hash: str, context: Dict[str, Any], failure_reason: str):
        """실패 패턴을 업데이트합니다."""
        if pattern_hash in self.failure_patterns:
            # 기존 패턴 업데이트
            pattern = self.failure_patterns[pattern_hash]
            pattern.failure_count += 1
            pattern.last_failure_date = datetime.now()
            
            if failure_reason not in pattern.common_reasons:
                pattern.common_reasons.append(failure_reason)
        else:
            # 새 패턴 생성
            pattern = FailurePattern(
                pattern_hash=pattern_hash,
                failure_count=1,
                common_context=context.copy(),
                common_reasons=[failure_reason],
                first_failure_date=datetime.now(),
                last_failure_date=datetime.now()
            )
            self.failure_patterns[pattern_hash] = pattern
    
    def _update_context_blacklist(self, context: Dict[str, Any], failure_reason: str):
        """컨텍스트 블랙리스트를 업데이트합니다."""
        # 특정 조건에서 반복 실패하는 컨텍스트를 블랙리스트에 추가
        if failure_reason in ["성과 하락", "감정 악화", "지속적 실패"]:
            context_key = f"{list(context.keys())}_{list(context.values())}"
            self.context_blacklist.add(context_key)
    
    def is_context_blacklisted(self, context: Dict[str, Any]) -> bool:
        """컨텍스트가 블랙리스트에 있는지 확인합니다."""
        context_key = f"{list(context.keys())}_{list(context.values())}"
        return context_key in self.context_blacklist
    
    def get_similar_failures(self, context: Dict[str, Any], failure_reason: str) -> List[FailedStrategy]:
        """유사한 실패 사례를 찾습니다."""
        pattern_hash = self._generate_failure_pattern_hash(context, failure_reason)
        similar_failures = []
        
        for strategy in self.failed_strategies.values():
            if strategy.failure_pattern_hash == pattern_hash:
                similar_failures.append(strategy)
        
        return similar_failures
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """실패 통계를 반환합니다."""
        total_failures = len(self.failed_strategies)
        total_patterns = len(self.failure_patterns)
        
        # 실패 이유 분포
        failure_reasons = {}
        for strategy in self.failed_strategies.values():
            reason = strategy.failure_reason
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        
        # 평균 수정 횟수
        avg_modifications = sum(s.modification_count for s in self.failed_strategies.values()) / total_failures if total_failures > 0 else 0
        
        # 평균 전략 수명
        avg_age = sum(s.strategy_age_days for s in self.failed_strategies.values()) / total_failures if total_failures > 0 else 0
        
        return {
            "total_failures": total_failures,
            "total_patterns": total_patterns,
            "failure_reasons": failure_reasons,
            "average_modifications": avg_modifications,
            "average_strategy_age": avg_age,
            "blacklisted_contexts": len(self.context_blacklist)
        }
    
    def get_failure_patterns(self) -> Dict[str, Any]:
        """실패 패턴을 반환합니다."""
        patterns_info = {}
        
        for pattern_hash, pattern in self.failure_patterns.items():
            patterns_info[pattern_hash] = {
                "failure_count": pattern.failure_count,
                "common_context": pattern.common_context,
                "common_reasons": pattern.common_reasons,
                "first_failure_date": pattern.first_failure_date.isoformat(),
                "last_failure_date": pattern.last_failure_date.isoformat()
            }
        
        return patterns_info
    
    def get_recommendations_for_context(self, context: Dict[str, Any]) -> List[str]:
        """주어진 컨텍스트에 대한 권장사항을 반환합니다."""
        recommendations = []
        
        # 블랙리스트 확인
        if self.is_context_blacklisted(context):
            recommendations.append("이 컨텍스트는 과거에 실패한 패턴입니다. 다른 접근 방법을 고려하세요.")
        
        # 유사한 실패 패턴 확인
        similar_failures = []
        for pattern in self.failure_patterns.values():
            if self._contexts_are_similar(context, pattern.common_context):
                similar_failures.extend(pattern.common_reasons)
        
        if similar_failures:
            unique_reasons = list(set(similar_failures))
            recommendations.append(f"유사한 컨텍스트에서 다음 실패가 발생했습니다: {', '.join(unique_reasons)}")
        
        # 일반적인 권장사항
        if not recommendations:
            recommendations.append("이 컨텍스트에 대한 실패 기록이 없습니다. 신중하게 접근하세요.")
        
        return recommendations
    
    def _contexts_are_similar(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> bool:
        """두 컨텍스트가 유사한지 확인합니다."""
        # 간단한 유사도 검사 (키가 50% 이상 일치)
        keys1 = set(context1.keys())
        keys2 = set(context2.keys())
        
        if not keys1 or not keys2:
            return False
        
        common_keys = keys1.intersection(keys2)
        similarity = len(common_keys) / max(len(keys1), len(keys2))
        
        return similarity >= 0.5
    
    def _load_graveyard_data(self):
        """묘지 데이터를 로드합니다."""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 실패한 전략 로드
                for strategy_data in data.get('failed_strategies', []):
                    strategy = FailedStrategy(
                        strategy_id=strategy_data['strategy_id'],
                        failure_date=datetime.fromisoformat(strategy_data['failure_date']),
                        failure_reason=strategy_data['failure_reason'],
                        context=strategy_data['context'],
                        emotion_trend=strategy_data['emotion_trend'],
                        performance_history=strategy_data['performance_history'],
                        modification_count=strategy_data['modification_count'],
                        strategy_age_days=strategy_data['strategy_age_days'],
                        failure_pattern_hash=strategy_data['failure_pattern_hash']
                    )
                    self.failed_strategies[strategy.strategy_id] = strategy
                
                # 실패 패턴 로드
                for pattern_data in data.get('failure_patterns', []):
                    pattern = FailurePattern(
                        pattern_hash=pattern_data['pattern_hash'],
                        failure_count=pattern_data['failure_count'],
                        common_context=pattern_data['common_context'],
                        common_reasons=pattern_data['common_reasons'],
                        first_failure_date=datetime.fromisoformat(pattern_data['first_failure_date']),
                        last_failure_date=datetime.fromisoformat(pattern_data['last_failure_date'])
                    )
                    self.failure_patterns[pattern.pattern_hash] = pattern
                
                # 블랙리스트 로드
                self.context_blacklist = set(data.get('context_blacklist', []))
                
                logger.info(f"묘지 데이터 로드 완료: {len(self.failed_strategies)}개 전략, {len(self.failure_patterns)}개 패턴")
                
        except FileNotFoundError:
            logger.info("묘지 데이터 파일이 없습니다. 새로 시작합니다.")
        except Exception as e:
            logger.error(f"묘지 데이터 로드 실패: {e}")
    
    def _save_graveyard_data(self):
        """묘지 데이터를 저장합니다."""
        try:
            data = {
                'failed_strategies': [],
                'failure_patterns': [],
                'context_blacklist': list(self.context_blacklist)
            }
            
            # 실패한 전략 저장
            for strategy in self.failed_strategies.values():
                strategy_data = {
                    'strategy_id': strategy.strategy_id,
                    'failure_date': strategy.failure_date.isoformat(),
                    'failure_reason': strategy.failure_reason,
                    'context': strategy.context,
                    'emotion_trend': strategy.emotion_trend,
                    'performance_history': strategy.performance_history,
                    'modification_count': strategy.modification_count,
                    'strategy_age_days': strategy.strategy_age_days,
                    'failure_pattern_hash': strategy.failure_pattern_hash
                }
                data['failed_strategies'].append(strategy_data)
            
            # 실패 패턴 저장
            for pattern in self.failure_patterns.values():
                pattern_data = {
                    'pattern_hash': pattern.pattern_hash,
                    'failure_count': pattern.failure_count,
                    'common_context': pattern.common_context,
                    'common_reasons': pattern.common_reasons,
                    'first_failure_date': pattern.first_failure_date.isoformat(),
                    'last_failure_date': pattern.last_failure_date.isoformat()
                }
                data['failure_patterns'].append(pattern_data)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"묘지 데이터 저장 완료: {len(self.failed_strategies)}개 전략")
            
        except Exception as e:
            logger.error(f"묘지 데이터 저장 실패: {e}")

# 싱글톤 인스턴스
_strategy_graveyard = None

def get_strategy_graveyard() -> StrategyGraveyard:
    """StrategyGraveyard 싱글톤 인스턴스 반환"""
    global _strategy_graveyard
    if _strategy_graveyard is None:
        _strategy_graveyard = StrategyGraveyard()
    return _strategy_graveyard 