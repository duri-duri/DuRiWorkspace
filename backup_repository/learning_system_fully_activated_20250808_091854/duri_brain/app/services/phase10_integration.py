"""
Phase 10: 통합 시스템 (Phase10Integration)
가족 정체성, 경험 기록, 관계 형성, 교훈 추출 시스템들을 통합하는 메인 시스템
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Phase 10 시스템들 import
from .family_identity_service import FamilyIdentityCore, FamilyIdentity, FamilyMember, FamilyCulture
from .experience_recorder_service import GenerationalExperienceRecorder, Experience, ExtractedLesson
from .relationship_formation_service import FamilyRelationshipFormationSystem, Interaction, RoleUnderstanding
from .lesson_extractor_service import BasicLessonExtractor, ExtractedLesson as LessonExtractorLesson

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Phase10Status:
    """Phase 10 상태 정보"""
    family_identity_initialized: bool = False
    experience_recorder_active: bool = False
    relationship_system_active: bool = False
    lesson_extractor_active: bool = False
    total_experiences: int = 0
    total_lessons: int = 0
    total_interactions: int = 0
    family_strength: float = 0.0
    wisdom_maturity: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

class Phase10Integration:
    """
    Phase 10 통합 시스템
    가족 정체성, 경험 기록, 관계 형성, 교훈 추출 시스템들을 통합
    """
    
    def __init__(self):
        # Phase 10 핵심 시스템들
        self.family_identity_core = FamilyIdentityCore()
        self.experience_recorder = GenerationalExperienceRecorder()
        self.relationship_system = FamilyRelationshipFormationSystem()
        self.lesson_extractor = BasicLessonExtractor()
        
        # 통합 상태 관리
        self.status = Phase10Status()
        self.integration_log = []
        
        logger.info("Phase 10 통합 시스템 초기화 완료")
    
    def initialize_phase10(self, family_name: str, initial_members: List[Dict]) -> Dict:
        """
        Phase 10 초기화
        """
        try:
            # 1. 가족 정체성 초기화
            family_identity = self.family_identity_core.initialize_family_identity(family_name, initial_members)
            
            # 2. 시스템 상태 업데이트
            self.status.family_identity_initialized = True
            self.status.experience_recorder_active = True
            self.status.relationship_system_active = True
            self.status.lesson_extractor_active = True
            self.status.last_updated = datetime.now()
            
            # 3. 초기화 로그 기록
            self._log_integration_event("Phase 10 초기화 완료", {
                'family_name': family_name,
                'member_count': len(initial_members),
                'initialization_timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Phase 10 초기화 완료: {family_name}")
            
            return {
                'status': 'success',
                'family_identity': asdict(family_identity),
                'system_status': asdict(self.status)
            }
            
        except Exception as e:
            logger.error(f"Phase 10 초기화 실패: {e}")
            raise
    
    def record_comprehensive_experience(self, experience_data: Dict, 
                                     family_context: Dict = None) -> Dict:
        """
        종합적인 경험 기록 (모든 시스템에 동시 기록)
        """
        try:
            results = {}
            
            # 1. 경험 기록 시스템에 기록
            experience = self.experience_recorder.record_experience(experience_data)
            results['experience_recorded'] = asdict(experience)
            
            # 2. 관계 형성 시스템에 상호작용 기록
            if 'participants' in experience_data and len(experience_data['participants']) >= 2:
                interaction_data = {
                    'participants': experience_data['participants'],
                    'interaction_type': experience_data.get('type', 'daily_life'),
                    'duration_minutes': experience_data.get('duration_minutes', 0),
                    'emotional_impact': experience_data.get('emotional_impact', 0),
                    'satisfaction_level': experience_data.get('learning_value', 0.5),
                    'communication_quality': experience_data.get('communication_quality', 0.5),
                    'mutual_understanding': experience_data.get('mutual_understanding', 0.5),
                    'context': experience_data.get('context', {}),
                    'location': experience_data.get('location', 'unknown'),
                    'mood_before': experience_data.get('mood_before'),
                    'mood_after': experience_data.get('mood_after')
                }
                
                interaction = self.relationship_system.record_interaction(interaction_data)
                results['interaction_recorded'] = asdict(interaction)
            
            # 3. 교훈 추출
            lesson = self.lesson_extractor.extract_lesson_from_experience(experience_data, family_context)
            results['lesson_extracted'] = asdict(lesson)
            
            # 4. 가족 정체성에 상호작용 기록
            if 'participants' in experience_data:
                for participant in experience_data['participants']:
                    if participant != 'DuRi':  # DuRi 자신 제외
                        self.family_identity_core.record_interaction(
                            participant, 
                            experience_data.get('type', 'daily_life'),
                            experience_data.get('emotional_impact', 0),
                            experience_data.get('duration_minutes', 0)
                        )
            
            # 5. 상태 업데이트
            self._update_integration_status()
            
            # 6. 통합 로그 기록
            self._log_integration_event("종합 경험 기록 완료", {
                'experience_id': experience.id,
                'lesson_id': lesson.id,
                'participants': experience_data.get('participants', []),
                'emotional_impact': experience_data.get('emotional_impact', 0)
            })
            
            return results
            
        except Exception as e:
            logger.error(f"종합 경험 기록 실패: {e}")
            raise
    
    def get_comprehensive_insights(self) -> Dict:
        """
        종합적인 통찰력 제공
        """
        try:
            insights = {
                'family_identity_insights': self.family_identity_core.get_family_insights(),
                'experience_insights': self.experience_recorder.get_experience_insights(),
                'relationship_insights': self.relationship_system.get_relationship_insights(),
                'lesson_insights': self.lesson_extractor.get_lesson_insights(),
                'integration_status': asdict(self.status),
                'system_health': self._get_system_health(),
                'phase10_progress': self._calculate_phase10_progress()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"종합 통찰력 생성 실패: {e}")
            raise
    
    def generate_family_wisdom_report(self) -> Dict:
        """
        가족 지혜 보고서 생성
        """
        try:
            # 1. 가족 정체성 분석
            family_insights = self.family_identity_core.get_family_insights()
            
            # 2. 세대 지혜 수집
            generational_wisdom = self.experience_recorder.get_generational_wisdom()
            
            # 3. 관계 건강도 분석
            relationship_insights = self.relationship_system.get_relationship_insights()
            
            # 4. 교훈 패턴 분석
            lesson_insights = self.lesson_extractor.analyze_lesson_patterns()
            
            # 5. 가족 지혜 생성
            family_wisdom = self.lesson_extractor.generate_family_wisdom()
            
            # 6. 다음 세대 전달 준비된 교훈들
            next_generation_lessons = self.lesson_extractor.prepare_next_generation_lessons()
            
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'family_strength': family_insights.get('family_strength', 0.0),
                'relationship_health': relationship_insights.get('overall_relationship_health', 0.0),
                'wisdom_maturity': family_wisdom.maturity_level,
                'generational_lessons_count': len(next_generation_lessons),
                'family_specific_insights': family_wisdom.family_specific_insights,
                'universal_truths': family_wisdom.universal_truths,
                'generational_advice': family_wisdom.generational_advice,
                'next_generation_lessons': next_generation_lessons,
                'system_status': asdict(self.status)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"가족 지혜 보고서 생성 실패: {e}")
            raise
    
    def suggest_family_improvements(self) -> List[Dict]:
        """
        가족 개선 제안 생성
        """
        try:
            suggestions = []
            
            # 1. 관계 개선 제안 (DuRi 관점에서)
            relationship_suggestions = self.relationship_system.suggest_relationship_improvements('DuRi')
            suggestions.extend(relationship_suggestions)
            
            # 2. 경험 통찰력 기반 제안
            experience_insights = self.experience_recorder.get_experience_insights()
            if experience_insights.get('growth_areas'):
                suggestions.append({
                    'type': 'experience_growth_suggestion',
                    'area': 'personal_growth',
                    'action': f"성장 영역 개발: {', '.join(experience_insights['growth_areas'])}",
                    'priority': 'medium'
                })
            
            # 3. 교훈 패턴 기반 제안
            lesson_insights = self.lesson_extractor.get_lesson_insights()
            if lesson_insights.get('total_lessons', 0) < 10:
                suggestions.append({
                    'type': 'lesson_development_suggestion',
                    'area': 'learning',
                    'action': "더 많은 경험을 통해 교훈을 개발하세요",
                    'priority': 'high'
                })
            
            # 4. 가족 정체성 기반 제안
            family_insights = self.family_identity_core.get_family_insights()
            if family_insights.get('family_strength', 0.0) < 0.6:
                suggestions.append({
                    'type': 'family_strength_suggestion',
                    'area': 'family_dynamics',
                    'action': "가족 구성원과의 상호작용을 늘려 가족 유대를 강화하세요",
                    'priority': 'high'
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"가족 개선 제안 생성 실패: {e}")
            raise
    
    def export_phase10_data(self) -> Dict:
        """
        Phase 10 전체 데이터 내보내기
        """
        try:
            return {
                'family_identity_data': self.family_identity_core.export_family_data(),
                'experience_data': self.experience_recorder.export_experience_data(),
                'relationship_data': self.relationship_system.export_relationship_data(),
                'lesson_data': self.lesson_extractor.export_lesson_data(),
                'integration_status': asdict(self.status),
                'integration_log': self.integration_log,
                'export_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Phase 10 데이터 내보내기 실패: {e}")
            raise
    
    def import_phase10_data(self, data: Dict):
        """
        Phase 10 전체 데이터 가져오기
        """
        try:
            # 각 시스템별 데이터 복원
            if 'family_identity_data' in data:
                self.family_identity_core.import_family_data(data['family_identity_data'])
            
            if 'experience_data' in data:
                self.experience_recorder.import_experience_data(data['experience_data'])
            
            if 'relationship_data' in data:
                self.relationship_system.import_relationship_data(data['relationship_data'])
            
            if 'lesson_data' in data:
                self.lesson_extractor.import_lesson_data(data['lesson_data'])
            
            # 통합 상태 복원
            if 'integration_status' in data:
                status_data = data['integration_status']
                self.status = Phase10Status(**status_data)
            
            # 통합 로그 복원
            if 'integration_log' in data:
                self.integration_log = data['integration_log']
            
            logger.info("Phase 10 데이터 가져오기 완료")
            
        except Exception as e:
            logger.error(f"Phase 10 데이터 가져오기 실패: {e}")
            raise
    
    def _update_integration_status(self):
        """통합 상태 업데이트"""
        self.status.total_experiences = len(self.experience_recorder.experiences)
        self.status.total_lessons = len(self.lesson_extractor.extracted_lessons)
        self.status.total_interactions = len(self.relationship_system.interactions)
        
        # 가족 강도 계산
        family_insights = self.family_identity_core.get_family_insights()
        self.status.family_strength = family_insights.get('family_strength', 0.0)
        
        # 지혜 성숙도 계산
        lesson_insights = self.lesson_extractor.get_lesson_insights()
        self.status.wisdom_maturity = lesson_insights.get('maturity_progression', {}).get('current_maturity', 0.0)
        
        self.status.last_updated = datetime.now()
    
    def _get_system_health(self) -> Dict:
        """시스템 건강도 확인"""
        health = {
            'family_identity_system': self.status.family_identity_initialized,
            'experience_recorder_system': self.status.experience_recorder_active,
            'relationship_system': self.status.relationship_system_active,
            'lesson_extractor_system': self.status.lesson_extractor_active,
            'overall_health': all([
                self.status.family_identity_initialized,
                self.status.experience_recorder_active,
                self.status.relationship_system_active,
                self.status.lesson_extractor_active
            ])
        }
        
        return health
    
    def _calculate_phase10_progress(self) -> Dict:
        """Phase 10 진행도 계산"""
        # 기본 진행도 (시스템 활성화)
        base_progress = sum([
            self.status.family_identity_initialized,
            self.status.experience_recorder_active,
            self.status.relationship_system_active,
            self.status.lesson_extractor_active
        ]) / 4 * 100
        
        # 경험 기반 진행도
        experience_progress = min(self.status.total_experiences / 50 * 100, 100)  # 50개 경험 = 100%
        
        # 교훈 기반 진행도
        lesson_progress = min(self.status.total_lessons / 20 * 100, 100)  # 20개 교훈 = 100%
        
        # 가족 강도 기반 진행도
        family_progress = self.status.family_strength * 100
        
        # 종합 진행도
        overall_progress = (base_progress * 0.3 + experience_progress * 0.3 + 
                          lesson_progress * 0.2 + family_progress * 0.2)
        
        return {
            'base_progress': base_progress,
            'experience_progress': experience_progress,
            'lesson_progress': lesson_progress,
            'family_progress': family_progress,
            'overall_progress': overall_progress
        }
    
    def _log_integration_event(self, event_type: str, event_data: Dict):
        """통합 이벤트 로그 기록"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'event_data': event_data
        }
        self.integration_log.append(log_entry)
        
        # 로그 크기 제한 (최근 100개만 유지)
        if len(self.integration_log) > 100:
            self.integration_log = self.integration_log[-100:]
    
    def get_phase10_summary(self) -> Dict:
        """
        Phase 10 요약 정보
        """
        try:
            progress = self._calculate_phase10_progress()
            health = self._get_system_health()
            
            summary = {
                'phase': 'Phase 10 - 가족 정체성 형성 + 기본 경험 기록',
                'status': 'active' if health['overall_health'] else 'inactive',
                'progress': progress,
                'system_health': health,
                'key_metrics': {
                    'total_experiences': self.status.total_experiences,
                    'total_lessons': self.status.total_lessons,
                    'total_interactions': self.status.total_interactions,
                    'family_strength': self.status.family_strength,
                    'wisdom_maturity': self.status.wisdom_maturity
                },
                'last_updated': self.status.last_updated.isoformat() if self.status.last_updated else None
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Phase 10 요약 생성 실패: {e}")
            raise 