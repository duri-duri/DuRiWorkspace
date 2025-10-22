#!/usr/bin/env python3
"""
Extension 연결을 위한 실제 학습 기능이 구현된 서버 + 통합 시점 알림 시스템 + 학습 시각화 + 자기 성찰 시스템
"""

import ast
import base64
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="DuRi Extension Learning Server",
    description="실제 학습 기능이 구현된 Extension 서버 + 통합 시점 알림 + 학습 시각화 + 자기 성찰",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 학습 데이터 저장소
LEARNING_DATA_DIR = "/tmp/duri_learning_data"
os.makedirs(LEARNING_DATA_DIR, exist_ok=True)

# 통합 시점 모니터링
INTEGRATION_THRESHOLDS = {
    "learning_patterns": 50,  # 학습 패턴 수
    "response_time": 1.5,  # 응답 시간 (초)
    "code_complexity": 3,  # 코드 복잡도 단계
    "user_requirements": "advanced",  # 사용자 요구사항 수준
}


class SelfReflectionEngine:
    """자기 성찰 엔진 - DuRi가 자신의 답변을 평가하고 개선 방안을 제시"""

    def __init__(self):
        self.reflection_history = []
        self.improvement_suggestions = []

    def reflect_on_response(
        self, conversation: str, response_quality: float, learning_value: float
    ) -> Dict[str, Any]:
        """답변에 대한 자기 성찰 수행"""

        reflection = {
            "timestamp": datetime.now().isoformat(),
            "conversation": conversation,
            "response_quality": response_quality,
            "learning_value": learning_value,
            "self_questions": [],
            "improvement_areas": [],
            "action_plan": [],
        }

        # 자기 질문들
        reflection["self_questions"] = [
            "내 답변이 사용자의 질문을 충분히 해결했을까?",
            "더 구체적인 예제가 필요하지 않았을까?",
            "사용자의 수준에 맞는 설명이었을까?",
            "실용적인 정보를 제공했을까?",
        ]

        # 개선 영역 분석
        if response_quality < 0.5:
            reflection["improvement_areas"].append("답변 품질이 낮음 - 더 상세한 설명 필요")
        if learning_value < 0.3:
            reflection["improvement_areas"].append("학습 가치가 낮음 - 더 교육적인 내용 필요")
        if len(conversation.split()) < 10:
            reflection["improvement_areas"].append("질문이 간단함 - 더 구체적인 예제 제공 필요")

        # 액션 플랜 생성
        reflection["action_plan"] = self._generate_action_plan(reflection["improvement_areas"])

        # 성찰 기록 저장
        self.reflection_history.append(reflection)

        return reflection

    def _generate_action_plan(self, improvement_areas: List[str]) -> List[str]:
        """개선 영역에 따른 액션 플랜 생성"""
        action_plan = []

        for area in improvement_areas:
            if "답변 품질" in area:
                action_plan.append("더 상세한 단계별 설명 추가")
                action_plan.append("코드 예제와 함께 설명")
            elif "학습 가치" in area:
                action_plan.append("실습 예제 포함")
                action_plan.append("관련 개념 연결")
            elif "구체적인 예제" in area:
                action_plan.append("실제 사용 사례 추가")
                action_plan.append("단계별 튜토리얼 제공")

        return action_plan

    def get_improvement_suggestions(self) -> List[str]:
        """전체 개선 제안 수집"""
        suggestions = []

        for reflection in self.reflection_history[-5:]:  # 최근 5개 성찰만
            suggestions.extend(reflection["action_plan"])

        return list(set(suggestions))  # 중복 제거

    def analyze_trends(self) -> Dict[str, Any]:
        """성찰 트렌드 분석"""
        if not self.reflection_history:
            return {"message": "아직 성찰 데이터가 없습니다"}

        recent_reflections = self.reflection_history[-10:]  # 최근 10개

        avg_response_quality = sum(r["response_quality"] for r in recent_reflections) / len(
            recent_reflections
        )
        avg_learning_value = sum(r["learning_value"] for r in recent_reflections) / len(
            recent_reflections
        )

        improvement_frequency = defaultdict(int)
        for reflection in recent_reflections:
            for area in reflection["improvement_areas"]:
                improvement_frequency[area] += 1

        return {
            "avg_response_quality": avg_response_quality,
            "avg_learning_value": avg_learning_value,
            "most_common_improvements": sorted(
                improvement_frequency.items(), key=lambda x: x[1], reverse=True
            )[:3],
            "total_reflections": len(self.reflection_history),
        }


# 자기 성찰 엔진 인스턴스
self_reflection_engine = SelfReflectionEngine()


