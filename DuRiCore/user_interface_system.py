#!/usr/bin/env python3
"""
DuRi 사용자 인터페이스 시스템 - Phase 1-3 Week 3 Day 8
사용자 친화적인 인터페이스를 제공하는 시스템

기능:
1. 사용자 입력 처리
2. 시스템 상태 표시
3. 결과 시각화
4. 사용자 피드백 수집
"""

import asyncio
import json
import logging
import queue
import statistics
import threading
import time
import uuid
import weakref
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import numpy as np

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InputType(Enum):
    """입력 유형"""

    TEXT = "text"
    VOICE = "voice"
    GESTURE = "gesture"
    TOUCH = "touch"
    COMMAND = "command"
    FILE = "file"


class OutputType(Enum):
    """출력 유형"""

    TEXT = "text"
    VISUAL = "visual"
    AUDIO = "audio"
    INTERACTIVE = "interactive"
    NOTIFICATION = "notification"


class InterfaceMode(Enum):
    """인터페이스 모드"""

    CONSOLE = "console"
    GRAPHICAL = "graphical"
    WEB = "web"
    MOBILE = "mobile"
    VOICE = "voice"


@dataclass
class UserInput:
    """사용자 입력"""

    input_id: str
    input_type: InputType
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemOutput:
    """시스템 출력"""

    output_id: str
    output_type: OutputType
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    target_user: str = ""
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserFeedback:
    """사용자 피드백"""

    feedback_id: str
    user_id: str
    session_id: str
    rating: float = 0.0
    comment: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InterfaceState:
    """인터페이스 상태"""

    state_id: str
    mode: InterfaceMode
    active_session: str = ""
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    system_status: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class UserInterfaceSystem:
    """사용자 인터페이스 시스템"""

    def __init__(self):
        """초기화"""
        self.user_inputs: Dict[str, UserInput] = {}
        self.system_outputs: Dict[str, SystemOutput] = {}
        self.user_feedbacks: Dict[str, UserFeedback] = {}
        self.interface_states: Dict[str, InterfaceState] = {}
        self.system_registry: Dict[str, Any] = {}

        # 인터페이스 설정
        self.interface_config = {
            "default_mode": InterfaceMode.CONSOLE,
            "max_input_history": 1000,
            "max_output_history": 1000,
            "response_timeout": 30.0,
            "auto_save_interval": 60.0,
        }

        # 사용자 설정
        self.user_preferences = {
            "language": "ko",
            "theme": "default",
            "font_size": "medium",
            "accessibility": False,
            "notifications": True,
        }

        # 모니터링 데이터
        self.interface_metrics = {
            "total_inputs": 0,
            "total_outputs": 0,
            "total_feedbacks": 0,
            "average_response_time": 0.0,
            "user_satisfaction": 0.0,
            "interface_usage": {},
        }

        # 입력/출력 큐
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

        # 활성 세션
        self.active_sessions: Set[str] = set()

        logger.info("사용자 인터페이스 시스템 초기화 완료")

    async def register_system(self, system_name: str, system_instance: Any) -> bool:
        """시스템 등록"""
        try:
            self.system_registry[system_name] = system_instance
            logger.info(f"시스템 등록 완료: {system_name}")
            return True
        except Exception as e:
            logger.error(f"시스템 등록 실패: {system_name} - {e}")
            return False

    async def process_user_input(
        self,
        input_type: InputType,
        content: Any,
        user_id: str = "",
        session_id: str = "",
    ) -> str:
        """사용자 입력 처리"""
        input_id = f"input_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        user_input = UserInput(
            input_id=input_id,
            input_type=input_type,
            content=content,
            user_id=user_id,
            session_id=session_id,
        )

        self.user_inputs[input_id] = user_input
        await self.input_queue.put(user_input)

        # 메트릭 업데이트
        self.interface_metrics["total_inputs"] += 1

        logger.info(f"사용자 입력 처리: {input_id} ({input_type.value})")
        return input_id

    async def generate_system_output(
        self,
        output_type: OutputType,
        content: Any,
        target_user: str = "",
        session_id: str = "",
    ) -> str:
        """시스템 출력 생성"""
        output_id = f"output_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        system_output = SystemOutput(
            output_id=output_id,
            output_type=output_type,
            content=content,
            target_user=target_user,
            session_id=session_id,
        )

        self.system_outputs[output_id] = system_output
        await self.output_queue.put(system_output)

        # 메트릭 업데이트
        self.interface_metrics["total_outputs"] += 1

        logger.info(f"시스템 출력 생성: {output_id} ({output_type.value})")
        return output_id

    async def collect_user_feedback(
        self, user_id: str, session_id: str, rating: float, comment: str = ""
    ) -> str:
        """사용자 피드백 수집"""
        feedback_id = f"feedback_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        user_feedback = UserFeedback(
            feedback_id=feedback_id,
            user_id=user_id,
            session_id=session_id,
            rating=rating,
            comment=comment,
        )

        self.user_feedbacks[feedback_id] = user_feedback

        # 사용자 만족도 업데이트
        self._update_user_satisfaction(rating)

        # 메트릭 업데이트
        self.interface_metrics["total_feedbacks"] += 1

        logger.info(f"사용자 피드백 수집: {feedback_id} (평점: {rating})")
        return feedback_id

    async def create_interface_session(self, user_id: str, mode: InterfaceMode = None) -> str:
        """인터페이스 세션 생성"""
        session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        interface_state = InterfaceState(
            state_id=session_id,
            mode=mode or self.interface_config["default_mode"],
            active_session=session_id,
            user_preferences=self.user_preferences.copy(),
        )

        self.interface_states[session_id] = interface_state
        self.active_sessions.add(session_id)

        logger.info(f"인터페이스 세션 생성: {session_id} ({mode.value if mode else 'default'})")
        return session_id

    async def update_interface_state(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """인터페이스 상태 업데이트"""
        if session_id not in self.interface_states:
            return False

        interface_state = self.interface_states[session_id]

        # 상태 업데이트
        for key, value in updates.items():
            if hasattr(interface_state, key):
                setattr(interface_state, key, value)

        interface_state.timestamp = datetime.now()

        logger.info(f"인터페이스 상태 업데이트: {session_id}")
        return True

    async def display_system_status(self, session_id: str = None) -> Dict[str, Any]:
        """시스템 상태 표시"""
        status_data = {
            "timestamp": datetime.now(),
            "active_sessions": len(self.active_sessions),
            "total_inputs": self.interface_metrics["total_inputs"],
            "total_outputs": self.interface_metrics["total_outputs"],
            "average_response_time": self.interface_metrics["average_response_time"],
            "user_satisfaction": self.interface_metrics["user_satisfaction"],
        }

        # 등록된 시스템 상태 추가
        for system_name, system_instance in self.system_registry.items():
            if hasattr(system_instance, "get_system_status"):
                try:
                    system_status = (
                        await system_instance.get_system_status()
                        if asyncio.iscoroutinefunction(system_instance.get_system_status)
                        else system_instance.get_system_status()
                    )
                    status_data[f"system_{system_name}"] = system_status
                except Exception as e:
                    status_data[f"system_{system_name}"] = {"error": str(e)}

        # 세션별 상태 추가
        if session_id and session_id in self.interface_states:
            interface_state = self.interface_states[session_id]
            status_data["session_state"] = {
                "mode": interface_state.mode.value,
                "user_preferences": interface_state.user_preferences,
                "active_session": interface_state.active_session,
            }

        return status_data

    async def visualize_results(
        self, data: Any, visualization_type: str = "default"
    ) -> Dict[str, Any]:
        """결과 시각화"""
        visualization_id = f"viz_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        # 시각화 유형에 따른 처리
        if visualization_type == "chart":
            visualization = await self._create_chart_visualization(data)
        elif visualization_type == "table":
            visualization = await self._create_table_visualization(data)
        elif visualization_type == "graph":
            visualization = await self._create_graph_visualization(data)
        elif visualization_type == "dashboard":
            visualization = await self._create_dashboard_visualization(data)
        else:
            visualization = await self._create_default_visualization(data)

        visualization["visualization_id"] = visualization_id
        visualization["timestamp"] = datetime.now()
        visualization["type"] = visualization_type

        logger.info(f"결과 시각화 생성: {visualization_id} ({visualization_type})")
        return visualization

    async def handle_user_interaction(
        self,
        interaction_type: str,
        interaction_data: Dict[str, Any],
        session_id: str = "",
    ) -> Dict[str, Any]:
        """사용자 상호작용 처리"""
        interaction_id = f"interaction_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        start_time = time.time()

        try:
            # 상호작용 유형에 따른 처리
            if interaction_type == "command":
                result = await self._handle_command_interaction(interaction_data, session_id)
            elif interaction_type == "query":
                result = await self._handle_query_interaction(interaction_data, session_id)
            elif interaction_type == "configuration":
                result = await self._handle_configuration_interaction(interaction_data, session_id)
            elif interaction_type == "navigation":
                result = await self._handle_navigation_interaction(interaction_data, session_id)
            else:
                result = await self._handle_general_interaction(interaction_data, session_id)

            # 응답 시간 계산
            response_time = time.time() - start_time
            self._update_response_time(response_time)

            result["interaction_id"] = interaction_id
            result["response_time"] = response_time

            logger.info(f"사용자 상호작용 처리: {interaction_id} ({interaction_type})")
            return result

        except Exception as e:
            logger.error(f"사용자 상호작용 처리 실패: {interaction_id} - {e}")
            return {
                "interaction_id": interaction_id,
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time,
            }

    async def _handle_command_interaction(
        self, interaction_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """명령 상호작용 처리"""
        command = interaction_data.get("command", "")
        parameters = interaction_data.get("parameters", {})

        # 명령 처리
        if command == "status":
            return await self.display_system_status(session_id)
        elif command == "help":
            return {"type": "help", "content": self._get_help_content()}
        elif command == "config":
            return {"type": "config", "content": self.user_preferences}
        else:
            return {"type": "unknown_command", "content": f"알 수 없는 명령: {command}"}

    async def _handle_query_interaction(
        self, interaction_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """쿼리 상호작용 처리"""
        query = interaction_data.get("query", "")
        query_type = interaction_data.get("type", "general")

        # 쿼리 처리
        if query_type == "system_status":
            return await self.display_system_status(session_id)
        elif query_type == "user_data":
            return self._get_user_data(session_id)
        elif query_type == "system_metrics":
            return self.interface_metrics
        else:
            return {"type": "query_result", "content": f"쿼리 결과: {query}"}

    async def _handle_configuration_interaction(
        self, interaction_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """설정 상호작용 처리"""
        config_updates = interaction_data.get("updates", {})

        # 설정 업데이트
        for key, value in config_updates.items():
            if key in self.user_preferences:
                self.user_preferences[key] = value

        # 세션 상태 업데이트
        if session_id in self.interface_states:
            await self.update_interface_state(
                session_id, {"user_preferences": self.user_preferences.copy()}
            )

        return {"type": "configuration", "content": "설정이 업데이트되었습니다."}

    async def _handle_navigation_interaction(
        self, interaction_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """네비게이션 상호작용 처리"""
        navigation_target = interaction_data.get("target", "")
        navigation_type = interaction_data.get("type", "page")

        # 네비게이션 처리
        if navigation_type == "page":
            return {
                "type": "navigation",
                "content": f"페이지 이동: {navigation_target}",
            }
        elif navigation_type == "section":
            return {"type": "navigation", "content": f"섹션 이동: {navigation_target}"}
        else:
            return {"type": "navigation", "content": f"네비게이션: {navigation_target}"}

    async def _handle_general_interaction(
        self, interaction_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """일반 상호작용 처리"""
        interaction_type = interaction_data.get("type", "general")
        content = interaction_data.get("content", "")

        return {
            "type": "general_interaction",
            "content": f"일반 상호작용 처리: {interaction_type} - {content}",
        }

    async def _create_chart_visualization(self, data: Any) -> Dict[str, Any]:
        """차트 시각화 생성"""
        # 차트 시각화 시뮬레이션
        chart_data = {
            "type": "chart",
            "chart_type": "line",
            "data_points": len(data) if isinstance(data, (list, tuple)) else 1,
            "x_axis": "시간",
            "y_axis": "값",
            "data": data,
        }
        return chart_data

    async def _create_table_visualization(self, data: Any) -> Dict[str, Any]:
        """테이블 시각화 생성"""
        # 테이블 시각화 시뮬레이션
        table_data = {
            "type": "table",
            "columns": ["항목", "값", "상태"],
            "rows": data if isinstance(data, list) else [data],
            "total_rows": len(data) if isinstance(data, list) else 1,
        }
        return table_data

    async def _create_graph_visualization(self, data: Any) -> Dict[str, Any]:
        """그래프 시각화 생성"""
        # 그래프 시각화 시뮬레이션
        graph_data = {
            "type": "graph",
            "graph_type": "network",
            "nodes": len(data) if isinstance(data, (list, tuple)) else 1,
            "edges": max(0, len(data) - 1) if isinstance(data, (list, tuple)) else 0,
            "data": data,
        }
        return graph_data

    async def _create_dashboard_visualization(self, data: Any) -> Dict[str, Any]:
        """대시보드 시각화 생성"""
        # 대시보드 시각화 시뮬레이션
        dashboard_data = {
            "type": "dashboard",
            "widgets": ["시스템 상태", "성능 지표", "사용자 활동"],
            "layout": "grid",
            "data": data,
        }
        return dashboard_data

    async def _create_default_visualization(self, data: Any) -> Dict[str, Any]:
        """기본 시각화 생성"""
        # 기본 시각화 시뮬레이션
        default_data = {
            "type": "default",
            "format": "text",
            "content": str(data),
            "data_size": len(str(data)),
        }
        return default_data

    def _get_help_content(self) -> Dict[str, Any]:
        """도움말 내용 반환"""
        return {
            "commands": {
                "status": "시스템 상태 확인",
                "help": "도움말 표시",
                "config": "설정 확인",
                "visualize": "결과 시각화",
            },
            "interactions": {
                "command": "명령 실행",
                "query": "쿼리 실행",
                "configuration": "설정 변경",
                "navigation": "네비게이션",
            },
        }

    def _get_user_data(self, session_id: str) -> Dict[str, Any]:
        """사용자 데이터 반환"""
        if session_id in self.interface_states:
            interface_state = self.interface_states[session_id]
            return {
                "session_id": session_id,
                "mode": interface_state.mode.value,
                "preferences": interface_state.user_preferences,
                "active_session": interface_state.active_session,
            }
        else:
            return {"error": "세션을 찾을 수 없습니다."}

    def _update_user_satisfaction(self, rating: float):
        """사용자 만족도 업데이트"""
        current_satisfaction = self.interface_metrics["user_satisfaction"]
        total_feedbacks = self.interface_metrics["total_feedbacks"]

        if total_feedbacks > 0:
            self.interface_metrics["user_satisfaction"] = (
                current_satisfaction * (total_feedbacks - 1) + rating
            ) / total_feedbacks
        else:
            self.interface_metrics["user_satisfaction"] = rating

    def _update_response_time(self, response_time: float):
        """응답 시간 업데이트"""
        total_interactions = (
            self.interface_metrics["total_inputs"] + self.interface_metrics["total_outputs"]
        )
        current_avg = self.interface_metrics["average_response_time"]

        if total_interactions > 0:
            self.interface_metrics["average_response_time"] = (
                current_avg * (total_interactions - 1) + response_time
            ) / total_interactions
        else:
            self.interface_metrics["average_response_time"] = response_time

    def get_interface_metrics(self) -> Dict[str, Any]:
        """인터페이스 메트릭 반환"""
        return self.interface_metrics.copy()

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "registered_systems": list(self.system_registry.keys()),
            "active_sessions": len(self.active_sessions),
            "total_inputs": len(self.user_inputs),
            "total_outputs": len(self.system_outputs),
            "total_feedbacks": len(self.user_feedbacks),
            "interface_states": len(self.interface_states),
        }


async def test_user_interface_system():
    """사용자 인터페이스 시스템 테스트"""
    print("=== 사용자 인터페이스 시스템 테스트 시작 ===")

    # 사용자 인터페이스 시스템 초기화
    ui_system = UserInterfaceSystem()

    # 가상 시스템 등록
    class MockSystem:
        def __init__(self, name: str):
            self.name = name

        def get_system_status(self):
            return {"system": self.name, "status": "active"}

    # 시스템 등록
    systems = ["lida_attention", "realtime_learning", "dynamic_reasoning"]
    for system_name in systems:
        mock_system = MockSystem(system_name)
        await ui_system.register_system(system_name, mock_system)

    print(f"등록된 시스템 수: {len(ui_system.system_registry)}")

    # 1. 인터페이스 세션 생성 테스트
    print("\n1. 인터페이스 세션 생성 테스트")
    session_id = await ui_system.create_interface_session("user_001", InterfaceMode.CONSOLE)
    print(f"생성된 세션: {session_id}")

    # 2. 사용자 입력 처리 테스트
    print("\n2. 사용자 입력 처리 테스트")
    input_id = await ui_system.process_user_input(
        InputType.TEXT, "시스템 상태 확인", "user_001", session_id
    )
    print(f"처리된 입력: {input_id}")

    # 3. 시스템 출력 생성 테스트
    print("\n3. 시스템 출력 생성 테스트")
    output_id = await ui_system.generate_system_output(
        OutputType.TEXT, "시스템이 정상적으로 작동 중입니다.", "user_001", session_id
    )
    print(f"생성된 출력: {output_id}")

    # 4. 시스템 상태 표시 테스트
    print("\n4. 시스템 상태 표시 테스트")
    system_status = await ui_system.display_system_status(session_id)
    print(f"시스템 상태: {system_status}")

    # 5. 결과 시각화 테스트
    print("\n5. 결과 시각화 테스트")
    test_data = [{"x": 1, "y": 10}, {"x": 2, "y": 20}, {"x": 3, "y": 30}]
    visualization = await ui_system.visualize_results(test_data, "chart")
    print(f"시각화 결과: {visualization}")

    # 6. 사용자 상호작용 처리 테스트
    print("\n6. 사용자 상호작용 처리 테스트")
    interaction_result = await ui_system.handle_user_interaction(
        "command", {"command": "status"}, session_id
    )
    print(f"상호작용 결과: {interaction_result}")

    # 7. 사용자 피드백 수집 테스트
    print("\n7. 사용자 피드백 수집 테스트")
    feedback_id = await ui_system.collect_user_feedback(
        "user_001", session_id, 4.5, "매우 만족스러운 인터페이스입니다."
    )
    print(f"수집된 피드백: {feedback_id}")

    # 8. 메트릭 확인
    print("\n8. 메트릭 확인")
    interface_metrics = ui_system.get_interface_metrics()
    system_status = ui_system.get_system_status()

    print(f"인터페이스 메트릭: {interface_metrics}")
    print(f"시스템 상태: {system_status}")

    print("\n=== 사용자 인터페이스 시스템 테스트 완료 ===")

    return {
        "interface_metrics": interface_metrics,
        "system_status": system_status,
        "session_id": session_id,
    }


if __name__ == "__main__":
    asyncio.run(test_user_interface_system())
