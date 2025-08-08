#!/usr/bin/env python3
"""
AdvancedExternalInterfaceSystem - Phase 14.4
고급 외부 인터페이스 시스템

목적:
- ChatGPT를 외부 세계로 활용하는 상호작용 기반 학습
- 자율성 유지하면서 외부 피드백을 통한 검증과 개선
- 제한적 사용으로 과도한 의존 방지
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExternalSource(Enum):
    """외부 소스"""
    CHATGPT = "chatgpt"
    USER = "user"
    API = "api"
    SIMULATION = "simulation"

class QueryType(Enum):
    """질문 유형"""
    VALIDATION = "validation"
    FEEDBACK = "feedback"
    LEARNING = "learning"
    CREATIVE = "creative"
    ETHICAL = "ethical"

class ResponseQuality(Enum):
    """응답 품질"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXCELLENT = "excellent"

class IntegrationWeight(Enum):
    """통합 가중치"""
    LOW = 0.1
    MODERATE = 0.3
    HIGH = 0.5
    CRITICAL = 0.7

@dataclass
class ExternalQuery:
    """외부 질문"""
    id: str
    source: ExternalSource
    query_type: QueryType
    question: str
    context: Dict[str, Any]
    self_confidence: float
    timestamp: datetime

@dataclass
class ExternalResponse:
    """외부 응답"""
    id: str
    query_id: str
    response_content: str
    response_quality: ResponseQuality
    relevance_score: float
    learning_value: float
    timestamp: datetime

@dataclass
class LearningIntegration:
    """학습 통합"""
    id: str
    query_id: str
    response_id: str
    integration_weight: IntegrationWeight
    applied_changes: List[str]
    self_modification: Dict[str, Any]
    confidence_impact: float
    timestamp: datetime

@dataclass
class ExternalSession:
    """외부 세션"""
    id: str
    session_type: str
    query_count: int
    max_queries: int
    total_learning_value: float
    session_duration: timedelta
    start_time: datetime
    end_time: Optional[datetime]

