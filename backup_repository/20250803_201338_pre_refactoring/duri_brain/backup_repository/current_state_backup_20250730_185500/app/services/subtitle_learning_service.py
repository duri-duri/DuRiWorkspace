#!/usr/bin/env python3
"""
SubtitleBasedLearningSystem - Phase 11
자막 기반 영상 학습 시스템

기능:
- 유튜브 자막, 영상 설명 등 자막 기반 학습
- 자막 내용 분석 및 시각적 정보와 결합
- 가족 맥락에 맞는 영상 콘텐츠 필터링
- 영상 학습 진도 추적 및 관리
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import json
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoType(Enum):
    """영상 유형"""
    YOUTUBE = "youtube"
    EDUCATIONAL = "educational"
    FAMILY_CONTENT = "family_content"
    TUTORIAL = "tutorial"
    DOCUMENTARY = "documentary"
    OTHER = "other"

class SubtitleFormat(Enum):
    """자막 형식"""
    SRT = "srt"
    VTT = "vtt"
    TXT = "txt"
    JSON = "json"
    OTHER = "other"

class VisualLearningCategory(Enum):
    """시각적 학습 카테고리"""
    FAMILY_ACTIVITIES = "family_activities"
    EMOTIONAL_EXPRESSION = "emotional_expression"
    LIFE_SKILLS_DEMO = "life_skills_demo"
    CREATIVE_PROJECTS = "creative_projects"
    EDUCATIONAL_CONTENT = "educational_content"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"

@dataclass
class VideoContent:
    """영상 콘텐츠"""
    id: str
    title: str
    description: str
    video_type: VideoType
    duration_seconds: int
    source_url: Optional[str] = None
    channel_name: Optional[str] = None
    upload_date: Optional[datetime] = None
    view_count: int = 0
    like_count: int = 0

@dataclass
class SubtitleSegment:
    """자막 세그먼트"""
    id: str
    video_content_id: str
    start_time: float
    end_time: float
    text: str
    confidence: float = 1.0

@dataclass
class ExtractedVisualKnowledge:
    """추출된 시각적 지식"""
    id: str
    video_content_id: str
    key_concepts: List[str]
    visual_insights: List[str]
    family_relevant_scenes: List[str]
    learning_category: VisualLearningCategory
    difficulty_level: str
    confidence_score: float
    extraction_date: datetime
    notes: Optional[str] = None

@dataclass
class VisualLearningProgress:
    """시각적 학습 진도"""
    video_content_id: str
    completion_percentage: float
    understanding_score: float
    visual_comprehension_score: float
    family_application_score: float
    last_accessed: datetime
    total_watch_time_seconds: int = 0
    rewatch_count: int = 0

class SubtitleBasedLearningSystem:
    """자막 기반 영상 학습 시스템"""
    
    def __init__(self):
        self.video_contents: List[VideoContent] = []
        self.subtitle_segments: List[SubtitleSegment] = []
        self.extracted_visual_knowledge: List[ExtractedVisualKnowledge] = []
        self.visual_learning_progress: List[VisualLearningProgress] = []
        self.family_context: Dict[str, Any] = {}
        
        logger.info("SubtitleBasedLearningSystem 초기화 완료")
    
    def add_video_content(self, video_data: Dict[str, Any]) -> VideoContent:
        """영상 콘텐츠 추가"""
        try:
            # 기본 정보 설정
            video_id = f"video_{len(self.video_contents) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 영상 유형 파싱
            video_type = VideoType(video_data.get('video_type', 'other'))
            
            video_content = VideoContent(
                id=video_id,
                title=video_data.get('title', '제목 없음'),
                description=video_data.get('description', ''),
                video_type=video_type,
                duration_seconds=video_data.get('duration_seconds', 0),
                source_url=video_data.get('source_url'),
                channel_name=video_data.get('channel_name'),
                upload_date=video_data.get('upload_date'),
                view_count=video_data.get('view_count', 0),
                like_count=video_data.get('like_count', 0)
            )
            
            self.video_contents.append(video_content)
            logger.info(f"영상 콘텐츠 추가: {video_content.title}")
            
            return video_content
            
        except Exception as e:
            logger.error(f"영상 콘텐츠 추가 실패: {e}")
            raise
    
    def add_subtitle_segments(self, video_content_id: str, subtitle_data: List[Dict[str, Any]]) -> List[SubtitleSegment]:
        """자막 세그먼트 추가"""
        try:
            segments = []
            
            for i, segment_data in enumerate(subtitle_data):
                segment_id = f"subtitle_{video_content_id}_{i+1}"
                
                segment = SubtitleSegment(
                    id=segment_id,
                    video_content_id=video_content_id,
                    start_time=segment_data.get('start_time', 0.0),
                    end_time=segment_data.get('end_time', 0.0),
                    text=segment_data.get('text', ''),
                    confidence=segment_data.get('confidence', 1.0)
                )
                
                segments.append(segment)
                self.subtitle_segments.append(segment)
            
            logger.info(f"자막 세그먼트 {len(segments)}개 추가: {video_content_id}")
            return segments
            
        except Exception as e:
            logger.error(f"자막 세그먼트 추가 실패: {e}")
            raise
    
    def extract_visual_knowledge_from_video(self, video_content_id: str) -> ExtractedVisualKnowledge:
        """영상에서 시각적 지식 추출"""
        try:
            # 영상 콘텐츠 찾기
            video_content = next((vc for vc in self.video_contents if vc.id == video_content_id), None)
            if not video_content:
                raise ValueError(f"영상 콘텐츠를 찾을 수 없습니다: {video_content_id}")
            
            # 자막 세그먼트 찾기
            subtitle_segments = [s for s in self.subtitle_segments if s.video_content_id == video_content_id]
            
            # 전체 자막 텍스트 결합
            full_subtitle_text = ' '.join([segment.text for segment in subtitle_segments])
            
            # 키워드 추출
            words = full_subtitle_text.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3:  # 3글자 이상만
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # 가장 빈도가 높은 단어들을 키 컨셉으로
            key_concepts = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            key_concepts = [word for word, freq in key_concepts]
            
            # 시각적 인사이트 추출 (자막 기반)
            visual_insights = []
            for segment in subtitle_segments:
                if any(word in segment.text.lower() for word in ['보세요', '보시면', '이렇게', '이런', '그림', '화면']):
                    visual_insights.append(segment.text.strip())
            
            # 가족 관련 장면 추출
            family_keywords = ['가족', '부모', '자식', '아이', '아버지', '어머니', '형제', '자매', '사랑', '관계']
            family_scenes = []
            for segment in subtitle_segments:
                if any(keyword in segment.text for keyword in family_keywords):
                    family_scenes.append(f"{segment.start_time:.1f}s-{segment.end_time:.1f}s: {segment.text.strip()}")
            
            # 학습 카테고리 결정
            learning_category = self._determine_visual_learning_category(video_content, full_subtitle_text)
            
            # 난이도 결정
            difficulty_level = self._determine_difficulty_level(video_content, subtitle_segments)
            
            # 신뢰도 점수 계산
            confidence_score = self._calculate_visual_confidence_score(video_content, subtitle_segments, key_concepts, visual_insights)
            
            extracted_knowledge = ExtractedVisualKnowledge(
                id=f"visual_knowledge_{len(self.extracted_visual_knowledge) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                video_content_id=video_content_id,
                key_concepts=key_concepts,
                visual_insights=visual_insights,
                family_relevant_scenes=family_scenes,
                learning_category=learning_category,
                difficulty_level=difficulty_level,
                confidence_score=confidence_score,
                extraction_date=datetime.now()
            )
            
            self.extracted_visual_knowledge.append(extracted_knowledge)
            logger.info(f"시각적 지식 추출 완료: {extracted_knowledge.id}")
            
            return extracted_knowledge
            
        except Exception as e:
            logger.error(f"시각적 지식 추출 실패: {e}")
            raise
    
    def _determine_visual_learning_category(self, video_content: VideoContent, subtitle_text: str) -> VisualLearningCategory:
        """시각적 학습 카테고리 결정"""
        text_lower = subtitle_text.lower()
        title_lower = video_content.title.lower()
        
        if any(word in title_lower or word in text_lower for word in ['가족', '부모', '자식', '아이', '육아']):
            return VisualLearningCategory.FAMILY_ACTIVITIES
        elif any(word in text_lower for word in ['감정', '표정', '기쁨', '슬픔', '화남', '놀람']):
            return VisualLearningCategory.EMOTIONAL_EXPRESSION
        elif any(word in title_lower for word in ['방법', '하는법', '튜토리얼', '가이드']):
            return VisualLearningCategory.LIFE_SKILLS_DEMO
        elif any(word in text_lower for word in ['만들기', '그리기', '공작', '창작', '예술']):
            return VisualLearningCategory.CREATIVE_PROJECTS
        elif any(word in title_lower for word in ['교육', '학습', '강의', '수업']):
            return VisualLearningCategory.EDUCATIONAL_CONTENT
        else:
            return VisualLearningCategory.ENTERTAINMENT
    
    def _determine_difficulty_level(self, video_content: VideoContent, subtitle_segments: List[SubtitleSegment]) -> str:
        """난이도 결정"""
        # 영상 길이와 자막 복잡도 기반
        avg_words_per_segment = sum(len(segment.text.split()) for segment in subtitle_segments) / len(subtitle_segments) if subtitle_segments else 0
        
        if video_content.duration_seconds < 300 and avg_words_per_segment < 10:  # 5분 미만, 간단한 자막
            return "beginner"
        elif video_content.duration_seconds < 900 and avg_words_per_segment < 20:  # 15분 미만, 보통 자막
            return "intermediate"
        elif video_content.duration_seconds < 1800 and avg_words_per_segment < 30:  # 30분 미만, 복잡한 자막
            return "advanced"
        else:
            return "expert"
    
    def _calculate_visual_confidence_score(self, video_content: VideoContent, subtitle_segments: List[SubtitleSegment], key_concepts: List[str], visual_insights: List[str]) -> float:
        """시각적 신뢰도 점수 계산"""
        # 기본 점수
        base_score = 0.5
        
        # 자막 품질 점수
        subtitle_quality = sum(segment.confidence for segment in subtitle_segments) / len(subtitle_segments) if subtitle_segments else 0
        quality_score = subtitle_quality * 0.2
        
        # 키 컨셉 점수
        concept_score = min(0.2, len(key_concepts) * 0.02)
        
        # 시각적 인사이트 점수
        insight_score = min(0.1, len(visual_insights) * 0.02)
        
        return min(1.0, base_score + quality_score + concept_score + insight_score)
    
    def update_visual_learning_progress(self, video_content_id: str, progress_data: Dict[str, Any]) -> VisualLearningProgress:
        """시각적 학습 진도 업데이트"""
        try:
            # 기존 진도 찾기
            existing_progress = next((p for p in self.visual_learning_progress if p.video_content_id == video_content_id), None)
            
            if existing_progress:
                # 기존 진도 업데이트
                existing_progress.completion_percentage = progress_data.get('completion_percentage', existing_progress.completion_percentage)
                existing_progress.understanding_score = progress_data.get('understanding_score', existing_progress.understanding_score)
                existing_progress.visual_comprehension_score = progress_data.get('visual_comprehension_score', existing_progress.visual_comprehension_score)
                existing_progress.family_application_score = progress_data.get('family_application_score', existing_progress.family_application_score)
                existing_progress.last_accessed = datetime.now()
                existing_progress.total_watch_time_seconds += progress_data.get('watch_time_seconds', 0)
                existing_progress.rewatch_count += 1
                
                logger.info(f"시각적 학습 진도 업데이트: {video_content_id}")
                return existing_progress
            else:
                # 새로운 진도 생성
                new_progress = VisualLearningProgress(
                    video_content_id=video_content_id,
                    completion_percentage=progress_data.get('completion_percentage', 0.0),
                    understanding_score=progress_data.get('understanding_score', 0.0),
                    visual_comprehension_score=progress_data.get('visual_comprehension_score', 0.0),
                    family_application_score=progress_data.get('family_application_score', 0.0),
                    last_accessed=datetime.now(),
                    total_watch_time_seconds=progress_data.get('watch_time_seconds', 0),
                    rewatch_count=1
                )
                
                self.visual_learning_progress.append(new_progress)
                logger.info(f"새로운 시각적 학습 진도 생성: {video_content_id}")
                return new_progress
                
        except Exception as e:
            logger.error(f"시각적 학습 진도 업데이트 실패: {e}")
            raise
    
    def get_visual_learning_recommendations(self, family_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """시각적 학습 추천 제공"""
        try:
            recommendations = []
            
            # 가족 맥락에 맞는 영상 필터링
            relevant_videos = self._filter_family_relevant_videos(family_context)
            
            for video in relevant_videos:
                # 해당 영상의 시각적 지식 추출
                knowledge = next((k for k in self.extracted_visual_knowledge if k.video_content_id == video.id), None)
                
                if knowledge:
                    recommendation = {
                        'video_content': asdict(video),
                        'extracted_visual_knowledge': asdict(knowledge),
                        'recommendation_score': self._calculate_visual_recommendation_score(video, knowledge, family_context),
                        'learning_category': knowledge.learning_category.value,
                        'difficulty_level': knowledge.difficulty_level
                    }
                    recommendations.append(recommendation)
            
            # 추천 점수 순으로 정렬
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            logger.info(f"시각적 학습 추천 {len(recommendations)}개 생성")
            return recommendations[:10]  # 상위 10개만 반환
            
        except Exception as e:
            logger.error(f"시각적 학습 추천 생성 실패: {e}")
            return []
    
    def _filter_family_relevant_videos(self, family_context: Dict[str, Any] = None) -> List[VideoContent]:
        """가족 관련 영상 필터링"""
        if not family_context:
            return self.video_contents
        
        # 가족 맥락에 맞는 키워드
        family_keywords = ['가족', '부모', '자식', '아이', '육아', '사랑', '관계', '소통']
        
        relevant_videos = []
        for video in self.video_contents:
            title_lower = video.title.lower()
            description_lower = video.description.lower()
            
            if any(keyword in title_lower or keyword in description_lower for keyword in family_keywords):
                relevant_videos.append(video)
        
        return relevant_videos
    
    def _calculate_visual_recommendation_score(self, video: VideoContent, knowledge: ExtractedVisualKnowledge, family_context: Dict[str, Any] = None) -> float:
        """시각적 추천 점수 계산"""
        base_score = knowledge.confidence_score
        
        # 가족 관련성 점수
        family_relevance = len(knowledge.family_relevant_scenes) * 0.1
        
        # 영상 품질 점수 (조회수, 좋아요 기반)
        quality_score = min(0.2, (video.view_count / 1000) * 0.01 + (video.like_count / 100) * 0.01)
        
        # 난이도 적합성 점수
        difficulty_score = 0.0
        if knowledge.difficulty_level == "beginner":
            difficulty_score = 0.2
        elif knowledge.difficulty_level == "intermediate":
            difficulty_score = 0.3
        elif knowledge.difficulty_level == "advanced":
            difficulty_score = 0.4
        else:
            difficulty_score = 0.5
        
        return min(1.0, base_score + family_relevance + quality_score + difficulty_score)
    
    def get_visual_learning_statistics(self) -> Dict[str, Any]:
        """시각적 학습 통계 제공"""
        try:
            total_videos = len(self.video_contents)
            total_subtitle_segments = len(self.subtitle_segments)
            total_visual_knowledge = len(self.extracted_visual_knowledge)
            total_progress = len(self.visual_learning_progress)
            
            # 카테고리별 통계
            category_stats = {}
            for category in VisualLearningCategory:
                category_knowledge = [k for k in self.extracted_visual_knowledge if k.learning_category == category]
                category_stats[category.value] = len(category_knowledge)
            
            # 난이도별 통계
            difficulty_stats = {}
            for knowledge in self.extracted_visual_knowledge:
                difficulty = knowledge.difficulty_level
                difficulty_stats[difficulty] = difficulty_stats.get(difficulty, 0) + 1
            
            # 평균 신뢰도
            avg_confidence = sum(k.confidence_score for k in self.extracted_visual_knowledge) / len(self.extracted_visual_knowledge) if self.extracted_visual_knowledge else 0
            
            # 평균 학습 진도
            avg_completion = sum(p.completion_percentage for p in self.visual_learning_progress) / len(self.visual_learning_progress) if self.visual_learning_progress else 0
            
            statistics = {
                'total_videos': total_videos,
                'total_subtitle_segments': total_subtitle_segments,
                'total_visual_knowledge': total_visual_knowledge,
                'total_progress': total_progress,
                'category_stats': category_stats,
                'difficulty_stats': difficulty_stats,
                'average_confidence': avg_confidence,
                'average_completion': avg_completion,
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info("시각적 학습 통계 생성 완료")
            return statistics
            
        except Exception as e:
            logger.error(f"시각적 학습 통계 생성 실패: {e}")
            return {}
    
    def export_visual_learning_data(self) -> Dict[str, Any]:
        """시각적 학습 데이터 내보내기"""
        try:
            export_data = {
                'video_contents': [asdict(content) for content in self.video_contents],
                'subtitle_segments': [asdict(segment) for segment in self.subtitle_segments],
                'extracted_visual_knowledge': [asdict(knowledge) for knowledge in self.extracted_visual_knowledge],
                'visual_learning_progress': [asdict(progress) for progress in self.visual_learning_progress],
                'export_date': datetime.now().isoformat()
            }
            
            logger.info("시각적 학습 데이터 내보내기 완료")
            return export_data
            
        except Exception as e:
            logger.error(f"시각적 학습 데이터 내보내기 실패: {e}")
            return {}
    
    def import_visual_learning_data(self, data: Dict[str, Any]):
        """시각적 학습 데이터 가져오기"""
        try:
            # 영상 콘텐츠 가져오기
            for content_data in data.get('video_contents', []):
                # datetime 객체 변환
                if 'upload_date' in content_data and content_data['upload_date']:
                    content_data['upload_date'] = datetime.fromisoformat(content_data['upload_date'])
                
                video_content = VideoContent(**content_data)
                self.video_contents.append(video_content)
            
            # 자막 세그먼트 가져오기
            for segment_data in data.get('subtitle_segments', []):
                subtitle_segment = SubtitleSegment(**segment_data)
                self.subtitle_segments.append(subtitle_segment)
            
            # 추출된 시각적 지식 가져오기
            for knowledge_data in data.get('extracted_visual_knowledge', []):
                # datetime 객체 변환
                if 'extraction_date' in knowledge_data:
                    knowledge_data['extraction_date'] = datetime.fromisoformat(knowledge_data['extraction_date'])
                
                extracted_knowledge = ExtractedVisualKnowledge(**knowledge_data)
                self.extracted_visual_knowledge.append(extracted_knowledge)
            
            # 시각적 학습 진도 가져오기
            for progress_data in data.get('visual_learning_progress', []):
                # datetime 객체 변환
                if 'last_accessed' in progress_data:
                    progress_data['last_accessed'] = datetime.fromisoformat(progress_data['last_accessed'])
                
                visual_progress = VisualLearningProgress(**progress_data)
                self.visual_learning_progress.append(visual_progress)
            
            logger.info("시각적 학습 데이터 가져오기 완료")
            
        except Exception as e:
            logger.error(f"시각적 학습 데이터 가져오기 실패: {e}")
            raise

# 테스트 함수
def test_subtitle_learning_system():
    """자막 기반 영상 학습 시스템 테스트"""
    print("📹 SubtitleBasedLearningSystem 테스트 시작...")
    
    # 시스템 초기화
    subtitle_learning = SubtitleBasedLearningSystem()
    
    # 1. 영상 콘텐츠 추가
    sample_video = {
        'title': '가족과 함께하는 창의적 놀이 방법',
        'description': '아이들과 함께할 수 있는 재미있는 창작 활동을 소개합니다.',
        'video_type': 'family_content',
        'duration_seconds': 600,  # 10분
        'source_url': 'https://youtube.com/watch?v=example',
        'channel_name': '가족 놀이 채널',
        'view_count': 5000,
        'like_count': 150
    }
    
    video_content = subtitle_learning.add_video_content(sample_video)
    print(f"✅ 영상 콘텐츠 추가: {video_content.title}")
    
    # 2. 자막 세그먼트 추가
    sample_subtitles = [
        {'start_time': 0.0, 'end_time': 5.0, 'text': '안녕하세요! 오늘은 가족과 함께할 수 있는 재미있는 놀이를 소개해드릴게요.'},
        {'start_time': 5.0, 'end_time': 15.0, 'text': '먼저 준비물을 보시면 종이와 색연필이 필요합니다.'},
        {'start_time': 15.0, 'end_time': 30.0, 'text': '이렇게 접어보세요. 아이들이 따라하기 쉬운 단계별로 설명드릴게요.'},
        {'start_time': 30.0, 'end_time': 45.0, 'text': '아이들의 창의력을 키워주는 좋은 방법이에요. 부모님도 함께 참여하시면 더욱 즐거워집니다.'},
        {'start_time': 45.0, 'end_time': 60.0, 'text': '완성된 작품을 보시면 아이들의 얼굴에 웃음이 가득할 거예요.'}
    ]
    
    subtitle_segments = subtitle_learning.add_subtitle_segments(video_content.id, sample_subtitles)
    print(f"✅ 자막 세그먼트 추가: {len(subtitle_segments)}개")
    
    # 3. 시각적 지식 추출
    extracted_knowledge = subtitle_learning.extract_visual_knowledge_from_video(video_content.id)
    print(f"✅ 시각적 지식 추출 완료: {len(extracted_knowledge.key_concepts)}개 키 컨셉")
    print(f"   시각적 인사이트: {len(extracted_knowledge.visual_insights)}개")
    print(f"   가족 관련 장면: {len(extracted_knowledge.family_relevant_scenes)}개")
    print(f"   학습 카테고리: {extracted_knowledge.learning_category.value}")
    print(f"   난이도: {extracted_knowledge.difficulty_level}")
    print(f"   신뢰도 점수: {extracted_knowledge.confidence_score:.2f}")
    
    # 4. 시각적 학습 진도 업데이트
    progress_data = {
        'completion_percentage': 80.0,
        'understanding_score': 85.0,
        'visual_comprehension_score': 90.0,
        'family_application_score': 88.0,
        'watch_time_seconds': 480  # 8분 시청
    }
    
    visual_progress = subtitle_learning.update_visual_learning_progress(video_content.id, progress_data)
    print(f"✅ 시각적 학습 진도 업데이트: {visual_progress.completion_percentage}% 완료")
    
    # 5. 시각적 학습 추천
    family_context = {'family_type': 'nuclear', 'children_count': 2, 'children_ages': [5, 8]}
    recommendations = subtitle_learning.get_visual_learning_recommendations(family_context)
    print(f"✅ 시각적 학습 추천 {len(recommendations)}개 생성")
    
    # 6. 시각적 학습 통계
    statistics = subtitle_learning.get_visual_learning_statistics()
    print(f"✅ 시각적 학습 통계 생성: {statistics['total_videos']}개 영상, {statistics['total_visual_knowledge']}개 지식")
    
    # 7. 데이터 내보내기/가져오기
    export_data = subtitle_learning.export_visual_learning_data()
    print(f"✅ 시각적 학습 데이터 내보내기: {len(export_data['video_contents'])}개 영상")
    
    print("🎉 SubtitleBasedLearningSystem 테스트 완료!")

if __name__ == "__main__":
    test_subtitle_learning_system() 