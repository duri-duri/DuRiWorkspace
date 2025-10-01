#!/usr/bin/env python3
"""
Bias History Visualization Script

bias_history.json 파일을 읽어서 시간 흐름에 따른 편향 감지 히스토리를 시각화합니다.
"""

import os
import sys

# 1. Headless 환경: DISPLAY 없으면 Agg 백엔드로 설정 (pyplot import 전에!)
if "DISPLAY" not in os.environ:
    import matplotlib

    matplotlib.use("Agg")
    print("Headless 환경 감지: matplotlib backend를 'Agg'로 설정")

import argparse
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 2. 한글 폰트가 없으면 영어 폰트로 대체
TITLES_KO = {
    "timeline": "편향 감지 타임라인 (심각도별)",
    "scatter": "편향 타입별 신뢰도 분포",
    "type_dist": "편향 타입별 분포",
    "severity_dist": "편향 심각도별 분포",
    "hourly_heatmap": "요일/시간대별 편향 발생 빈도",
    "emotion_action_heatmap": "감정-행동별 편향 발생 빈도",
    "time": "시간",
    "bias_detection": "편향 감지",
    "confidence": "신뢰도",
    "severity": "심각도",
    "occurrence_count": "발생 횟수",
    "day": "요일",
    "hour": "시간",
    "emotion": "감정",
    "action": "행동",
}
TITLES_EN = {
    "timeline": "Bias Detection Timeline (by Severity)",
    "scatter": "Bias Type Confidence Distribution",
    "type_dist": "Bias Type Distribution",
    "severity_dist": "Bias Severity Distribution",
    "hourly_heatmap": "Bias Frequency by Day/Hour",
    "emotion_action_heatmap": "Bias Frequency by Emotion/Action",
    "time": "Time",
    "bias_detection": "Bias Detection",
    "confidence": "Confidence",
    "severity": "Severity",
    "occurrence_count": "Occurrence Count",
    "day": "Day",
    "hour": "Hour",
    "emotion": "Emotion",
    "action": "Action",
}


def setup_font_and_titles():
    try:
        plt.rcParams["font.family"] = [
            "DejaVu Sans",
            "NanumGothic",
            "Malgun Gothic",
            "AppleGothic",
            "sans-serif",
        ]
        plt.rcParams["axes.unicode_minus"] = False
        fig, ax = plt.subplots(figsize=(1, 1))
        ax.text(0.5, 0.5, "테스트", fontsize=12)
        plt.close()
        print("한글 폰트 설정 완료")
        return TITLES_KO, True
    except Exception as e:
        print(f"한글 폰트 설정 실패: {e}")
        print("영어로 대체합니다.")
        return TITLES_EN, False


TITLES, KOREAN_FONT_AVAILABLE = setup_font_and_titles()

# 스타일 설정
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


def is_interactive_backend():
    # Agg는 headless용, show()를 부르면 안 됨
    return plt.get_backend().lower() not in [
        "agg",
        "module://matplotlib_inline.backend_inline",
    ]


