#!/usr/bin/env python3
"""
LLMInterface - Phase 11
LLM 인터페이스 시스템

기능:
- ChatGPT, Claude, Gemini 등 LLM 통합
- 가족 맥락에 맞는 질문 생성 및 응답 처리
- 학습 보조 및 대화 지원
- 응답 품질 평가 및 필터링
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import json
import requests
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """LLM 제공자"""
    CHATGPT = "chatgpt"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LOCAL = "local"

class QueryType(Enum):
    """질문 유형"""
    LEARNING_HELP = "learning_help"
    FAMILY_ADVICE = "family_advice"
    EMOTIONAL_SUPPORT = "emotional_support"
    CREATIVE_INSPIRATION = "creative_inspiration"
    KNOWLEDGE_QUESTION = "knowledge_question"
    OTHER = "other"

class ResponseQuality(Enum):
    """응답 품질"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class LLMQuery:
    """LLM 질문"""
    id: str
    query_type: QueryType
    question: str
    family_context: Dict[str, Any]
    provider: LLMProvider
    timestamp: datetime
    additional_context: Optional[str] = None

@dataclass
class LLMResponse:
    """LLM 응답"""
    id: str
    query_id: str
    provider: LLMProvider
    response_text: str
    response_quality: ResponseQuality
    confidence_score: float
    processing_time_seconds: float
    timestamp: datetime
    family_relevance_score: float = 0.0
    notes: Optional[str] = None

@dataclass
class LLMProviderConfig:
    """LLM 제공자 설정"""
    provider: LLMProvider
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    model_name: str = ""
    max_tokens: int = 1000
    temperature: float = 0.7
    is_active: bool = True

