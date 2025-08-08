"""
Day 6: 실시간 대시보드 API
DuRi Memory System의 실시간 모니터링 대시보드를 위한 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from typing import Dict, List, Any, Optional
import asyncio
import json
import time
from datetime import datetime, timedelta

from ..services.memory_service import MemoryService
from ..services.dashboard_service import DashboardService
from ..services.metrics_service import MetricsService
from ..models.memory import MemoryEntry
from ..schemas.dashboard import (
    DashboardOverview,
    MemoryDashboard,
    ServiceStatus,
    PerformanceMetrics,
    RealtimeData
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# 의존성 주입
def get_memory_service() -> MemoryService:
    return MemoryService()

def get_dashboard_service() -> DashboardService:
    return DashboardService()

def get_metrics_service() -> MetricsService:
    return MetricsService()

@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    memory_service: MemoryService = Depends(get_memory_service),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    전체 시스템 대시보드 개요
    """
    try:
        # 메모리 통계
        memory_stats = await memory_service.get_memory_stats()
        
        # 서비스 상태
        service_status = await dashboard_service.get_service_status()
        
        # 성능 지표
        performance_metrics = await dashboard_service.get_performance_metrics()
        
        # 실시간 데이터
        realtime_data = await dashboard_service.get_realtime_data()
        
        return DashboardOverview(
            timestamp=datetime.now(),
            memory_stats=memory_stats,
            service_status=service_status,
            performance_metrics=performance_metrics,
            realtime_data=realtime_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 데이터 조회 실패: {str(e)}")

@router.get("/memory", response_model=MemoryDashboard)
async def get_memory_dashboard(
    memory_service: MemoryService = Depends(get_memory_service),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    메모리 시스템 대시보드
    """
    try:
        # 메모리 통계
        memory_stats = await memory_service.get_memory_stats()
        
        # 최근 메모리 항목들
        recent_memories = await memory_service.query_memories(
            limit=20,
            sort_by="created_at",
            sort_order="desc"
        )
        
        # 메모리 타입별 분포
        memory_by_type = await dashboard_service.get_memory_by_type()
        
        # 메모리 소스별 분포
        memory_by_source = await dashboard_service.get_memory_by_source()
        
        # 중요도별 분포
        memory_by_importance = await dashboard_service.get_memory_by_importance()
        
        return MemoryDashboard(
            timestamp=datetime.now(),
            stats=memory_stats,
            recent_memories=recent_memories,
            by_type=memory_by_type,
            by_source=memory_by_source,
            by_importance=memory_by_importance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메모리 대시보드 조회 실패: {str(e)}")

@router.get("/services", response_model=List[ServiceStatus])
async def get_services_status(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    서비스 상태 대시보드
    """
    try:
        services = await dashboard_service.get_all_service_status()
        return services
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서비스 상태 조회 실패: {str(e)}")

@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_dashboard(
    metrics_service: MetricsService = Depends(get_metrics_service),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    성능 지표 대시보드
    """
    try:
        # 시스템 리소스 사용량
        system_metrics = await metrics_service.get_system_metrics()
        
        # API 응답 시간
        api_metrics = await metrics_service.get_api_metrics()
        
        # 데이터베이스 성능
        db_metrics = await metrics_service.get_database_metrics()
        
        # 메모리 사용량
        memory_metrics = await metrics_service.get_memory_usage_metrics()
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            system=system_metrics,
            api=api_metrics,
            database=db_metrics,
            memory=memory_metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 지표 조회 실패: {str(e)}")

@router.get("/realtime", response_model=RealtimeData)
async def get_realtime_data(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    실시간 데이터 스트림
    """
    try:
        realtime_data = await dashboard_service.get_realtime_data()
        return realtime_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실시간 데이터 조회 실패: {str(e)}")

@router.get("/ui", response_class=HTMLResponse)
async def get_dashboard_ui():
    """
    대시보드 웹 UI
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DuRi 실시간 대시보드</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .dashboard {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5em;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .card h3 {
                margin-top: 0;
                color: #fff;
                font-size: 1.3em;
            }
            .metric {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 10px 0;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
            .metric-value {
                font-size: 1.2em;
                font-weight: bold;
            }
            .status {
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 0.9em;
                font-weight: bold;
            }
            .status.healthy { background: #4CAF50; }
            .status.warning { background: #FF9800; }
            .status.error { background: #F44336; }
            .chart-container {
                position: relative;
                height: 300px;
                margin-top: 15px;
            }
            .refresh-btn {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                margin: 10px 0;
            }
            .refresh-btn:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>🚀 DuRi 실시간 대시보드</h1>
                <p>Day 6: 실시간 모니터링 시스템</p>
            </div>
            
            <button class="refresh-btn" onclick="refreshDashboard()">🔄 새로고침</button>
            
            <div class="grid">
                <div class="card">
                    <h3>📊 시스템 개요</h3>
                    <div id="overview-metrics"></div>
                </div>
                
                <div class="card">
                    <h3>🧠 메모리 시스템</h3>
                    <div id="memory-metrics"></div>
                    <div class="chart-container">
                        <canvas id="memoryChart"></canvas>
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚙️ 서비스 상태</h3>
                    <div id="service-status"></div>
                </div>
                
                <div class="card">
                    <h3>📈 성능 지표</h3>
                    <div id="performance-metrics"></div>
                    <div class="chart-container">
                        <canvas id="performanceChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let memoryChart, performanceChart;
            
            // 차트 초기화
            function initCharts() {
                const memoryCtx = document.getElementById('memoryChart').getContext('2d');
                memoryChart = new Chart(memoryCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['단기 기억', '중기 기억', '장기 기억'],
                        datasets: [{
                            data: [30, 50, 20],
                            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: { color: 'white' }
                            }
                        }
                    }
                });
                
                const performanceCtx = document.getElementById('performanceChart').getContext('2d');
                performanceChart = new Chart(performanceCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'CPU 사용률',
                            data: [],
                            borderColor: '#FF6384',
                            tension: 0.4
                        }, {
                            label: '메모리 사용률',
                            data: [],
                            borderColor: '#36A2EB',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                ticks: { color: 'white' }
                            },
                            x: {
                                ticks: { color: 'white' }
                            }
                        },
                        plugins: {
                            legend: {
                                labels: { color: 'white' }
                            }
                        }
                    }
                });
            }
            
            // 대시보드 데이터 로드
            async function loadDashboardData() {
                try {
                    const [overview, memory, services, performance] = await Promise.all([
                        fetch('/dashboard/overview').then(r => r.json()),
                        fetch('/dashboard/memory').then(r => r.json()),
                        fetch('/dashboard/services').then(r => r.json()),
                        fetch('/dashboard/performance').then(r => r.json())
                    ]);
                    
                    updateOverview(overview);
                    updateMemory(memory);
                    updateServices(services);
                    updatePerformance(performance);
                    
                } catch (error) {
                    console.error('대시보드 데이터 로드 실패:', error);
                    document.getElementById('overview-metrics').innerHTML = 
                        '<div class="metric"><span>연결 중...</span></div>';
                }
            }
            
            function updateOverview(data) {
                const container = document.getElementById('overview-metrics');
                container.innerHTML = `
                    <div class="metric">
                        <span>총 메모리</span>
                        <span class="metric-value">${data.memory_stats?.total_memories || 0}</span>
                    </div>
                    <div class="metric">
                        <span>활성 서비스</span>
                        <span class="metric-value">${data.service_status?.length || 0}</span>
                    </div>
                    <div class="metric">
                        <span>시스템 상태</span>
                        <span class="status healthy">정상</span>
                    </div>
                `;
            }
            
            function updateMemory(data) {
                const container = document.getElementById('memory-metrics');
                container.innerHTML = `
                    <div class="metric">
                        <span>총 기억</span>
                        <span class="metric-value">${data.stats?.total_memories || 0}</span>
                    </div>
                    <div class="metric">
                        <span>최근 24시간</span>
                        <span class="metric-value">${data.stats?.recent_24h || 0}</span>
                    </div>
                `;
                
                // 차트 업데이트
                if (memoryChart && data.by_type) {
                    memoryChart.data.labels = Object.keys(data.by_type);
                    memoryChart.data.datasets[0].data = Object.values(data.by_type);
                    memoryChart.update();
                }
            }
            
            function updateServices(services) {
                const container = document.getElementById('service-status');
                container.innerHTML = services.map(service => `
                    <div class="metric">
                        <span>${service.name}</span>
                        <span class="status ${service.status === 'healthy' ? 'healthy' : 'error'}">
                            ${service.status}
                        </span>
                    </div>
                `).join('');
            }
            
            function updatePerformance(data) {
                const container = document.getElementById('performance-metrics');
                container.innerHTML = `
                    <div class="metric">
                        <span>CPU 사용률</span>
                        <span class="metric-value">${data.system?.cpu_usage || 0}%</span>
                    </div>
                    <div class="metric">
                        <span>메모리 사용률</span>
                        <span class="metric-value">${data.system?.memory_usage || 0}%</span>
                    </div>
                    <div class="metric">
                        <span>API 응답 시간</span>
                        <span class="metric-value">${data.api?.avg_response_time || 0}ms</span>
                    </div>
                `;
                
                // 성능 차트 업데이트
                if (performanceChart && data.system) {
                    const now = new Date().toLocaleTimeString();
                    performanceChart.data.labels.push(now);
                    performanceChart.data.datasets[0].data.push(data.system.cpu_usage || 0);
                    performanceChart.data.datasets[1].data.push(data.system.memory_usage || 0);
                    
                    // 최근 10개 데이터만 유지
                    if (performanceChart.data.labels.length > 10) {
                        performanceChart.data.labels.shift();
                        performanceChart.data.datasets[0].data.shift();
                        performanceChart.data.datasets[1].data.shift();
                    }
                    
                    performanceChart.update();
                }
            }
            
            function refreshDashboard() {
                loadDashboardData();
            }
            
            // 초기화
            document.addEventListener('DOMContentLoaded', function() {
                initCharts();
                loadDashboardData();
                
                // 5초마다 자동 새로고침
                setInterval(loadDashboardData, 5000);
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/ws")
async def websocket_endpoint():
    """
    WebSocket 실시간 데이터 스트림
    """
    # WebSocket 구현은 별도로 추가 예정
    pass 