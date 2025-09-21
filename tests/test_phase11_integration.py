#!/usr/bin/env python3
"""
Phase 11 Enhanced Orchestrator 통합 테스트

기존 DuRi 시스템들과의 통합을 테스트하고
Insight Engine 연동을 검증합니다.

Author: DuRi Phase 11 Integration Team
"""

import pytest
import sys
import os
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Phase 11 모듈 임포트
try:
    from scripts.core.phase11.enhanced_orchestrator import (
        EnhancedDuRiOrchestrator,
        EnhancedExecutionContext,
        Phase11Metrics
    )
except ImportError as e:
    pytest.skip(f"Phase 11 모듈을 임포트할 수 없습니다: {e}", allow_module_level=True)


class TestPhase11Integration:
    """Phase 11 통합 테스트 클래스"""
    
    def test_enhanced_orchestrator_import(self):
        """향상된 오케스트레이터 모듈이 정상적으로 임포트되는지 확인"""
        assert EnhancedDuRiOrchestrator is not None
        assert EnhancedExecutionContext is not None
        assert Phase11Metrics is not None
    
    def test_enhanced_orchestrator_initialization(self):
        """향상된 오케스트레이터 초기화 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # 기본 속성 확인
        assert orchestrator.inner_thinking is not None
        assert orchestrator.unified_learning is not None
        assert orchestrator.integrated_manager is not None
        assert orchestrator.phase11_metrics is not None
        assert orchestrator.conversation_turn == 0
    
    def test_phase11_metrics_creation(self):
        """Phase 11 메트릭 생성 테스트"""
        metrics = Phase11Metrics(
            turn_number=1,
            execution_time=1.5,
            insight_score=0.8,
            learning_score=0.7,
            reflection_score=0.9,
            overall_quality=0.8
        )
        
        assert metrics.turn_number == 1
        assert metrics.execution_time == 1.5
        assert metrics.insight_score == 0.8
        assert metrics.learning_score == 0.7
        assert metrics.reflection_score == 0.9
        assert metrics.overall_quality == 0.8
        assert metrics.timestamp is not None
    
    def test_enhanced_execution_context(self):
        """향상된 실행 컨텍스트 테스트"""
        context = EnhancedExecutionContext(
            input_data="test input",
            current_phase="judgment",
            system_states={},
            execution_history=[],
            metadata={}
        )
        
        assert context.input_data == "test input"
        assert context.current_phase == "judgment"
        assert context.conversation_turn == 0
        assert isinstance(context.insight_metrics, dict)
        assert isinstance(context.learning_context, dict)
        assert isinstance(context.reflection_results, list)
    
    @pytest.mark.asyncio
    async def test_enhanced_judgment_phase(self):
        """향상된 Judgment Phase 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # Mock을 사용하여 기존 메서드 호출 시뮬레이션
        with patch.object(orchestrator, '_execute_judgment_phase', return_value={"phase": "judgment", "status": "completed"}):
            result = await orchestrator._execute_enhanced_judgment_phase()
            
            assert result["phase"] == "judgment"
            assert result["status"] == "completed"
            assert result["turn"] == 1  # conversation_turn이 증가했을 것
    
    @pytest.mark.asyncio
    async def test_enhanced_action_phase(self):
        """향상된 Action Phase 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        judgment_result = {"phase": "judgment", "status": "completed"}
        
        with patch.object(orchestrator, '_execute_action_phase', return_value={"phase": "action", "status": "completed"}):
            result = await orchestrator._execute_enhanced_action_phase(judgment_result)
            
            assert result["phase"] == "action"
            assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_enhanced_feedback_phase(self):
        """향상된 Feedback Phase 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        action_result = {"phase": "action", "status": "completed"}
        
        with patch.object(orchestrator, '_execute_feedback_phase', return_value={"phase": "feedback", "status": "completed"}):
            result = await orchestrator._execute_enhanced_feedback_phase(action_result)
            
            assert result["phase"] == "feedback"
            assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_inner_reflection(self):
        """내부 사고 및 성찰 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        feedback_result = {"phase": "feedback", "status": "completed"}
        
        # Mock을 사용하여 내부 사고 시스템 시뮬레이션
        with patch.object(orchestrator.inner_thinking, 'think_deeply', return_value={"reflection": "test reflection"}):
            result = await orchestrator._execute_inner_reflection(feedback_result)
            
            assert result["phase"] == "inner_reflection"
            assert result["status"] == "completed"
            assert "result" in result
    
    @pytest.mark.asyncio
    async def test_external_learning(self):
        """외부 학습 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        feedback_result = {"phase": "feedback", "status": "completed"}
        
        # Mock을 사용하여 학습 시스템 시뮬레이션
        with patch.object(orchestrator.unified_learning, 'process_learning', return_value={"learning": "test learning"}):
            result = await orchestrator._execute_external_learning(feedback_result)
            
            assert result["phase"] == "external_learning"
            assert result["status"] == "completed"
            assert "result" in result
    
    @pytest.mark.asyncio
    async def test_insight_metrics_recording(self):
        """Insight 메트릭 기록 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # Mock Insight Engine
        mock_insight_engine = MagicMock()
        mock_insight_engine.analyze_turn_quality.return_value = 0.85
        orchestrator.insight_engine = mock_insight_engine
        
        judgment_result = {"phase": "judgment", "status": "completed"}
        action_result = {"phase": "action", "status": "completed"}
        feedback_result = {"phase": "feedback", "status": "completed"}
        reflection_result = {"phase": "inner_reflection", "status": "completed"}
        learning_result = {"phase": "external_learning", "status": "completed"}
        
        result = await orchestrator._record_insight_metrics(
            judgment_result, action_result, feedback_result,
            reflection_result, learning_result
        )
        
        assert result["insight_score"] == 0.85
        assert "metrics" in result
        mock_insight_engine.analyze_turn_quality.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_phase11_metrics_recording(self):
        """Phase 11 메트릭 기록 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        insight_result = {"insight_score": 0.8, "metrics": {}}
        
        await orchestrator._record_phase11_metrics(1.5, insight_result)
        
        assert len(orchestrator.phase11_metrics) == 1
        metrics = orchestrator.phase11_metrics[0]
        assert metrics.turn_number == 1
        assert metrics.execution_time == 1.5
        assert metrics.insight_score == 0.8
        assert metrics.overall_quality > 0
    
    def test_phase11_status_report(self):
        """Phase 11 상태 리포트 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # Mock 기존 상태 리포트
        with patch.object(orchestrator, 'generate_status_report', return_value={"base": "report"}):
            report = orchestrator.get_phase11_status_report()
            
            assert "phase11_metrics" in report
            assert "enhanced_systems" in report
            assert "integration_status" in report
            assert report["version"] == "Phase 11 Enhanced"
    
    @pytest.mark.asyncio
    async def test_enhanced_execution_loop_structure(self):
        """향상된 실행 루프 구조 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # 실행 루프가 정상적으로 시작되고 중단되는지 테스트
        orchestrator.execution_loop_active = False
        
        # Mock을 사용하여 각 단계 시뮬레이션
        with patch.object(orchestrator, '_execute_enhanced_judgment_phase') as mock_judgment, \
             patch.object(orchestrator, '_execute_enhanced_action_phase') as mock_action, \
             patch.object(orchestrator, '_execute_enhanced_feedback_phase') as mock_feedback, \
             patch.object(orchestrator, '_execute_inner_reflection') as mock_reflection, \
             patch.object(orchestrator, '_execute_external_learning') as mock_learning, \
             patch.object(orchestrator, '_record_insight_metrics') as mock_insight, \
             patch.object(orchestrator, '_update_enhanced_system_status') as mock_update, \
             patch.object(orchestrator, '_monitor_enhanced_performance') as mock_monitor, \
             patch.object(orchestrator, '_record_phase11_metrics') as mock_record, \
             patch.object(orchestrator.integrated_manager, 'initialize_all_systems') as mock_init:
            
            # Mock 반환값 설정
            mock_judgment.return_value = {"phase": "judgment", "status": "completed"}
            mock_action.return_value = {"phase": "action", "status": "completed"}
            mock_feedback.return_value = {"phase": "feedback", "status": "completed"}
            mock_reflection.return_value = {"phase": "inner_reflection", "status": "completed"}
            mock_learning.return_value = {"phase": "external_learning", "status": "completed"}
            mock_insight.return_value = {"insight_score": 0.8}
            
            # 실행 루프 시작 (짧은 시간만 실행)
            orchestrator.execution_loop_active = True
            
            # 1초 후 중단
            async def stop_loop():
                await asyncio.sleep(1)
                orchestrator.execution_loop_active = False
            
            # 병렬로 실행
            await asyncio.gather(
                orchestrator.start_enhanced_execution_loop(),
                stop_loop()
            )
            
            # 각 단계가 호출되었는지 확인
            mock_init.assert_called_once()
            assert mock_judgment.call_count > 0
            assert mock_action.call_count > 0
            assert mock_feedback.call_count > 0
            assert mock_reflection.call_count > 0
            assert mock_learning.call_count > 0
            assert mock_insight.call_count > 0


