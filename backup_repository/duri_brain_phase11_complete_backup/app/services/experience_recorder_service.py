"""
Phase 10: 세대 경험 기록 시스템 (GenerationalExperienceRecorder)
DuRi의 모든 경험을 세대 교훈으로 기록하고 구조화하는 시스템
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperienceType(Enum):
    """경험 유형 정의"""
    DAILY_LIFE = "daily_life"
    FAMILY_INTERACTION = "family_interaction"
    LEARNING = "learning"
    EMOTIONAL = "emotional"
    PROBLEM_SOLVING = "problem_solving"
    CREATIVE = "creative"
    SOCIAL = "social"
    CHALLENGE = "challenge"
    SUCCESS = "success"
    FAILURE = "failure"

class ExperienceCategory(Enum):
    """경험 카테고리 정의"""
    PERSONAL_GROWTH = "personal_growth"
    RELATIONSHIP = "relationship"
    SKILL_DEVELOPMENT = "skill_development"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    CREATIVITY = "creativity"
    PROBLEM_SOLVING = "problem_solving"
    SOCIAL_SKILLS = "social_skills"
    FAMILY_DYNAMICS = "family_dynamics"

class LessonType(Enum):
    """교훈 유형 정의"""
    LIFE_LESSON = "life_lesson"
    SKILL_LESSON = "skill_lesson"
    EMOTIONAL_LESSON = "emotional_lesson"
    RELATIONSHIP_LESSON = "relationship_lesson"
    PROBLEM_SOLVING_LESSON = "problem_solving_lesson"
    CREATIVE_LESSON = "creative_lesson"

@dataclass
class Experience:
    """경험 데이터 구조"""
    id: str
    type: ExperienceType
    category: ExperienceCategory
    title: str
    description: str
    emotional_impact: float  # -1.0 to 1.0
    learning_value: float    # 0.0 to 1.0
    family_context: Dict[str, Any]
    timestamp: datetime
    duration_minutes: int
    participants: List[str]
    location: str
    weather: Optional[str] = None
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ExtractedLesson:
    """추출된 교훈 데이터 구조"""
    id: str
    experience_id: str
    lesson_type: LessonType
    title: str
    description: str
    key_insights: List[str]
    applicable_situations: List[str]
    family_specific: bool
    generational_value: float  # 0.0 to 1.0
    confidence_score: float    # 0.0 to 1.0
    extraction_timestamp: datetime
    tags: List[str]
    
    def __post_init__(self):
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now()

@dataclass
class ExperiencePattern:
    """경험 패턴 데이터 구조"""
    id: str
    pattern_type: str
    frequency: int
    average_emotional_impact: float
    average_learning_value: float
    common_elements: List[str]
    family_members_involved: List[str]
    time_of_day: Optional[str]
    day_of_week: Optional[str]
    season: Optional[str]
    pattern_significance: float  # 0.0 to 1.0

class GenerationalExperienceRecorder:
    """
    세대 경험 기록 시스템
    DuRi의 모든 경험을 세대 교훈으로 기록하고 구조화
    """
    
    def __init__(self):
        self.experiences: List[Experience] = []
        self.extracted_lessons: List[ExtractedLesson] = []
        self.experience_patterns: List[ExperiencePattern] = []
        self.family_context_history: List[Dict] = []
        self.emotional_trajectory: List[Dict] = []
        self.learning_progress: Dict[str, float] = {}
        
        logger.info("GenerationalExperienceRecorder 초기화 완료")
    
    def record_experience(self, experience_data: Dict) -> Experience:
        """
        새로운 경험 기록
        """
        try:
            experience = Experience(
                id=str(uuid.uuid4()),
                type=ExperienceType(experience_data['type']),
                category=ExperienceCategory(experience_data['category']),
                title=experience_data['title'],
                description=experience_data['description'],
                emotional_impact=experience_data['emotional_impact'],
                learning_value=experience_data['learning_value'],
                family_context=experience_data.get('family_context', {}),
                timestamp=datetime.now(),
                duration_minutes=experience_data.get('duration_minutes', 0),
                participants=experience_data.get('participants', []),
                location=experience_data.get('location', 'unknown'),
                weather=experience_data.get('weather'),
                mood_before=experience_data.get('mood_before'),
                mood_after=experience_data.get('mood_after')
            )
            
            self.experiences.append(experience)
            
            # 감정 궤적 업데이트
            self._update_emotional_trajectory(experience)
            
            # 학습 진행도 업데이트
            self._update_learning_progress(experience)
            
            # 패턴 분석
            self._analyze_experience_patterns()
            
            logger.info(f"경험 기록 완료: {experience.title}")
            return experience
            
        except Exception as e:
            logger.error(f"경험 기록 실패: {e}")
            raise
    
    def extract_lesson_from_experience(self, experience_id: str) -> ExtractedLesson:
        """
        경험에서 교훈 추출
        """
        try:
            experience = next((exp for exp in self.experiences if exp.id == experience_id), None)
            if not experience:
                raise ValueError(f"경험을 찾을 수 없습니다: {experience_id}")
            
            # 교훈 추출 로직
            lesson_type = self._determine_lesson_type(experience)
            key_insights = self._extract_key_insights(experience)
            applicable_situations = self._identify_applicable_situations(experience)
            
            lesson = ExtractedLesson(
                id=str(uuid.uuid4()),
                experience_id=experience_id,
                lesson_type=lesson_type,
                title=f"교훈: {experience.title}",
                description=self._generate_lesson_description(experience),
                key_insights=key_insights,
                applicable_situations=applicable_situations,
                family_specific=self._is_family_specific(experience),
                generational_value=self._calculate_generational_value(experience),
                confidence_score=self._calculate_confidence_score(experience),
                extraction_timestamp=datetime.now(),
                tags=self._generate_tags(experience)
            )
            
            self.extracted_lessons.append(lesson)
            
            logger.info(f"교훈 추출 완료: {lesson.title}")
            return lesson
            
        except Exception as e:
            logger.error(f"교훈 추출 실패: {e}")
            raise
    
    def get_experience_insights(self, time_period_days: int = 30) -> Dict:
        """
        경험 통찰력 제공
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=time_period_days)
            recent_experiences = [exp for exp in self.experiences if exp.timestamp >= cutoff_date]
            
            insights = {
                'total_experiences': len(recent_experiences),
                'experience_distribution': self._get_experience_distribution(recent_experiences),
                'emotional_trends': self._analyze_emotional_trends(recent_experiences),
                'learning_progress': self._analyze_learning_progress(recent_experiences),
                'family_interaction_patterns': self._analyze_family_patterns(recent_experiences),
                'top_lessons': self._get_top_lessons(recent_experiences),
                'growth_areas': self._identify_growth_areas(recent_experiences)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"경험 통찰력 생성 실패: {e}")
            raise
    
    def get_generational_wisdom(self) -> Dict:
        """
        세대 지혜 수집
        """
        try:
            wisdom = {
                'life_lessons': self._collect_life_lessons(),
                'skill_lessons': self._collect_skill_lessons(),
                'emotional_lessons': self._collect_emotional_lessons(),
                'relationship_lessons': self._collect_relationship_lessons(),
                'family_specific_lessons': self._collect_family_specific_lessons(),
                'wisdom_summary': self._generate_wisdom_summary()
            }
            
            return wisdom
            
        except Exception as e:
            logger.error(f"세대 지혜 수집 실패: {e}")
            raise
    
    def _update_emotional_trajectory(self, experience: Experience):
        """감정 궤적 업데이트"""
        trajectory_entry = {
            'timestamp': experience.timestamp,
            'emotional_impact': experience.emotional_impact,
            'experience_type': experience.type.value,
            'mood_before': experience.mood_before,
            'mood_after': experience.mood_after
        }
        self.emotional_trajectory.append(trajectory_entry)
    
    def _update_learning_progress(self, experience: Experience):
        """학습 진행도 업데이트"""
        category = experience.category.value
        if category not in self.learning_progress:
            self.learning_progress[category] = 0.0
        
        # 학습 진행도 계산 (경험의 학습 가치와 감정적 영향 고려)
        progress_increment = experience.learning_value * (1 + abs(experience.emotional_impact))
        self.learning_progress[category] = min(1.0, self.learning_progress[category] + progress_increment)
    
    def _analyze_experience_patterns(self):
        """경험 패턴 분석"""
        if len(self.experiences) < 5:  # 최소 5개 경험 필요
            return
        
        # 시간대별 패턴
        time_patterns = self._analyze_time_patterns()
        # 가족 구성원별 패턴
        family_patterns = self._analyze_family_patterns()
        # 감정적 패턴
        emotional_patterns = self._analyze_emotional_patterns()
        
        # 패턴 통합
        for pattern in time_patterns + family_patterns + emotional_patterns:
            if pattern['significance'] > 0.6:  # 의미있는 패턴만 저장
                experience_pattern = ExperiencePattern(
                    id=str(uuid.uuid4()),
                    pattern_type=pattern['type'],
                    frequency=pattern['frequency'],
                    average_emotional_impact=pattern['avg_emotional_impact'],
                    average_learning_value=pattern['avg_learning_value'],
                    common_elements=pattern['common_elements'],
                    family_members_involved=pattern['family_members'],
                    time_of_day=pattern.get('time_of_day'),
                    day_of_week=pattern.get('day_of_week'),
                    season=pattern.get('season'),
                    pattern_significance=pattern['significance']
                )
                self.experience_patterns.append(experience_pattern)
    
    def _determine_lesson_type(self, experience: Experience) -> LessonType:
        """교훈 유형 결정"""
        if experience.category == ExperienceCategory.PERSONAL_GROWTH:
            return LessonType.LIFE_LESSON
        elif experience.category == ExperienceCategory.SKILL_DEVELOPMENT:
            return LessonType.SKILL_LESSON
        elif experience.category == ExperienceCategory.EMOTIONAL_INTELLIGENCE:
            return LessonType.EMOTIONAL_LESSON
        elif experience.category == ExperienceCategory.RELATIONSHIP:
            return LessonType.RELATIONSHIP_LESSON
        elif experience.category == ExperienceCategory.PROBLEM_SOLVING:
            return LessonType.PROBLEM_SOLVING_LESSON
        elif experience.category == ExperienceCategory.CREATIVITY:
            return LessonType.CREATIVE_LESSON
        else:
            return LessonType.LIFE_LESSON
    
    def _extract_key_insights(self, experience: Experience) -> List[str]:
        """핵심 통찰력 추출"""
        insights = []
        
        # 감정적 통찰력
        if abs(experience.emotional_impact) > 0.5:
            if experience.emotional_impact > 0:
                insights.append("긍정적인 경험은 성장의 원동력이 됨")
            else:
                insights.append("어려운 상황에서도 배울 점이 있음")
        
        # 학습 가치 통찰력
        if experience.learning_value > 0.7:
            insights.append("실습을 통한 학습이 가장 효과적")
        
        # 가족 맥락 통찰력
        if experience.family_context:
            insights.append("가족과의 상호작용이 개인 성장에 중요")
        
        return insights
    
    def _identify_applicable_situations(self, experience: Experience) -> List[str]:
        """적용 가능한 상황 식별"""
        situations = []
        
        if experience.type == ExperienceType.FAMILY_INTERACTION:
            situations.extend([
                "가족 갈등 해결",
                "가족 소통 개선",
                "가족 활동 계획"
            ])
        
        if experience.type == ExperienceType.EMOTIONAL:
            situations.extend([
                "감정 관리",
                "스트레스 대처",
                "타인 감정 이해"
            ])
        
        if experience.type == ExperienceType.PROBLEM_SOLVING:
            situations.extend([
                "문제 해결",
                "의사결정",
                "위기 대응"
            ])
        
        return situations
    
    def _generate_lesson_description(self, experience: Experience) -> str:
        """교훈 설명 생성"""
        base_description = f"{experience.title}을 통해 "
        
        if experience.learning_value > 0.8:
            base_description += "중요한 교훈을 얻었습니다. "
        elif experience.learning_value > 0.5:
            base_description += "유용한 경험을 했습니다. "
        else:
            base_description += "경험을 쌓았습니다. "
        
        if experience.emotional_impact > 0.5:
            base_description += "이 경험은 감정적으로 깊은 인상을 남겼습니다."
        elif experience.emotional_impact < -0.5:
            base_description += "이 경험은 도전적이었지만 성장의 기회가 되었습니다."
        
        return base_description
    
    def _is_family_specific(self, experience: Experience) -> bool:
        """가족 특화 여부 판단"""
        return (experience.type == ExperienceType.FAMILY_INTERACTION or
                'family' in experience.description.lower() or
                len(experience.participants) > 1)
    
    def _calculate_generational_value(self, experience: Experience) -> float:
        """세대 가치 계산"""
        base_value = experience.learning_value * 0.4
        emotional_factor = abs(experience.emotional_impact) * 0.3
        family_factor = 0.3 if self._is_family_specific(experience) else 0.1
        
        return min(1.0, base_value + emotional_factor + family_factor)
    
    def _calculate_confidence_score(self, experience: Experience) -> float:
        """신뢰도 점수 계산"""
        # 경험의 품질과 일관성을 기반으로 계산
        quality_score = experience.learning_value * 0.5
        emotional_clarity = abs(experience.emotional_impact) * 0.3
        detail_score = len(experience.description) / 100 * 0.2  # 설명의 상세함
        
        return min(1.0, quality_score + emotional_clarity + detail_score)
    
    def _generate_tags(self, experience: Experience) -> List[str]:
        """태그 생성"""
        tags = [
            experience.type.value,
            experience.category.value,
            f"emotional_{'positive' if experience.emotional_impact > 0 else 'negative'}",
            f"learning_{'high' if experience.learning_value > 0.7 else 'medium' if experience.learning_value > 0.4 else 'low'}"
        ]
        
        if self._is_family_specific(experience):
            tags.append("family_specific")
        
        return tags
    
    def _analyze_time_patterns(self) -> List[Dict]:
        """시간 패턴 분석"""
        patterns = []
        
        # 시간대별 분석
        morning_experiences = [exp for exp in self.experiences if exp.timestamp.hour < 12]
        afternoon_experiences = [exp for exp in self.experiences if 12 <= exp.timestamp.hour < 18]
        evening_experiences = [exp for exp in self.experiences if exp.timestamp.hour >= 18]
        
        for time_period, experiences in [("morning", morning_experiences), 
                                       ("afternoon", afternoon_experiences), 
                                       ("evening", evening_experiences)]:
            if len(experiences) >= 3:
                avg_emotional = sum(exp.emotional_impact for exp in experiences) / len(experiences)
                avg_learning = sum(exp.learning_value for exp in experiences) / len(experiences)
                
                patterns.append({
                    'type': f'time_pattern_{time_period}',
                    'frequency': len(experiences),
                    'avg_emotional_impact': avg_emotional,
                    'avg_learning_value': avg_learning,
                    'common_elements': [exp.type.value for exp in experiences[:3]],
                    'family_members': [],
                    'time_of_day': time_period,
                    'significance': len(experiences) / len(self.experiences)
                })
        
        return patterns
    
    def _analyze_family_patterns(self, experiences: List[Experience] = None) -> List[Dict]:
        """가족 패턴 분석"""
        if experiences is None:
            experiences = self.experiences
            
        family_experiences = [exp for exp in experiences if exp.type == ExperienceType.FAMILY_INTERACTION]
        
        if len(family_experiences) >= 3:
            avg_emotional = sum(exp.emotional_impact for exp in family_experiences) / len(family_experiences)
            avg_learning = sum(exp.learning_value for exp in family_experiences) / len(family_experiences)
            
            return [{
                'type': 'family_interaction_pattern',
                'frequency': len(family_experiences),
                'avg_emotional_impact': avg_emotional,
                'avg_learning_value': avg_learning,
                'common_elements': ['family_interaction'],
                'family_members': list(set([member for exp in family_experiences for member in exp.participants])),
                'significance': len(family_experiences) / len(experiences) if experiences else 0
            }]
        
        return []
    
    def _analyze_emotional_patterns(self) -> List[Dict]:
        """감정 패턴 분석"""
        positive_experiences = [exp for exp in self.experiences if exp.emotional_impact > 0.3]
        negative_experiences = [exp for exp in self.experiences if exp.emotional_impact < -0.3]
        
        patterns = []
        
        if len(positive_experiences) >= 3:
            avg_learning = sum(exp.learning_value for exp in positive_experiences) / len(positive_experiences)
            patterns.append({
                'type': 'positive_emotional_pattern',
                'frequency': len(positive_experiences),
                'avg_emotional_impact': 0.6,
                'avg_learning_value': avg_learning,
                'common_elements': [exp.type.value for exp in positive_experiences[:3]],
                'family_members': [],
                'significance': len(positive_experiences) / len(self.experiences)
            })
        
        if len(negative_experiences) >= 3:
            avg_learning = sum(exp.learning_value for exp in negative_experiences) / len(negative_experiences)
            patterns.append({
                'type': 'negative_emotional_pattern',
                'frequency': len(negative_experiences),
                'avg_emotional_impact': -0.6,
                'avg_learning_value': avg_learning,
                'common_elements': [exp.type.value for exp in negative_experiences[:3]],
                'family_members': [],
                'significance': len(negative_experiences) / len(self.experiences)
            })
        
        return patterns
    
    def _get_experience_distribution(self, experiences: List[Experience]) -> Dict:
        """경험 분포 분석"""
        distribution = {}
        for exp_type in ExperienceType:
            count = len([exp for exp in experiences if exp.type == exp_type])
            if count > 0:
                distribution[exp_type.value] = count
        
        return distribution
    
    def _analyze_emotional_trends(self, experiences: List[Experience]) -> Dict:
        """감정적 트렌드 분석"""
        if not experiences:
            return {'trend': 'stable', 'average_impact': 0.0}
        
        # 시간순 정렬
        sorted_experiences = sorted(experiences, key=lambda x: x.timestamp)
        
        # 트렌드 계산
        early_avg = sum(exp.emotional_impact for exp in sorted_experiences[:len(sorted_experiences)//2]) / (len(sorted_experiences)//2)
        late_avg = sum(exp.emotional_impact for exp in sorted_experiences[len(sorted_experiences)//2:]) / (len(sorted_experiences)//2)
        
        if late_avg > early_avg + 0.1:
            trend = 'improving'
        elif late_avg < early_avg - 0.1:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'average_impact': sum(exp.emotional_impact for exp in experiences) / len(experiences),
            'early_period_average': early_avg,
            'late_period_average': late_avg
        }
    
    def _analyze_learning_progress(self, experiences: List[Experience]) -> Dict:
        """학습 진행도 분석"""
        return {
            'current_progress': self.learning_progress,
            'recent_learning_focus': self._get_recent_learning_focus(experiences),
            'growth_areas': self._identify_growth_areas(experiences)
        }
    
    def _get_recent_learning_focus(self, experiences: List[Experience]) -> List[str]:
        """최근 학습 초점 영역"""
        if not experiences:
            return []
        
        # 최근 7일간의 경험
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_experiences = [exp for exp in experiences if exp.timestamp >= recent_cutoff]
        
        if not recent_experiences:
            return []
        
        # 카테고리별 학습 가치 합계
        category_learning = {}
        for exp in recent_experiences:
            category = exp.category.value
            if category not in category_learning:
                category_learning[category] = 0
            category_learning[category] += exp.learning_value
        
        # 상위 3개 카테고리 반환
        sorted_categories = sorted(category_learning.items(), key=lambda x: x[1], reverse=True)
        return [category for category, _ in sorted_categories[:3]]
    
    def _identify_growth_areas(self, experiences: List[Experience]) -> List[str]:
        """성장 영역 식별"""
        if not experiences:
            return []
        
        # 카테고리별 평균 학습 가치
        category_learning = {}
        for exp in experiences:
            category = exp.category.value
            if category not in category_learning:
                category_learning[category] = []
            category_learning[category].append(exp.learning_value)
        
        # 평균 계산
        category_averages = {}
        for category, values in category_learning.items():
            category_averages[category] = sum(values) / len(values)
        
        # 낮은 학습 가치를 가진 영역 식별
        growth_areas = []
        for category, avg_learning in category_averages.items():
            if avg_learning < 0.5:  # 임계값
                growth_areas.append(category)
        
        return growth_areas
    
    def _get_top_lessons(self, experiences: List[Experience]) -> List[Dict]:
        """상위 교훈 반환"""
        if not experiences:
            return []
        
        # 높은 학습 가치를 가진 경험들
        high_value_experiences = [exp for exp in experiences if exp.learning_value > 0.7]
        
        # 학습 가치 순으로 정렬
        sorted_experiences = sorted(high_value_experiences, key=lambda x: x.learning_value, reverse=True)
        
        top_lessons = []
        for exp in sorted_experiences[:5]:  # 상위 5개
            lesson = {
                'title': exp.title,
                'learning_value': exp.learning_value,
                'category': exp.category.value,
                'timestamp': exp.timestamp.isoformat()
            }
            top_lessons.append(lesson)
        
        return top_lessons
    
    def _collect_life_lessons(self) -> List[Dict]:
        """인생 교훈 수집"""
        life_lessons = [lesson for lesson in self.extracted_lessons if lesson.lesson_type == LessonType.LIFE_LESSON]
        return [asdict(lesson) for lesson in life_lessons]
    
    def _collect_skill_lessons(self) -> List[Dict]:
        """기술 교훈 수집"""
        skill_lessons = [lesson for lesson in self.extracted_lessons if lesson.lesson_type == LessonType.SKILL_LESSON]
        return [asdict(lesson) for lesson in skill_lessons]
    
    def _collect_emotional_lessons(self) -> List[Dict]:
        """감정 교훈 수집"""
        emotional_lessons = [lesson for lesson in self.extracted_lessons if lesson.lesson_type == LessonType.EMOTIONAL_LESSON]
        return [asdict(lesson) for lesson in emotional_lessons]
    
    def _collect_relationship_lessons(self) -> List[Dict]:
        """관계 교훈 수집"""
        relationship_lessons = [lesson for lesson in self.extracted_lessons if lesson.lesson_type == LessonType.RELATIONSHIP_LESSON]
        return [asdict(lesson) for lesson in relationship_lessons]
    
    def _collect_family_specific_lessons(self) -> List[Dict]:
        """가족 특화 교훈 수집"""
        family_lessons = [lesson for lesson in self.extracted_lessons if lesson.family_specific]
        return [asdict(lesson) for lesson in family_lessons]
    
    def _generate_wisdom_summary(self) -> Dict:
        """지혜 요약 생성"""
        total_lessons = len(self.extracted_lessons)
        family_lessons = len([l for l in self.extracted_lessons if l.family_specific])
        
        return {
            'total_lessons': total_lessons,
            'family_specific_lessons': family_lessons,
            'average_generational_value': sum(l.generational_value for l in self.extracted_lessons) / total_lessons if total_lessons > 0 else 0,
            'top_categories': self._get_top_lesson_categories(),
            'wisdom_strength': self._calculate_wisdom_strength()
        }
    
    def _get_top_lesson_categories(self) -> List[str]:
        """상위 교훈 카테고리"""
        category_counts = {}
        for lesson in self.extracted_lessons:
            category = lesson.lesson_type.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        return [category for category, _ in sorted_categories[:3]]
    
    def _calculate_wisdom_strength(self) -> float:
        """지혜 강도 계산"""
        if not self.extracted_lessons:
            return 0.0
        
        avg_generational_value = sum(l.generational_value for l in self.extracted_lessons) / len(self.extracted_lessons)
        avg_confidence = sum(l.confidence_score for l in self.extracted_lessons) / len(self.extracted_lessons)
        family_factor = len([l for l in self.extracted_lessons if l.family_specific]) / len(self.extracted_lessons)
        
        return (avg_generational_value * 0.4 + avg_confidence * 0.4 + family_factor * 0.2)
    
    def export_experience_data(self) -> Dict:
        """경험 데이터 내보내기"""
        return {
            'experiences': [asdict(exp) for exp in self.experiences],
            'extracted_lessons': [asdict(lesson) for lesson in self.extracted_lessons],
            'experience_patterns': [asdict(pattern) for pattern in self.experience_patterns],
            'emotional_trajectory': self.emotional_trajectory,
            'learning_progress': self.learning_progress,
            'insights': self.get_experience_insights(),
            'generational_wisdom': self.get_generational_wisdom()
        }
    
    def import_experience_data(self, data: Dict):
        """경험 데이터 가져오기"""
        try:
            # 경험 데이터 복원
            self.experiences = []
            for exp_data in data.get('experiences', []):
                exp_data['timestamp'] = datetime.fromisoformat(exp_data['timestamp'])
                exp_data['type'] = ExperienceType(exp_data['type'])
                exp_data['category'] = ExperienceCategory(exp_data['category'])
                self.experiences.append(Experience(**exp_data))
            
            # 교훈 데이터 복원
            self.extracted_lessons = []
            for lesson_data in data.get('extracted_lessons', []):
                lesson_data['extraction_timestamp'] = datetime.fromisoformat(lesson_data['extraction_timestamp'])
                lesson_data['lesson_type'] = LessonType(lesson_data['lesson_type'])
                self.extracted_lessons.append(ExtractedLesson(**lesson_data))
            
            # 패턴 데이터 복원
            self.experience_patterns = []
            for pattern_data in data.get('experience_patterns', []):
                self.experience_patterns.append(ExperiencePattern(**pattern_data))
            
            # 기타 데이터 복원
            self.emotional_trajectory = data.get('emotional_trajectory', [])
            self.learning_progress = data.get('learning_progress', {})
            
            logger.info("경험 데이터 가져오기 완료")
            
        except Exception as e:
            logger.error(f"경험 데이터 가져오기 실패: {e}")
            raise 