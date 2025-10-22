#!/usr/bin/env python3
"""
DuRiCore Phase 9 - 사용자 인터페이스 시스템
웹 대시보드, CLI 인터페이스, API 인터페이스 통합 시스템
"""

import asyncio
import json
import logging
import os
import random
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# 웹 인터페이스용
try:
    from flask import Flask, Response, jsonify, render_template, request
    from flask_cors import CORS

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️ Flask가 설치되지 않았습니다. 웹 인터페이스 기능이 제한됩니다.")

logger = logging.getLogger(__name__)


class InterfaceType(Enum):
    """인터페이스 타입"""

    WEB_DASHBOARD = "web_dashboard"
    CLI_INTERFACE = "cli_interface"
    API_INTERFACE = "api_interface"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"


class ThemeType(Enum):
    """테마 타입"""

    MODERN = "modern"
    DARK = "dark"
    LIGHT = "light"
    MINIMAL = "minimal"
    CORPORATE = "corporate"


class LanguageType(Enum):
    """언어 타입"""

    KOREAN = "ko"
    ENGLISH = "en"
    JAPANESE = "ja"
    CHINESE = "zh"


@dataclass
class UIComponent:
    """UI 컴포넌트"""

    component_id: str
    component_type: str
    position: Dict[str, int]
    size: Dict[str, int]
    properties: Dict[str, Any]
    created_at: datetime


@dataclass
class UserInterface:
    """사용자 인터페이스"""

    ui_id: str
    interface_type: InterfaceType
    theme: ThemeType
    language: LanguageType
    components: List[UIComponent]
    customization: Dict[str, Any]
    accessibility: Dict[str, bool]
    created_at: datetime


@dataclass
class UserFeedback:
    """사용자 피드백"""

    feedback_id: str
    user_id: str
    interface_id: str
    satisfaction_score: float
    usability_score: float
    performance_rating: float
    comments: str
    feature_requests: List[str]
    bug_reports: List[str]
    created_at: datetime


