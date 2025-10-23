#!/usr/bin/env python3
"""
DuRi 대시보드 생성 시스템
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List


class DashboardGenerator:
    """DuRi 학습 현황 대시보드 생성"""

    def __init__(self):
        self.dashboard_path = "/tmp/duri_dashboard.html"

    def generate_dashboard(
        self,
        performance_summary: Dict[str, Any],
        learning_statistics: Dict[str, Any],
        meta_learning_stats: Dict[str, Any],
    ) -> str:
        """실시간 대시보드 HTML 생성"""

        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DuRi 자가진화 AI 시스템 대시보드</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
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
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-5px);
        }}

        .card h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }}

        .metric-label {{
            font-weight: 600;
            color: #555;
        }}

        .metric-value {{
            font-weight: bold;
            color: #667eea;
        }}

        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .status-healthy {{
            background: #28a745;
        }}

        .status-warning {{
            background: #ffc107;
        }}

        .status-critical {{
            background: #dc3545;
        }}

        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }}

        .chart-container {{
            margin-top: 15px;
            height: 200px;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }}

        .refresh-button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
        }}

        .refresh-button:hover {{
            background: #5a6fd8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 DuRi 자가진화 AI 시스템</h1>
            <p>실시간 학습 현황 및 성능 모니터링</p>
            <button class="refresh-button" onclick="location.reload()">🔄 새로고침</button>
        </div>

        <div class="dashboard-grid">
            <!-- 시스템 상태 -->
            <div class="card">
                <h3>📊 시스템 상태</h3>
                <div class="metric">
                    <span class="metric-label">
                        <span class="status-indicator status-{performance_summary.get('system_health', {}).get('overall_status', 'healthy')}"></span>
                        전체 상태
                    </span>
                    <span class="metric-value">{performance_summary.get('system_health', {}).get('overall_status', 'healthy').upper()}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">가동 시간</span>
                    <span class="metric-value">{self._format_uptime(performance_summary.get('system_health', {}).get('uptime', 0))}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">총 요청 수</span>
                    <span class="metric-value">{performance_summary.get('system_health', {}).get('total_requests', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">오류율</span>
                    <span class="metric-value">{performance_summary.get('system_health', {}).get('error_rate', 0):.2%}</span>
                </div>
            </div>

            <!-- 학습 통계 -->
            <div class="card">
                <h3>📈 학습 통계</h3>
                <div class="metric">
                    <span class="metric-label">총 대화 수</span>
                    <span class="metric-value">{learning_statistics.get('statistics', {}).get('total_conversations', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">평균 학습 가치</span>
                    <span class="metric-value">{learning_statistics.get('statistics', {}).get('avg_learning_value', 0):.2f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">평균 응답 시간</span>
                    <span class="metric-value">{learning_statistics.get('statistics', {}).get('avg_response_time', 0):.3f}초</span>
                </div>
                <div class="metric">
                    <span class="metric-label">고가치 대화</span>
                    <span class="metric-value">{learning_statistics.get('statistics', {}).get('high_value_conversations', 0)}</span>
                </div>
            </div>

            <!-- 메타 학습 -->
            <div class="card">
                <h3>🔄 메타 학습</h3>
                <div class="metric">
                    <span class="metric-label">메타 평가 수</span>
                    <span class="metric-value">{meta_learning_stats.get('meta_learning_statistics', {}).get('total_meta_evaluations', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">성공률</span>
                    <span class="metric-value">{meta_learning_stats.get('meta_learning_statistics', {}).get('success_rate', 0):.1%}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">평균 개선도</span>
                    <span class="metric-value">{meta_learning_stats.get('meta_learning_statistics', {}).get('average_improvement', 0):.3f}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">성공한 개선</span>
                    <span class="metric-value">{meta_learning_stats.get('meta_learning_statistics', {}).get('successful_improvements', 0)}</span>
                </div>
            </div>

            <!-- 성능 지표 -->
            <div class="card">
                <h3>⚡ 성능 지표</h3>
                {self._generate_performance_metrics(performance_summary)}
            </div>

            <!-- 학습 메트릭 -->
            <div class="card">
                <h3>📊 학습 메트릭</h3>
                {self._generate_learning_metrics(performance_summary)}
            </div>

            <!-- 최근 활동 -->
            <div class="card">
                <h3>🕒 최근 활동</h3>
                <div class="metric">
                    <span class="metric-label">마지막 업데이트</span>
                    <span class="metric-value">{datetime.now().strftime('%H:%M:%S')}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">서비스 상태</span>
                    <span class="metric-value">🟢 정상</span>
                </div>
                <div class="metric">
                    <span class="metric-label">모듈 상태</span>
                    <span class="metric-value">✅ 모든 모듈 정상</span>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>DuRi 자가진화 AI 시스템 - 실시간 모니터링 대시보드</p>
            <p>마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        // 자동 새로고침 (30초마다)
        setTimeout(() => {{
            location.reload();
        }}, 30000);

        // 실시간 업데이트를 위한 WebSocket 연결 (향후 구현)
        // const ws = new WebSocket('ws://localhost:8088/ws');
    </script>
</body>
</html>
        """

        # 대시보드 파일 저장
        with open(self.dashboard_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return self.dashboard_path

    def _format_uptime(self, seconds: float) -> str:
        """가동 시간 포맷팅"""
        if seconds < 60:
            return f"{seconds:.0f}초"
        elif seconds < 3600:
            return f"{seconds/60:.0f}분"
        else:
            return f"{seconds/3600:.1f}시간"

    def _generate_performance_metrics(self, performance_summary: Dict[str, Any]) -> str:
        """성능 지표 HTML 생성"""
        endpoint_performance = performance_summary.get("endpoint_performance", {})

        html = ""
        for endpoint, perf in endpoint_performance.items():
            avg_time = perf.get("avg_response_time", 0)
            error_rate = perf.get("error_rate", 0)

            html += f"""
                <div class="metric">
                    <span class="metric-label">{endpoint}</span>
                    <span class="metric-value">{avg_time:.3f}초</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(error_rate * 100, 100)}%"></div>
                </div>
            """

        return html

    def _generate_learning_metrics(self, performance_summary: Dict[str, Any]) -> str:
        """학습 메트릭 HTML 생성"""
        learning_metrics = performance_summary.get("learning_metrics", {})

        html = ""
        for metric_name, metric_data in learning_metrics.items():
            current_value = metric_data.get("current_value", 0)
            trend = metric_data.get("trend", "stable")

            trend_icon = (
                "➡️" if trend == "stable" else "📈" if trend == "improving" else "📉"
            )

            html += f"""
                <div class="metric">
                    <span class="metric-label">{metric_name}</span>
                    <span class="metric-value">{current_value:.3f} {trend_icon}</span>
                </div>
            """

        return html


# 모듈 인스턴스 생성
dashboard_generator = DashboardGenerator()
