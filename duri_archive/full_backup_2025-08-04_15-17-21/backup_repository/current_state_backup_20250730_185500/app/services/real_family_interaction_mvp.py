#!/usr/bin/env python3
"""
RealFamilyInteractionMVP - Phase 17.1
실제 가족이 사용할 수 있는 MVP 시스템
"""
import json
import logging
import os
import random
import threading
import webbrowser
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, redirect, render_template, request, url_for

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FamilyMember:
    id: str
    name: str
    role: str
    is_online: bool = False
    last_active: Optional[datetime] = None


@dataclass
class DailyQuestion:
    id: str
    question_text: str
    target_member: str
    timestamp: datetime
    context: str
    question_type: str
    is_answered: bool = False


@dataclass
class FamilyResponse:
    id: str
    question_id: str
    responder_id: str
    response_text: str
    emotional_tone: str
    satisfaction_score: float
    timestamp: datetime


@dataclass
class FamilyInteraction:
    id: str
    interaction_type: str
    participants: List[str]
    summary: str
    duration_minutes: int
    outcome: str
    timestamp: datetime
    feedback_score: float


class RealFamilyInteractionMVP:
    def __init__(self):
        self.family_members: Dict[str, FamilyMember] = {
            "김신": FamilyMember("김신", "김신", "아빠"),
            "김제니": FamilyMember("김제니", "김제니", "엄마"),
            "김건": FamilyMember("김건", "김건", "첫째 아들"),
            "김율": FamilyMember("김율", "김율", "둘째 딸"),
            "김홍(셋째딸)": FamilyMember("김홍(셋째딸)", "김홍(셋째딸)", "셋째 딸"),
        }
        self.daily_questions: List[DailyQuestion] = []
        self.family_responses: List[FamilyResponse] = []
        self.family_interactions: List[FamilyInteraction] = []
        self.current_session: Optional[str] = None

        # Flask 앱 초기화 - 템플릿 폴더 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(current_dir, "..", "..", "templates")
        self.app = Flask(__name__, template_folder=templates_dir)
        self.setup_routes()
        logger.info("RealFamilyInteractionMVP 초기화 완료")

    def setup_routes(self):
        @self.app.route("/")
        def home():
            return render_template(
                "family_home.html",
                family_members=self.family_members,
                questions=self.daily_questions,
                responses=self.family_responses,
            )

        @self.app.route("/question/<question_id>")
        def view_question(question_id):
            question = next(
                (q for q in self.daily_questions if q.id == question_id), None
            )
            responses = [
                r for r in self.family_responses if r.question_id == question_id
            ]
            return render_template(
                "question_detail.html",
                question=question,
                responses=responses,
                family_members=self.family_members,
            )

        @self.app.route("/answer", methods=["POST"])
        def submit_answer():
            data = request.get_json()
            question_id = data.get("question_id")
            responder_id = data.get("responder_id")
            response_text = data.get("response_text")
            emotional_tone = data.get("emotional_tone", "neutral")
            satisfaction_score = float(data.get("satisfaction_score", 0.8))

            response = self.record_family_response(
                question_id=question_id,
                responder_id=responder_id,
                response_text=response_text,
                emotional_tone=emotional_tone,
                satisfaction_score=satisfaction_score,
            )

            # 질문을 답변 완료로 표시
            for q in self.daily_questions:
                if q.id == question_id:
                    q.is_answered = True
                    break

            return jsonify({"success": True, "response_id": response.id})

        @self.app.route("/generate_questions", methods=["POST"])
        def generate_questions():
            num_questions = int(request.get_json().get("num_questions", 10))
            questions = self.generate_daily_questions(num_questions)
            return jsonify({"success": True, "questions_count": len(questions)})

        @self.app.route("/api/stats")
        def get_stats():
            return jsonify(self.get_interaction_statistics())

    def generate_daily_questions(self, num_questions: int = 10) -> List[DailyQuestion]:
        """매일 가족에게 물을 질문 리스트 생성"""
        questions_data = [
            {
                "text": "오늘 가족을 위해 특별히 해주고 싶은 일이 있으신가요?",
                "target": "김신",
                "type": "reflection",
            },
            {
                "text": "오늘 가장 감사했던 순간은 언제인가요?",
                "target": "김제니",
                "type": "emotion",
            },
            {
                "text": "오늘 새롭게 배운 것이 있나요?",
                "target": "김건",
                "type": "learning",
            },
            {
                "text": "오늘 가장 기뻤던 일은 무엇인가요?",
                "target": "김율",
                "type": "emotion",
            },
            {
                "text": "오늘 도움이 필요했던 순간이 있었나요?",
                "target": "김홍(셋째딸)",
                "type": "support",
            },
            {
                "text": "오늘 가족과 함께한 시간 중 가장 특별했던 순간은?",
                "target": "전체 가족",
                "type": "bonding",
            },
            {
                "text": "오늘 DuRi에게 기대하는 역할이 있으신가요?",
                "target": "김신",
                "type": "feedback",
            },
            {
                "text": "오늘 가족을 위해 더 하고 싶었던 일이 있나요?",
                "target": "김제니",
                "type": "reflection",
            },
            {
                "text": "오늘 부모님께 감사했던 일이 있나요?",
                "target": "아이들",
                "type": "gratitude",
            },
            {
                "text": "내일 가족을 위해 특별히 준비하고 싶은 것이 있나요?",
                "target": "전체 가족",
                "type": "planning",
            },
            {
                "text": "오늘 가장 어려웠던 순간은 언제였나요?",
                "target": "김신",
                "type": "support",
            },
            {
                "text": "오늘 가족 중 누구에게 가장 감사했나요?",
                "target": "김제니",
                "type": "gratitude",
            },
            {
                "text": "오늘 가장 재미있었던 일은 무엇인가요?",
                "target": "김건",
                "type": "emotion",
            },
            {
                "text": "오늘 부모님께 도움이 되었던 일이 있나요?",
                "target": "김율",
                "type": "contribution",
            },
            {
                "text": "오늘 가장 배고팠던 순간은 언제였나요?",
                "target": "김홍(셋째딸)",
                "type": "daily",
            },
        ]

        selected_questions = random.sample(
            questions_data, min(num_questions, len(questions_data))
        )

        generated_list = []
        for q_data in selected_questions:
            q_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.daily_questions)}"
            question = DailyQuestion(
                id=q_id,
                question_text=q_data["text"],
                target_member=q_data["target"],
                timestamp=datetime.now(),
                context="daily_interaction",
                question_type=q_data["type"],
            )
            self.daily_questions.append(question)
            generated_list.append(question)

        logger.info(f"일일 질문 리스트 생성 완료: {len(generated_list)}개")
        return generated_list

    def record_family_response(
        self,
        question_id: str,
        responder_id: str,
        response_text: str,
        emotional_tone: str,
        satisfaction_score: float,
    ) -> FamilyResponse:
        """가족의 질문에 대한 응답 기록"""
        response_id = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        response = FamilyResponse(
            id=response_id,
            question_id=question_id,
            responder_id=responder_id,
            response_text=response_text,
            emotional_tone=emotional_tone,
            satisfaction_score=satisfaction_score,
            timestamp=datetime.now(),
        )
        self.family_responses.append(response)

        # 가족 구성원 활성화 상태 업데이트
        if responder_id in self.family_members:
            self.family_members[responder_id].is_online = True
            self.family_members[responder_id].last_active = datetime.now()

        logger.info(f"가족 응답 기록 완료: {response_id}")
        return response

    def log_family_interaction(
        self,
        interaction_type: str,
        participants: List[str],
        summary: str,
        duration_minutes: int,
        outcome: str,
        feedback_score: float,
    ) -> FamilyInteraction:
        """가족 상호작용 로그 기록"""
        interaction_id = f"interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        interaction = FamilyInteraction(
            id=interaction_id,
            interaction_type=interaction_type,
            participants=participants,
            summary=summary,
            duration_minutes=duration_minutes,
            outcome=outcome,
            timestamp=datetime.now(),
            feedback_score=feedback_score,
        )
        self.family_interactions.append(interaction)
        logger.info(f"가족 상호작용 기록 완료: {interaction_id}")
        return interaction

    def get_interaction_statistics(self) -> Dict[str, Any]:
        """상호작용 통계"""
        total_questions = len(self.daily_questions)
        total_responses = len(self.family_responses)
        total_interactions = len(self.family_interactions)

        response_rate = (
            (total_responses / total_questions) * 100 if total_questions > 0 else 0.0
        )
        answered_questions = len([q for q in self.daily_questions if q.is_answered])

        avg_satisfaction = sum(
            r.satisfaction_score for r in self.family_responses
        ) / max(total_responses, 1)
        avg_feedback_score = sum(
            i.feedback_score for i in self.family_interactions
        ) / max(total_interactions, 1)

        online_members = [m for m in self.family_members.values() if m.is_online]

        return {
            "total_questions_generated": total_questions,
            "answered_questions": answered_questions,
            "total_family_responses": total_responses,
            "response_rate": response_rate,
            "average_satisfaction_score": avg_satisfaction,
            "total_family_interactions_logged": total_interactions,
            "average_interaction_feedback_score": avg_feedback_score,
            "online_family_members": len(online_members),
            "system_status": "active",
        }

    def start_web_server(self, port: int = 5000):
        """웹 서버 시작"""

        def run_server():
            self.app.run(host="0.0.0.0", port=port, debug=False)

        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        # 브라우저 자동 열기
        webbrowser.open(f"http://localhost:{port}")

        logger.info(f"웹 서버가 http://localhost:{port} 에서 시작되었습니다.")
        return server_thread