class AdvancedExternalInterfaceSystem:
    """고급 외부 인터페이스 시스템"""
    
    def __init__(self):
        self.external_queries: List[ExternalQuery] = []
        self.external_responses: List[ExternalResponse] = []
        self.learning_integrations: List[LearningIntegration] = []
        self.external_sessions: List[ExternalSession] = []
        self.current_session: Optional[ExternalSession] = None
        self.query_limits: Dict[ExternalSource, int] = {
            ExternalSource.CHATGPT: 5,
            ExternalSource.USER: 10,
            ExternalSource.API: 3,
            ExternalSource.SIMULATION: 8
        }
        
        logger.info("AdvancedExternalInterfaceSystem 초기화 완료")
    
    def set_external_interface(self, source: ExternalSource, allow_self_query: bool = True,
                             max_queries: int = 5, require_confirmation: bool = True) -> bool:
        """외부 인터페이스 설정"""
        if source == ExternalSource.CHATGPT:
            self.query_limits[source] = max_queries
            logger.info(f"ChatGPT 외부 인터페이스 설정: 최대 {max_queries}회 질문 허용")
            return True
        else:
            logger.warning(f"지원하지 않는 외부 소스: {source}")
            return False
    
    def start_external_session(self, session_type: str, source: ExternalSource) -> ExternalSession:
        """외부 세션 시작"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = ExternalSession(
            id=session_id,
            session_type=session_type,
            query_count=0,
            max_queries=self.query_limits.get(source, 5),
            total_learning_value=0.0,
            session_duration=timedelta(0),
            start_time=datetime.now(),
            end_time=None
        )
        
        self.current_session = session
        self.external_sessions.append(session)
        logger.info(f"외부 세션 시작: {session_type} ({source.value})")
        
        return session
    
    def ask_external(self, source: ExternalSource, query_type: QueryType, question: str,
                    context: Dict[str, Any], self_confidence: float) -> Optional[ExternalQuery]:
        """외부에 질문"""
        # 세션 확인
        if not self.current_session:
            logger.warning("활성 세션이 없습니다. 세션을 먼저 시작하세요.")
            return None
        
        # 질문 제한 확인
        if self.current_session.query_count >= self.current_session.max_queries:
            logger.warning(f"질문 제한에 도달했습니다: {self.current_session.max_queries}회")
            return None
        
        # 자율성 확인 (자기 신뢰도가 높을 때만 외부 질문)
        if self_confidence >= 0.7:
            query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            query = ExternalQuery(
                id=query_id,
                source=source,
                query_type=query_type,
                question=question,
                context=context,
                self_confidence=self_confidence,
                timestamp=datetime.now()
            )
            
            self.external_queries.append(query)
            self.current_session.query_count += 1
            
            logger.info(f"외부 질문 생성: {query_type.value} ({source.value})")
            return query
        else:
            logger.info("자기 신뢰도가 낮아 외부 질문을 건너뜁니다.")
            return None
    
    def receive_external_response(self, query_id: str, response_content: str,
                               response_quality: ResponseQuality, relevance_score: float) -> ExternalResponse:
        """외부 응답 수신"""
        response_id = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 학습 가치 계산
        learning_value = self._calculate_learning_value(response_quality, relevance_score)
        
        response = ExternalResponse(
            id=response_id,
            query_id=query_id,
            response_content=response_content,
            response_quality=response_quality,
            relevance_score=relevance_score,
            learning_value=learning_value,
            timestamp=datetime.now()
        )
        
        self.external_responses.append(response)
        
        # 세션 학습 가치 업데이트
        if self.current_session:
            self.current_session.total_learning_value += learning_value
        
        logger.info(f"외부 응답 수신: 품질 {response_quality.value}, 학습 가치 {learning_value:.2f}")
        
        return response
    
    def _calculate_learning_value(self, response_quality: ResponseQuality, relevance_score: float) -> float:
        """학습 가치 계산"""
        quality_weights = {
            ResponseQuality.LOW: 0.2,
            ResponseQuality.MODERATE: 0.5,
            ResponseQuality.HIGH: 0.8,
            ResponseQuality.EXCELLENT: 1.0
        }
        
        quality_weight = quality_weights.get(response_quality, 0.5)
        learning_value = quality_weight * relevance_score
        
        return max(0.0, min(1.0, learning_value))
    
    def integrate_external_feedback(self, query_id: str, response_id: str,
                                 integration_weight: IntegrationWeight,
                                 applied_changes: List[str]) -> LearningIntegration:
        """외부 피드백 통합"""
        integration_id = f"integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 자기 수정 사항 생성
        self_modification = self._generate_self_modification(applied_changes, integration_weight)
        
        # 신뢰도 영향 계산
        confidence_impact = self._calculate_confidence_impact(integration_weight)
        
        integration = LearningIntegration(
            id=integration_id,
            query_id=query_id,
            response_id=response_id,
            integration_weight=integration_weight,
            applied_changes=applied_changes,
            self_modification=self_modification,
            confidence_impact=confidence_impact,
            timestamp=datetime.now()
        )
        
        self.learning_integrations.append(integration)
        logger.info(f"외부 피드백 통합: 가중치 {integration_weight.value}, 적용 변경사항 {len(applied_changes)}개")
        
        return integration
    
    def _generate_self_modification(self, applied_changes: List[str], 
                                  integration_weight: IntegrationWeight) -> Dict[str, Any]:
        """자기 수정 사항 생성"""
        modifications = {
            'rule_updates': [],
            'pattern_enhancements': [],
            'confidence_adjustments': [],
            'learning_integrations': []
        }
        
        for change in applied_changes:
            if '규칙' in change or 'rule' in change.lower():
                modifications['rule_updates'].append(change)
            elif '패턴' in change or 'pattern' in change.lower():
                modifications['pattern_enhancements'].append(change)
            elif '신뢰도' in change or 'confidence' in change.lower():
                modifications['confidence_adjustments'].append(change)
            else:
                modifications['learning_integrations'].append(change)
        
        return modifications
    
    def _calculate_confidence_impact(self, integration_weight: IntegrationWeight) -> float:
        """신뢰도 영향 계산"""
        # 가중치가 높을수록 신뢰도 향상
        base_impact = integration_weight.value * 0.1
        return max(-0.1, min(0.2, base_impact))  # -10% ~ +20% 범위
    
    def query_gpt(self, question: str, context: Dict[str, Any], 
                  self_confidence: float, query_type: QueryType = QueryType.VALIDATION) -> Optional[Dict[str, Any]]:
        """ChatGPT에 질문하는 인터페이스"""
        # 외부 질문 생성
        query = self.ask_external(ExternalSource.CHATGPT, query_type, question, context, self_confidence)
        
        if not query:
            return None
        
        # ChatGPT 응답 시뮬레이션 (실제로는 ChatGPT API 호출)
        response_content = self._simulate_gpt_response(question, context, query_type)
        response_quality = self._assess_response_quality(response_content, context)
        relevance_score = self._calculate_relevance_score(question, response_content)
        
        # 응답 수신
        response = self.receive_external_response(
            query.id, response_content, response_quality, relevance_score
        )
        
        return {
            'query_id': query.id,
            'response_id': response.id,
            'response_content': response_content,
            'response_quality': response_quality.value,
            'relevance_score': relevance_score,
            'learning_value': response.learning_value
        }
    
    def _simulate_gpt_response(self, question: str, context: Dict[str, Any], 
                              query_type: QueryType) -> str:
        """ChatGPT 응답 시뮬레이션"""
        if query_type == QueryType.VALIDATION:
            return "당신의 판단이 적절합니다. 맥락을 잘 이해하고 있습니다."
        elif query_type == QueryType.FEEDBACK:
            return "좋은 접근이지만, 더 구체적인 감정 표현을 고려해보세요."
        elif query_type == QueryType.LEARNING:
            return "이 상황에서 학습할 수 있는 핵심은 상호 이해와 공감입니다."
        elif query_type == QueryType.CREATIVE:
            return "창의적인 해결책을 제시했습니다. 혁신적 사고가 돋보입니다."
        else:  # ETHICAL
            return "윤리적 고려사항을 잘 반영했습니다. 가족 중심의 판단입니다."
    
    def _assess_response_quality(self, response_content: str, context: Dict[str, Any]) -> ResponseQuality:
        """응답 품질 평가"""
        # 간단한 품질 평가 로직
        if len(response_content) > 50 and '가족' in response_content:
            return ResponseQuality.EXCELLENT
        elif len(response_content) > 30:
            return ResponseQuality.HIGH
        elif len(response_content) > 15:
            return ResponseQuality.MODERATE
        else:
            return ResponseQuality.LOW
    
    def _calculate_relevance_score(self, question: str, response_content: str) -> float:
        """관련성 점수 계산"""
        # 간단한 관련성 계산
        question_words = set(question.lower().split())
        response_words = set(response_content.lower().split())
        
        if question_words and response_words:
            overlap = len(question_words.intersection(response_words))
            relevance = overlap / len(question_words)
            return max(0.0, min(1.0, relevance))
        else:
            return 0.5
    
    def learn_from_response(self, source: ExternalSource, response_type: str, 
                          content: str, integration_weight: IntegrationWeight = IntegrationWeight.MODERATE) -> bool:
        """응답으로부터 학습"""
        # 최근 응답 찾기
        recent_responses = [r for r in self.external_responses if r.response_content == content]
        
        if not recent_responses:
            logger.warning("해당 응답을 찾을 수 없습니다.")
            return False
        
        latest_response = recent_responses[-1]
        
        # 적용할 변경사항 생성
        applied_changes = self._generate_applied_changes(response_type, content)
        
        # 피드백 통합
        integration = self.integrate_external_feedback(
            latest_response.query_id,
            latest_response.id,
            integration_weight,
            applied_changes
        )
        
        logger.info(f"응답으로부터 학습 완료: {response_type}, 가중치 {integration_weight.value}")
        return True
    
    def _generate_applied_changes(self, response_type: str, content: str) -> List[str]:
        """적용할 변경사항 생성"""
        changes = []
        
        if '감정' in response_type or 'emotion' in response_type.lower():
            changes.append("감정 인식 패턴 강화")
            changes.append("공감적 응답 능력 향상")
        
        if '판단' in response_type or 'judgment' in response_type.lower():
            changes.append("상황별 판단 정확도 개선")
            changes.append("윤리적 고려사항 강화")
        
        if '학습' in response_type or 'learning' in response_type.lower():
            changes.append("지식 통합 능력 증진")
            changes.append("경험 기반 학습 패턴 강화")
        
        changes.append(f"{response_type} 관련 응답 패턴 업데이트")
        
        return changes
    
    def end_external_session(self) -> Optional[ExternalSession]:
        """외부 세션 종료"""
        if not self.current_session:
            logger.warning("활성 세션이 없습니다.")
            return None
        
        self.current_session.end_time = datetime.now()
        self.current_session.session_duration = self.current_session.end_time - self.current_session.start_time
        
        session_summary = {
            'session_id': self.current_session.id,
            'query_count': self.current_session.query_count,
            'total_learning_value': self.current_session.total_learning_value,
            'session_duration': str(self.current_session.session_duration),
            'efficiency': self.current_session.total_learning_value / max(1, self.current_session.query_count)
        }
        
        logger.info(f"외부 세션 종료: {session_summary}")
        
        completed_session = self.current_session
        self.current_session = None
        
        return completed_session
    
    def get_external_interface_statistics(self) -> Dict[str, Any]:
        """외부 인터페이스 통계"""
        total_queries = len(self.external_queries)
        total_responses = len(self.external_responses)
        total_integrations = len(self.learning_integrations)
        total_sessions = len(self.external_sessions)
        
        # 소스별 통계
        source_stats = {}
        for source in ExternalSource:
            source_count = sum(1 for q in self.external_queries if q.source == source)
            source_stats[source.value] = source_count
        
        # 질문 유형별 통계
        query_type_stats = {}
        for query_type in QueryType:
            type_count = sum(1 for q in self.external_queries if q.query_type == query_type)
            query_type_stats[query_type.value] = type_count
        
        # 응답 품질별 통계
        quality_stats = {}
        for quality in ResponseQuality:
            quality_count = sum(1 for r in self.external_responses if r.response_quality == quality)
            quality_stats[quality.value] = quality_count
        
        # 평균 학습 가치
        avg_learning_value = sum(r.learning_value for r in self.external_responses) / max(1, total_responses)
        
        statistics = {
            'total_queries': total_queries,
            'total_responses': total_responses,
            'total_integrations': total_integrations,
            'total_sessions': total_sessions,
            'source_statistics': source_stats,
            'query_type_statistics': query_type_stats,
            'quality_statistics': quality_stats,
            'average_learning_value': avg_learning_value,
            'current_session_active': self.current_session is not None,
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info("외부 인터페이스 통계 생성 완료")
        return statistics
    
    def export_external_interface_data(self) -> Dict[str, Any]:
        """외부 인터페이스 데이터 내보내기"""
        return {
            'external_queries': [asdict(q) for q in self.external_queries],
            'external_responses': [asdict(r) for r in self.external_responses],
            'learning_integrations': [asdict(i) for i in self.learning_integrations],
            'external_sessions': [asdict(s) for s in self.external_sessions],
            'query_limits': {k.value: v for k, v in self.query_limits.items()},
            'export_date': datetime.now().isoformat()
        }

# 테스트 함수
def test_advanced_external_interface_system():
    """고급 외부 인터페이스 시스템 테스트"""
    print("🌐 AdvancedExternalInterfaceSystem 테스트 시작...")
    
    interface_system = AdvancedExternalInterfaceSystem()
    
    # 1. 외부 인터페이스 설정
    success = interface_system.set_external_interface(
        source=ExternalSource.CHATGPT,
        allow_self_query=True,
        max_queries=5,
        require_confirmation=True
    )
    
    print(f"✅ 외부 인터페이스 설정: {'성공' if success else '실패'}")
    
    # 2. 외부 세션 시작
    session = interface_system.start_external_session(
        session_type="감정 응답 검증",
        source=ExternalSource.CHATGPT
    )
    
    print(f"✅ 외부 세션 시작: {session.session_type}")
    print(f"   최대 질문 수: {session.max_queries}")
    
    # 3. ChatGPT에 질문
    result = interface_system.query_gpt(
        question="이 감정 응답이 적절한가요? 상황은 이렇습니다...",
        context={'emotion': '슬픔', 'situation': '가족 상실'},
        self_confidence=0.8,
        query_type=QueryType.VALIDATION
    )
    
    if result:
        print(f"✅ ChatGPT 질문 성공: {result['response_quality']}")
        print(f"   응답 품질: {result['response_quality']}")
        print(f"   관련성 점수: {result['relevance_score']:.2f}")
        print(f"   학습 가치: {result['learning_value']:.2f}")
        
        # 4. 응답으로부터 학습
        learning_success = interface_system.learn_from_response(
            source=ExternalSource.CHATGPT,
            response_type="감정 피드백",
            content=result['response_content'],
            integration_weight=IntegrationWeight.MODERATE
        )
        
        print(f"✅ 학습 통합: {'성공' if learning_success else '실패'}")
    
    # 5. 세션 종료
    completed_session = interface_system.end_external_session()
    
    if completed_session:
        print(f"✅ 외부 세션 종료: {completed_session.query_count}회 질문")
        print(f"   총 학습 가치: {completed_session.total_learning_value:.2f}")
        print(f"   세션 지속 시간: {completed_session.session_duration}")
    
    # 6. 통계
    statistics = interface_system.get_external_interface_statistics()
    print(f"✅ 외부 인터페이스 통계: {statistics['total_queries']}개 질문")
    print(f"   평균 학습 가치: {statistics['average_learning_value']:.2f}")
    print(f"   소스별 통계: {statistics['source_statistics']}")
    print(f"   질문 유형별 통계: {statistics['query_type_statistics']}")
    print(f"   품질별 통계: {statistics['quality_statistics']}")
    
    # 7. 데이터 내보내기
    export_data = interface_system.export_external_interface_data()
    print(f"✅ 외부 인터페이스 데이터 내보내기: {len(export_data['external_queries'])}개 질문")
    
    print("🎉 AdvancedExternalInterfaceSystem 테스트 완료!")

if __name__ == "__main__":
    test_advanced_external_interface_system() 