class LLMInterface:
    """LLM 인터페이스 시스템"""
    
    def __init__(self):
        self.provider_configs: Dict[LLMProvider, LLMProviderConfig] = {}
        self.queries: List[LLMQuery] = []
        self.responses: List[LLMResponse] = []
        self.family_context: Dict[str, Any] = {}
        
        # 기본 제공자 설정
        self._initialize_default_providers()
        
        logger.info("LLMInterface 초기화 완료")
    
    def _initialize_default_providers(self):
        """기본 제공자 설정 초기화"""
        # ChatGPT 설정 (실제 API 키는 환경변수에서 가져와야 함)
        self.provider_configs[LLMProvider.CHATGPT] = LLMProviderConfig(
            provider=LLMProvider.CHATGPT,
            api_key=None,  # 실제 구현시 환경변수에서 가져옴
            api_url="https://api.openai.com/v1/chat/completions",
            model_name="gpt-4",
            max_tokens=1000,
            temperature=0.7,
            is_active=True
        )
        
        # Claude 설정
        self.provider_configs[LLMProvider.CLAUDE] = LLMProviderConfig(
            provider=LLMProvider.CLAUDE,
            api_key=None,  # 실제 구현시 환경변수에서 가져옴
            api_url="https://api.anthropic.com/v1/messages",
            model_name="claude-3-sonnet",
            max_tokens=1000,
            temperature=0.7,
            is_active=True
        )
        
        # Gemini 설정
        self.provider_configs[LLMProvider.GEMINI] = LLMProviderConfig(
            provider=LLMProvider.GEMINI,
            api_key=None,  # 실제 구현시 환경변수에서 가져옴
            api_url="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            model_name="gemini-pro",
            max_tokens=1000,
            temperature=0.7,
            is_active=True
        )
        
        # 로컬 모델 설정 (시뮬레이션용)
        self.provider_configs[LLMProvider.LOCAL] = LLMProviderConfig(
            provider=LLMProvider.LOCAL,
            api_key=None,
            api_url="http://localhost:8000/generate",
            model_name="local-model",
            max_tokens=1000,
            temperature=0.7,
            is_active=True
        )
    
    def add_provider_config(self, config: LLMProviderConfig):
        """LLM 제공자 설정 추가"""
        try:
            self.provider_configs[config.provider] = config
            logger.info(f"LLM 제공자 설정 추가: {config.provider.value}")
        except Exception as e:
            logger.error(f"LLM 제공자 설정 추가 실패: {e}")
            raise
    
    def create_family_context_prompt(self, family_context: Dict[str, Any]) -> str:
        """가족 맥락 프롬프트 생성"""
        prompt = "당신은 가족 중심 AI DuRi입니다. 다음 가족 맥락을 고려하여 답변해주세요:\n\n"
        
        if family_context:
            if 'family_type' in family_context:
                prompt += f"가족 유형: {family_context['family_type']}\n"
            if 'children_count' in family_context:
                prompt += f"자녀 수: {family_context['children_count']}명\n"
            if 'children_ages' in family_context:
                ages = family_context['children_ages']
                prompt += f"자녀 나이: {', '.join(map(str, ages))}세\n"
            if 'family_values' in family_context:
                values = family_context['family_values']
                prompt += f"가족 가치관: {', '.join(values)}\n"
        
        prompt += "\n가족의 복지와 조화를 최우선으로 고려하여 답변해주세요."
        return prompt
    
    def ask_llm(self, question: str, query_type: QueryType, family_context: Dict[str, Any] = None, provider: LLMProvider = LLMProvider.CHATGPT) -> LLMResponse:
        """LLM에 질문하기"""
        try:
            # 질문 생성
            query_id = f"query_{len(self.queries) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            llm_query = LLMQuery(
                id=query_id,
                query_type=query_type,
                question=question,
                family_context=family_context or {},
                provider=provider,
                timestamp=datetime.now()
            )
            
            self.queries.append(llm_query)
            logger.info(f"LLM 질문 생성: {query_id}")
            
            # 제공자 설정 확인
            if provider not in self.provider_configs:
                raise ValueError(f"지원하지 않는 LLM 제공자: {provider.value}")
            
            config = self.provider_configs[provider]
            if not config.is_active:
                raise ValueError(f"비활성화된 LLM 제공자: {provider.value}")
            
            # 응답 생성 시작 시간
            start_time = time.time()
            
            # 실제 LLM 호출 (시뮬레이션)
            response_text = self._simulate_llm_response(question, query_type, family_context, provider)
            
            # 처리 시간 계산
            processing_time = time.time() - start_time
            
            # 응답 품질 평가
            response_quality = self._evaluate_response_quality(response_text, query_type)
            
            # 신뢰도 점수 계산
            confidence_score = self._calculate_confidence_score(response_text, query_type)
            
            # 가족 관련성 점수 계산
            family_relevance_score = self._calculate_family_relevance_score(response_text, family_context)
            
            # 응답 생성
            response_id = f"response_{len(self.responses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            llm_response = LLMResponse(
                id=response_id,
                query_id=query_id,
                provider=provider,
                response_text=response_text,
                response_quality=response_quality,
                confidence_score=confidence_score,
                processing_time_seconds=processing_time,
                timestamp=datetime.now(),
                family_relevance_score=family_relevance_score
            )
            
            self.responses.append(llm_response)
            logger.info(f"LLM 응답 생성: {response_id}")
            
            return llm_response
            
        except Exception as e:
            logger.error(f"LLM 질문 실패: {e}")
            raise
    
    def _simulate_llm_response(self, question: str, query_type: QueryType, family_context: Dict[str, Any], provider: LLMProvider) -> str:
        """LLM 응답 시뮬레이션 (실제 구현시 실제 API 호출)"""
        # 가족 맥락 프롬프트 생성
        family_prompt = self.create_family_context_prompt(family_context)
        
        # 질문 유형별 시뮬레이션 응답
        if query_type == QueryType.LEARNING_HELP:
            return f"{family_prompt}\n\n학습 도움말: {question}에 대한 답변을 제공합니다. 가족과 함께 학습할 수 있는 방법을 제안합니다."
        elif query_type == QueryType.FAMILY_ADVICE:
            return f"{family_prompt}\n\n가족 조언: {question}에 대해 가족의 조화를 고려한 조언을 제공합니다."
        elif query_type == QueryType.EMOTIONAL_SUPPORT:
            return f"{family_prompt}\n\n정서적 지원: {question}에 대해 공감과 이해를 바탕으로 한 지원을 제공합니다."
        elif query_type == QueryType.CREATIVE_INSPIRATION:
            return f"{family_prompt}\n\n창의적 영감: {question}에 대해 가족과 함께할 수 있는 창의적 아이디어를 제안합니다."
        elif query_type == QueryType.KNOWLEDGE_QUESTION:
            return f"{family_prompt}\n\n지식 질문: {question}에 대한 정확하고 유용한 정보를 제공합니다."
        else:
            return f"{family_prompt}\n\n일반 응답: {question}에 대한 도움이 되는 답변을 제공합니다."
    
    def _evaluate_response_quality(self, response_text: str, query_type: QueryType) -> ResponseQuality:
        """응답 품질 평가"""
        # 간단한 품질 평가 (실제 구현시 더 정교한 평가 필요)
        word_count = len(response_text.split())
        
        if word_count > 100 and any(word in response_text.lower() for word in ['가족', '사랑', '이해', '지지']):
            return ResponseQuality.EXCELLENT
        elif word_count > 50:
            return ResponseQuality.GOOD
        elif word_count > 20:
            return ResponseQuality.FAIR
        else:
            return ResponseQuality.POOR
    
    def _calculate_confidence_score(self, response_text: str, query_type: QueryType) -> float:
        """신뢰도 점수 계산"""
        # 기본 점수
        base_score = 0.6
        
        # 응답 길이 점수
        word_count = len(response_text.split())
        length_score = min(0.2, word_count * 0.002)
        
        # 질문 유형별 점수
        type_score = 0.0
        if query_type == QueryType.FAMILY_ADVICE:
            type_score = 0.1
        elif query_type == QueryType.EMOTIONAL_SUPPORT:
            type_score = 0.1
        else:
            type_score = 0.05
        
        return min(1.0, base_score + length_score + type_score)
    
    def _calculate_family_relevance_score(self, response_text: str, family_context: Dict[str, Any]) -> float:
        """가족 관련성 점수 계산"""
        family_keywords = ['가족', '부모', '자식', '사랑', '관계', '소통', '이해', '지지', '성장']
        
        relevant_words = sum(1 for keyword in family_keywords if keyword in response_text.lower())
        
        return min(1.0, relevant_words * 0.1)
    
    def get_learning_help(self, question: str, family_context: Dict[str, Any] = None) -> LLMResponse:
        """학습 도움 요청"""
        return self.ask_llm(question, QueryType.LEARNING_HELP, family_context, LLMProvider.CHATGPT)
    
    def get_family_advice(self, question: str, family_context: Dict[str, Any] = None) -> LLMResponse:
        """가족 조언 요청"""
        return self.ask_llm(question, QueryType.FAMILY_ADVICE, family_context, LLMProvider.CLAUDE)
    
    def get_emotional_support(self, question: str, family_context: Dict[str, Any] = None) -> LLMResponse:
        """정서적 지원 요청"""
        return self.ask_llm(question, QueryType.EMOTIONAL_SUPPORT, family_context, LLMProvider.CHATGPT)
    
    def get_creative_inspiration(self, question: str, family_context: Dict[str, Any] = None) -> LLMResponse:
        """창의적 영감 요청"""
        return self.ask_llm(question, QueryType.CREATIVE_INSPIRATION, family_context, LLMProvider.GEMINI)
    
    def get_knowledge_answer(self, question: str, family_context: Dict[str, Any] = None) -> LLMResponse:
        """지식 질문 답변"""
        return self.ask_llm(question, QueryType.KNOWLEDGE_QUESTION, family_context, LLMProvider.CHATGPT)
    
    def get_llm_statistics(self) -> Dict[str, Any]:
        """LLM 사용 통계"""
        try:
            total_queries = len(self.queries)
            total_responses = len(self.responses)
            
            # 제공자별 통계
            provider_stats = {}
            for provider in LLMProvider:
                provider_responses = [r for r in self.responses if r.provider == provider]
                provider_stats[provider.value] = len(provider_responses)
            
            # 질문 유형별 통계
            query_type_stats = {}
            for query_type in QueryType:
                type_queries = [q for q in self.queries if q.query_type == query_type]
                query_type_stats[query_type.value] = len(type_queries)
            
            # 응답 품질별 통계
            quality_stats = {}
            for quality in ResponseQuality:
                quality_responses = [r for r in self.responses if r.response_quality == quality]
                quality_stats[quality.value] = len(quality_responses)
            
            # 평균 처리 시간
            avg_processing_time = sum(r.processing_time_seconds for r in self.responses) / len(self.responses) if self.responses else 0
            
            # 평균 신뢰도
            avg_confidence = sum(r.confidence_score for r in self.responses) / len(self.responses) if self.responses else 0
            
            # 평균 가족 관련성
            avg_family_relevance = sum(r.family_relevance_score for r in self.responses) / len(self.responses) if self.responses else 0
            
            statistics = {
                'total_queries': total_queries,
                'total_responses': total_responses,
                'provider_stats': provider_stats,
                'query_type_stats': query_type_stats,
                'quality_stats': quality_stats,
                'average_processing_time': avg_processing_time,
                'average_confidence': avg_confidence,
                'average_family_relevance': avg_family_relevance,
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info("LLM 사용 통계 생성 완료")
            return statistics
            
        except Exception as e:
            logger.error(f"LLM 사용 통계 생성 실패: {e}")
            return {}
    
    def export_llm_data(self) -> Dict[str, Any]:
        """LLM 데이터 내보내기"""
        try:
            export_data = {
                'queries': [asdict(query) for query in self.queries],
                'responses': [asdict(response) for response in self.responses],
                'provider_configs': {provider.value: asdict(config) for provider, config in self.provider_configs.items()},
                'export_date': datetime.now().isoformat()
            }
            
            logger.info("LLM 데이터 내보내기 완료")
            return export_data
            
        except Exception as e:
            logger.error(f"LLM 데이터 내보내기 실패: {e}")
            return {}
    
    def import_llm_data(self, data: Dict[str, Any]):
        """LLM 데이터 가져오기"""
        try:
            # 질문 가져오기
            for query_data in data.get('queries', []):
                # datetime 객체 변환
                if 'timestamp' in query_data:
                    query_data['timestamp'] = datetime.fromisoformat(query_data['timestamp'])
                
                llm_query = LLMQuery(**query_data)
                self.queries.append(llm_query)
            
            # 응답 가져오기
            for response_data in data.get('responses', []):
                # datetime 객체 변환
                if 'timestamp' in response_data:
                    response_data['timestamp'] = datetime.fromisoformat(response_data['timestamp'])
                
                llm_response = LLMResponse(**response_data)
                self.responses.append(llm_response)
            
            # 제공자 설정 가져오기
            for provider_name, config_data in data.get('provider_configs', {}).items():
                provider = LLMProvider(provider_name)
                llm_config = LLMProviderConfig(**config_data)
                self.provider_configs[provider] = llm_config
            
            logger.info("LLM 데이터 가져오기 완료")
            
        except Exception as e:
            logger.error(f"LLM 데이터 가져오기 실패: {e}")
            raise

# 테스트 함수
def test_llm_interface():
    """LLM 인터페이스 테스트"""
    print("🤖 LLMInterface 테스트 시작...")
    
    # 시스템 초기화
    llm_interface = LLMInterface()
    
    # 가족 맥락 설정
    family_context = {
        'family_type': 'nuclear',
        'children_count': 2,
        'children_ages': [5, 8],
        'family_values': ['사랑', '소통', '성장', '창의성']
    }
    
    # 1. 학습 도움 요청
    learning_question = "아이들과 함께할 수 있는 창의적인 놀이 방법을 알려주세요."
    learning_response = llm_interface.get_learning_help(learning_question, family_context)
    print(f"✅ 학습 도움 응답: {learning_response.response_quality.value} 품질, {learning_response.confidence_score:.2f} 신뢰도")
    
    # 2. 가족 조언 요청
    advice_question = "아이들이 싸울 때 어떻게 대처해야 할까요?"
    advice_response = llm_interface.get_family_advice(advice_question, family_context)
    print(f"✅ 가족 조언 응답: {advice_response.response_quality.value} 품질, {advice_response.family_relevance_score:.2f} 가족 관련성")
    
    # 3. 정서적 지원 요청
    emotional_question = "아이가 학교에서 친구와 다퉈서 속상해해요."
    emotional_response = llm_interface.get_emotional_support(emotional_question, family_context)
    print(f"✅ 정서적 지원 응답: {emotional_response.response_quality.value} 품질, {emotional_response.processing_time_seconds:.2f}초 처리시간")
    
    # 4. 창의적 영감 요청
    creative_question = "주말에 가족과 함께할 수 있는 재미있는 활동을 제안해주세요."
    creative_response = llm_interface.get_creative_inspiration(creative_question, family_context)
    print(f"✅ 창의적 영감 응답: {creative_response.response_quality.value} 품질, {creative_response.confidence_score:.2f} 신뢰도")
    
    # 5. 지식 질문
    knowledge_question = "아이의 창의력을 키우는 방법은 무엇인가요?"
    knowledge_response = llm_interface.get_knowledge_answer(knowledge_question, family_context)
    print(f"✅ 지식 질문 응답: {knowledge_response.response_quality.value} 품질, {knowledge_response.family_relevance_score:.2f} 가족 관련성")
    
    # 6. LLM 사용 통계
    statistics = llm_interface.get_llm_statistics()
    print(f"✅ LLM 사용 통계: {statistics['total_queries']}개 질문, {statistics['total_responses']}개 응답")
    print(f"   제공자별: {statistics['provider_stats']}")
    print(f"   질문 유형별: {statistics['query_type_stats']}")
    print(f"   응답 품질별: {statistics['quality_stats']}")
    
    # 7. 데이터 내보내기/가져오기
    export_data = llm_interface.export_llm_data()
    print(f"✅ LLM 데이터 내보내기: {len(export_data['queries'])}개 질문, {len(export_data['responses'])}개 응답")
    
    print("🎉 LLMInterface 테스트 완료!")

if __name__ == "__main__":
    test_llm_interface() 