def create_html_templates():
    """HTML 템플릿 생성"""
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)

    # 메인 페이지 템플릿
    home_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DuRi 가족 상호작용</title>
    <style>
        body { font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #333; margin-bottom: 10px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .questions-section { margin-bottom: 30px; }
        .question-card { background: #f8f9fa; padding: 20px; margin: 10px 0; border-radius: 10px; border-left: 5px solid #667eea; }
        .question-text { font-size: 1.1em; margin-bottom: 10px; }
        .question-meta { color: #666; font-size: 0.9em; }
        .btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #5a6fd8; }
        .response-form { margin-top: 15px; padding: 15px; background: white; border-radius: 8px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .family-members { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
        .member-card { background: #e3f2fd; padding: 10px; border-radius: 8px; text-align: center; }
        .online { background: #c8e6c9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 DuRi 가족 상호작용</h1>
            <p>가족과 함께하는 의미 있는 대화를 시작해보세요</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-questions">0</div>
                <div>생성된 질문</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="response-rate">0%</div>
                <div>응답률</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="avg-satisfaction">0</div>
                <div>평균 만족도</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="online-members">0</div>
                <div>온라인 가족</div>
            </div>
        </div>

        <div class="family-members">
            {% for member in family_members.values() %}
            <div class="member-card {% if member.is_online %}online{% endif %}">
                <div>{{ member.name }}</div>
                <div style="font-size: 0.8em;">{{ member.role }}</div>
            </div>
            {% endfor %}
        </div>

        <div style="text-align: center; margin-bottom: 30px;">
            <button class="btn" onclick="generateQuestions()">새 질문 생성</button>
        </div>

        <div class="questions-section">
            <h2>오늘의 질문들</h2>
            {% for question in questions %}
            <div class="question-card">
                <div class="question-text">{{ question.question_text }}</div>
                <div class="question-meta">
                    대상: {{ question.target_member }} |
                    유형: {{ question.question_type }} |
                    {% if question.is_answered %}
                    <span style="color: green;">✓ 답변 완료</span>
                    {% else %}
                    <span style="color: orange;">⏳ 답변 대기</span>
                    {% endif %}
                </div>
                <button class="btn" onclick="showResponseForm('{{ question.id }}')">답변하기</button>

                <div id="response-form-{{ question.id }}" class="response-form" style="display: none;">
                    <form onsubmit="submitResponse(event, '{{ question.id }}')">
                        <div class="form-group">
                            <label>답변자:</label>
                            <select name="responder_id" required>
                                {% for member in family_members.values() %}
                                <option value="{{ member.id }}">{{ member.name }} ({{ member.role }})</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>답변:</label>
                            <textarea name="response_text" rows="3" required placeholder="답변을 입력해주세요..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>감정 상태:</label>
                            <select name="emotional_tone">
                                <option value="positive">긍정적</option>
                                <option value="neutral">중립적</option>
                                <option value="negative">부정적</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>만족도 (1-10):</label>
                            <input type="number" name="satisfaction_score" min="1" max="10" value="8" required>
                        </div>
                        <button type="submit" class="btn">답변 제출</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function generateQuestions() {
            fetch('/generate_questions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({num_questions: 10})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        }

        function showResponseForm(questionId) {
            const form = document.getElementById('response-form-' + questionId);
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }

        function submitResponse(event, questionId) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);

            const data = {
                question_id: questionId,
                responder_id: formData.get('responder_id'),
                response_text: formData.get('response_text'),
                emotional_tone: formData.get('emotional_tone'),
                satisfaction_score: formData.get('satisfaction_score')
            };

            fetch('/answer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        }

        // 통계 업데이트
        function updateStats() {
            fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('total-questions').textContent = data.total_questions_generated;
                document.getElementById('response-rate').textContent = data.response_rate.toFixed(1) + '%';
                document.getElementById('avg-satisfaction').textContent = data.average_satisfaction_score.toFixed(1);
                document.getElementById('online-members').textContent = data.online_family_members;
            });
        }

        // 페이지 로드 시 통계 업데이트
        updateStats();
        // 30초마다 통계 업데이트
        setInterval(updateStats, 30000);
    </script>
</body>
</html>
    """

    with open(f"{templates_dir}/family_home.html", "w", encoding="utf-8") as f:
        f.write(home_template)

    # 질문 상세 페이지 템플릿
    question_detail_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>질문 상세 - DuRi 가족 상호작용</title>
    <style>
        body { font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .question-detail { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .response-card { background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #2196f3; }
        .btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #5a6fd8; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="btn">← 홈으로 돌아가기</a>

        {% if question %}
        <div class="question-detail">
            <h2>{{ question.question_text }}</h2>
            <p><strong>대상:</strong> {{ question.target_member }}</p>
            <p><strong>유형:</strong> {{ question.question_type }}</p>
            <p><strong>생성 시간:</strong> {{ question.timestamp.strftime('%Y-%m-%d %H:%M') }}</p>
        </div>

        <h3>답변들</h3>
        {% for response in responses %}
        <div class="response-card">
            <p><strong>{{ response.responder_id }}</strong>의 답변:</p>
            <p>{{ response.response_text }}</p>
            <p><small>감정: {{ response.emotional_tone }} | 만족도: {{ response.satisfaction_score }}/10 | 시간: {{ response.timestamp.strftime('%H:%M') }}</small></p>
        </div>
        {% endfor %}

        {% if not responses %}
        <p>아직 답변이 없습니다.</p>
        {% endif %}
        {% else %}
        <p>질문을 찾을 수 없습니다.</p>
        {% endif %}
    </div>
</body>
</html>
    """

    with open(f"{templates_dir}/question_detail.html", "w", encoding="utf-8") as f:
        f.write(question_detail_template)


def test_real_family_interaction_mvp():
    """실제 가족 상호작용 MVP 테스트"""
    print("🏠 RealFamilyInteractionMVP 테스트 시작...")

    # HTML 템플릿 생성
    create_html_templates()
    print("✅ HTML 템플릿 생성 완료")

    # MVP 시스템 초기화
    mvp = RealFamilyInteractionMVP()

    # 일일 질문 생성
    questions = mvp.generate_daily_questions(num_questions=10)
    print(f"✅ 일일 질문 생성 완료: {len(questions)}개")

    # 웹 서버 시작
    print("🌐 웹 서버를 시작합니다...")
    server_thread = mvp.start_web_server(port=5000)

    print("✅ RealFamilyInteractionMVP 테스트 완료!")
    print(
        "🌐 웹 브라우저에서 http://localhost:5000 으로 접속하여 실제 테스트를 진행하세요!"
    )
    print("📱 가족 구성원들과 함께 실제 상호작용을 테스트해보세요!")

    # 서버가 계속 실행되도록 대기
    try:
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 서버를 종료합니다...")


if __name__ == "__main__":
    test_real_family_interaction_mvp()
