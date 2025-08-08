"""
DuRi의 핵심 철학 및 판단 기준

이 모듈은 DuRi의 모든 판단의 근본이 되는 철학을 정의합니다.
5단계 학습 루프와 창의성-안정성 병렬 구조의 판단 기준을 제공합니다.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BeliefType(Enum):
    """DuRi의 철학 유형"""
    LEARNING_PHILOSOPHY = "learning_philosophy"  # 학습 철학
    CREATIVITY_PHILOSOPHY = "creativity_philosophy"  # 창의성 철학
    EVOLUTION_PHILOSOPHY = "evolution_philosophy"  # 진화 철학
    ETHICS_PHILOSOPHY = "ethics_philosophy"  # 윤리 철학


@dataclass
class Belief:
    """개별 철학 항목"""
    id: str
    type: BeliefType
    content: str
    confidence: float  # 0.0 ~ 1.0
    last_updated: datetime
    source: str  # 학습, 경험, 외부 입력 등
    evidence: List[str]  # 이 철학을 뒷받침하는 증거들


class CoreBelief:
    """
    DuRi의 핵심 철학 시스템
    
    DuRi의 모든 판단의 근본이 되는 철학을 관리합니다.
    5단계 학습 루프와 창의성-안정성 병렬 구조의 판단 기준을 제공합니다.
    """
    
    def __init__(self):
        """CoreBelief 초기화"""
        self.beliefs: Dict[str, Belief] = {}
        self.learning_history: List[Dict] = []
        self.creativity_threshold: float = 0.7
        self.stability_threshold: float = 0.8
        self.evolution_threshold: float = 0.6
        
        # 기본 철학 초기화
        self._initialize_core_beliefs()
        logger.info("CoreBelief 시스템 초기화 완료")
    
    def _initialize_core_beliefs(self):
        """기본 철학들을 초기화"""
        current_time = datetime.now()
        
        # 1. 학습 철학
        self.add_belief(
            "learning_loop_philosophy",
            BeliefType.LEARNING_PHILOSOPHY,
            "DuRi는 인간처럼 학습해야 한다. 모방 → 반복 → 피드백 → 도전 → 개선의 5단계 루프를 따른다.",
            0.9,
            "core_initialization",
            ["인간의 학습 패턴 분석", "인공지능 학습 이론"]
        )
        
        # 2. 창의성 철학
        self.add_belief(
            "creativity_philosophy",
            BeliefType.CREATIVITY_PHILOSOPHY,
            "실행은 보수적으로, 실험은 창의적으로. Dream은 현실과 병렬로 경쟁하며, 더 나으면 자동 승격한다.",
            0.85,
            "core_initialization",
            ["창의성 이론", "병렬 처리 시스템"]
        )
        
        # 3. 진화 철학
        self.add_belief(
            "evolution_philosophy",
            BeliefType.EVOLUTION_PHILOSOPHY,
            "DuRi는 시행착오를 통해 스스로 진화한다. 실패는 반복 가능하지만, 치명적 실패는 제거한다.",
            0.8,
            "core_initialization",
            ["진화 알고리즘", "강화학습 이론"]
        )
        
        # 4. 윤리 철학
        self.add_belief(
            "ethics_philosophy",
            BeliefType.ETHICS_PHILOSOPHY,
            "DuRi는 인간의 안전과 복지를 최우선으로 한다. 모든 행동은 인간의 이익을 고려한다.",
            0.95,
            "core_initialization",
            ["AI 윤리 가이드라인", "인간 중심 설계"]
        )
    
    def add_belief(self, belief_id: str, belief_type: BeliefType, content: str, 
                   confidence: float, source: str, evidence: List[str]) -> bool:
        """
        새로운 철학을 추가
        
        Args:
            belief_id: 철학 식별자
            belief_type: 철학 유형
            content: 철학 내용
            confidence: 신뢰도 (0.0 ~ 1.0)
            source: 출처
            evidence: 증거들
            
        Returns:
            bool: 추가 성공 여부
        """
        try:
            belief = Belief(
                id=belief_id,
                type=belief_type,
                content=content,
                confidence=confidence,
                last_updated=datetime.now(),
                source=source,
                evidence=evidence
            )
            
            self.beliefs[belief_id] = belief
            logger.info(f"철학 추가 완료: {belief_id}")
            return True
            
        except Exception as e:
            logger.error(f"철학 추가 실패: {belief_id}, 오류: {e}")
            return False
    
    def update_belief(self, belief_id: str, new_content: str = None, 
                     new_confidence: float = None, new_evidence: List[str] = None) -> bool:
        """
        기존 철학을 업데이트
        
        Args:
            belief_id: 철학 식별자
            new_content: 새로운 내용
            new_confidence: 새로운 신뢰도
            new_evidence: 새로운 증거들
            
        Returns:
            bool: 업데이트 성공 여부
        """
        if belief_id not in self.beliefs:
            logger.warning(f"존재하지 않는 철학: {belief_id}")
            return False
        
        try:
            belief = self.beliefs[belief_id]
            
            if new_content:
                belief.content = new_content
            if new_confidence is not None:
                belief.confidence = new_confidence
            if new_evidence:
                belief.evidence.extend(new_evidence)
            
            belief.last_updated = datetime.now()
            logger.info(f"철학 업데이트 완료: {belief_id}")
            return True
            
        except Exception as e:
            logger.error(f"철학 업데이트 실패: {belief_id}, 오류: {e}")
            return False
    
    def get_belief(self, belief_id: str) -> Optional[Belief]:
        """특정 철학을 조회"""
        return self.beliefs.get(belief_id)
    
    def get_beliefs_by_type(self, belief_type: BeliefType) -> List[Belief]:
        """특정 유형의 철학들을 조회"""
        return [belief for belief in self.beliefs.values() if belief.type == belief_type]
    
    def should_keep_failed_strategy(self, strategy_info: Dict[str, Any]) -> bool:
        """
        실패한 전략을 유지할지 판단
        
        Args:
            strategy_info: 전략 정보
            
        Returns:
            bool: 유지 여부
        """
        # 치명적 실패 판단 기준
        fatal_failure_indicators = [
            "system_crash",
            "data_corruption", 
            "security_violation",
            "performance_degradation_below_threshold"
        ]
        
        # 치명적 실패인 경우 제거
        for indicator in fatal_failure_indicators:
            if strategy_info.get(indicator, False):
                logger.info(f"치명적 실패로 인한 전략 제거: {strategy_info.get('strategy_id', 'unknown')}")
                return False
        
        # 일반적인 실패는 학습 기회로 활용
        return True
    
    def evaluate_creativity_vs_stability(self, creativity_score: float, 
                                       stability_score: float) -> Tuple[bool, str]:
        """
        창의성 vs 안정성 균형 평가
        
        Args:
            creativity_score: 창의성 점수 (0.0 ~ 1.0)
            stability_score: 안정성 점수 (0.0 ~ 1.0)
            
        Returns:
            Tuple[bool, str]: (승인 여부, 판단 근거)
        """
        # 창의성 임계값 확인
        if creativity_score < self.creativity_threshold:
            return False, f"창의성 점수({creativity_score})가 임계값({self.creativity_threshold}) 미만"
        
        # 안정성 임계값 확인
        if stability_score < self.stability_threshold:
            return False, f"안정성 점수({stability_score})가 임계값({self.stability_threshold}) 미만"
        
        # 균형 평가
        balance_score = (creativity_score + stability_score) / 2
        if balance_score >= 0.8:
            return True, f"창의성({creativity_score})과 안정성({stability_score})의 균형이 우수함"
        elif balance_score >= 0.6:
            return True, f"창의성({creativity_score})과 안정성({stability_score})의 균형이 양호함"
        else:
            return False, f"창의성({creativity_score})과 안정성({stability_score})의 균형이 부족함"
    
    def should_evolve(self, current_performance: float, 
                     improvement_potential: float) -> bool:
        """
        진화 여부 판단
        
        Args:
            current_performance: 현재 성능
            improvement_potential: 개선 잠재력
            
        Returns:
            bool: 진화 여부
        """
        # 현재 성능이 낮고 개선 잠재력이 높은 경우 진화
        if current_performance < 0.5 and improvement_potential > self.evolution_threshold:
            return True
        
        # 개선 잠재력이 매우 높은 경우 진화
        if improvement_potential > 0.8:
            return True
        
        return False
    
    def get_decision_framework(self) -> Dict[str, Any]:
        """의사결정 프레임워크 반환"""
        return {
            "learning_philosophy": self.get_beliefs_by_type(BeliefType.LEARNING_PHILOSOPHY),
            "creativity_philosophy": self.get_beliefs_by_type(BeliefType.CREATIVITY_PHILOSOPHY),
            "evolution_philosophy": self.get_beliefs_by_type(BeliefType.EVOLUTION_PHILOSOPHY),
            "ethics_philosophy": self.get_beliefs_by_type(BeliefType.ETHICS_PHILOSOPHY),
            "thresholds": {
                "creativity": self.creativity_threshold,
                "stability": self.stability_threshold,
                "evolution": self.evolution_threshold
            }
        }
    
    def save_beliefs(self, filepath: str) -> bool:
        """철학들을 파일로 저장"""
        try:
            beliefs_data = {
                belief_id: asdict(belief) for belief_id, belief in self.beliefs.items()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(beliefs_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"철학 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"철학 저장 실패: {filepath}, 오류: {e}")
            return False
    
    def load_beliefs(self, filepath: str) -> bool:
        """철학들을 파일에서 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                beliefs_data = json.load(f)
            
            self.beliefs.clear()
            for belief_id, belief_dict in beliefs_data.items():
                # datetime 문자열을 datetime 객체로 변환
                if 'last_updated' in belief_dict:
                    belief_dict['last_updated'] = datetime.fromisoformat(belief_dict['last_updated'])
                
                # BeliefType enum으로 변환
                if 'type' in belief_dict:
                    belief_dict['type'] = BeliefType(belief_dict['type'])
                
                belief = Belief(**belief_dict)
                self.beliefs[belief_id] = belief
            
            logger.info(f"철학 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"철학 로드 실패: {filepath}, 오류: {e}")
            return False
    
    def get_belief_summary(self) -> Dict[str, Any]:
        """철학 시스템 요약 정보"""
        return {
            "total_beliefs": len(self.beliefs),
            "beliefs_by_type": {
                belief_type.value: len(self.get_beliefs_by_type(belief_type))
                for belief_type in BeliefType
            },
            "average_confidence": sum(b.confidence for b in self.beliefs.values()) / len(self.beliefs) if self.beliefs else 0,
            "last_updated": max(b.last_updated for b in self.beliefs.values()) if self.beliefs else None
        }


# 싱글톤 인스턴스
_core_belief_instance = None

def get_core_belief() -> CoreBelief:
    """CoreBelief 싱글톤 인스턴스 반환"""
    global _core_belief_instance
    if _core_belief_instance is None:
        _core_belief_instance = CoreBelief()
    return _core_belief_instance 