class BiasHistoryVisualizer:
    """편향 히스토리 시각화 클래스"""

    def __init__(self, bias_history_file: str = "bias_history.json"):
        """
        BiasHistoryVisualizer 초기화

        Args:
            bias_history_file (str): 편향 히스토리 파일 경로
        """
        self.bias_history_file = bias_history_file
        self.data = []
        self.df = None

        # 편향 심각도별 색상 매핑
        self.severity_colors = {
            "low": "#90EE90",  # 연한 녹색
            "medium": "#FFD700",  # 금색
            "high": "#FF8C00",  # 주황색
            "critical": "#FF0000",  # 빨간색
        }

        # 편향 타입별 마커 스타일
        self.bias_type_markers = {
            "emotion_bias": "o",
            "action_bias": "s",
            "temporal_bias": "^",
            "intensity_bias": "D",
            "pattern_bias": "v",
            "frequency_bias": "p",
        }

    def load_data(self) -> bool:
        """
        편향 히스토리 데이터 로드

        Returns:
            bool: 로드 성공 여부
        """
        try:
            if not os.path.exists(self.bias_history_file):
                print(f"경고: {self.bias_history_file} 파일이 존재하지 않습니다.")
                return False

            with open(self.bias_history_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            if not self.data:
                print("경고: 편향 히스토리 데이터가 비어있습니다.")
                return False

            print(f"편향 히스토리 데이터 로드 완료: {len(self.data)}개 항목")
            return True

        except Exception as e:
            print(f"데이터 로드 실패: {e}")
            return False

    def preprocess_data(self):
        """데이터 전처리 및 DataFrame 생성"""
        processed_data = []

        for entry in self.data:
            try:
                # 타임스탬프 파싱
                timestamp_str = entry.get("timestamp", "")
                if timestamp_str:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                else:
                    timestamp = datetime.now()

                # 편향 감지 결과 처리
                detections = entry.get("detections", [])
                if not detections:
                    continue

                for detection in detections:
                    processed_data.append(
                        {
                            "timestamp": timestamp,
                            "bias_type": detection.get("type", "unknown"),
                            "severity": detection.get("severity", "low"),
                            "confidence": detection.get("confidence", 0.0),
                            "description": detection.get("description", ""),
                            "emotion": entry.get("emotion", "unknown"),
                            "action": entry.get("action", "unknown"),
                        }
                    )

            except Exception as e:
                print(f"데이터 항목 처리 실패: {e}")
                continue

        if processed_data:
            self.df = pd.DataFrame(processed_data)
            self.df = self.df.sort_values("timestamp")
            print(f"데이터 전처리 완료: {len(self.df)}개 편향 감지")
        else:
            print("경고: 처리할 수 있는 편향 데이터가 없습니다.")

    def create_timeline_plot(
        self, save_path: str = "bias_timeline.png", show_plot: bool = True
    ):
        """
        시간 흐름에 따른 편향 타임라인 플롯 생성

        Args:
            save_path (str): 저장할 파일 경로
            show_plot (bool): 플롯 표시 여부
        """
        if self.df is None or self.df.empty:
            print("경고: 시각화할 데이터가 없습니다.")
            return

        # 그래프 크기 설정
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))

        # 1. 편향 심각도별 타임라인 (막대 그래프)
        self._create_severity_timeline(ax1)

        # 2. 편향 타입별 분포 (산점도)
        self._create_bias_type_scatter(ax2)

        # 레이아웃 조정
        plt.tight_layout()

        # 저장
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"타임라인 플롯 저장: {save_path}")

        if show_plot and is_interactive_backend():
            plt.show()
        else:
            plt.close()

    def _create_severity_timeline(self, ax):
        """편향 심각도별 타임라인 생성"""
        # 심각도별로 데이터 분리
        for severity in ["low", "medium", "high", "critical"]:
            severity_data = self.df[self.df["severity"] == severity]
            if not severity_data.empty:
                # 각 편향을 개별 막대로 표시
                for idx, row in severity_data.iterrows():
                    ax.bar(
                        row["timestamp"],
                        1,
                        color=self.severity_colors[severity],
                        alpha=0.7,
                        width=timedelta(hours=1),
                        label=severity if idx == severity_data.index[0] else "",
                    )

        # 축 설정
        ax.set_title(TITLES["timeline"], fontsize=14, fontweight="bold")
        ax.set_xlabel(TITLES["time"], fontsize=12)
        ax.set_ylabel(TITLES["bias_detection"], fontsize=12)

        # 시간축 포맷 설정
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        # 범례 설정
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(
            by_label.values(),
            by_label.keys(),
            title=TITLES["severity"],
            loc="upper right",
        )

        # 격자 설정
        ax.grid(True, alpha=0.3)

    def _create_bias_type_scatter(self, ax):
        """편향 타입별 산점도 생성"""
        # 편향 타입별로 다른 마커와 색상 사용
        for bias_type in self.df["bias_type"].unique():
            type_data = self.df[self.df["bias_type"] == bias_type]

            # 심각도별로 색상 구분
            for severity in ["low", "medium", "high", "critical"]:
                severity_data = type_data[type_data["severity"] == severity]
                if not severity_data.empty:
                    ax.scatter(
                        severity_data["timestamp"],
                        severity_data["confidence"],
                        c=[self.severity_colors[severity]],
                        marker=self.bias_type_markers.get(bias_type, "o"),
                        s=100,
                        alpha=0.7,
                        label=f"{bias_type} ({severity})",
                    )

        # 축 설정
        ax.set_title(TITLES["scatter"], fontsize=14, fontweight="bold")
        ax.set_xlabel(TITLES["time"], fontsize=12)
        ax.set_ylabel(TITLES["confidence"], fontsize=12)

        # 시간축 포맷 설정
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        # 범례 설정
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        # 격자 설정
        ax.grid(True, alpha=0.3)

    def create_summary_plots(self, save_dir: str = ".", show_plot: bool = True):
        """
        요약 플롯들 생성

        Args:
            save_dir (str): 저장할 디렉토리
            show_plot (bool): 플롯 표시 여부
        """
        if self.df is None or self.df.empty:
            print("경고: 시각화할 데이터가 없습니다.")
            return

        # 1. 편향 타입별 분포 (파이 차트)
        self._create_bias_type_pie(save_dir, show_plot)

        # 2. 심각도별 분포 (막대 차트)
        self._create_severity_bar(save_dir, show_plot)

        # 3. 시간대별 편향 발생 빈도 (히트맵)
        self._create_hourly_heatmap(save_dir, show_plot)

        # 4. 감정-행동별 편향 분포
        self._create_emotion_action_heatmap(save_dir, show_plot)

    def _create_bias_type_pie(self, save_dir: str, show_plot: bool):
        """편향 타입별 분포 파이 차트"""
        bias_type_counts = self.df["bias_type"].value_counts()

        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(bias_type_counts)))

        wedges, texts, autotexts = ax.pie(
            bias_type_counts.values,
            labels=bias_type_counts.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )

        ax.set_title(TITLES["type_dist"], fontsize=14, fontweight="bold")

        # 저장
        save_path = os.path.join(save_dir, "bias_type_distribution.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"편향 타입 분포 차트 저장: {save_path}")

        if show_plot and is_interactive_backend():
            plt.show()
        else:
            plt.close()

    def _create_severity_bar(self, save_dir: str, show_plot: bool):
        """심각도별 분포 막대 차트"""
        severity_counts = self.df["severity"].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = [self.severity_colors[sev] for sev in severity_counts.index]

        bars = ax.bar(
            severity_counts.index, severity_counts.values, color=colors, alpha=0.7
        )

        # 값 표시
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
            )

        ax.set_title(TITLES["severity_dist"], fontsize=14, fontweight="bold")
        ax.set_xlabel(TITLES["severity"], fontsize=12)
        ax.set_ylabel(TITLES["occurrence_count"], fontsize=12)

        # 저장
        save_path = os.path.join(save_dir, "bias_severity_distribution.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"심각도 분포 차트 저장: {save_path}")

        if show_plot and is_interactive_backend():
            plt.show()
        else:
            plt.close()

    def _create_hourly_heatmap(self, save_dir: str, show_plot: bool):
        """시간대별 편향 발생 빈도 히트맵"""
        # 시간대별 데이터 생성
        self.df["hour"] = self.df["timestamp"].dt.hour
        self.df["day_of_week"] = self.df["timestamp"].dt.day_name()

        # 요일별, 시간대별 편향 발생 빈도
        hourly_data = (
            self.df.groupby(["day_of_week", "hour"]).size().unstack(fill_value=0)
        )

        # 요일 순서 정렬
        day_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        hourly_data = hourly_data.reindex(
            [day for day in day_order if day in hourly_data.index]
        )

        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(hourly_data, annot=True, fmt="d", cmap="YlOrRd", ax=ax)

        ax.set_title(TITLES["hourly_heatmap"], fontsize=14, fontweight="bold")
        ax.set_xlabel(TITLES["hour"], fontsize=12)
        ax.set_ylabel(TITLES["day"], fontsize=12)

        # 저장
        save_path = os.path.join(save_dir, "bias_hourly_heatmap.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"시간대별 히트맵 저장: {save_path}")

        if show_plot and is_interactive_backend():
            plt.show()
        else:
            plt.close()

    def _create_emotion_action_heatmap(self, save_dir: str, show_plot: bool):
        """감정-행동별 편향 분포 히트맵"""
        # 감정-행동 조합별 편향 발생 빈도
        emotion_action_counts = (
            self.df.groupby(["emotion", "action"]).size().unstack(fill_value=0)
        )

        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(emotion_action_counts, annot=True, fmt="d", cmap="Blues", ax=ax)

        ax.set_title(TITLES["emotion_action_heatmap"], fontsize=14, fontweight="bold")
        ax.set_xlabel(TITLES["action"], fontsize=12)
        ax.set_ylabel(TITLES["emotion"], fontsize=12)

        # 저장
        save_path = os.path.join(save_dir, "bias_emotion_action_heatmap.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"감정-행동 히트맵 저장: {save_path}")

        if show_plot and is_interactive_backend():
            plt.show()
        else:
            plt.close()

    def print_summary_statistics(self):
        """요약 통계 출력"""
        if self.df is None or self.df.empty:
            print("출력할 데이터가 없습니다.")
            return

        print("\n" + "=" * 50)
        if KOREAN_FONT_AVAILABLE:
            print("편향 히스토리 요약 통계")
        else:
            print("Bias History Summary Statistics")
        print("=" * 50)

        # 기본 통계
        if KOREAN_FONT_AVAILABLE:
            print(f"총 편향 감지 횟수: {len(self.df)}")
            print(
                f"분석 기간: {self.df['timestamp'].min()} ~ {self.df['timestamp'].max()}"
            )

            # 편향 타입별 통계
            print(f"\n편향 타입별 분포:")
            bias_type_stats = self.df["bias_type"].value_counts()
            for bias_type, count in bias_type_stats.items():
                percentage = (count / len(self.df)) * 100
                print(f"  {bias_type}: {count}회 ({percentage:.1f}%)")

            # 심각도별 통계
            print(f"\n심각도별 분포:")
            severity_stats = self.df["severity"].value_counts()
            for severity, count in severity_stats.items():
                percentage = (count / len(self.df)) * 100
                print(f"  {severity}: {count}회 ({percentage:.1f}%)")

            # 평균 신뢰도
            avg_confidence = self.df["confidence"].mean()
            print(f"\n평균 신뢰도: {avg_confidence:.2f}")

            # 가장 빈번한 감정-행동 조합
            print(f"\n가장 빈번한 감정-행동 조합:")
            emotion_action_stats = (
                self.df.groupby(["emotion", "action"])
                .size()
                .sort_values(ascending=False)
            )
            for (emotion, action), count in emotion_action_stats.head(5).items():
                print(f"  {emotion} -> {action}: {count}회")
        else:
            print(f"Total bias detections: {len(self.df)}")
            print(
                f"Analysis period: {self.df['timestamp'].min()} ~ {self.df['timestamp'].max()}"
            )

            # 편향 타입별 통계
            print(f"\nBias type distribution:")
            bias_type_stats = self.df["bias_type"].value_counts()
            for bias_type, count in bias_type_stats.items():
                percentage = (count / len(self.df)) * 100
                print(f"  {bias_type}: {count} times ({percentage:.1f}%)")

            # 심각도별 통계
            print(f"\nSeverity distribution:")
            severity_stats = self.df["severity"].value_counts()
            for severity, count in severity_stats.items():
                percentage = (count / len(self.df)) * 100
                print(f"  {severity}: {count} times ({percentage:.1f}%)")

            # 평균 신뢰도
            avg_confidence = self.df["confidence"].mean()
            print(f"\nAverage confidence: {avg_confidence:.2f}")

            # 가장 빈번한 감정-행동 조합
            print(f"\nMost frequent emotion-action combinations:")
            emotion_action_stats = (
                self.df.groupby(["emotion", "action"])
                .size()
                .sort_values(ascending=False)
            )
            for (emotion, action), count in emotion_action_stats.head(5).items():
                print(f"  {emotion} -> {action}: {count} times")

        print("=" * 50)


def create_sample_bias_history():
    """샘플 편향 히스토리 데이터 생성 (테스트용)"""
    import numpy as np

    sample_data = []
    base_time = datetime.now() - timedelta(days=7)

    bias_types = [
        "emotion_bias",
        "action_bias",
        "temporal_bias",
        "intensity_bias",
        "pattern_bias",
        "frequency_bias",
    ]
    severities = ["low", "medium", "high", "critical"]
    emotions = ["happy", "sad", "angry", "frustrated", "curious"]
    actions = ["reflect", "wait", "console", "observe"]

    for i in range(50):
        timestamp = base_time + timedelta(hours=np.random.randint(0, 168))

        # 여러 편향 감지
        detections = []
        num_detections = np.random.randint(1, 4)

        for j in range(num_detections):
            detection = {
                "type": np.random.choice(bias_types),
                "severity": np.random.choice(severities, p=[0.4, 0.3, 0.2, 0.1]),
                "confidence": np.random.uniform(0.3, 0.95),
                "description": f"Sample bias detection {j+1}",
                "recommendations": ["Increase exploration", "Adjust parameters"],
            }
            detections.append(detection)

        entry = {
            "timestamp": timestamp.isoformat(),
            "emotion": np.random.choice(emotions),
            "action": np.random.choice(actions),
            "detections": detections,
        }
        sample_data.append(entry)

    # 시간순 정렬
    sample_data.sort(key=lambda x: x["timestamp"])

    with open("bias_history.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)

    print("샘플 편향 히스토리 데이터 생성 완료: bias_history.json")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="편향 히스토리 시각화")
    parser.add_argument(
        "--file",
        "-f",
        default="bias_history.json",
        help="편향 히스토리 파일 경로 (기본값: bias_history.json)",
    )
    parser.add_argument(
        "--output", "-o", default=".", help="출력 디렉토리 (기본값: 현재 디렉토리)"
    )
    parser.add_argument(
        "--no-show", action="store_true", help="플롯을 화면에 표시하지 않음"
    )
    parser.add_argument("--create-sample", action="store_true", help="샘플 데이터 생성")

    args = parser.parse_args()

    # 샘플 데이터 생성
    if args.create_sample:
        create_sample_bias_history()
        return

    # 시각화 실행
    visualizer = BiasHistoryVisualizer(args.file)

    if not visualizer.load_data():
        print(
            "데이터 로드 실패. 샘플 데이터를 생성하려면 --create-sample 옵션을 사용하세요."
        )
        return

    visualizer.preprocess_data()

    if visualizer.df is not None and not visualizer.df.empty:
        # 요약 통계 출력
        visualizer.print_summary_statistics()

        # 타임라인 플롯 생성
        timeline_path = os.path.join(args.output, "bias_timeline.png")
        visualizer.create_timeline_plot(timeline_path, not args.no_show)

        # 요약 플롯들 생성
        visualizer.create_summary_plots(args.output, not args.no_show)

        if KOREAN_FONT_AVAILABLE:
            print(
                f"\n시각화 완료! 결과 파일들이 {args.output} 디렉토리에 저장되었습니다."
            )
        else:
            print(
                f"\nVisualization completed! Result files saved in {args.output} directory."
            )
    else:
        print("시각화할 데이터가 없습니다.")


if __name__ == "__main__":
    # numpy import (히트맵에서 사용)
    import numpy as np

    main()
