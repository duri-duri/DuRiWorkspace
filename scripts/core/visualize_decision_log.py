#!/usr/bin/env python3
"""
Decision Log Visualization Script

decision_log.json 파일을 불러와서 감정-행동 조합별 판단 결과를 시간 순으로 시각화합니다.
"""

import json
import os
from datetime import datetime, timedelta

import matplotlib
import numpy as np
import pandas as pd

# Headless 환경 감지 및 matplotlib 백엔드 설정
if not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")
    print("Headless environment detected. Using 'Agg' backend for matplotlib.")

import matplotlib.pyplot as plt
import seaborn as sns

from duri_common.config.config import Config


class DecisionLogVisualizer:
    """판단 로그 시각화 클래스"""

    def __init__(self, log_file: str = "decision_log.json"):
        """
        DecisionLogVisualizer 초기화

        Args:
            log_file (str): 로그 파일 경로
        """
        self.log_file = log_file
        self.decision_data = None
        self.df = None

    def load_decision_log(self):
        """판단 로그 데이터 로드"""
        try:
            if not os.path.exists(self.log_file):
                print(f"판단 로그 파일을 찾을 수 없습니다: {self.log_file}")
                return False

            # JSON Lines 형식으로 읽기
            data = []
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))

            self.decision_data = data
            self.df = pd.DataFrame(data)

            # 타임스탬프를 datetime으로 변환
            self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
            self.df["date"] = self.df["timestamp"].dt.date

            print(f"판단 로그 데이터 로드 완료: {len(data)}개 기록")
            return True

        except Exception as e:
            print(f"판단 로그 데이터 로드 실패: {e}")
            return False

    def create_timeline_visualization(self, output_file: str = None):
        """시간 순 판단 결과 시각화"""
        if self.df is None or self.df.empty:
            print("판단 로그 데이터가 로드되지 않았습니다.")
            return False

        # 폰트 설정
        plt.rcParams["font.family"] = "DejaVu Sans"
        plt.rcParams["axes.unicode_minus"] = False

        # 그래프 크기 설정
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

        # 1. 시간 순 성공/실패 점 그래프
        success_data = self.df[self.df["success"] == True]
        fail_data = self.df[self.df["success"] == False]

        ax1.scatter(
            success_data["timestamp"],
            success_data["emotion"] + "_" + success_data["action"],
            c="green",
            alpha=0.7,
            s=50,
            label="Success",
            marker="o",
        )
        ax1.scatter(
            fail_data["timestamp"],
            fail_data["emotion"] + "_" + fail_data["action"],
            c="red",
            alpha=0.7,
            s=50,
            label="Fail",
            marker="x",
        )

        ax1.set_title("Decision Results Timeline", fontsize=14, pad=20)
        ax1.set_xlabel("Time", fontsize=12)
        ax1.set_ylabel("Emotion-Action Combination", fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # x축 레이블 회전
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

        # 2. 성공률 변화 추세 그래프
        # 일별 성공률 계산
        daily_success_rate = (
            self.df.groupby("date").agg({"success": ["count", "sum"]}).reset_index()
        )
        daily_success_rate.columns = ["date", "total_count", "success_count"]
        daily_success_rate["success_rate"] = (
            daily_success_rate["success_count"] / daily_success_rate["total_count"]
        )

        # 이동평균 계산 (3일)
        daily_success_rate["success_rate_ma"] = (
            daily_success_rate["success_rate"].rolling(window=3, min_periods=1).mean()
        )

        ax2.plot(
            daily_success_rate["date"],
            daily_success_rate["success_rate"],
            "o-",
            alpha=0.7,
            label="Daily Success Rate",
            color="blue",
        )
        ax2.plot(
            daily_success_rate["date"],
            daily_success_rate["success_rate_ma"],
            "-",
            linewidth=2,
            label="3-Day Moving Average",
            color="red",
        )

        ax2.set_title("Success Rate Trend Over Time", fontsize=14, pad=20)
        ax2.set_xlabel("Date", fontsize=12)
        ax2.set_ylabel("Success Rate", fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)

        # x축 레이블 회전
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

        # 레이아웃 조정
        plt.tight_layout()

        # 출력 파일명 설정
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"decision_timeline_{timestamp}.pdf"

        # PDF로 저장
        plt.savefig(output_file, format="pdf", dpi=300, bbox_inches="tight")
        print(f"Timeline visualization saved: {output_file}")

        # 그래프 표시 (GUI 환경이 아닌 경우 주석 처리)
        if matplotlib.get_backend() != "Agg":
            try:
                plt.show()
            except Exception as e:
                print(f"GUI display failed: {e}")
        else:
            print("Headless environment: Skipping plt.show()")

        return True

    def create_emotion_action_heatmap(self, output_file: str = None):
        """감정-행동 조합별 성공률 히트맵"""
        if self.df is None or self.df.empty:
            print("판단 로그 데이터가 로드되지 않았습니다.")
            return False

        # 감정-행동 조합별 성공률 계산
        success_matrix = (
            self.df.groupby(["emotion", "action"])
            .agg({"success": ["count", "sum"]})
            .reset_index()
        )
        success_matrix.columns = ["emotion", "action", "total_count", "success_count"]
        success_matrix["success_rate"] = (
            success_matrix["success_count"] / success_matrix["total_count"]
        )

        # 피벗 테이블 생성
        pivot_data = success_matrix.pivot(
            index="emotion", columns="action", values="success_rate"
        )

        # 그래프 생성
        plt.figure(figsize=(12, 8))

        sns.heatmap(
            pivot_data,
            annot=True,
            fmt=".2f",
            cmap="RdYlGn",
            vmin=0,
            vmax=1,
            cbar_kws={"label": "Success Rate"},
            ax=plt.gca(),
        )

        plt.title("Emotion-Action Success Rate Heatmap", fontsize=16, pad=20)
        plt.xlabel("Action", fontsize=12)
        plt.ylabel("Emotion", fontsize=12)

        # 레이아웃 조정
        plt.tight_layout()

        # 출력 파일명 설정
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"decision_heatmap_{timestamp}.pdf"

        # PDF로 저장
        plt.savefig(output_file, format="pdf", dpi=300, bbox_inches="tight")
        print(f"Heatmap saved: {output_file}")

        return True

    def create_summary_statistics(self):
        """요약 통계 생성"""
        if self.df is None or self.df.empty:
            print("판단 로그 데이터가 로드되지 않았습니다.")
            return

        print("\n=== Decision Log Summary Statistics ===")

        # 전체 통계
        total_decisions = len(self.df)
        successful_decisions = self.df["success"].sum()
        overall_success_rate = (
            successful_decisions / total_decisions if total_decisions > 0 else 0
        )

        print(f"Total decisions: {total_decisions}")
        print(f"Successful decisions: {successful_decisions}")
        print(f"Overall success rate: {overall_success_rate:.1%}")

        # 감정별 통계
        print("\n--- Emotion Statistics ---")
        emotion_stats = (
            self.df.groupby("emotion").agg({"success": ["count", "sum"]}).reset_index()
        )
        emotion_stats.columns = ["emotion", "total_count", "success_count"]
        emotion_stats["success_rate"] = (
            emotion_stats["success_count"] / emotion_stats["total_count"]
        )

        for _, row in emotion_stats.sort_values(
            "success_rate", ascending=False
        ).iterrows():
            print(
                f"{row['emotion']}: {row['success_rate']:.1%} ({row['success_count']}/{row['total_count']})"
            )

        # 행동별 통계
        print("\n--- Action Statistics ---")
        action_stats = (
            self.df.groupby("action").agg({"success": ["count", "sum"]}).reset_index()
        )
        action_stats.columns = ["action", "total_count", "success_count"]
        action_stats["success_rate"] = (
            action_stats["success_count"] / action_stats["total_count"]
        )

        for _, row in action_stats.sort_values(
            "success_rate", ascending=False
        ).iterrows():
            print(
                f"{row['action']}: {row['success_rate']:.1%} ({row['success_count']}/{row['total_count']})"
            )

        # 시간별 통계
        print("\n--- Time-based Statistics ---")
        if len(self.df) > 1:
            time_span = self.df["timestamp"].max() - self.df["timestamp"].min()
            decisions_per_day = (
                total_decisions / time_span.days if time_span.days > 0 else 0
            )
            print(f"Time span: {time_span.days} days")
            print(f"Decisions per day: {decisions_per_day:.1f}")

    def run_visualization(self, output_prefix: str = None):
        """전체 시각화 프로세스 실행"""
        print("=== Decision Log Visualization Started ===")

        # 1. 판단 로그 데이터 로드
        if not self.load_decision_log():
            return False

        # 2. 요약 통계 출력
        self.create_summary_statistics()

        # 3. 타임라인 시각화
        if output_prefix:
            timeline_file = f"{output_prefix}_timeline.pdf"
        else:
            timeline_file = None

        if not self.create_timeline_visualization(timeline_file):
            return False

        # 4. 히트맵 시각화
        if output_prefix:
            heatmap_file = f"{output_prefix}_heatmap.pdf"
        else:
            heatmap_file = None

        if not self.create_emotion_action_heatmap(heatmap_file):
            return False

        print("=== Visualization Completed ===")
        return True


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Decision Log Visualization")
    parser.add_argument(
        "--log-file",
        default="decision_log.json",
        help="Decision log file path (default: decision_log.json)",
    )
    parser.add_argument("--output-prefix", help="Output file prefix")

    args = parser.parse_args()

    # 시각화 실행
    visualizer = DecisionLogVisualizer(args.log_file)
    success = visualizer.run_visualization(args.output_prefix)

    if not success:
        print("Visualization failed")
        exit(1)


if __name__ == "__main__":
    main()