class LearningVisualizer:
    """학습 패턴 시각화 시스템"""

    def __init__(self):
        self.chart_cache = {}

    def generate_learning_trend_chart(self) -> str:
        """학습 트렌드 차트 생성"""
        try:
            # 학습 데이터 로드
            learning_data = self._load_learning_data()

            if not learning_data:
                return self._create_empty_chart("학습 데이터가 없습니다")

            # 차트 생성
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

            # 학습 가치 트렌드
            timestamps = [data.get("timestamp", "") for data in learning_data]
            learning_values = [data.get("learning_value", 0) for data in learning_data]

            ax1.plot(
                range(len(learning_values)),
                learning_values,
                "b-o",
                linewidth=2,
                markersize=6,
            )
            ax1.set_title("Learning Value Trend", fontsize=14, fontweight="bold")
            ax1.set_ylabel("Learning Value", fontsize=12)
            ax1.set_ylim(0, 1)
            ax1.grid(True, alpha=0.3)

            # 복잡도 트렌드
            complexities = [data.get("learning_complexity", 0) for data in learning_data]
            ax2.plot(range(len(complexities)), complexities, "r-s", linewidth=2, markersize=6)
            ax2.set_title("Learning Complexity Trend", fontsize=14, fontweight="bold")
            ax2.set_ylabel("Complexity", fontsize=12)
            ax2.set_xlabel("Learning Session", fontsize=12)
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()

            # 차트를 base64로 인코딩
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            return chart_base64

        except Exception as e:
            print(f"차트 생성 오류: {e}")
            return self._create_empty_chart("차트 생성 실패")

    def generate_concept_analysis_chart(self) -> str:
        """개념 분석 차트 생성"""
        try:
            learning_data = self._load_learning_data()

            if not learning_data:
                return self._create_empty_chart("학습 데이터가 없습니다")

            # 개념 빈도 분석
            concept_freq = defaultdict(int)
            for data in learning_data:
                concepts = data.get("key_concepts", [])
                for concept in concepts:
                    concept_freq[concept] += 1

            if not concept_freq:
                return self._create_empty_chart("개념 데이터가 없습니다")

            # 상위 10개 개념만 선택
            top_concepts = sorted(concept_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            concepts, frequencies = zip(*top_concepts)

            # 차트 생성
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(range(len(concepts)), frequencies, color="skyblue", alpha=0.7)

            ax.set_title("Key Concept Frequency Analysis", fontsize=14, fontweight="bold")
            ax.set_xlabel("Concepts", fontsize=12)
            ax.set_ylabel("Frequency", fontsize=12)
            ax.set_xticks(range(len(concepts)))
            ax.set_xticklabels(concepts, rotation=45, ha="right")

            # 값 표시
            for i, v in enumerate(frequencies):
                ax.text(i, v + 0.1, str(v), ha="center", va="bottom", fontweight="bold")

            plt.tight_layout()

            # 차트를 base64로 인코딩
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()

            return chart_base64

        except Exception as e:
            print(f"개념 분석 차트 생성 오류: {e}")
            return self._create_empty_chart("개념 분석 차트 생성 실패")

    def _load_learning_data(self) -> List[Dict[str, Any]]:
        """학습 데이터 로드"""
        learning_data = []

        try:
            for filename in os.listdir(LEARNING_DATA_DIR):
                if filename.endswith(".json"):
                    filepath = os.path.join(LEARNING_DATA_DIR, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        learning_data.append(data)
        except Exception as e:
            print(f"학습 데이터 로드 오류: {e}")

        return learning_data

    def _create_empty_chart(self, message: str) -> str:
        """빈 차트 생성"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=14,
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return chart_base64


# 학습 시각화 인스턴스
learning_visualizer = LearningVisualizer()


class IntegrationMonitor:
    """통합 시점 모니터링 시스템"""

    def __init__(self):
        self.learning_patterns_count = 0
        self.response_times = []
        self.code_complexity_level = 1
        self.user_requirements_level = "basic"
        self.integration_alerts = []

    def check_integration_needed(self) -> Dict[str, Any]:
        """통합 필요성 체크"""
        alerts = []

        # 학습 패턴 수 체크
        if self.learning_patterns_count >= INTEGRATION_THRESHOLDS["learning_patterns"]:
            alerts.append(
                f"⚠️ 학습 패턴이 {self.learning_patterns_count}개 축적됨 (임계값: {INTEGRATION_THRESHOLDS['learning_patterns']})"
            )

        # 응답 시간 체크
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            if avg_response_time >= INTEGRATION_THRESHOLDS["response_time"]:
                alerts.append(
                    f"⚠️ 평균 응답 시간이 {avg_response_time:.2f}초 (임계값: {INTEGRATION_THRESHOLDS['response_time']}초)"
                )

        # 코드 복잡도 체크
        if self.code_complexity_level >= INTEGRATION_THRESHOLDS["code_complexity"]:
            alerts.append(
                f"⚠️ 코드 복잡도가 {self.code_complexity_level}단계 (임계값: {INTEGRATION_THRESHOLDS['code_complexity']}단계)"
            )

        # 사용자 요구사항 체크
        if self.user_requirements_level == "advanced":
            alerts.append("⚠️ 고급 기능 요구사항이 감지됨")

        # 통합 필요성 판단
        integration_needed = len(alerts) >= 2  # 2개 이상의 경고가 있으면 통합 필요

        return {
            "integration_needed": integration_needed,
            "alerts": alerts,
            "metrics": {
                "learning_patterns": self.learning_patterns_count,
                "avg_response_time": (
                    sum(self.response_times) / len(self.response_times)
                    if self.response_times
                    else 0
                ),
                "code_complexity": self.code_complexity_level,
                "user_requirements": self.user_requirements_level,
            },
            "thresholds": INTEGRATION_THRESHOLDS,
        }

    def update_metrics(self, response_time: float, complexity_increase: bool = False):
        """메트릭 업데이트"""
        self.response_times.append(response_time)
        if len(self.response_times) > 10:  # 최근 10개만 유지
            self.response_times.pop(0)

        if complexity_increase:
            self.code_complexity_level += 1

    def increment_learning_patterns(self):
        """학습 패턴 수 증가"""
        self.learning_patterns_count += 1


# 통합 모니터 인스턴스
integration_monitor = IntegrationMonitor()


class LearningAnalyzer:
    """실제 학습 분석기"""

    def __init__(self):
        self.conversation_history = []
        self.learning_patterns = defaultdict(int)
        self.key_concepts = set()

    def analyze_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """대화 내용을 분석하여 학습 가치를 평가"""

        conversation = conversation_data.get("conversation", "")
        user = conversation_data.get("user", "unknown")
        timestamp = conversation_data.get("timestamp", datetime.now().isoformat())

        # 대화 내용 분석
        analysis_result = {
            "conversation_length": len(conversation),
            "word_count": len(conversation.split()),
            "key_concepts": self._extract_key_concepts(conversation),
            "learning_complexity": self._calculate_complexity(conversation),
            "user_engagement": self._analyze_engagement(conversation),
            "timestamp": timestamp,
            "user": user,
        }

        # 학습 가치 계산
        learning_value = self._calculate_learning_value(analysis_result)
        analysis_result["learning_value"] = learning_value

        # 패턴 저장
        self._save_learning_pattern(analysis_result)

        # 통합 모니터링 업데이트
        integration_monitor.increment_learning_patterns()

        return analysis_result

    def _extract_key_concepts(self, conversation: str) -> List[str]:
        """대화에서 핵심 개념 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
        keywords = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", conversation)
        technical_terms = re.findall(
            r"\b(?:API|HTTP|JSON|Python|JavaScript|React|Vue|Node|Server|Client|Database|Cache|Async|Sync)\b",
            conversation,
            re.IGNORECASE,
        )

        concepts = list(set(keywords + technical_terms))
        return concepts[:10]  # 상위 10개만 반환

    def _calculate_complexity(self, conversation: str) -> float:
        """대화의 복잡도 계산"""
        sentences = re.split(r"[.!?]+", conversation)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(
            len(sentences), 1
        )

        # 기술적 용어 비율
        tech_terms = len(
            re.findall(
                r"\b(?:API|HTTP|JSON|Python|JavaScript|React|Vue|Node|Server|Client|Database|Cache|Async|Sync)\b",
                conversation,
                re.IGNORECASE,
            )
        )
        tech_ratio = tech_terms / max(len(conversation.split()), 1)

        complexity = (avg_sentence_length * 0.3) + (tech_ratio * 100 * 0.7)
        return min(complexity, 1.0)

    def _analyze_engagement(self, conversation: str) -> float:
        """사용자 참여도 분석"""
        questions = len(re.findall(r"\?", conversation))
        explanations = len(
            re.findall(
                r"\b(?:because|since|therefore|thus|hence|so|as|for)\b",
                conversation,
                re.IGNORECASE,
            )
        )

        engagement = (questions * 0.4) + (explanations * 0.6)
        return min(engagement / max(len(conversation.split()), 1), 1.0)

    def _calculate_learning_value(self, analysis: Dict[str, Any]) -> float:
        """학습 가치 계산"""
        complexity = analysis.get("learning_complexity", 0)
        engagement = analysis.get("user_engagement", 0)
        concept_count = len(analysis.get("key_concepts", []))

        # 가중 평균으로 학습 가치 계산
        learning_value = (
            (complexity * 0.4) + (engagement * 0.3) + (min(concept_count / 5, 1.0) * 0.3)
        )
        return round(learning_value, 3)

    def _save_learning_pattern(self, analysis: Dict[str, Any]):
        """학습 패턴 저장"""
        timestamp = analysis.get("timestamp", datetime.now().isoformat())
        filename = f"{LEARNING_DATA_DIR}/learning_pattern_{timestamp.replace(':', '-')}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)


# 학습 분석기 인스턴스
learning_analyzer = LearningAnalyzer()


class ChatGPTEvaluator:
    """ChatGPT의 6차원 답변 평가 시스템"""

    EVALUATION_CRITERIA = {
        "correctness": 0.30,  # 정확성 (사실, 개념, 로직)
        "relevance": 0.20,  # 적합성 (질문 의도와의 밀접도)
        "depth": 0.15,  # 깊이 (근본적 원인 분석)
        "structure": 0.10,  # 구조화 (논리적 구성)
        "clarity": 0.15,  # 명료성 (이해하기 쉬운 설명)
        "actionability": 0.10,  # 실용성 (적용 가능성)
    }

    def evaluate_response(self, duri_response: str, user_question: str) -> Dict[str, Any]:
        """ChatGPT가 DuRi 답변을 6차원으로 평가"""

        evaluation = {
            "scores": self._calculate_6d_scores(duri_response, user_question),
            "suggestions": self._identify_improvements(duri_response),
            "critical_issues": self._find_critical_issues(duri_response),
            "overall_assessment": self._generate_overall_assessment(duri_response),
            "timestamp": datetime.now().isoformat(),
        }

        # 총점 계산
        total_score = sum(
            evaluation["scores"][criterion] * weight
            for criterion, weight in self.EVALUATION_CRITERIA.items()
        )
        evaluation["total_score"] = round(total_score, 3)

        return evaluation

    def _calculate_6d_scores(self, response: str, question: str) -> Dict[str, float]:
        """6차원 점수 계산"""
        scores = {}

        # 정확성: 기술적 용어와 개념의 정확성
        tech_terms = len(
            re.findall(
                r"\b(?:API|HTTP|JSON|Python|JavaScript|React|Vue|Node|Server|Client|Database|Cache|Async|Sync)\b",
                response,
                re.IGNORECASE,
            )
        )
        scores["correctness"] = min(tech_terms / max(len(response.split()), 1) * 10, 1.0)

        # 적합성: 질문 키워드와 답변의 일치도
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        overlap = len(question_words.intersection(response_words))
        scores["relevance"] = min(overlap / max(len(question_words), 1), 1.0)

        # 깊이: 분석적 내용의 깊이
        analytical_words = len(
            re.findall(
                r"\b(?:because|since|therefore|thus|hence|analysis|compare|difference|advantage|disadvantage)\b",
                response,
                re.IGNORECASE,
            )
        )
        scores["depth"] = min(analytical_words / max(len(response.split()), 1) * 5, 1.0)

        # 구조화: 논리적 구성
        structure_indicators = len(
            re.findall(
                r"\b(?:first|second|third|finally|however|moreover|in addition|conclusion)\b",
                response,
                re.IGNORECASE,
            )
        )
        scores["structure"] = min(structure_indicators / max(len(response.split()), 1) * 8, 1.0)

        # 명료성: 이해하기 쉬운 설명
        simple_sentences = len([s for s in response.split(".") if len(s.split()) < 20])
        total_sentences = len(response.split("."))
        scores["clarity"] = min(simple_sentences / max(total_sentences, 1), 1.0)

        # 실용성: 적용 가능한 내용
        practical_indicators = len(
            re.findall(
                r"\b(?:example|code|implementation|step|guide|tutorial|practice)\b",
                response,
                re.IGNORECASE,
            )
        )
        scores["actionability"] = min(practical_indicators / max(len(response.split()), 1) * 3, 1.0)

        return {k: round(v, 3) for k, v in scores.items()}

    def _identify_improvements(self, response: str) -> List[str]:
        """개선점 식별"""
        suggestions = []

        if len(response.split()) < 50:
            suggestions.append("더 상세한 설명이 필요합니다")

        if "example" not in response.lower() and "code" not in response.lower():
            suggestions.append("실제 코드 예제를 추가해보세요")

        if "because" not in response.lower() and "reason" not in response.lower():
            suggestions.append("이유와 근거를 더 명확히 설명해보세요")

        if len(re.findall(r"\b(?:first|second|finally)\b", response, re.IGNORECASE)) < 2:
            suggestions.append("단계별로 구조화된 설명을 추가해보세요")

        return suggestions

    def _find_critical_issues(self, response: str) -> List[str]:
        """중요한 문제점 발견"""
        issues = []

        if len(response.split()) < 20:
            issues.append("답변이 너무 짧습니다")

        if not re.search(
            r"\b(?:API|HTTP|JSON|Python|JavaScript|React|Vue|Node|Server|Client|Database|Cache|Async|Sync)\b",
            response,
            re.IGNORECASE,
        ):
            issues.append("기술적 내용이 부족합니다")

        if "?" in response and len(response.split("?")) > 2:
            issues.append("질문보다는 답변에 집중해보세요")

        return issues

    def _generate_overall_assessment(self, response: str) -> str:
        """전체 평가 생성"""
        word_count = len(response.split())

        if word_count < 30:
            return "답변이 너무 간단합니다. 더 구체적인 정보가 필요합니다."
        elif word_count < 100:
            return "적절한 수준이지만, 더 깊이 있는 분석이 가능합니다."
        else:
            return "상세하고 포괄적인 답변입니다. 잘 작성되었습니다."


# ChatGPT 평가기 인스턴스
chatgpt_evaluator = ChatGPTEvaluator()


class DuRiSelfReflector:
    """DuRi의 2차 성찰 시스템"""

    def __init__(self):
        self.reflection_history = []
        self.improvement_proposals = []

    def reflect_on_chatgpt_feedback(
        self,
        chatgpt_evaluation: Dict[str, Any],
        original_response: str,
        user_question: str,
    ) -> Dict[str, Any]:
        """ChatGPT 피드백을 받아 DuRi가 자기성찰"""

        reflection = {
            "timestamp": datetime.now().isoformat(),
            "chatgpt_evaluation": chatgpt_evaluation,
            "original_response": original_response,
            "user_question": user_question,
            "accepted_criticisms": self._analyze_accepted_points(chatgpt_evaluation),
            "disagreements": self._identify_disagreements(chatgpt_evaluation),
            "improvement_proposal": self._generate_improvement_proposal(chatgpt_evaluation),
            "discussion_request": "ChatGPT와 이 개선안에 대해 논의하고 싶습니다.",
            "self_assessment": self._self_assess_response(original_response, user_question),
        }

        # 성찰 기록 저장
        self.reflection_history.append(reflection)

        return reflection

    def _analyze_accepted_points(self, evaluation: Dict[str, Any]) -> List[str]:
        """ChatGPT 평가에서 수용할 점들 분석"""
        accepted = []

        scores = evaluation.get("scores", {})
        suggestions = evaluation.get("suggestions", [])

        # 낮은 점수 영역 수용
        for criterion, score in scores.items():
            if score < 0.6:
                accepted.append(f"{criterion} 영역 개선 필요 (점수: {score})")

        # 제안사항 수용
        accepted.extend(suggestions)

        return accepted

    def _identify_disagreements(self, evaluation: Dict[str, Any]) -> List[str]:
        """ChatGPT 평가와 의견이 다른 부분 식별"""
        disagreements = []

        scores = evaluation.get("scores", {})
        total_score = evaluation.get("total_score", 0)

        # DuRi의 자기 평가와 비교
        if total_score < 0.7:
            disagreements.append("ChatGPT가 평가한 점수가 예상보다 낮습니다")

        if scores.get("actionability", 0) < 0.5:
            disagreements.append("실용성 평가에 대해 더 구체적인 기준이 필요합니다")

        return disagreements

    def _generate_improvement_proposal(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """개선 제안 생성"""
        proposal = {
            "reasoning": self._analyze_improvement_reasoning(evaluation),
            "specific_improvements": self._generate_specific_improvements(evaluation),
            "code_examples": self._suggest_code_examples(evaluation),
            "structure_changes": self._suggest_structure_changes(evaluation),
            "priority": self._determine_priority(evaluation),
        }

        return proposal

    def _analyze_improvement_reasoning(self, evaluation: Dict[str, Any]) -> str:
        """개선 이유 분석"""
        scores = evaluation.get("scores", {})
        critical_issues = evaluation.get("critical_issues", [])

        if scores.get("actionability", 0) < 0.5:
            return "실용적인 예제와 코드가 부족하여 개선이 필요합니다"
        elif scores.get("depth", 0) < 0.6:
            return "분석의 깊이가 부족하여 더 근본적인 설명이 필요합니다"
        elif len(critical_issues) > 0:
            return f"중요한 문제점들이 발견되어 우선적으로 해결해야 합니다: {', '.join(critical_issues)}"
        else:
            return "전반적으로 양호하지만 세부적인 개선이 가능합니다"

    def _generate_specific_improvements(self, evaluation: Dict[str, Any]) -> List[str]:
        """구체적인 개선 방안 생성"""
        improvements = []
        scores = evaluation.get("scores", {})

        if scores.get("actionability", 0) < 0.5:
            improvements.append("실제 코드 예제 추가")
            improvements.append("단계별 구현 가이드 제공")

        if scores.get("depth", 0) < 0.6:
            improvements.append("이유와 근거를 더 명확히 설명")
            improvements.append("비교 분석 추가")

        if scores.get("structure", 0) < 0.7:
            improvements.append("논리적 구조 개선")
            improvements.append("단계별 설명 추가")

        return improvements

    def _suggest_code_examples(self, evaluation: Dict[str, Any]) -> List[str]:
        """코드 예제 제안"""
        examples = []
        scores = evaluation.get("scores", {})

        if scores.get("actionability", 0) < 0.5:
            examples.append("기본 사용법 예제")
            examples.append("실제 프로젝트 적용 예제")
            examples.append("에러 처리 예제")

        return examples

    def _suggest_structure_changes(self, evaluation: Dict[str, Any]) -> List[str]:
        """구조 변경 제안"""
        changes = []
        scores = evaluation.get("scores", {})

        if scores.get("structure", 0) < 0.7:
            changes.append("개요-설명-예제-결론 구조로 변경")
            changes.append("단계별 번호 매기기")
            changes.append("중요 포인트 강조")

        return changes

    def _determine_priority(self, evaluation: Dict[str, Any]) -> str:
        """우선순위 결정"""
        critical_issues = evaluation.get("critical_issues", [])
        total_score = evaluation.get("total_score", 0)

        if len(critical_issues) > 0:
            return "high"
        elif total_score < 0.6:
            return "medium"
        else:
            return "low"

    def _self_assess_response(self, response: str, question: str) -> Dict[str, Any]:
        """DuRi의 자기 평가"""
        return {
            "response_length": len(response.split()),
            "technical_depth": len(
                re.findall(
                    r"\b(?:API|HTTP|JSON|Python|JavaScript|React|Vue|Node|Server|Client|Database|Cache|Async|Sync)\b",
                    response,
                    re.IGNORECASE,
                )
            ),
            "has_examples": "example" in response.lower() or "code" in response.lower(),
            "has_structure": len(
                re.findall(
                    r"\b(?:first|second|finally|however|moreover)\b",
                    response,
                    re.IGNORECASE,
                )
            )
            > 0,
            "self_score": min(len(response.split()) / 100, 1.0),
        }


# DuRi 자기성찰기 인스턴스
duri_self_reflector = DuRiSelfReflector()


class DuRiChatGPTDiscussion:
    """DuRi와 ChatGPT 간의 대화 기반 협의 시스템"""

    def __init__(self):
        self.discussion_history = []
        self.agreement_threshold = 0.7
        self.max_discussion_rounds = 3

    def initiate_discussion(
        self,
        duri_improvement_proposal: Dict[str, Any],
        chatgpt_evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """DuRi의 개선안에 대한 ChatGPT와의 논의 시작"""

        discussion = {
            "timestamp": datetime.now().isoformat(),
            "round": 1,
            "duri_proposal": duri_improvement_proposal,
            "chatgpt_evaluation": chatgpt_evaluation,
            "discussion_points": [],
            "agreement_level": 0.0,
            "final_consensus": None,
            "action_items": [],
        }

        # 논의 포인트 생성
        discussion["discussion_points"] = self._generate_discussion_points(
            duri_improvement_proposal, chatgpt_evaluation
        )

        # 합의 수준 계산
        discussion["agreement_level"] = self._calculate_agreement_level(
            duri_improvement_proposal, chatgpt_evaluation
        )

        # 최종 합의 도출
        discussion["final_consensus"] = self._reach_consensus(discussion)

        # 실행 항목 생성
        discussion["action_items"] = self._generate_action_items(discussion["final_consensus"])

        # 논의 기록 저장
        self.discussion_history.append(discussion)

        return discussion

    def _generate_discussion_points(
        self, duri_proposal: Dict[str, Any], chatgpt_eval: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """논의 포인트 생성"""
        points = []

        # DuRi의 개선안 분석
        duri_improvements = duri_proposal.get("specific_improvements", [])
        chatgpt_suggestions = chatgpt_eval.get("suggestions", [])

        # 일치하는 개선안 찾기
        common_improvements = []
        for duri_imp in duri_improvements:
            for chatgpt_sug in chatgpt_suggestions:
                if self._similar_improvements(duri_imp, chatgpt_sug):
                    common_improvements.append(
                        {
                            "type": "agreement",
                            "duri_suggestion": duri_imp,
                            "chatgpt_suggestion": chatgpt_sug,
                            "priority": "high",
                        }
                    )

        # 추가 제안사항
        additional_suggestions = []
        for chatgpt_sug in chatgpt_suggestions:
            if not any(
                self._similar_improvements(duri_imp, chatgpt_sug) for duri_imp in duri_improvements
            ):
                additional_suggestions.append(
                    {
                        "type": "chatgpt_additional",
                        "suggestion": chatgpt_sug,
                        "priority": "medium",
                    }
                )

        # DuRi의 고유 제안
        duri_unique = []
        for duri_imp in duri_improvements:
            if not any(
                self._similar_improvements(duri_imp, chatgpt_sug)
                for chatgpt_sug in chatgpt_suggestions
            ):
                duri_unique.append(
                    {
                        "type": "duri_unique",
                        "suggestion": duri_imp,
                        "priority": "medium",
                    }
                )

        points.extend(common_improvements)
        points.extend(additional_suggestions)
        points.extend(duri_unique)

        return points

    def _similar_improvements(self, improvement1: str, improvement2: str) -> bool:
        """두 개선안이 유사한지 판단"""
        keywords1 = set(improvement1.lower().split())
        keywords2 = set(improvement2.lower().split())

        # 키워드 유사도 계산
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)

        if len(union) == 0:
            return False

        similarity = len(intersection) / len(union)
        return similarity > 0.3  # 30% 이상 유사하면 같은 개선안으로 간주

    def _calculate_agreement_level(
        self, duri_proposal: Dict[str, Any], chatgpt_eval: Dict[str, Any]
    ) -> float:
        """합의 수준 계산"""
        duri_improvements = set(duri_proposal.get("specific_improvements", []))
        chatgpt_suggestions = set(chatgpt_eval.get("suggestions", []))

        # 유사한 제안 수 계산
        similar_count = 0
        for duri_imp in duri_improvements:
            for chatgpt_sug in chatgpt_suggestions:
                if self._similar_improvements(duri_imp, chatgpt_sug):
                    similar_count += 1
                    break

        # 합의 수준 계산
        total_suggestions = len(duri_improvements) + len(chatgpt_suggestions)
        if total_suggestions == 0:
            return 1.0

        agreement_level = (similar_count * 2) / total_suggestions
        return min(agreement_level, 1.0)

    def _reach_consensus(self, discussion: Dict[str, Any]) -> Dict[str, Any]:
        """최종 합의 도출"""
        consensus = {
            "agreement_level": discussion["agreement_level"],
            "accepted_improvements": [],
            "rejected_improvements": [],
            "compromise_suggestions": [],
            "implementation_plan": [],
        }

        # 합의 수준에 따른 처리
        if discussion["agreement_level"] >= self.agreement_threshold:
            # 높은 합의 - 대부분의 제안 수용
            for point in discussion["discussion_points"]:
                if point["type"] == "agreement":
                    consensus["accepted_improvements"].append(point["duri_suggestion"])
                elif point["type"] in ["chatgpt_additional", "duri_unique"]:
                    consensus["accepted_improvements"].append(point["suggestion"])
        else:
            # 낮은 합의 - 타협안 생성
            for point in discussion["discussion_points"]:
                if point["type"] == "agreement":
                    consensus["accepted_improvements"].append(point["duri_suggestion"])
                else:
                    consensus["compromise_suggestions"].append(point["suggestion"])

        # 구현 계획 생성
        consensus["implementation_plan"] = self._generate_implementation_plan(consensus)

        return consensus

    def _generate_implementation_plan(self, consensus: Dict[str, Any]) -> List[Dict[str, Any]]:
        """구현 계획 생성"""
        plan = []

        for improvement in consensus["accepted_improvements"]:
            plan.append(
                {
                    "action": improvement,
                    "priority": "high",
                    "estimated_effort": "medium",
                    "dependencies": [],
                }
            )

        for suggestion in consensus["compromise_suggestions"]:
            plan.append(
                {
                    "action": suggestion,
                    "priority": "medium",
                    "estimated_effort": "low",
                    "dependencies": [],
                }
            )

        return plan

    def _generate_action_items(self, consensus: Dict[str, Any]) -> List[Dict[str, Any]]:
        """실행 항목 생성"""
        action_items = []

        for item in consensus["implementation_plan"]:
            action_items.append(
                {
                    "description": item["action"],
                    "priority": item["priority"],
                    "status": "pending",
                    "assigned_to": "duri_system",
                    "deadline": "immediate",
                }
            )

        return action_items


# DuRi-ChatGPT 논의 시스템 인스턴스 생성
duri_chatgpt_discussion = DuRiChatGPTDiscussion()


class SafeCodeImprovementSystem:
    """안전한 코드 개선 시스템 - ChatGPT 제안 기반"""

    def __init__(self):
        self.backup_dir = "/tmp/duri_code_backups"
        self.pending_proposals = []
        self.approval_threshold = 0.7
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_code_improvement(
        self, discussion_result: Dict[str, Any], target_file: str = None
    ) -> Dict[str, Any]:
        """논의 결과를 바탕으로 코드 개선안 생성"""

        improvement = {
            "timestamp": datetime.now().isoformat(),
            "discussion_score": discussion_result.get("agreement_level", 0.0),
            "target_file": target_file or "test_extension_server.py",
            "improvement_type": "code_enhancement",
            "changes": [],
            "backup_created": False,
            "static_analysis_passed": False,
            "user_approval_required": True,
            "status": "pending",
        }

        # 논의 결과에서 개선안 추출
        consensus = discussion_result.get("final_consensus", {})
        accepted_improvements = consensus.get("accepted_improvements", [])

        # 코드 개선안 생성
        improvement["changes"] = self._generate_code_changes(accepted_improvements)

        # 백업 생성
        if target_file and os.path.exists(target_file):
            improvement["backup_created"] = self._create_backup(target_file)

        # 정적 분석
        if improvement["changes"]:
            improvement["static_analysis_passed"] = self._static_analysis(improvement["changes"])

        return improvement

    def _generate_code_changes(self, improvements: List[str]) -> List[Dict[str, Any]]:
        """개선안을 코드 변경사항으로 변환"""
        changes = []

        for improvement in improvements:
            if "코드 예제" in improvement:
                changes.append(
                    {
                        "type": "add_example",
                        "description": "실제 코드 예제 추가",
                        "code": self._generate_code_example(),
                        "location": "function_definition",
                    }
                )
            elif "구조" in improvement:
                changes.append(
                    {
                        "type": "restructure",
                        "description": "논리적 구조 개선",
                        "code": self._generate_structured_code(),
                        "location": "function_body",
                    }
                )
            elif "설명" in improvement:
                changes.append(
                    {
                        "type": "add_documentation",
                        "description": "상세한 설명 추가",
                        "code": self._generate_detailed_documentation(),
                        "location": "docstring",
                    }
                )

        return changes

    def _generate_code_example(self) -> str:
        """코드 예제 생성"""
        return '''
# 실제 사용 예제
@app.post("/example-endpoint")
async def example_endpoint(request: Dict[str, Any]):
    """
    실제 사용 예제를 포함한 엔드포인트
    """
    try:
        # 1. 입력 검증
        if not request.get("data"):
            raise HTTPException(status_code=400, detail="데이터가 필요합니다")

        # 2. 비즈니스 로직 처리
        result = process_business_logic(request["data"])

        # 3. 응답 생성
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.exception("예제 엔드포인트 오류")
        raise HTTPException(status_code=500, detail=str(e))
'''

    def _generate_structured_code(self) -> str:
        """구조화된 코드 생성"""
        return '''
def structured_function():
    """
    논리적 구조를 가진 함수
    """
    # 1. 초기화
    config = load_configuration()

    # 2. 데이터 검증
    validate_input_data()

    # 3. 핵심 처리
    result = process_core_logic()

    # 4. 결과 검증
    validate_output(result)

    # 5. 응답 반환
    return format_response(result)
'''

    def _generate_detailed_documentation(self) -> str:
        """상세한 문서화 생성"""
        return '''
"""
상세한 설명을 포함한 함수

Args:
    param1 (str): 첫 번째 매개변수 설명
    param2 (int): 두 번째 매개변수 설명

Returns:
    Dict[str, Any]: 처리 결과

Raises:
    ValueError: 잘못된 입력 시
    HTTPException: 서버 오류 시

Example:
    >>> result = detailed_function("test", 123)
    >>> print(result)
    {'status': 'success', 'data': 'processed'}
"""
'''

    def _create_backup(self, file_path: str) -> bool:
        """파일 백업 생성"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"{Path(file_path).stem}_{timestamp}.bak")
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            print(f"백업 생성 실패: {e}")
            return False

    def _static_analysis(self, changes: List[Dict[str, Any]]) -> bool:
        """정적 분석으로 코드 유효성 검사"""
        try:
            for change in changes:
                if "code" in change:
                    # AST를 사용한 구문 검사
                    ast.parse(change["code"])
            return True
        except SyntaxError:
            return False

    def apply_improvement(
        self, improvement: Dict[str, Any], user_approval: bool = False
    ) -> Dict[str, Any]:
        """개선안 적용"""

        result = {
            "status": "pending",
            "message": "",
            "applied_changes": [],
            "errors": [],
        }

        # 승인 조건 확인
        if not user_approval:
            result["status"] = "rejected"
            result["message"] = "사용자 승인이 필요합니다"
            return result

        if improvement["discussion_score"] < self.approval_threshold:
            result["status"] = "rejected"
            result["message"] = (
                f"합의 점수가 낮습니다 ({improvement['discussion_score']:.2f} < {self.approval_threshold})"
            )
            return result

        if not improvement["static_analysis_passed"]:
            result["status"] = "rejected"
            result["message"] = "정적 분석을 통과하지 못했습니다"
            return result

        # 실제 코드 적용
        try:
            target_file = improvement["target_file"]

            # 임시 파일에 변경사항 적용
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 변경사항 적용 (간단한 예시)
            for change in improvement["changes"]:
                if change["type"] == "add_example":
                    # 함수 끝에 예제 추가
                    content += "\n" + change["code"]
                    result["applied_changes"].append(change["description"])

            # 변경된 내용을 파일에 쓰기
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)

            result["status"] = "applied"
            result["message"] = f"{len(result['applied_changes'])}개 변경사항이 적용되었습니다"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"코드 적용 중 오류: {str(e)}"
            result["errors"].append(str(e))

        return result


# 안전한 코드 개선 시스템 인스턴스 생성
safe_code_improvement = SafeCodeImprovementSystem()


@app.post("/chatgpt-evaluate")
async def chatgpt_evaluate_response(evaluation_request: Dict[str, Any]):
    """ChatGPT가 DuRi 답변을 평가하는 엔드포인트"""
    try:
        duri_response = evaluation_request.get("duri_response", "")
        user_question = evaluation_request.get("user_question", "")

        if not duri_response or not user_question:
            raise HTTPException(
                status_code=400, detail="duri_response와 user_question이 필요합니다"
            )

        evaluation = chatgpt_evaluator.evaluate_response(duri_response, user_question)

        print(f"🤖 ChatGPT 평가 완료: 총점 {evaluation['total_score']}")
        print(f"   📊 세부 점수: {evaluation['scores']}")
        print(f"   💡 개선 제안: {evaluation['suggestions']}")

        return {
            "status": "success",
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ ChatGPT 평가 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/duri-self-reflect")
async def duri_self_reflect_endpoint(reflection_request: Dict[str, Any]):
    """DuRi가 ChatGPT 피드백을 받아 자기성찰하는 엔드포인트"""
    try:
        chatgpt_evaluation = reflection_request.get("chatgpt_evaluation", {})
        original_response = reflection_request.get("original_response", "")
        user_question = reflection_request.get("user_question", "")

        if not chatgpt_evaluation or not original_response:
            raise HTTPException(
                status_code=400,
                detail="chatgpt_evaluation과 original_response가 필요합니다",
            )

        reflection = duri_self_reflector.reflect_on_chatgpt_feedback(
            chatgpt_evaluation, original_response, user_question
        )

        print(f"🤔 DuRi 자기성찰 완료")
        print(f"   ✅ 수용한 비판: {len(reflection['accepted_criticisms'])}개")
        print(f"   ❓ 의견 차이: {len(reflection['disagreements'])}개")
        print(
            f"   💡 개선 제안: {len(reflection['improvement_proposal']['specific_improvements'])}개"
        )

        return {
            "status": "success",
            "reflection": reflection,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ DuRi 자기성찰 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reflection-history")
async def get_reflection_history():
    """성찰 히스토리 조회"""
    return {
        "total_reflections": len(duri_self_reflector.reflection_history),
        "recent_reflections": duri_self_reflector.reflection_history[-5:],
        "improvement_trends": _analyze_improvement_trends(),
    }


def _analyze_improvement_trends():
    """개선 트렌드 분석"""
    if not duri_self_reflector.reflection_history:
        return {"message": "아직 성찰 데이터가 없습니다"}

    recent_reflections = duri_self_reflector.reflection_history[-10:]

    avg_total_scores = []
    improvement_frequency = defaultdict(int)

    for reflection in recent_reflections:
        evaluation = reflection.get("chatgpt_evaluation", {})
        total_score = evaluation.get("total_score", 0)
        avg_total_scores.append(total_score)

        improvements = reflection.get("improvement_proposal", {}).get("specific_improvements", [])
        for improvement in improvements:
            improvement_frequency[improvement] += 1

    return {
        "avg_total_score": (
            sum(avg_total_scores) / len(avg_total_scores) if avg_total_scores else 0
        ),
        "most_common_improvements": sorted(
            improvement_frequency.items(), key=lambda x: x[1], reverse=True
        )[:5],
        "reflection_count": len(recent_reflections),
    }


@app.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "service": "duri-learning-server",
        "timestamp": datetime.now().isoformat(),
        "learning_data_count": len(os.listdir(LEARNING_DATA_DIR)),
        "integration_status": integration_monitor.check_integration_needed(),
    }


@app.get("/integration-status")
async def get_integration_status():
    """통합 상태 확인"""
    return integration_monitor.check_integration_needed()


@app.get("/self-reflection")
async def get_self_reflection():
    """자기 성찰 결과 확인"""
    trends = self_reflection_engine.analyze_trends()
    suggestions = self_reflection_engine.get_improvement_suggestions()

    return {
        "trends": trends,
        "improvement_suggestions": suggestions,
        "total_reflections": len(self_reflection_engine.reflection_history),
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def get_learning_dashboard():
    """학습 대시보드"""
    integration_status = integration_monitor.check_integration_needed()

    # 차트 생성
    trend_chart = learning_visualizer.generate_learning_trend_chart()
    concept_chart = learning_visualizer.generate_concept_analysis_chart()

    # 자기 성찰 데이터
    reflection_trends = self_reflection_engine.analyze_trends()
    improvement_suggestions = self_reflection_engine.get_improvement_suggestions()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DuRi Learning Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
            .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
            .charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
            .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .alert {{ background: #ff6b6b; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; }}
            .success {{ background: #51cf66; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; }}
            .reflection-section {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 DuRi Learning Dashboard</h1>
                <p>Real-time learning analysis and self-reflection monitoring</p>
            </div>

            {f'<div class="alert"><h3>🚨 Integration Point Reached!</h3><ul>{"".join([f"<li>{alert}</li>" for alert in integration_status["alerts"]])}</ul></div>' if integration_status["integration_needed"] else '<div class="success"><h3>✅ System Stable</h3><p>Currently learning in progress, no integration needed.</p></div>'}

            <div class="metrics">
                <div class="metric-card">
                    <h3>📊 Learning Patterns</h3>
                    <div class="metric-value">{integration_status["metrics"]["learning_patterns"]}</div>
                    <p>Threshold: {integration_status["thresholds"]["learning_patterns"]}</p>
                </div>
                <div class="metric-card">
                    <h3>⏱️ Response Time</h3>
                    <div class="metric-value">{integration_status["metrics"]["avg_response_time"]:.3f}s</div>
                    <p>Threshold: {integration_status["thresholds"]["response_time"]}s</p>
                </div>
                <div class="metric-card">
                    <h3>🔧 Code Complexity</h3>
                    <div class="metric-value">{integration_status["metrics"]["code_complexity"]}</div>
                    <p>Threshold: {integration_status["thresholds"]["code_complexity"]}</p>
                </div>
                <div class="metric-card">
                    <h3>👤 Requirements</h3>
                    <div class="metric-value">{integration_status["metrics"]["user_requirements"]}</div>
                    <p>Threshold: {integration_status["thresholds"]["user_requirements"]}</p>
                </div>
            </div>

            <div class="reflection-section">
                <h2>🤔 Self-Reflection Analysis</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h3>📈 Reflection Trends</h3>
                        <p><strong>Average Response Quality:</strong> {reflection_trends.get('avg_response_quality', 0):.3f}</p>
                        <p><strong>Average Learning Value:</strong> {reflection_trends.get('avg_learning_value', 0):.3f}</p>
                        <p><strong>Total Reflections:</strong> {reflection_trends.get('total_reflections', 0)}</p>
                    </div>
                    <div>
                        <h3>💡 Improvement Suggestions</h3>
                        <ul>
                            {''.join([f'<li>{suggestion}</li>' for suggestion in improvement_suggestions[:5]])}
                        </ul>
                    </div>
                </div>
            </div>

            <div class="charts">
                <div class="chart-container">
                    <h3>📈 Learning Trends</h3>
                    <img src="data:image/png;base64,{trend_chart}" style="width: 100%; height: auto;" />
                </div>
                <div class="chart-container">
                    <h3>🎯 Concept Analysis</h3>
                    <img src="data:image/png;base64,{concept_chart}" style="width: 100%; height: auto;" />
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.post("/automated-learning/process")
async def process_automated_learning(conversation_data: Dict[str, Any]):
    """
    자동화 학습 데이터 수신 및 실제 분석 처리 + 자기 성찰
    """
    start_time = datetime.now()

    try:
        print(f"📥 자동화 학습 입력: {conversation_data}")

        # 실제 학습 분석 수행
        analysis_result = learning_analyzer.analyze_conversation(conversation_data)

        # 응답 시간 계산
        response_time = (datetime.now() - start_time).total_seconds()
        integration_monitor.update_metrics(response_time)

        # 통합 필요성 체크
        integration_status = integration_monitor.check_integration_needed()

        # 자기 성찰 수행
        conversation = conversation_data.get("conversation", "")
        response_quality = min(response_time * 10, 1.0)  # 응답 시간 기반 품질 추정
        learning_value = analysis_result["learning_value"]

        reflection = self_reflection_engine.reflect_on_response(
            conversation, response_quality, learning_value
        )

        # 학습 결과 생성
        learning_result = {
            "status": "success",
            "message": "자동화 학습 분석 완료",
            "data": {
                "package_id": f"auto_learn_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "summary": f"대화 분석 완료 - {len(analysis_result['key_concepts'])}개 핵심 개념 발견",
                "learning_value": analysis_result["learning_value"],
                "analysis_details": analysis_result,
                "recommendations": _generate_recommendations(analysis_result),
                "response_time": response_time,
                "integration_status": integration_status,
                "self_reflection": reflection,
            },
            "timestamp": datetime.now().isoformat(),
        }

        print(f"📊 학습 분석 결과: {learning_result['data']['summary']}")
        print(f"🤔 자기 성찰: {len(reflection['improvement_areas'])}개 개선 영역 발견")

        # 통합 알림 출력
        if integration_status["integration_needed"]:
            print("🚨 통합 시점 도달! 실제 서버들과 통합이 필요합니다.")
            for alert in integration_status["alerts"]:
                print(f"   {alert}")

        return learning_result

    except Exception as e:
        print(f"❌ 자동화 학습 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/adaptive-learning/process")
async def process_adaptive_learning(adaptive_data: Dict[str, Any]):
    """
    적응적 학습 데이터 수신 및 처리
    """
    start_time = datetime.now()

    try:
        print(f"📥 적응적 학습 입력: {adaptive_data}")

        # 기존 분석 결과 활용
        conversation_data = adaptive_data.get("conversation_data", {})
        if conversation_data:
            analysis_result = learning_analyzer.analyze_conversation(conversation_data)
        else:
            analysis_result = {"learning_value": 0.5, "learning_complexity": 0.5}

        # 응답 시간 계산
        response_time = (datetime.now() - start_time).total_seconds()
        integration_monitor.update_metrics(response_time)

        # 통합 필요성 체크
        integration_status = integration_monitor.check_integration_needed()

        # 적응적 학습 결과 생성
        adaptive_result = {
            "status": "success",
            "message": "적응적 학습 처리 완료",
            "data": {
                "selected_format": _select_optimal_format(analysis_result),
                "learning_result": "성공적으로 학습됨",
                "efficiency_metrics": _calculate_efficiency_metrics(analysis_result),
                "exploration_rate": _calculate_exploration_rate(analysis_result),
                "optimal_format": _select_optimal_format(analysis_result),
                "reason": _generate_learning_reason(analysis_result),
                "response_time": response_time,
                "integration_status": integration_status,
            },
            "timestamp": datetime.now().isoformat(),
        }

        print(f"🔄 적응적 학습 결과: {adaptive_result['data']['learning_result']}")

        # 통합 알림 출력
        if integration_status["integration_needed"]:
            print("🚨 통합 시점 도달! 실제 서버들과 통합이 필요합니다.")
            for alert in integration_status["alerts"]:
                print(f"   {alert}")

        return adaptive_result

    except Exception as e:
        print(f"❌ 적응적 학습 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/duri-chatgpt-discuss")
async def duri_chatgpt_discussion_endpoint(discussion_request: Dict[str, Any]):
    """
    DuRi와 ChatGPT 간의 대화 기반 협의 시작
    """
    try:
        print(f"📥 DuRi-ChatGPT 논의 요청: {discussion_request}")

        # 필수 필드 확인
        required_fields = ["duri_improvement_proposal", "chatgpt_evaluation"]
        for field in required_fields:
            if field not in discussion_request:
                raise HTTPException(status_code=400, detail=f"필수 필드 누락: {field}")

        # 논의 시작
        discussion_result = duri_chatgpt_discussion.initiate_discussion(
            discussion_request["duri_improvement_proposal"],
            discussion_request["chatgpt_evaluation"],
        )

        print(f"✅ DuRi-ChatGPT 논의 완료: 합의 수준 {discussion_result['agreement_level']:.2f}")

        return {
            "status": "success",
            "discussion": discussion_result,
            "message": f"논의 완료 (합의 수준: {discussion_result['agreement_level']:.2f})",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ DuRi-ChatGPT 논의 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/discussion-history")
async def get_discussion_history():
    """
    DuRi-ChatGPT 논의 기록 조회
    """
    try:
        return {
            "status": "success",
            "discussions": duri_chatgpt_discussion.discussion_history,
            "total_discussions": len(duri_chatgpt_discussion.discussion_history),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 논의 기록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """학습 결과 기반 추천사항 생성"""
    recommendations = []

    if analysis["learning_value"] < 0.3:
        recommendations.append("더 구체적인 질문을 해보세요")
    elif analysis["learning_value"] < 0.6:
        recommendations.append("실습 예제를 함께 다뤄보세요")
    else:
        recommendations.append("이제 실제 프로젝트에 적용해보세요")

    if analysis["learning_complexity"] > 0.7:
        recommendations.append("복잡한 개념을 단계별로 나누어 학습하세요")

    if len(analysis["key_concepts"]) < 3:
        recommendations.append("관련 개념들을 더 탐색해보세요")

    return recommendations


def _select_optimal_format(analysis: Dict[str, Any]) -> str:
    """최적의 학습 형식 선택"""
    complexity = analysis.get("learning_complexity", 0.5)

    if complexity < 0.3:
        return "simple"
    elif complexity < 0.7:
        return "detailed"
    else:
        return "comprehensive"


def _calculate_efficiency_metrics(analysis: Dict[str, Any]) -> Dict[str, float]:
    """효율성 지표 계산"""
    learning_value = analysis.get("learning_value", 0.5)
    complexity = analysis.get("learning_complexity", 0.5)
    engagement = analysis.get("user_engagement", 0.5)

    return {
        "response_accuracy": min(learning_value * 1.2, 1.0),
        "application_power": min(complexity * 1.1, 1.0),
        "reproducibility": min(engagement * 1.3, 1.0),
        "learning_speed": min((learning_value + complexity) / 2, 1.0),
        "overall_score": round((learning_value + complexity + engagement) / 3, 2),
    }


def _calculate_exploration_rate(analysis: Dict[str, Any]) -> float:
    """탐색률 계산"""
    concept_count = len(analysis.get("key_concepts", []))
    return min(concept_count / 10, 1.0)


def _generate_learning_reason(analysis: Dict[str, Any]) -> str:
    """학습 이유 생성"""
    learning_value = analysis.get("learning_value", 0.5)

    if learning_value > 0.8:
        return "고급 학습 내용으로 심화 학습에 적합"
    elif learning_value > 0.6:
        return "중급 학습 내용으로 실무 적용에 적합"
    elif learning_value > 0.4:
        return "기초 학습 내용으로 개념 이해에 적합"
    else:
        return "입문 학습 내용으로 기초 다지기에 적합"


@app.post("/apply-improvement")
async def apply_improvement_endpoint(improvement_request: Dict[str, Any]):
    """
    ChatGPT 제안 기반 안전한 코드 개선 적용
    """
    try:
        print(f"📥 코드 개선 적용 요청: {improvement_request}")

        # 필수 필드 확인
        required_fields = ["discussion_result", "user_approval"]
        for field in required_fields:
            if field not in improvement_request:
                raise HTTPException(status_code=400, detail=f"필수 필드 누락: {field}")

        # 코드 개선안 생성
        improvement = safe_code_improvement.create_code_improvement(
            improvement_request["discussion_result"],
            improvement_request.get("target_file"),
        )

        # 개선안 적용
        result = safe_code_improvement.apply_improvement(
            improvement, improvement_request["user_approval"]
        )

        print(f"✅ 코드 개선 적용 결과: {result['status']} - {result['message']}")

        return {
            "status": "success",
            "improvement": improvement,
            "application_result": result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ 코드 개선 적용 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create-improvement-proposal")
async def create_improvement_proposal_endpoint(proposal_request: Dict[str, Any]):
    """
    논의 결과를 바탕으로 코드 개선안 생성 (적용 전)
    """
    try:
        print(f"📥 코드 개선안 생성 요청: {proposal_request}")

        # 필수 필드 확인
        if "discussion_result" not in proposal_request:
            raise HTTPException(status_code=400, detail="discussion_result 필드가 필요합니다")

        # 코드 개선안 생성
        improvement = safe_code_improvement.create_code_improvement(
            proposal_request["discussion_result"], proposal_request.get("target_file")
        )

        print(f"✅ 코드 개선안 생성 완료: {len(improvement['changes'])}개 변경사항")

        return {
            "status": "success",
            "improvement_proposal": improvement,
            "message": f"{len(improvement['changes'])}개 변경사항이 제안되었습니다",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ 코드 개선안 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/improvement-status")
async def get_improvement_status():
    """
    코드 개선 시스템 상태 조회
    """
    try:
        return {
            "status": "success",
            "system_info": {
                "backup_directory": safe_code_improvement.backup_dir,
                "approval_threshold": safe_code_improvement.approval_threshold,
                "pending_proposals": len(safe_code_improvement.pending_proposals),
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 개선 상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8086)


# 실제 사용 예제
@app.post("/example-endpoint")
async def example_endpoint(request: Dict[str, Any]):
    """
    실제 사용 예제를 포함한 엔드포인트
    """
    try:
        # 1. 입력 검증
        if not request.get("data"):
            raise HTTPException(status_code=400, detail="데이터가 필요합니다")

        # 2. 비즈니스 로직 처리
        result = process_business_logic(request["data"])

        # 3. 응답 생성
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.exception("예제 엔드포인트 오류")
        raise HTTPException(status_code=500, detail=str(e))
