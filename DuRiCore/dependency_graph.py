#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 의존성 그래프 시스템

이 모듈은 DuRi 시스템의 모듈 간 의존성을 관리하는 의존성 그래프 시스템입니다.
위상 정렬을 통한 로드 순서 결정과 사이클 감지 기능을 제공합니다.

주요 기능:
- 의존성 추가/제거
- 위상 정렬을 통한 로드 순서 결정
- 사이클 감지
- 의존성 분석
"""

import logging
from collections import defaultdict, deque
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class DependencyGraph:
    """의존성 그래프"""

    def __init__(self):
        self.graph: Dict[str, List[str]] = defaultdict(list)
        self.reverse_graph: Dict[str, List[str]] = defaultdict(list)
        self.in_degree: Dict[str, int] = defaultdict(int)

    def add_dependency(self, module: str, depends_on: str) -> None:
        """의존성 추가"""
        if depends_on not in self.graph[module]:
            self.graph[module].append(depends_on)
            self.reverse_graph[depends_on].append(module)
            self.in_degree[module] += 1
            logger.debug(f"의존성 추가: {module} -> {depends_on}")

    def remove_dependency(self, module: str, depends_on: str) -> None:
        """의존성 제거"""
        if depends_on in self.graph[module]:
            self.graph[module].remove(depends_on)
            self.reverse_graph[depends_on].remove(module)
            self.in_degree[module] -= 1
            logger.debug(f"의존성 제거: {module} -> {depends_on}")

    def get_load_order(self) -> List[str]:
        """위상 정렬을 통한 로드 순서 결정"""
        result = []
        queue = deque()

        # 진입 차수가 0인 노드들을 큐에 추가
        for module in self.graph:
            if self.in_degree[module] == 0:
                queue.append(module)

        while queue:
            current = queue.popleft()
            result.append(current)

            # 현재 노드에 의존하는 노드들의 진입 차수 감소
            for dependent in self.reverse_graph[current]:
                self.in_degree[dependent] -= 1
                if self.in_degree[dependent] == 0:
                    queue.append(dependent)

        # 사이클이 있는 경우 감지
        if len(result) != len(self.graph):
            raise ValueError("의존성 사이클이 감지되었습니다!")

        return result

    def has_cycle(self) -> bool:
        """사이클 존재 여부 확인"""
        try:
            self.get_load_order()
            return False
        except ValueError:
            return True

    def get_dependencies(self, module: str) -> List[str]:
        """모듈의 의존성 목록 반환"""
        return self.graph.get(module, [])

    def get_dependents(self, module: str) -> List[str]:
        """모듈에 의존하는 모듈 목록 반환"""
        return self.reverse_graph.get(module, [])

    def get_all_dependencies(self, module: str) -> Set[str]:
        """모듈의 모든 의존성 (직접 + 간접) 반환"""
        dependencies = set()
        visited = set()

        def dfs(current: str):
            if current in visited:
                return
            visited.add(current)

            for dep in self.graph.get(current, []):
                dependencies.add(dep)
                dfs(dep)

        dfs(module)
        return dependencies

    def get_affected_modules(self, module: str) -> List[str]:
        """모듈 변경 시 영향을 받는 모듈 목록 반환"""
        affected = []
        visited = set()

        def dfs(current: str):
            if current in visited:
                return
            visited.add(current)
            affected.append(current)

            for dependent in self.reverse_graph.get(current, []):
                dfs(dependent)

        dfs(module)
        return affected

    def is_dependent(self, module: str, depends_on: str) -> bool:
        """module이 depends_on에 의존하는지 확인"""
        return depends_on in self.get_all_dependencies(module)

    def get_cycle_path(self) -> List[str]:
        """사이클 경로 반환 (사이클이 있는 경우)"""
        if not self.has_cycle():
            return []

        # DFS를 통한 사이클 탐지
        visited = set()
        rec_stack = set()
        cycle_path = []

        def dfs(current: str, path: List[str]):
            visited.add(current)
            rec_stack.add(current)
            path.append(current)

            for neighbor in self.graph.get(current, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # 사이클 발견
                    cycle_start = path.index(neighbor)
                    cycle_path.extend(path[cycle_start:])
                    return True

            rec_stack.remove(current)
            path.pop()
            return False

        for module in self.graph:
            if module not in visited:
                if dfs(module, []):
                    break

        return cycle_path

    def get_statistics(self) -> Dict[str, any]:
        """의존성 그래프 통계"""
        total_modules = len(self.graph)
        total_dependencies = sum(len(deps) for deps in self.graph.values())

        # 진입 차수 분포
        in_degree_dist = defaultdict(int)
        for module in self.graph:
            in_degree_dist[self.in_degree[module]] += 1

        # 진출 차수 분포
        out_degree_dist = defaultdict(int)
        for deps in self.graph.values():
            out_degree_dist[len(deps)] += 1

        return {
            "total_modules": total_modules,
            "total_dependencies": total_dependencies,
            "average_dependencies": (
                total_dependencies / total_modules if total_modules > 0 else 0
            ),
            "in_degree_distribution": dict(in_degree_dist),
            "out_degree_distribution": dict(out_degree_dist),
            "has_cycle": self.has_cycle(),
            "cycle_path": self.get_cycle_path() if self.has_cycle() else [],
        }

    def visualize(self) -> str:
        """의존성 그래프 시각화 (텍스트 기반)"""
        lines = ["Dependency Graph:"]
        lines.append("=" * 50)

        for module, deps in self.graph.items():
            if deps:
                lines.append(f"{module} -> {', '.join(deps)}")
            else:
                lines.append(f"{module} (no dependencies)")

        lines.append("=" * 50)

        # 통계 정보 추가
        stats = self.get_statistics()
        lines.append(f"Total modules: {stats['total_modules']}")
        lines.append(f"Total dependencies: {stats['total_dependencies']}")
        lines.append(f"Average dependencies: {stats['average_dependencies']:.2f}")
        lines.append(f"Has cycle: {stats['has_cycle']}")

        return "\n".join(lines)
