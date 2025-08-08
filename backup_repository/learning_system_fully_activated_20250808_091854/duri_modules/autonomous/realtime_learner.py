#!/usr/bin/env python3
"""
DuRi 실시간 학습 시스템
대화가 발생하는 즉시 학습을 수행
"""
import asyncio
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RealtimeLearner:
    def __init__(self, autonomous_learner):
        self.autonomous_learner = autonomous_learner
        self.is_active = False
        self.learning_thread = None
        self.conversation_queue = asyncio.Queue()
        self.last_conversation_time = None
        self.learning_interval = 60  # 1분마다 학습
        self.last_learning_time = None
        self.current_session = None
        self.learning_history = []
        
    def start_realtime_learning(self):
        """실시간 학습 시작"""
        if self.is_active:
            logger.warning("실시간 학습이 이미 실행 중입니다.")
            return False
            
        self.is_active = True
        self.learning_thread = threading.Thread(target=self._realtime_learning_loop)
        self.learning_thread.daemon = True
        self.learning_thread.start()
        
        logger.info("🚀 DuRi 실시간 학습 시스템 시작")
        return True
        
    def stop_realtime_learning(self):
        """실시간 학습 중지"""
        if not self.is_active:
            logger.warning("실시간 학습이 실행 중이 아닙니다.")
            return False
            
        self.is_active = False
        logger.info("🛑 DuRi 실시간 학습 시스템 중지")
        return True
        
    def _realtime_learning_loop(self):
        """실시간 학습 루프"""
        while self.is_active:
            try:
                # 대화 큐에서 메시지 확인
                if not self.conversation_queue.empty():
                    conversation = self.conversation_queue.get_nowait()
                    self._process_conversation_realtime(conversation)
                    
                time.sleep(1)  # 1초마다 확인
                
            except Exception as e:
                logger.error(f"실시간 학습 루프 오류: {e}")
                
    def _process_conversation_realtime(self, conversation: Dict[str, Any]):
        """실시간 대화 처리"""
        try:
            user_input = conversation.get("user_input", "")
            assistant_response = conversation.get("assistant_response", "")
            
            if not user_input or not assistant_response:
                return
                
            # 즉시 학습 사이클 실행
            self._execute_realtime_learning_cycle(user_input, assistant_response)
            
            # 자동 학습 시스템에도 전달
            self._update_autonomous_learner(user_input, assistant_response)
            
            logger.info(f"실시간 학습 완료: {len(user_input)}자 입력, {len(assistant_response)}자 응답")
            
        except Exception as e:
            logger.error(f"실시간 대화 처리 오류: {e}")
            
    def _execute_realtime_learning_cycle(self, user_input: str, assistant_response: str):
        """실시간 학습 사이클 실행"""
        try:
            # 1. 즉시 평가
            evaluation_result = self._evaluate_response_realtime(assistant_response, user_input)
            
            # 2. 즉시 자기성찰
            reflection_result = self._reflect_realtime(evaluation_result, user_input, assistant_response)
            
            # 3. 즉시 개선 제안
            improvement_suggestions = self._generate_improvements_realtime(reflection_result)
            
            # 4. 학습 메트릭 업데이트
            self._update_learning_metrics_realtime(evaluation_result, reflection_result)
            
            # 5. 실시간 피드백 생성
            self._generate_realtime_feedback(evaluation_result, improvement_suggestions)
            
        except Exception as e:
            logger.error(f"실시간 학습 사이클 오류: {e}")
            
    def _evaluate_response_realtime(self, response: str, user_input: str) -> Dict[str, Any]:
        """실시간 응답 평가"""
        # 간단한 실시간 평가 (전체 ChatGPT 평가 대신)
        evaluation = {
            "relevance_score": self._calculate_relevance_score(response, user_input),
            "clarity_score": self._calculate_clarity_score(response),
            "actionability_score": self._calculate_actionability_score(response),
            "overall_score": 0.0
        }
        
        # 전체 점수 계산
        evaluation["overall_score"] = (
            evaluation["relevance_score"] * 0.4 +
            evaluation["clarity_score"] * 0.3 +
            evaluation["actionability_score"] * 0.3
        )
        
        return evaluation
        
    def _calculate_relevance_score(self, response: str, user_input: str) -> float:
        """관련성 점수 계산"""
        # 간단한 키워드 매칭
        input_keywords = set(user_input.lower().split())
        response_keywords = set(response.lower().split())
        
        if not input_keywords:
            return 0.0
            
        overlap = len(input_keywords.intersection(response_keywords))
        return min(overlap / len(input_keywords), 1.0)
        
    def _calculate_clarity_score(self, response: str) -> float:
        """명확성 점수 계산"""
        # 문장 길이와 구조 기반
        sentences = response.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        # 적절한 문장 길이 (10-20단어)를 선호
        if 10 <= avg_sentence_length <= 20:
            return 1.0
        elif 5 <= avg_sentence_length <= 30:
            return 0.7
        else:
            return 0.3
            
    def _calculate_actionability_score(self, response: str) -> float:
        """실행 가능성 점수 계산"""
        action_indicators = [
            "다음과 같이", "이렇게", "다음 단계", "실행", "구현", "코드",
            "예제", "방법", "단계", "설치", "설정", "생성"
        ]
        
        score = 0.0
        for indicator in action_indicators:
            if indicator in response:
                score += 0.2
                
        return min(score, 1.0)
        
    def _reflect_realtime(self, evaluation: Dict[str, Any], user_input: str, response: str) -> Dict[str, Any]:
        """실시간 자기성찰"""
        reflection = {
            "accepted_criticisms": [],
            "disagreements": [],
            "improvement_suggestions": []
        }
        
        # 평가 결과에 따른 성찰
        if evaluation["relevance_score"] < 0.5:
            reflection["accepted_criticisms"].append("사용자 질문과 관련성이 부족함")
            reflection["improvement_suggestions"].append("사용자 질문의 핵심 키워드를 더 정확히 파악하라")
            
        if evaluation["clarity_score"] < 0.5:
            reflection["accepted_criticisms"].append("응답이 명확하지 않음")
            reflection["improvement_suggestions"].append("더 간결하고 명확한 문장으로 구성하라")
            
        if evaluation["actionability_score"] < 0.5:
            reflection["accepted_criticisms"].append("실행 가능한 구체적 지침 부족")
            reflection["improvement_suggestions"].append("구체적인 단계나 예제를 포함하라")
            
        return reflection
        
    def _generate_improvements_realtime(self, reflection: Dict[str, Any]) -> list:
        """실시간 개선 제안 생성"""
        return reflection.get("improvement_suggestions", [])
        
    def _update_learning_metrics_realtime(self, evaluation: Dict[str, Any], reflection: Dict[str, Any]):
        """실시간 학습 메트릭 업데이트"""
        # 자동 학습 시스템의 메트릭 업데이트
        if hasattr(self.autonomous_learner, 'learning_history'):
            metric = {
                "timestamp": datetime.now().isoformat(),
                "realtime_evaluation": evaluation,
                "realtime_reflection": reflection,
                "learning_type": "realtime"
            }
            self.autonomous_learner.learning_history.append(metric)
            
    def _generate_realtime_feedback(self, evaluation: Dict[str, Any], improvements: list):
        """실시간 피드백 생성"""
        if evaluation["overall_score"] < 0.5:
            logger.warning(f"실시간 학습: 응답 품질이 낮음 (점수: {evaluation['overall_score']:.2f})")
            if improvements:
                logger.info(f"개선 제안: {', '.join(improvements[:3])}")
        else:
            logger.info(f"실시간 학습: 응답 품질 양호 (점수: {evaluation['overall_score']:.2f})")
            
    def _update_autonomous_learner(self, user_input: str, assistant_response: str):
        """자동 학습 시스템 업데이트"""
        # 자동 학습 시스템에 대화 데이터 전달
        if hasattr(self.autonomous_learner, '_save_learning_record'):
            metrics = {
                "realtime_conversation": True,
                "user_input_length": len(user_input),
                "assistant_response_length": len(assistant_response),
                "conversation_timestamp": datetime.now().isoformat()
            }
            self.autonomous_learner._save_learning_record(metrics, 0.5)
            
    def add_conversation(self, user_input: str, assistant_response: str):
        """대화 추가 (실시간 처리)"""
        conversation = {
            "user_input": user_input,
            "assistant_response": assistant_response,
            "timestamp": datetime.now().isoformat()
        }
        
        # 실시간 처리
        self._process_conversation_realtime(conversation)
        
        # 큐에도 추가 (백업용)
        try:
            self.conversation_queue.put_nowait(conversation)
        except:
            pass  # 큐가 가득 찬 경우 무시
            
    def get_realtime_status(self) -> Dict[str, Any]:
        """실시간 학습 상태 반환"""
        return {
            "is_active": self.is_active,
            "queue_size": self.conversation_queue.qsize() if hasattr(self.conversation_queue, 'qsize') else 0,
            "last_conversation_time": self.last_conversation_time,
            "learning_history_count": len(self.autonomous_learner.learning_history) if hasattr(self.autonomous_learner, 'learning_history') else 0
        }

# 전역 인스턴스
realtime_learner = None

def initialize_realtime_learner(autonomous_learner):
    """실시간 학습 시스템 초기화"""
    global realtime_learner
    realtime_learner = RealtimeLearner(autonomous_learner)
    return realtime_learner 