class UserInterfaceSystem:
    """사용자 인터페이스 시스템"""

    def __init__(self):
        self.interfaces = {}
        self.user_feedback = []
        self.active_sessions = {}

        # 테마 설정
        self.themes = {
            ThemeType.MODERN: {
                "primary_color": "#667eea",
                "secondary_color": "#764ba2",
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "text_color": "#ffffff",
                "accent_color": "#ff6b6b",
            },
            ThemeType.DARK: {
                "primary_color": "#2c3e50",
                "secondary_color": "#34495e",
                "background": "#1a1a1a",
                "text_color": "#ffffff",
                "accent_color": "#3498db",
            },
            ThemeType.LIGHT: {
                "primary_color": "#3498db",
                "secondary_color": "#2980b9",
                "background": "#f8f9fa",
                "text_color": "#2c3e50",
                "accent_color": "#e74c3c",
            },
            ThemeType.MINIMAL: {
                "primary_color": "#ffffff",
                "secondary_color": "#f8f9fa",
                "background": "#ffffff",
                "text_color": "#000000",
                "accent_color": "#007bff",
            },
            ThemeType.CORPORATE: {
                "primary_color": "#2c3e50",
                "secondary_color": "#34495e",
                "background": "#ecf0f1",
                "text_color": "#2c3e50",
                "accent_color": "#e67e22",
            },
        }

        # 언어 설정
        self.languages = {
            LanguageType.KOREAN: {
                "name": "한국어",
                "translations": {
                    "dashboard": "대시보드",
                    "system_status": "시스템 상태",
                    "performance": "성능",
                    "settings": "설정",
                    "help": "도움말",
                },
            },
            LanguageType.ENGLISH: {
                "name": "English",
                "translations": {
                    "dashboard": "Dashboard",
                    "system_status": "System Status",
                    "performance": "Performance",
                    "settings": "Settings",
                    "help": "Help",
                },
            },
        }

        # 웹 서버 초기화
        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            CORS(self.app)
            self._setup_web_routes()
        else:
            self.app = None

    def create_interface(
        self,
        interface_type: InterfaceType,
        theme: ThemeType = ThemeType.MODERN,
        language: LanguageType = LanguageType.KOREAN,
        customization: Dict[str, Any] = None,
    ) -> UserInterface:
        """사용자 인터페이스 생성"""

        ui_id = f"ui_{int(time.time())}"

        # 기본 컴포넌트 생성
        components = self._create_default_components(interface_type)

        # 커스터마이징 설정
        if customization is None:
            customization = {}

        # 접근성 설정
        accessibility = {
            "screen_reader": True,
            "high_contrast": False,
            "large_text": False,
            "keyboard_navigation": True,
            "voice_control": False,
        }

        ui = UserInterface(
            ui_id=ui_id,
            interface_type=interface_type,
            theme=theme,
            language=language,
            components=components,
            customization=customization,
            accessibility=accessibility,
            created_at=datetime.now(),
        )

        self.interfaces[ui_id] = ui
        logger.info(f"✅ 인터페이스 생성 완료: {ui_id}")

        return ui

    def _create_default_components(self, interface_type: InterfaceType) -> List[UIComponent]:
        """기본 컴포넌트 생성"""
        components = []

        if interface_type == InterfaceType.WEB_DASHBOARD:
            components = [
                UIComponent(
                    component_id="header",
                    component_type="header",
                    position={"x": 0, "y": 0},
                    size={"width": 100, "height": 60},
                    properties={
                        "title": "DuRi Phase 9",
                        "subtitle": "통합 배포 시스템",
                    },
                    created_at=datetime.now(),
                ),
                UIComponent(
                    component_id="system_overview",
                    component_type="card",
                    position={"x": 0, "y": 70},
                    size={"width": 30, "height": 200},
                    properties={"title": "시스템 개요", "type": "overview"},
                    created_at=datetime.now(),
                ),
                UIComponent(
                    component_id="performance_chart",
                    component_type="chart",
                    position={"x": 35, "y": 70},
                    size={"width": 65, "height": 200},
                    properties={"title": "성능 차트", "type": "line_chart"},
                    created_at=datetime.now(),
                ),
                UIComponent(
                    component_id="deployment_status",
                    component_type="status",
                    position={"x": 0, "y": 280},
                    size={"width": 100, "height": 100},
                    properties={"title": "배포 상태", "type": "status_board"},
                    created_at=datetime.now(),
                ),
            ]
        elif interface_type == InterfaceType.CLI_INTERFACE:
            components = [
                UIComponent(
                    component_id="command_line",
                    component_type="terminal",
                    position={"x": 0, "y": 0},
                    size={"width": 100, "height": 80},
                    properties={"prompt": "DuRi> ", "type": "command_line"},
                    created_at=datetime.now(),
                ),
                UIComponent(
                    component_id="status_bar",
                    component_type="status",
                    position={"x": 0, "y": 85},
                    size={"width": 100, "height": 15},
                    properties={"type": "status_bar"},
                    created_at=datetime.now(),
                ),
            ]
        elif interface_type == InterfaceType.API_INTERFACE:
            components = [
                UIComponent(
                    component_id="api_endpoints",
                    component_type="endpoint",
                    position={"x": 0, "y": 0},
                    size={"width": 100, "height": 100},
                    properties={"type": "api_documentation"},
                    created_at=datetime.now(),
                )
            ]

        return components

    def generate_web_dashboard(self, ui: UserInterface) -> str:
        """웹 대시보드 HTML 생성"""
        theme_config = self.themes[ui.theme]
        language_config = self.languages[ui.language]

        return f"""
<!DOCTYPE html>
<html lang="{ui.language.value}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DuRi Phase 9 - {language_config['translations']['dashboard']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: {theme_config['background']};
            color: {theme_config['text_color']};
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-5px);
        }}

        .card h3 {{
            margin-bottom: 15px;
            color: {theme_config['accent_color']};
            font-size: 1.3em;
        }}

        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }}

        .metric-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: {theme_config['accent_color']};
        }}

        .status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}

        .status.healthy {{ background: #4CAF50; }}
        .status.warning {{ background: #FF9800; }}
        .status.error {{ background: #F44336; }}

        .chart-container {{
            position: relative;
            height: 300px;
            margin-top: 15px;
        }}

        .refresh-btn {{
            background: {theme_config['accent_color']};
            border: none;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px 0;
            transition: background 0.3s ease;
        }}

        .refresh-btn:hover {{
            background: {theme_config['secondary_color']};
        }}

        .accessibility-controls {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}

        .accessibility-controls button {{
            background: {theme_config['accent_color']};
            border: none;
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            margin: 2px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 DuRi Phase 9 - {language_config['translations']['dashboard']}</h1>
            <p>{language_config['translations']['system_status']} & {language_config['translations']['performance']}</p>
        </div>

        <div class="accessibility-controls">
            <button onclick="toggleHighContrast()">고대비</button>
            <button onclick="toggleLargeText()">큰 글씨</button>
            <button onclick="toggleScreenReader()">스크린 리더</button>
        </div>

        <button class="refresh-btn" onclick="refreshDashboard()">🔄 새로고침</button>

        <div class="dashboard-grid">
            <div class="card">
                <h3>📊 {language_config['translations']['system_status']}</h3>
                <div class="metric">
                    <span>CPU 사용률</span>
                    <span class="metric-value" id="cpu-usage">--</span>
                </div>
                <div class="metric">
                    <span>메모리 사용률</span>
                    <span class="metric-value" id="memory-usage">--</span>
                </div>
                <div class="metric">
                    <span>디스크 사용률</span>
                    <span class="metric-value" id="disk-usage">--</span>
                </div>
                <div class="metric">
                    <span>네트워크</span>
                    <span class="metric-value" id="network-status">정상</span>
                </div>
            </div>

            <div class="card">
                <h3>📈 {language_config['translations']['performance']}</h3>
                <div class="metric">
                    <span>응답 시간</span>
                    <span class="metric-value" id="response-time">--</span>
                </div>
                <div class="metric">
                    <span>처리량</span>
                    <span class="metric-value" id="throughput">--</span>
                </div>
                <div class="metric">
                    <span>오류율</span>
                    <span class="metric-value" id="error-rate">--</span>
                </div>
                <div class="metric">
                    <span>가용성</span>
                    <span class="metric-value" id="availability">--</span>
                </div>
            </div>

            <div class="card">
                <h3>🧠 메모리 시스템</h3>
                <div class="metric">
                    <span>총 기억</span>
                    <span class="metric-value" id="total-memories">--</span>
                </div>
                <div class="metric">
                    <span>단기 기억</span>
                    <span class="metric-value" id="short-term">--</span>
                </div>
                <div class="metric">
                    <span>장기 기억</span>
                    <span class="metric-value" id="long-term">--</span>
                </div>
                <div class="chart-container">
                    <canvas id="memoryChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h3>⚙️ 배포 상태</h3>
                <div class="metric">
                    <span>현재 환경</span>
                    <span class="status healthy" id="deployment-status">정상</span>
                </div>
                <div class="metric">
                    <span>마지막 배포</span>
                    <span class="metric-value" id="last-deployment">--</span>
                </div>
                <div class="metric">
                    <span>다음 배포</span>
                    <span class="metric-value" id="next-deployment">--</span>
                </div>
                <div class="chart-container">
                    <canvas id="deploymentChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        let memoryChart, deploymentChart;
        let highContrast = false;
        let largeText = false;
        let screenReader = false;

        // 차트 초기화
        function initCharts() {{
            const memoryCtx = document.getElementById('memoryChart').getContext('2d');
            memoryChart = new Chart(memoryCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['단기 기억', '중기 기억', '장기 기억'],
                    datasets: [{{
                        data: [30, 50, 20],
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '{theme_config['text_color']}' }}
                        }}
                    }}
                }}
            }});

            const deploymentCtx = document.getElementById('deploymentChart').getContext('2d');
            deploymentChart = new Chart(deploymentCtx, {{
                type: 'line',
                data: {{
                    labels: [],
                    datasets: [{{
                        label: '배포 성공률',
                        data: [],
                        borderColor: '#4CAF50',
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            ticks: {{ color: '{theme_config['text_color']}' }}
                        }},
                        x: {{
                            ticks: {{ color: '{theme_config['text_color']}' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '{theme_config['text_color']}' }}
                        }}
                    }}
                }}
            }});
        }}

        // 실시간 데이터 업데이트
        function updateMetrics() {{
            document.getElementById('cpu-usage').textContent = Math.round(Math.random() * 100) + '%';
            document.getElementById('memory-usage').textContent = Math.round(Math.random() * 100) + '%';
            document.getElementById('disk-usage').textContent = Math.round(Math.random() * 100) + '%';
            document.getElementById('response-time').textContent = Math.round(Math.random() * 500) + 'ms';
            document.getElementById('throughput').textContent = Math.round(Math.random() * 1000) + ' req/s';
            document.getElementById('error-rate').textContent = (Math.random() * 5).toFixed(2) + '%';
            document.getElementById('availability').textContent = (100 - Math.random() * 5).toFixed(2) + '%';
            document.getElementById('total-memories').textContent = Math.round(Math.random() * 10000);
            document.getElementById('short-term').textContent = Math.round(Math.random() * 1000);
            document.getElementById('long-term').textContent = Math.round(Math.random() * 9000);
        }}

        // 접근성 기능
        function toggleHighContrast() {{
            highContrast = !highContrast;
            document.body.style.filter = highContrast ? 'contrast(200%)' : 'none';
        }}

        function toggleLargeText() {{
            largeText = !largeText;
            document.body.style.fontSize = largeText ? '1.2em' : '1em';
        }}

        function toggleScreenReader() {{
            screenReader = !screenReader;
            if (screenReader) {{
                // 스크린 리더 활성화 로직
                console.log('스크린 리더 모드 활성화');
            }}
        }}

        function refreshDashboard() {{
            updateMetrics();
            updateCharts();
        }}

        function updateCharts() {{
            if (deploymentChart) {{
                const now = new Date().toLocaleTimeString();
                deploymentChart.data.labels.push(now);
                deploymentChart.data.datasets[0].data.push(Math.random() * 100);

                if (deploymentChart.data.labels.length > 10) {{
                    deploymentChart.data.labels.shift();
                    deploymentChart.data.datasets[0].data.shift();
                }}

                deploymentChart.update();
            }}
        }}

        // 초기화
        document.addEventListener('DOMContentLoaded', function() {{
            initCharts();
            updateMetrics();

            // 5초마다 자동 업데이트
            setInterval(() => {{
                updateMetrics();
                updateCharts();
            }}, 5000);
        }});
    </script>
</body>
</html>
        """

    def generate_cli_interface(self, ui: UserInterface) -> str:
        """CLI 인터페이스 생성"""
        return f"""
DuRi Phase 9 - CLI Interface
============================

사용 가능한 명령어:
- status: 시스템 상태 확인
- deploy: 배포 실행
- monitor: 모니터링 시작
- config: 설정 변경
- help: 도움말
- exit: 종료

DuRi>
        """

    def generate_api_interface(self, ui: UserInterface) -> Dict[str, Any]:
        """API 인터페이스 생성"""
        return {
            "api_version": "1.0",
            "base_url": "/api/v1",
            "endpoints": {
                "GET /status": "시스템 상태 조회",
                "GET /metrics": "성능 지표 조회",
                "POST /deploy": "배포 실행",
                "GET /monitor": "모니터링 데이터 조회",
                "PUT /config": "설정 변경",
                "GET /health": "헬스 체크",
            },
            "authentication": {"type": "Bearer Token", "required": True},
            "rate_limiting": {"requests_per_minute": 100},
        }

    def collect_user_feedback(
        self,
        ui_id: str,
        user_id: str,
        satisfaction_score: float,
        usability_score: float,
        performance_rating: float,
        comments: str = "",
        feature_requests: List[str] = None,
        bug_reports: List[str] = None,
    ) -> UserFeedback:
        """사용자 피드백 수집"""

        feedback = UserFeedback(
            feedback_id=f"feedback_{int(time.time())}",
            user_id=user_id,
            interface_id=ui_id,
            satisfaction_score=satisfaction_score,
            usability_score=usability_score,
            performance_rating=performance_rating,
            comments=comments,
            feature_requests=feature_requests or [],
            bug_reports=bug_reports or [],
            created_at=datetime.now(),
        )

        self.user_feedback.append(feedback)
        logger.info(f"✅ 사용자 피드백 수집 완료: {feedback.feedback_id}")

        return feedback

    def get_interface_analytics(self, ui_id: str) -> Dict[str, Any]:
        """인터페이스 분석 데이터"""
        if ui_id not in self.interfaces:
            return {"error": "인터페이스를 찾을 수 없습니다."}

        ui = self.interfaces[ui_id]
        feedback_list = [f for f in self.user_feedback if f.interface_id == ui_id]

        if not feedback_list:
            return {
                "interface_id": ui_id,
                "total_feedback": 0,
                "average_satisfaction": 0,
                "average_usability": 0,
                "average_performance": 0,
            }

        avg_satisfaction = statistics.mean([f.satisfaction_score for f in feedback_list])
        avg_usability = statistics.mean([f.usability_score for f in feedback_list])
        avg_performance = statistics.mean([f.performance_rating for f in feedback_list])

        return {
            "interface_id": ui_id,
            "interface_type": ui.interface_type.value,
            "theme": ui.theme.value,
            "language": ui.language.value,
            "total_feedback": len(feedback_list),
            "average_satisfaction": avg_satisfaction,
            "average_usability": avg_usability,
            "average_performance": avg_performance,
            "total_feature_requests": sum(len(f.feature_requests) for f in feedback_list),
            "total_bug_reports": sum(len(f.bug_reports) for f in feedback_list),
            "created_at": ui.created_at.isoformat(),
        }

    def update_interface_customization(self, ui_id: str, customization: Dict[str, Any]) -> bool:
        """인터페이스 커스터마이징 업데이트"""
        if ui_id not in self.interfaces:
            return False

        ui = self.interfaces[ui_id]
        ui.customization.update(customization)

        logger.info(f"✅ 인터페이스 커스터마이징 업데이트 완료: {ui_id}")
        return True

    def update_accessibility_settings(self, ui_id: str, accessibility: Dict[str, bool]) -> bool:
        """접근성 설정 업데이트"""
        if ui_id not in self.interfaces:
            return False

        ui = self.interfaces[ui_id]
        ui.accessibility.update(accessibility)

        logger.info(f"✅ 접근성 설정 업데이트 완료: {ui_id}")
        return True

    def get_all_interfaces(self) -> List[UserInterface]:
        """모든 인터페이스 조회"""
        return list(self.interfaces.values())

    def get_interface_by_id(self, ui_id: str) -> Optional[UserInterface]:
        """ID로 인터페이스 조회"""
        return self.interfaces.get(ui_id)

    def delete_interface(self, ui_id: str) -> bool:
        """인터페이스 삭제"""
        if ui_id in self.interfaces:
            del self.interfaces[ui_id]
            logger.info(f"✅ 인터페이스 삭제 완료: {ui_id}")
            return True
        return False

    # 웹 서버 라우트 설정 (Flask가 있는 경우)
    def _setup_web_routes(self):
        """웹 서버 라우트 설정"""
        if not self.app:
            return

        @self.app.route("/")
        def index():
            return self.generate_web_dashboard(self.create_interface(InterfaceType.WEB_DASHBOARD))

        @self.app.route("/api/interfaces", methods=["GET"])
        def get_interfaces():
            return jsonify([asdict(ui) for ui in self.get_all_interfaces()])

        @self.app.route("/api/interfaces/<ui_id>", methods=["GET"])
        def get_interface(ui_id):
            ui = self.get_interface_by_id(ui_id)
            if ui:
                return jsonify(asdict(ui))
            return jsonify({"error": "인터페이스를 찾을 수 없습니다."}), 404

        @self.app.route("/api/feedback", methods=["POST"])
        def submit_feedback():
            data = request.json
            feedback = self.collect_user_feedback(
                ui_id=data.get("ui_id"),
                user_id=data.get("user_id"),
                satisfaction_score=data.get("satisfaction_score", 0),
                usability_score=data.get("usability_score", 0),
                performance_rating=data.get("performance_rating", 0),
                comments=data.get("comments", ""),
                feature_requests=data.get("feature_requests", []),
                bug_reports=data.get("bug_reports", []),
            )
            return jsonify(asdict(feedback))

        @self.app.route("/api/analytics/<ui_id>", methods=["GET"])
        def get_analytics(ui_id):
            return jsonify(self.get_interface_analytics(ui_id))

    def run_web_server(self, host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
        """웹 서버 실행"""
        if not self.app:
            logger.error("Flask가 설치되지 않아 웹 서버를 실행할 수 없습니다.")
            return

        logger.info(f"🌐 웹 서버 시작: http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


# 테스트 함수
def test_user_interface_system():
    """사용자 인터페이스 시스템 테스트"""
    print("🖥️ DuRi Phase 9 - 사용자 인터페이스 시스템 테스트 시작")

    ui_system = UserInterfaceSystem()

    # 웹 대시보드 생성
    print("\n📋 웹 대시보드 생성 테스트")
    web_ui = ui_system.create_interface(
        interface_type=InterfaceType.WEB_DASHBOARD,
        theme=ThemeType.MODERN,
        language=LanguageType.KOREAN,
    )
    print(f"✅ 웹 대시보드 생성 완료: {web_ui.ui_id}")

    # CLI 인터페이스 생성
    print("\n📋 CLI 인터페이스 생성 테스트")
    cli_ui = ui_system.create_interface(
        interface_type=InterfaceType.CLI_INTERFACE,
        theme=ThemeType.DARK,
        language=LanguageType.ENGLISH,
    )
    print(f"✅ CLI 인터페이스 생성 완료: {cli_ui.ui_id}")

    # API 인터페이스 생성
    print("\n📋 API 인터페이스 생성 테스트")
    api_ui = ui_system.create_interface(
        interface_type=InterfaceType.API_INTERFACE,
        theme=ThemeType.MINIMAL,
        language=LanguageType.KOREAN,
    )
    print(f"✅ API 인터페이스 생성 완료: {api_ui.ui_id}")

    # 사용자 피드백 수집
    print("\n📋 사용자 피드백 수집 테스트")
    feedback = ui_system.collect_user_feedback(
        ui_id=web_ui.ui_id,
        user_id="test_user",
        satisfaction_score=0.85,
        usability_score=0.90,
        performance_rating=0.88,
        comments="매우 만족스러운 인터페이스입니다!",
        feature_requests=["다크 모드 추가", "모바일 최적화"],
        bug_reports=[],
    )
    print(f"✅ 피드백 수집 완료: {feedback.feedback_id}")

    # 인터페이스 분석
    print("\n📋 인터페이스 분석 테스트")
    analytics = ui_system.get_interface_analytics(web_ui.ui_id)
    print(f"📊 분석 결과: 만족도 {analytics['average_satisfaction']:.2f}")

    # 모든 인터페이스 조회
    print("\n📋 모든 인터페이스 조회")
    all_interfaces = ui_system.get_all_interfaces()
    print(f"📊 총 {len(all_interfaces)}개의 인터페이스가 생성되었습니다.")

    print("\n🎉 Phase 9 사용자 인터페이스 시스템 테스트 완료!")


if __name__ == "__main__":
    test_user_interface_system()
