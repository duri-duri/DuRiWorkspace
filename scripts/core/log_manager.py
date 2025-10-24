#!/usr/bin/env python3
"""
로그 파일 관리 유틸리티
"""

import glob
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

from duri_common.config.config import Config

config = Config()


class LogManager:
    """로그 파일 관리자"""

    def __init__(self, log_dir: str = None):
        """
        LogManager 초기화

        Args:
            log_dir (str, optional): 로그 디렉토리 경로
        """
        self.log_dir = log_dir or config.get_log_dir()

    def get_log_files(self, date: str = None, log_type: str = None) -> List[str]:
        """
        로그 파일 목록 조회

        Args:
            date (str, optional): 특정 날짜 (YYYY-MM-DD)
            log_type (str, optional): 로그 타입 (requests, responses)

        Returns:
            List[str]: 로그 파일 경로 목록
        """
        pattern = os.path.join(self.log_dir, "*_emotion_*.json")

        if date:
            pattern = os.path.join(self.log_dir, f"{date}_emotion_*.json")

        if log_type:
            pattern = os.path.join(self.log_dir, f"*_emotion_{log_type}.json")

        if date and log_type:
            pattern = os.path.join(self.log_dir, f"{date}_emotion_{log_type}.json")

        return glob.glob(pattern)

    def read_log_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        로그 파일 읽기

        Args:
            file_path (str): 로그 파일 경로

        Returns:
            List[Dict]: 로그 엔트리 목록
        """
        entries = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception as e:
            print(f"로그 파일 읽기 실패: {file_path} - {e}")

        return entries

    def get_daily_stats(self, date: str) -> Dict[str, Any]:
        """
        특정 날짜의 로그 통계 조회

        Args:
            date (str): 날짜 (YYYY-MM-DD)

        Returns:
            Dict: 통계 정보
        """
        request_files = self.get_log_files(date, "requests")
        response_files = self.get_log_files(date, "responses")

        stats = {
            "date": date,
            "request_files": len(request_files),
            "response_files": len(response_files),
            "total_requests": 0,
            "total_responses": 0,
            "success_count": 0,
            "error_count": 0,
            "avg_processing_time": 0.0,
        }

        # 요청 통계
        for file_path in request_files:
            entries = self.read_log_file(file_path)
            stats["total_requests"] += len(entries)

        # 응답 통계
        processing_times = []
        for file_path in response_files:
            entries = self.read_log_file(file_path)
            stats["total_responses"] += len(entries)

            for entry in entries:
                response_data = entry.get("response_data", {})
                status = response_data.get("status", "unknown")

                if status == "success":
                    stats["success_count"] += 1
                elif status == "error":
                    stats["error_count"] += 1

                # 처리 시간 수집
                if "processing_time" in response_data:
                    processing_times.append(response_data["processing_time"])

        # 평균 처리 시간 계산
        if processing_times:
            stats["avg_processing_time"] = sum(processing_times) / len(processing_times)

        return stats

    def get_date_range_stats(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        날짜 범위의 로그 통계 조회

        Args:
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)

        Returns:
            List[Dict]: 날짜별 통계 목록
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        stats_list = []
        current = start

        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            stats = self.get_daily_stats(date_str)
            stats_list.append(stats)
            current += timedelta(days=1)

        return stats_list

    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
        """
        오래된 로그 파일 정리

        Args:
            days_to_keep (int): 보관할 일수

        Returns:
            int: 삭제된 파일 수
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0

        all_log_files = self.get_log_files()

        for file_path in all_log_files:
            try:
                # 파일명에서 날짜 추출
                filename = os.path.basename(file_path)
                date_str = filename.split("_")[0]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff_date:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"삭제됨: {file_path}")

            except Exception as e:
                print(f"파일 삭제 실패: {file_path} - {e}")

        return deleted_count

    def export_logs(self, start_date: str, end_date: str, output_file: str) -> bool:
        """
        로그 데이터 내보내기

        Args:
            start_date (str): 시작 날짜 (YYYY-MM-DD)
            end_date (str): 종료 날짜 (YYYY-MM-DD)
            output_file (str): 출력 파일 경로

        Returns:
            bool: 내보내기 성공 여부
        """
        try:
            all_entries = []

            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            current = start

            while current <= end:
                date_str = current.strftime("%Y-%m-%d")

                # 요청 로그 읽기
                request_files = self.get_log_files(date_str, "requests")
                for file_path in request_files:
                    entries = self.read_log_file(file_path)
                    all_entries.extend(entries)

                # 응답 로그 읽기
                response_files = self.get_log_files(date_str, "responses")
                for file_path in response_files:
                    entries = self.read_log_file(file_path)
                    all_entries.extend(entries)

                current += timedelta(days=1)

            # JSON 파일로 저장
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_entries, f, indent=2, ensure_ascii=False)

            print(f"로그 내보내기 완료: {output_file} ({len(all_entries)}개 엔트리)")
            return True

        except Exception as e:
            print(f"로그 내보내기 실패: {e}")
            return False


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="DuRi 로그 파일 관리")
    parser.add_argument(
        "--action",
        choices=["stats", "cleanup", "export"],
        required=True,
        help="실행할 작업",
    )
    parser.add_argument("--date", help="특정 날짜 (YYYY-MM-DD)")
    parser.add_argument("--start-date", help="시작 날짜 (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="종료 날짜 (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=30, help="보관할 일수 (cleanup용)")
    parser.add_argument("--output", help="출력 파일 경로 (export용)")

    args = parser.parse_args()

    log_manager = LogManager()

    if args.action == "stats":
        if args.date:
            stats = log_manager.get_daily_stats(args.date)
            print(f"=== {args.date} 로그 통계 ===")
            print(f"요청 파일: {stats['request_files']}개")
            print(f"응답 파일: {stats['response_files']}개")
            print(f"총 요청: {stats['total_requests']}개")
            print(f"총 응답: {stats['total_responses']}개")
            print(f"성공: {stats['success_count']}개")
            print(f"실패: {stats['error_count']}개")
            print(f"평균 처리시간: {stats['avg_processing_time']:.3f}초")
        elif args.start_date and args.end_date:
            stats_list = log_manager.get_date_range_stats(args.start_date, args.end_date)
            print(f"=== {args.start_date} ~ {args.end_date} 로그 통계 ===")
            for stats in stats_list:
                print(f"{stats['date']}: 요청 {stats['total_requests']}개, 응답 {stats['total_responses']}개")
        else:
            print("--date 또는 --start-date, --end-date를 지정해주세요.")

    elif args.action == "cleanup":
        deleted_count = log_manager.cleanup_old_logs(args.days)
        print(f"정리 완료: {deleted_count}개 파일 삭제됨")

    elif args.action == "export":
        if not all([args.start_date, args.end_date, args.output]):
            print("--start-date, --end-date, --output를 모두 지정해주세요.")
            return

        success = log_manager.export_logs(args.start_date, args.end_date, args.output)
        if success:
            print("내보내기 완료")
        else:
            print("내보내기 실패")


if __name__ == "__main__":
    main()
