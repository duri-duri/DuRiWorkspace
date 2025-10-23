#!/usr/bin/env python3
"""
Pattern Visualization Script

experience_stats.json 파일을 불러와서 감정-행동 별 성공률을 heatmap으로 시각화합니다.
"""

import json
import os
from datetime import datetime

import matplotlib
import numpy as np
import pandas as pd

# Headless 환경 감지 및 matplotlib 백엔드 설정
if not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")
    print("Headless environment detected. Using 'Agg' backend for matplotlib.")

import matplotlib.pyplot as plt
import seaborn as sns


class PatternVisualizer:
    """패턴 시각화 클래스"""

    def __init__(self, stats_file: str = "experience_stats.json"):
        """
        PatternVisualizer 초기화

        Args:
            stats_file (str): 통계 파일 경로
        """
        self.stats_file = stats_file
        self.stats_data = None
        self.success_rate_matrix = None

    def load_stats(self):
        """통계 데이터 로드"""
        try:
            if not os.path.exists(self.stats_file):
                print(f"통계 파일을 찾을 수 없습니다: {self.stats_file}")
                return False

            with open(self.stats_file, "r", encoding="utf-8") as f:
                self.stats_data = json.load(f)

            print(f"통계 데이터 로드 완료: {len(self.stats_data)}개 조합")
            return True

        except Exception as e:
            print(f"통계 데이터 로드 실패: {e}")
            return False

    def calculate_success_rates(self):
        """성공률 계산 및 매트릭스 생성"""
        if not self.stats_data:
            print("통계 데이터가 로드되지 않았습니다.")
            return False

        # 감정과 행동 목록 추출
        emotions = set()
        actions = set()

        for key, data in self.stats_data.items():
            emotions.add(data["emotion"])
            actions.add(data["action"])

        emotions = sorted(list(emotions))
        actions = sorted(list(actions))

        # 성공률 매트릭스 생성
        success_rate_matrix = np.zeros((len(emotions), len(actions)))

        for i, emotion in enumerate(emotions):
            for j, action in enumerate(actions):
                key = f"{emotion}_{action}"
                if key in self.stats_data:
                    data = self.stats_data[key]
                    success_rate = data["success_rate"] * 100  # 퍼센트로 변환
                    success_rate_matrix[i, j] = success_rate

        self.success_rate_matrix = success_rate_matrix
        self.emotions = emotions
        self.actions = actions

        print(f"성공률 계산 완료: {len(emotions)}개 감정, {len(actions)}개 행동")
        return True

    def create_heatmap(self, output_file: str = None):
        """성공률 heatmap 생성"""
        if self.success_rate_matrix is None:
            print("성공률 매트릭스가 계산되지 않았습니다.")
            return False

        # 폰트 설정 - 한글 대신 영어 사용
        plt.rcParams["font.family"] = "DejaVu Sans"
        plt.rcParams["axes.unicode_minus"] = False

        # 그래프 크기 설정
        fig, ax = plt.subplots(figsize=(14, 10))

        # Heatmap 생성
        sns.heatmap(
            self.success_rate_matrix,
            annot=True,  # 값 표시
            fmt=".1f",  # 소수점 1자리
            cmap="RdYlGn",  # 빨강-노랑-초록 색상맵
            vmin=0,  # 최소값
            vmax=100,  # 최대값
            cbar_kws={"label": "Success Rate (%)"},
            xticklabels=self.actions,
            yticklabels=self.emotions,
            ax=ax,
        )

        # 제목 및 레이블 설정 (영어로)
        plt.title("DuRi Emotion-Action Success Rate Heatmap", fontsize=16, pad=20)
        plt.xlabel("Action", fontsize=12)
        plt.ylabel("Emotion", fontsize=12)

        # x축 레이블 회전
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)

        # 레이아웃 조정
        plt.tight_layout()

        # 출력 파일명 설정
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"pattern_heatmap_{timestamp}.pdf"

        # PDF로 저장
        plt.savefig(output_file, format="pdf", dpi=300, bbox_inches="tight")
        print(f"Heatmap saved: {output_file}")

        # 그래프 표시 (GUI 환경이 아닌 경우 주석 처리)
        if matplotlib.get_backend() != "Agg":
            try:
                plt.show()
            except Exception as e:
                print(f"GUI display failed: {e}")
        else:
            print("Headless environment: Skipping plt.show()")

        return True

    def create_summary_statistics(self):
        """요약 통계 생성"""
        if not self.stats_data:
            print("통계 데이터가 로드되지 않았습니다.")
            return

        print("\n=== Summary Statistics ===")

        # 전체 통계
        total_combinations = len(self.stats_data)
        total_attempts = sum(data["total_count"] for data in self.stats_data.values())
        total_successes = sum(
            data["success_count"] for data in self.stats_data.values()
        )
        overall_success_rate = (
            (total_successes / total_attempts * 100) if total_attempts > 0 else 0
        )

        print(f"Total combinations: {total_combinations}")
        print(f"Total attempts: {total_attempts}")
        print(f"Total successes: {total_successes}")
        print(f"Overall success rate: {overall_success_rate:.1f}%")

        # 감정별 통계
        print("\n--- Emotion Statistics ---")
        emotion_stats = {}
        for data in self.stats_data.values():
            emotion = data["emotion"]
            if emotion not in emotion_stats:
                emotion_stats[emotion] = {"total": 0, "success": 0}
            emotion_stats[emotion]["total"] += data["total_count"]
            emotion_stats[emotion]["success"] += data["success_count"]

        for emotion, stats in sorted(emotion_stats.items()):
            success_rate = (
                (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            )
            print(
                f"{emotion}: {success_rate:.1f}% ({stats['success']}/{stats['total']})"
            )

        # 행동별 통계
        print("\n--- Action Statistics ---")
        action_stats = {}
        for data in self.stats_data.values():
            action = data["action"]
            if action not in action_stats:
                action_stats[action] = {"total": 0, "success": 0}
            action_stats[action]["total"] += data["total_count"]
            action_stats[action]["success"] += data["success_count"]

        for action, stats in sorted(action_stats.items()):
            success_rate = (
                (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            )
            print(
                f"{action}: {success_rate:.1f}% ({stats['success']}/{stats['total']})"
            )

        # 최고/최저 성공률 조합
        print("\n--- Best/Worst Success Rate Combinations ---")
        success_rates = []
        for key, data in self.stats_data.items():
            if data["total_count"] >= 3:  # 최소 3회 이상 시도된 조합만
                success_rates.append((key, data["success_rate"] * 100))

        if success_rates:
            success_rates.sort(key=lambda x: x[1], reverse=True)
            print(
                f"Best success rate: {success_rates[0][0]} ({success_rates[0][1]:.1f}%)"
            )
            print(
                f"Worst success rate: {success_rates[-1][0]} ({success_rates[-1][1]:.1f}%)"
            )

    def run_visualization(self, output_file: str = None):
        """전체 시각화 프로세스 실행"""
        print("=== DuRi Pattern Visualization Started ===")

        # 1. 통계 데이터 로드
        if not self.load_stats():
            return False

        # 2. 성공률 계산
        if not self.calculate_success_rates():
            return False

        # 3. 요약 통계 출력
        self.create_summary_statistics()

        # 4. Heatmap 생성
        if not self.create_heatmap(output_file):
            return False

        print("=== Visualization Completed ===")
        return True


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="DuRi Pattern Visualization")
    parser.add_argument(
        "--stats-file",
        default="experience_stats.json",
        help="Statistics file path (default: experience_stats.json)",
    )
    parser.add_argument("--output", help="Output PDF file path")

    args = parser.parse_args()

    # 시각화 실행
    visualizer = PatternVisualizer(args.stats_file)
    success = visualizer.run_visualization(args.output)

    if not success:
        print("Visualization failed")
        exit(1)


if __name__ == "__main__":
    main()
