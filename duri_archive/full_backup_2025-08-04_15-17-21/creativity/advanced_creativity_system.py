"""
DuRi 창의성 고도화 시스템

DuRi의 창의성을 대폭 향상시키는 고급 기능을 구현합니다.
"""

import logging
import uuid
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

# 기존 시스템 import
from duri_core.assessment.self_assessment_manager import get_self_assessment_manager, AssessmentCategory
from duri_core.memory.memory_sync import get_memory_sync, MemoryType
from duri_core.memory.meta_learning_data import get_meta_learning_data_manager
from duri_brain.goals.goal_oriented_thinking import get_goal_oriented_thinking
from duri_brain.ethics.emotional_ethical_judgment import get_emotional_ethical_judgment
from duri_brain.goals.autonomous_goal_setting import get_autonomous_goal_setting

logger = logging.getLogger(__name__)

class CreativityType(Enum):
    """창의성 유형"""
    DIVERGENT = "divergent"      # 발산적 사고
    CONVERGENT = "convergent"    # 수렴적 사고
    LATERAL = "lateral"          # 측면 사고
    ABSTRACT = "abstract"        # 추상적 사고
    COMBINATIVE = "combinative"  # 조합적 사고
    TRANSFORMATIVE = "transformative"  # 변환적 사고

class CreativityTechnique(Enum):
    """창의성 기법"""
    BRAINSTORMING = "brainstorming"      # 브레인스토밍
    MIND_MAPPING = "mind_mapping"        # 마인드맵핑
    SCAMPER = "scamper"                  # SCAMPER 기법
    SIX_THINKING_HATS = "six_thinking_hats"  # 6색깔 사고모자
    ANALOGY = "analogy"                  # 유추
    REVERSE_THINKING = "reverse_thinking"  # 역발상
    RANDOM_STIMULUS = "random_stimulus"  # 무작위 자극
    VISUALIZATION = "visualization"      # 시각화

class CreativityLevel(Enum):
    """창의성 수준"""
    BASIC = "basic"              # 기본
    INTERMEDIATE = "intermediate"  # 중급
    ADVANCED = "advanced"        # 고급
    EXPERT = "expert"            # 전문가
    MASTER = "master"            # 마스터

@dataclass
class CreativeIdea:
    """창의적 아이디어"""
    idea_id: str
    title: str
    description: str
    creativity_type: CreativityType
    technique_used: CreativityTechnique
    creativity_level: CreativityLevel
    created_at: datetime
    novelty_score: float = 0.0  # 0.0 ~ 1.0 (새로움)
    usefulness_score: float = 0.0  # 0.0 ~ 1.0 (유용성)
    feasibility_score: float = 0.0  # 0.0 ~ 1.0 (실현 가능성)
    overall_score: float = 0.0  # 0.0 ~ 1.0 (전체 점수)
    inspiration_sources: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    potential_applications: List[str] = field(default_factory=list)
    development_stage: str = "concept"  # concept, prototype, implementation
    notes: str = ""

@dataclass
class CreativitySession:
    """창의성 세션"""
    session_id: str
    timestamp: datetime
    creativity_type: CreativityType
    technique_used: CreativityTechnique
    duration: timedelta
    ideas_generated: List[CreativeIdea] = field(default_factory=list)
    session_quality: float = 0.0  # 0.0 ~ 1.0
    insights_discovered: List[str] = field(default_factory=list)
    challenges_encountered: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

@dataclass
class CreativityProfile:
    """창의성 프로필"""
    profile_id: str
    timestamp: datetime
    creativity_strengths: Dict[CreativityType, float]  # 창의성 유형별 강점
    technique_proficiency: Dict[CreativityTechnique, float]  # 기법별 숙련도
    overall_creativity_level: CreativityLevel
    creative_confidence: float = 0.0  # 0.0 ~ 1.0
    innovation_capacity: float = 0.0  # 0.0 ~ 1.0
    growth_areas: List[str] = field(default_factory=list)