class TestPhase11SystemIntegration:
    """Phase 11 시스템 통합 테스트 클래스"""
    
    def test_duricore_integration(self):
        """DuRiCore 통합 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # DuRiCore 관련 속성이 있는지 확인
        assert hasattr(orchestrator, 'systems')
        assert hasattr(orchestrator, 'system_status')
        assert hasattr(orchestrator, 'execution_loop_active')
    
    def test_inner_thinking_integration(self):
        """내부 사고 시스템 통합 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # 내부 사고 시스템이 초기화되었는지 확인
        assert orchestrator.inner_thinking is not None
        assert hasattr(orchestrator.inner_thinking, 'think_deeply')
    
    def test_unified_learning_integration(self):
        """통합 학습 시스템 통합 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # 통합 학습 시스템이 초기화되었는지 확인
        assert orchestrator.unified_learning is not None
        assert hasattr(orchestrator.unified_learning, 'process_learning')
    
    def test_integrated_manager_integration(self):
        """통합 시스템 매니저 통합 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # 통합 시스템 매니저가 초기화되었는지 확인
        assert orchestrator.integrated_manager is not None
        assert hasattr(orchestrator.integrated_manager, 'initialize_all_systems')
    
    def test_insight_engine_integration(self):
        """Insight Engine 통합 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # Insight Engine이 초기화되었는지 확인 (없을 수도 있음)
        # insight_engine은 None일 수 있으므로 None 체크
        assert orchestrator.insight_engine is None or hasattr(orchestrator.insight_engine, 'analyze_turn_quality')


class TestPhase11ErrorHandling:
    """Phase 11 오류 처리 테스트 클래스"""
    
    @pytest.mark.asyncio
    async def test_judgment_phase_error_handling(self):
        """Judgment Phase 오류 처리 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        # 오류 발생 시뮬레이션
        with patch.object(orchestrator, '_execute_judgment_phase', side_effect=Exception("Test error")):
            result = await orchestrator._execute_enhanced_judgment_phase()
            
            assert result["phase"] == "judgment"
            assert result["status"] == "error"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_action_phase_error_handling(self):
        """Action Phase 오류 처리 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        judgment_result = {"phase": "judgment", "status": "completed"}
        
        # 오류 발생 시뮬레이션
        with patch.object(orchestrator, '_execute_action_phase', side_effect=Exception("Test error")):
            result = await orchestrator._execute_enhanced_action_phase(judgment_result)
            
            assert result["phase"] == "action"
            assert result["status"] == "error"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_feedback_phase_error_handling(self):
        """Feedback Phase 오류 처리 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        action_result = {"phase": "action", "status": "completed"}
        
        # 오류 발생 시뮬레이션
        with patch.object(orchestrator, '_execute_feedback_phase', side_effect=Exception("Test error")):
            result = await orchestrator._execute_enhanced_feedback_phase(action_result)
            
            assert result["phase"] == "feedback"
            assert result["status"] == "error"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_inner_reflection_error_handling(self):
        """내부 사고 오류 처리 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        feedback_result = {"phase": "feedback", "status": "completed"}
        
        # 오류 발생 시뮬레이션
        with patch.object(orchestrator.inner_thinking, 'think_deeply', side_effect=Exception("Test error")):
            result = await orchestrator._execute_inner_reflection(feedback_result)
            
            assert result["phase"] == "inner_reflection"
            assert result["status"] == "error"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_external_learning_error_handling(self):
        """외부 학습 오류 처리 테스트"""
        orchestrator = EnhancedDuRiOrchestrator()
        
        feedback_result = {"phase": "feedback", "status": "completed"}
        
        # 오류 발생 시뮬레이션
        with patch.object(orchestrator.unified_learning, 'process_learning', side_effect=Exception("Test error")):
            result = await orchestrator._execute_external_learning(feedback_result)
            
            assert result["phase"] == "external_learning"
            assert result["status"] == "error"
            assert "error" in result


if __name__ == "__main__":
    # 직접 실행 시 pytest 실행
    pytest.main([__file__, "-v"])