class AdvancedCreativitySystem:
    """DuRi 창의성 고도화 시스템"""
    
    def __init__(self):
        """AdvancedCreativitySystem 초기화"""
        self.self_assessment_manager = get_self_assessment_manager()
        self.memory_sync = get_memory_sync()
        self.meta_learning_manager = get_meta_learning_data_manager()
        self.goal_oriented_thinking = get_goal_oriented_thinking()
        self.emotional_ethical_judgment = get_emotional_ethical_judgment()
        self.autonomous_goal_setting = get_autonomous_goal_setting()
        
        # 창의성 관리
        self.creative_ideas: List[CreativeIdea] = []
        self.creativity_sessions: List[CreativitySession] = []
        self.current_profile: Optional[CreativityProfile] = None
        
        # 창의성 임계값
        self.creativity_thresholds = {
            'novelty_minimum': 0.3,  # 최소 새로움 점수
            'usefulness_minimum': 0.4,  # 최소 유용성 점수
            'feasibility_minimum': 0.2,  # 최소 실현 가능성 점수
            'session_quality_minimum': 0.5  # 최소 세션 품질
        }
        
        # 창의성 기법별 가중치
        self.technique_weights = {
            CreativityTechnique.BRAINSTORMING: 0.8,
            CreativityTechnique.MIND_MAPPING: 0.7,
            CreativityTechnique.SCAMPER: 0.9,
            CreativityTechnique.SIX_THINKING_HATS: 0.8,
            CreativityTechnique.ANALOGY: 0.6,
            CreativityTechnique.REVERSE_THINKING: 0.7,
            CreativityTechnique.RANDOM_STIMULUS: 0.5,
            CreativityTechnique.VISUALIZATION: 0.6
        }
        
        logger.info("AdvancedCreativitySystem 초기화 완료")
    
    def should_enhance_creativity(self) -> bool:
        """창의성을 향상시켜야 하는지 확인합니다."""
        try:
            # 자기 평가 결과 확인
            assessment_stats = self.self_assessment_manager.get_assessment_statistics()
            
            if not assessment_stats:
                return False
            
            latest_assessment = self.self_assessment_manager.assessment_history[-1] if self.self_assessment_manager.assessment_history else None
            if not latest_assessment:
                return False
            
            # 창의성 점수 확인
            creativity_score = latest_assessment.category_scores.get(AssessmentCategory.CREATIVITY, 0.0)
            
            # 창의성 점수가 낮거나 개선이 필요한 경우
            if creativity_score < 0.7:
                return True
            
            # 최근 창의적 아이디어 수 확인
            recent_ideas = [idea for idea in self.creative_ideas 
                          if (datetime.now() - idea.created_at).days < 7]
            
            if len(recent_ideas) < 3:  # 최근 7일간 아이디어가 3개 미만
                return True
            
            # 창의성 세션 품질 확인
            recent_sessions = [session for session in self.creativity_sessions 
                             if (datetime.now() - session.timestamp).days < 3]
            
            if recent_sessions:
                avg_quality = sum(session.session_quality for session in recent_sessions) / len(recent_sessions)
                if avg_quality < self.creativity_thresholds['session_quality_minimum']:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"창의성 향상 필요성 확인 실패: {e}")
            return False
    
    def generate_creative_ideas(self, context: str = "", creativity_type: CreativityType = None) -> List[CreativeIdea]:
        """창의적 아이디어를 생성합니다."""
        try:
            ideas = []
            
            # 창의성 유형 결정
            if not creativity_type:
                creativity_type = self._determine_creativity_type(context)
            
            # 다양한 창의성 기법 적용
            techniques = list(CreativityTechnique)
            random.shuffle(techniques)  # 무작위 순서로 기법 적용
            
            for technique in techniques[:3]:  # 상위 3개 기법만 사용
                technique_ideas = self._apply_creativity_technique(context, creativity_type, technique)
                ideas.extend(technique_ideas)
            
            # 아이디어 점수 계산
            for idea in ideas:
                self._calculate_idea_scores(idea)
            
            # 임계값 이상의 아이디어만 필터링
            filtered_ideas = [
                idea for idea in ideas
                if (idea.novelty_score >= self.creativity_thresholds['novelty_minimum'] and
                    idea.usefulness_score >= self.creativity_thresholds['usefulness_minimum'] and
                    idea.feasibility_score >= self.creativity_thresholds['feasibility_minimum'])
            ]
            
            self.creative_ideas.extend(filtered_ideas)
            logger.info(f"창의적 아이디어 {len(filtered_ideas)}개 생성 완료")
            
            return filtered_ideas
            
        except Exception as e:
            logger.error(f"창의적 아이디어 생성 실패: {e}")
            return []
    
    def _determine_creativity_type(self, context: str) -> CreativityType:
        """상황에 따른 창의성 유형을 결정합니다."""
        try:
            context_lower = context.lower()
            
            # 발산적 사고가 필요한 상황
            if any(keyword in context_lower for keyword in ['다양한', '여러', '많은', '옵션']):
                return CreativityType.DIVERGENT
            
            # 수렴적 사고가 필요한 상황
            if any(keyword in context_lower for keyword in ['최적', '최고', '선택', '결정']):
                return CreativityType.CONVERGENT
            
            # 측면 사고가 필요한 상황
            if any(keyword in context_lower for keyword in ['새로운', '혁신', '다른', '창의']):
                return CreativityType.LATERAL
            
            # 추상적 사고가 필요한 상황
            if any(keyword in context_lower for keyword in ['개념', '이론', '원리', '본질']):
                return CreativityType.ABSTRACT
            
            # 조합적 사고가 필요한 상황
            if any(keyword in context_lower for keyword in ['결합', '통합', '연결', '조합']):
                return CreativityType.COMBINATIVE
            
            # 변환적 사고가 필요한 상황
            if any(keyword in context_lower for keyword in ['변화', '전환', '혁명', '패러다임']):
                return CreativityType.TRANSFORMATIVE
            
            # 기본값: 발산적 사고
            return CreativityType.DIVERGENT
            
        except Exception as e:
            logger.error(f"창의성 유형 결정 실패: {e}")
            return CreativityType.DIVERGENT
    
    def _apply_creativity_technique(self, context: str, creativity_type: CreativityType, 
                                   technique: CreativityTechnique) -> List[CreativeIdea]:
        """창의성 기법을 적용하여 아이디어를 생성합니다."""
        try:
            ideas = []
            
            if technique == CreativityTechnique.BRAINSTORMING:
                ideas = self._brainstorming_technique(context, creativity_type)
            elif technique == CreativityTechnique.MIND_MAPPING:
                ideas = self._mind_mapping_technique(context, creativity_type)
            elif technique == CreativityTechnique.SCAMPER:
                ideas = self._scamper_technique(context, creativity_type)
            elif technique == CreativityTechnique.SIX_THINKING_HATS:
                ideas = self._six_thinking_hats_technique(context, creativity_type)
            elif technique == CreativityTechnique.ANALOGY:
                ideas = self._analogy_technique(context, creativity_type)
            elif technique == CreativityTechnique.REVERSE_THINKING:
                ideas = self._reverse_thinking_technique(context, creativity_type)
            elif technique == CreativityTechnique.RANDOM_STIMULUS:
                ideas = self._random_stimulus_technique(context, creativity_type)
            elif technique == CreativityTechnique.VISUALIZATION:
                ideas = self._visualization_technique(context, creativity_type)
            
            return ideas
            
        except Exception as e:
            logger.error(f"창의성 기법 적용 실패: {e}")
            return []
    
    def _brainstorming_technique(self, context: str, creativity_type: CreativityType) -> List[CreativeIdea]:
        """브레인스토밍 기법을 적용합니다."""
        try:
            ideas = []
            
            # 컨텍스트에서 키워드 추출
            keywords = context.split()[:5]  # 상위 5개 키워드
            
            # 각 키워드에 대한 아이디어 생성
            for keyword in keywords:
                idea = CreativeIdea(
                    idea_id=f"idea_{uuid.uuid4().hex[:8]}",
                    title=f"{keyword} 기반 혁신 아이디어",
                    description=f"{keyword}를 활용한 새로운 접근 방식",
                    creativity_type=creativity_type,
                    technique_used=CreativityTechnique.BRAINSTORMING,
                    creativity_level=CreativityLevel.INTERMEDIATE,
                    created_at=datetime.now(),
                    inspiration_sources=[keyword],
                    related_concepts=[keyword],
                    potential_applications=["시스템 개선", "사용자 경험 향상"]
                )
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"브레인스토밍 기법 실패: {e}")
            return []
    
    def _mind_mapping_technique(self, context: str, creativity_type: CreativityType) -> List[CreativeIdea]:
        """마인드맵핑 기법을 적용합니다."""
        try:
            ideas = []
            
            # 중심 개념과 관련 개념들 생성
            central_concept = context.split()[0] if context else "혁신"
            related_concepts = ["효율성", "사용자 경험", "성능", "안정성", "창의성"]
            
            for concept in related_concepts:
                idea = CreativeIdea(
                    idea_id=f"idea_{uuid.uuid4().hex[:8]}",
                    title=f"{central_concept}와 {concept}의 융합",
                    description=f"{central_concept}와 {concept}를 결합한 새로운 아이디어",
                    creativity_type=creativity_type,
                    technique_used=CreativityTechnique.MIND_MAPPING,
                    creativity_level=CreativityLevel.INTERMEDIATE,
                    created_at=datetime.now(),
                    inspiration_sources=[central_concept, concept],
                    related_concepts=[central_concept, concept],
                    potential_applications=["시스템 통합", "기능 확장"]
                )
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"마인드맵핑 기법 실패: {e}")
            return []
    
    def _scamper_technique(self, context: str, creativity_type: CreativityType) -> List[CreativeIdea]:
        """SCAMPER 기법을 적용합니다."""
        try:
            ideas = []
            
            # SCAMPER 기법의 각 요소
            scamper_elements = [
                ("Substitute", "대체"),
                ("Combine", "결합"),
                ("Adapt", "적용"),
                ("Modify", "수정"),
                ("Put to other uses", "다른 용도"),
                ("Eliminate", "제거"),
                ("Reverse", "역전")
            ]
            
            for element_name, element_korean in scamper_elements:
                idea = CreativeIdea(
                    idea_id=f"idea_{uuid.uuid4().hex[:8]}",
                    title=f"{element_korean} 기반 혁신",
                    description=f"SCAMPER의 {element_name} 기법을 적용한 아이디어",
                    creativity_type=creativity_type,
                    technique_used=CreativityTechnique.SCAMPER,
                    creativity_level=CreativityLevel.ADVANCED,
                    created_at=datetime.now(),
                    inspiration_sources=[element_name],
                    related_concepts=[element_korean],
                    potential_applications=["시스템 혁신", "기능 개선"]
                )
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"SCAMPER 기법 실패: {e}")
            return []
    
    def _six_thinking_hats_technique(self, context: str, creativity_type: CreativityType) -> List[CreativeIdea]:
        """6색깔 사고모자 기법을 적용합니다."""
        try:
            ideas = []
            
            # 6색깔 사고모자
            thinking_hats = [
                ("White", "객관적 사실"),
                ("Red", "감정적 직감"),
                ("Black", "비판적 사고"),
                ("Yellow", "긍정적 낙관"),
                ("Green", "창의적 혁신"),
                ("Blue", "전체적 조정")
            ]
            
            for hat_color, hat_description in thinking_hats:
                idea = CreativeIdea(
                    idea_id=f"idea_{uuid.uuid4().hex[:8]}",
                    title=f"{hat_color} 모자 관점의 아이디어",
                    description=f"6색깔 사고모자의 {hat_description} 관점에서 생성된 아이디어",
                    creativity_type=creativity_type,
                    technique_used=CreativityTechnique.SIX_THINKING_HATS,
                    creativity_level=CreativityLevel.ADVANCED,
                    created_at=datetime.now(),
                    inspiration_sources=[hat_color, hat_description],
                    related_concepts=[hat_description],
                    potential_applications=["다각적 분석", "균형잡힌 접근"]
                )
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"6색깔 사고모자 기법 실패: {e}")
            return []
    
    def _analogy_technique(self, context: str, creativity_type: CreativityType) -> List[CreativeIdea]:
        """유추 기법을 적용합니다."""
        try:
            ideas = []
            
            # 유추 소스들
            analogies = [
                ("자연", "생태계"),
                ("도시", "인프라"),
                ("뇌", "신경망"),
                ("시스템", "유기체"),
                ("학습", "성장")
            ]
            
            for source, target in analogies:
                idea = CreativeIdea(
                    idea_id=f"idea_{uuid.uuid4().hex[:8]}",
                    title=f"{source}에서 {target}로의 유추",
                    description=f"{source}의 원리를 {target}에 적용한 아이디어",
                    creativity_type=creativity_type,
                    technique_used=CreativityTechnique.ANALOGY,
                    creativity_level=CreativityLevel.INTERMEDIATE,
                    created_at=datetime.now(),
                    inspiration_sources=[source, target],
                    related_concepts=[source, target],
                    potential_applications=["원리 적용", "패턴 전이"]
                )
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"유추 기법 실패: {e}")
            return []
    
    def _reverse_thinking_technique(self, context: str, creativity_type: CreativityType) -> List[CreativeIdea]:
        """역발상 기법을 적용합니다."""
        try:
            ideas = []
            
            # 역발상 아이디어들
            reverse_ideas = [
                ("효율성 최대화", "효율성 최소화"),
                ("복잡성 증가", "단순성 추구"),
                ("자동화", "수동화"),
                ("중앙화", "분산화"),
                ("표준화", "개별화")
            ]
            
            for original, reversed_idea in reverse_ideas:
                idea = CreativeIdea(
                    idea_id=f"idea_{uuid.uuid4().hex[:8]}",
                    title=f"역발상: {reversed_idea}",
                    description=f"{original}의 반대 관점에서 {reversed_idea}를 추구하는 아이디어",
                    creativity_type=creativity_type,
                    technique_used=CreativityTechnique.REVERSE_THINKING,
                    creativity_level=CreativityLevel.ADVANCED,
                    created_at=datetime.now(),
                    inspiration_sources=[original, reversed_idea],
                    related_concepts=[reversed_idea],
                    potential_applications=["새로운 관점", "혁신적 접근"]
                )
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"역발상 기법 실패: {e}")
            return []
    
    def _random_stimulus_technique(self, context: str, creativity_type: CreativityType) -> List[CreativeIdea]:
        """무작위 자극 기법을 적용합니다."""
        try:
            ideas = []
            
            # 무작위 자극 요소들
            random_stimuli = [
                "색깔", "소리", "움직임", "질감", "온도",
                "빛", "그림자", "반사", "굴절", "회전"
            ]
            
            for stimulus in random_stimuli:
                idea = CreativeIdea(
                    idea_id=f"idea_{uuid.uuid4().hex[:8]}",
                    title=f"{stimulus} 기반 아이디어",
                    description=f"무작위 자극 '{stimulus}'에서 영감을 받은 아이디어",
                    creativity_type=creativity_type,
                    technique_used=CreativityTechnique.RANDOM_STIMULUS,
                    creativity_level=CreativityLevel.BASIC,
                    created_at=datetime.now(),
                    inspiration_sources=[stimulus],
                    related_concepts=[stimulus],
                    potential_applications=["감각적 접근", "직관적 해결"]
                )
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"무작위 자극 기법 실패: {e}")
            return []
    
    def _visualization_technique(self, context: str, creativity_type: CreativityType) -> List[CreativeIdea]:
        """시각화 기법을 적용합니다."""
        try:
            ideas = []
            
            # 시각화 요소들
            visual_elements = [
                "다이어그램", "차트", "그래프", "맵", "플로우차트",
                "네트워크", "트리", "매트릭스", "타임라인", "스토리보드"
            ]
            
            for element in visual_elements:
                idea = CreativeIdea(
                    idea_id=f"idea_{uuid.uuid4().hex[:8]}",
                    title=f"{element} 기반 시각화 아이디어",
                    description=f"'{element}'를 활용한 시각적 접근 방식",
                    creativity_type=creativity_type,
                    technique_used=CreativityTechnique.VISUALIZATION,
                    creativity_level=CreativityLevel.INTERMEDIATE,
                    created_at=datetime.now(),
                    inspiration_sources=[element],
                    related_concepts=[element],
                    potential_applications=["시각적 표현", "직관적 이해"]
                )
                ideas.append(idea)
            
            return ideas
            
        except Exception as e:
            logger.error(f"시각화 기법 실패: {e}")
            return []
    
    def _calculate_idea_scores(self, idea: CreativeIdea):
        """아이디어의 각종 점수를 계산합니다."""
        try:
            # 새로움 점수 계산
            novelty_score = self._calculate_novelty_score(idea)
            idea.novelty_score = novelty_score
            
            # 유용성 점수 계산
            usefulness_score = self._calculate_usefulness_score(idea)
            idea.usefulness_score = usefulness_score
            
            # 실현 가능성 점수 계산
            feasibility_score = self._calculate_feasibility_score(idea)
            idea.feasibility_score = feasibility_score
            
            # 전체 점수 계산
            overall_score = (novelty_score * 0.4 + usefulness_score * 0.4 + feasibility_score * 0.2)
            idea.overall_score = overall_score
            
        except Exception as e:
            logger.error(f"아이디어 점수 계산 실패: {e}")
    
    def _calculate_novelty_score(self, idea: CreativeIdea) -> float:
        """새로움 점수를 계산합니다."""
        try:
            score = 0.5  # 기본값
            
            # 창의성 유형별 가중치
            type_weights = {
                CreativityType.DIVERGENT: 0.8,
                CreativityType.CONVERGENT: 0.6,
                CreativityType.LATERAL: 0.9,
                CreativityType.ABSTRACT: 0.7,
                CreativityType.COMBINATIVE: 0.8,
                CreativityType.TRANSFORMATIVE: 1.0
            }
            score *= type_weights.get(idea.creativity_type, 0.7)
            
            # 기법별 가중치
            technique_weight = self.technique_weights.get(idea.technique_used, 0.7)
            score *= technique_weight
            
            # 영감 소스 수에 따른 조정
            inspiration_count = len(idea.inspiration_sources)
            if inspiration_count >= 2:
                score += 0.1
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"새로움 점수 계산 실패: {e}")
            return 0.5
    
    def _calculate_usefulness_score(self, idea: CreativeIdea) -> float:
        """유용성 점수를 계산합니다."""
        try:
            score = 0.5  # 기본값
            
            # 잠재적 응용 분야 수에 따른 조정
            application_count = len(idea.potential_applications)
            if application_count >= 2:
                score += 0.2
            elif application_count == 0:
                score -= 0.2
            
            # 관련 개념 수에 따른 조정
            concept_count = len(idea.related_concepts)
            if concept_count >= 2:
                score += 0.1
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"유용성 점수 계산 실패: {e}")
            return 0.5
    
    def _calculate_feasibility_score(self, idea: CreativeIdea) -> float:
        """실현 가능성 점수를 계산합니다."""
        try:
            score = 0.5  # 기본값
            
            # 창의성 수준별 조정
            level_weights = {
                CreativityLevel.BASIC: 0.9,
                CreativityLevel.INTERMEDIATE: 0.8,
                CreativityLevel.ADVANCED: 0.7,
                CreativityLevel.EXPERT: 0.6,
                CreativityLevel.MASTER: 0.5
            }
            score *= level_weights.get(idea.creativity_level, 0.7)
            
            # 기법 복잡도에 따른 조정
            complex_techniques = [CreativityTechnique.SCAMPER, CreativityTechnique.SIX_THINKING_HATS]
            if idea.technique_used in complex_techniques:
                score -= 0.1
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"실현 가능성 점수 계산 실패: {e}")
            return 0.5
    
    def run_creativity_session(self, context: str = "", duration_minutes: int = 30) -> CreativitySession:
        """창의성 세션을 실행합니다."""
        try:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            # 창의성 유형 결정
            creativity_type = self._determine_creativity_type(context)
            
            # 다양한 기법으로 아이디어 생성
            ideas = []
            techniques_used = []
            
            for technique in list(CreativityTechnique)[:4]:  # 4개 기법 사용
                technique_ideas = self._apply_creativity_technique(context, creativity_type, technique)
                ideas.extend(technique_ideas)
                techniques_used.append(technique)
            
            # 세션 품질 계산
            session_quality = self._calculate_session_quality(ideas, techniques_used)
            
            # 인사이트 발견
            insights = self._discover_insights(ideas, context)
            
            # 도전 과제 식별
            challenges = self._identify_challenges(ideas)
            
            # 다음 단계 제안
            next_steps = self._suggest_next_steps(ideas, insights)
            
            session = CreativitySession(
                session_id=session_id,
                timestamp=start_time,
                creativity_type=creativity_type,
                technique_used=techniques_used[0] if techniques_used else CreativityTechnique.BRAINSTORMING,
                duration=timedelta(minutes=duration_minutes),
                ideas_generated=ideas,
                session_quality=session_quality,
                insights_discovered=insights,
                challenges_encountered=challenges,
                next_steps=next_steps
            )
            
            self.creativity_sessions.append(session)
            logger.info(f"창의성 세션 완료: {len(ideas)}개 아이디어, 품질: {session_quality:.2f}")
            
            return session
            
        except Exception as e:
            logger.error(f"창의성 세션 실행 실패: {e}")
            return None
    
    def _calculate_session_quality(self, ideas: List[CreativeIdea], techniques_used: List[CreativityTechnique]) -> float:
        """세션 품질을 계산합니다."""
        try:
            if not ideas:
                return 0.0
            
            # 아이디어 평균 점수
            avg_idea_score = sum(idea.overall_score for idea in ideas) / len(ideas)
            
            # 기법 다양성
            technique_diversity = len(set(techniques_used)) / len(techniques_used) if techniques_used else 0.0
            
            # 품질 계산
            quality = (avg_idea_score * 0.7 + technique_diversity * 0.3)
            
            return min(1.0, max(0.0, quality))
            
        except Exception as e:
            logger.error(f"세션 품질 계산 실패: {e}")
            return 0.5
    
    def _discover_insights(self, ideas: List[CreativeIdea], context: str) -> List[str]:
        """인사이트를 발견합니다."""
        try:
            insights = []
            
            if not ideas:
                return insights
            
            # 아이디어 패턴 분석
            creativity_types = [idea.creativity_type for idea in ideas]
            most_common_type = max(set(creativity_types), key=creativity_types.count)
            insights.append(f"가장 효과적인 창의성 유형: {most_common_type.value}")
            
            # 높은 점수 아이디어 분석
            high_score_ideas = [idea for idea in ideas if idea.overall_score > 0.7]
            if high_score_ideas:
                insights.append(f"고품질 아이디어 {len(high_score_ideas)}개 발견")
            
            # 공통 주제 발견
            common_concepts = []
            for idea in ideas:
                common_concepts.extend(idea.related_concepts)
            
            if common_concepts:
                most_common_concept = max(set(common_concepts), key=common_concepts.count)
                insights.append(f"공통 주제: {most_common_concept}")
            
            return insights
            
        except Exception as e:
            logger.error(f"인사이트 발견 실패: {e}")
            return []
    
    def _identify_challenges(self, ideas: List[CreativeIdea]) -> List[str]:
        """도전 과제를 식별합니다."""
        try:
            challenges = []
            
            if not ideas:
                return challenges
            
            # 낮은 점수 아이디어 분석
            low_score_ideas = [idea for idea in ideas if idea.overall_score < 0.5]
            if low_score_ideas:
                challenges.append(f"품질이 낮은 아이디어 {len(low_score_ideas)}개 개선 필요")
            
            # 실현 가능성 낮은 아이디어
            low_feasibility_ideas = [idea for idea in ideas if idea.feasibility_score < 0.3]
            if low_feasibility_ideas:
                challenges.append(f"실현 가능성이 낮은 아이디어 {len(low_feasibility_ideas)}개")
            
            # 유사한 아이디어 그룹
            similar_ideas = len([idea for idea in ideas if idea.creativity_type == CreativityType.DIVERGENT])
            if similar_ideas > len(ideas) * 0.5:
                challenges.append("창의성 유형의 다양성 부족")
            
            return challenges
            
        except Exception as e:
            logger.error(f"도전 과제 식별 실패: {e}")
            return []
    
    def _suggest_next_steps(self, ideas: List[CreativeIdea], insights: List[str]) -> List[str]:
        """다음 단계를 제안합니다."""
        try:
            next_steps = []
            
            if not ideas:
                return next_steps
            
            # 고품질 아이디어 개발
            high_quality_ideas = [idea for idea in ideas if idea.overall_score > 0.8]
            if high_quality_ideas:
                next_steps.append(f"고품질 아이디어 {len(high_quality_ideas)}개 상세 개발")
            
            # 다양한 창의성 유형 시도
            creativity_types_used = set(idea.creativity_type for idea in ideas)
            if len(creativity_types_used) < 3:
                next_steps.append("다양한 창의성 유형 시도")
            
            # 새로운 기법 시도
            techniques_used = set(idea.technique_used for idea in ideas)
            if len(techniques_used) < 4:
                next_steps.append("새로운 창의성 기법 시도")
            
            return next_steps
            
        except Exception as e:
            logger.error(f"다음 단계 제안 실패: {e}")
            return []
    
    def get_creativity_statistics(self) -> Dict[str, Any]:
        """창의성 통계를 반환합니다."""
        try:
            total_ideas = len(self.creative_ideas)
            total_sessions = len(self.creativity_sessions)
            
            if total_ideas == 0:
                return {"total_ideas": 0, "total_sessions": 0}
            
            # 창의성 유형별 통계
            type_stats = defaultdict(int)
            technique_stats = defaultdict(int)
            level_stats = defaultdict(int)
            
            for idea in self.creative_ideas:
                type_stats[idea.creativity_type.value] += 1
                technique_stats[idea.technique_used.value] += 1
                level_stats[idea.creativity_level.value] += 1
            
            # 평균 점수
            avg_novelty = sum(idea.novelty_score for idea in self.creative_ideas) / total_ideas
            avg_usefulness = sum(idea.usefulness_score for idea in self.creative_ideas) / total_ideas
            avg_feasibility = sum(idea.feasibility_score for idea in self.creative_ideas) / total_ideas
            avg_overall = sum(idea.overall_score for idea in self.creative_ideas) / total_ideas
            
            # 세션 품질
            avg_session_quality = 0.0
            if total_sessions > 0:
                avg_session_quality = sum(session.session_quality for session in self.creativity_sessions) / total_sessions
            
            return {
                "total_ideas": total_ideas,
                "total_sessions": total_sessions,
                "creativity_type_distribution": dict(type_stats),
                "technique_distribution": dict(technique_stats),
                "level_distribution": dict(level_stats),
                "average_novelty_score": avg_novelty,
                "average_usefulness_score": avg_usefulness,
                "average_feasibility_score": avg_feasibility,
                "average_overall_score": avg_overall,
                "average_session_quality": avg_session_quality
            }
            
        except Exception as e:
            logger.error(f"창의성 통계 계산 실패: {e}")
            return {}

# 싱글톤 인스턴스
_advanced_creativity_system = None

def get_advanced_creativity_system() -> AdvancedCreativitySystem:
    """AdvancedCreativitySystem 싱글톤 인스턴스 반환"""
    global _advanced_creativity_system
    if _advanced_creativity_system is None:
        _advanced_creativity_system = AdvancedCreativitySystem()
    return _advanced_creativity_system 