#!/usr/bin/env python3
"""
Summary Report Generation for Emotion Analysis
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from duri_common.logger import get_logger
from .summary_loader import DataLoader
from .summary_analyzer import EmotionSummaryAnalyzer

logger = get_logger("duri_core.visualize.reporter")


class SummaryReporter:
    """요약 보고서 생성기"""
    
    def __init__(self, loader: DataLoader, analyzer: EmotionSummaryAnalyzer):
        """
        초기화
        
        Args:
            loader (DataLoader): 데이터 로더
            analyzer (EmotionSummaryAnalyzer): 분석기
        """
        self.loader = loader
        self.analyzer = analyzer
    
    def generate_summary_report(self) -> Dict:
        """
        종합 요약 보고서 생성
        
        Returns:
            Dict: 종합 분석 보고서
        """
        # 각종 분석 수행
        level_analysis = self.analyzer.analyze_by_emotion_level()
        evolution_analysis = self.analyzer.analyze_evolution_by_level()
        detailed_analysis = self.analyzer.get_detailed_emotion_analysis()
        action_analysis = self.analyzer.get_action_analysis()
        pair_analysis = self.analyzer.get_emotion_action_pair_analysis()
        
        # 데이터 요약 정보
        data_summary = self.loader.get_data_summary()
        
        # 요약 통계
        overview = self._create_overview(level_analysis, data_summary)
        
        # 보고서 구성
        report = {
            "overview": overview,
            "level_analysis": level_analysis,
            "evolution_analysis": evolution_analysis,
            "detailed_analysis": detailed_analysis,
            "action_analysis": action_analysis,
            "pair_analysis": pair_analysis,
            "data_summary": data_summary,
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info("종합 요약 보고서 생성 완료")
        return report
    
    def _create_overview(self, level_analysis: Dict, data_summary: Dict) -> Dict:
        """
        개요 정보 생성
        
        Args:
            level_analysis (Dict): 레벨별 분석 결과
            data_summary (Dict): 데이터 요약 정보
        
        Returns:
            Dict: 개요 정보
        """
        total_stats = level_analysis.get("total", {})
        
        return {
            "total_emotions_processed": total_stats.get("total", 0),
            "total_success_rate": round(total_stats.get("success_rate", 0), 2),
            "level_1_count": level_analysis.get("level_1", {}).get("emotion_count", 0),
            "level_2_count": level_analysis.get("level_2", {}).get("emotion_count", 0),
            "level_3_count": level_analysis.get("level_3", {}).get("emotion_count", 0),
            "unknown_count": level_analysis.get("unknown", {}).get("emotion_count", 0),
            "total_emotions": data_summary.get("stats", {}).get("emotion_count", 0),
            "total_actions": data_summary.get("stats", {}).get("action_count", 0),
            "total_evolution_entries": data_summary.get("evolution", {}).get("total_entries", 0)
        }
    
    def generate_level_summary(self) -> Dict:
        """
        레벨별 요약 보고서 생성
        
        Returns:
            Dict: 레벨별 요약 보고서
        """
        level_analysis = self.analyzer.analyze_by_emotion_level()
        
        summary = {
            "total": level_analysis.get("total", {}),
            "levels": {}
        }
        
        for level in [1, 2, 3]:
            level_key = f"level_{level}"
            level_data = level_analysis.get(level_key, {})
            
            summary["levels"][level_key] = {
                "total": level_data.get("total", 0),
                "success": level_data.get("success", 0),
                "fail": level_data.get("fail", 0),
                "success_rate": round(level_data.get("success_rate", 0), 2),
                "emotion_count": level_data.get("emotion_count", 0),
                "emotions": list(level_data.get("emotions", {}).keys())
            }
        
        # 알 수 없는 감정 요약
        unknown_data = level_analysis.get("unknown", {})
        summary["unknown"] = {
            "total": unknown_data.get("total", 0),
            "success": unknown_data.get("success", 0),
            "fail": unknown_data.get("fail", 0),
            "success_rate": round(unknown_data.get("success_rate", 0), 2),
            "emotion_count": unknown_data.get("emotion_count", 0),
            "emotions": list(unknown_data.get("emotions", {}).keys())
        }
        
        return summary
    
    def generate_emotion_ranking(self, top_n: int = 10) -> Dict:
        """
        감정별 성공률 랭킹 생성
        
        Args:
            top_n (int): 상위 N개 감정
        
        Returns:
            Dict: 감정 랭킹
        """
        detailed_analysis = self.analyzer.get_detailed_emotion_analysis()
        
        # 성공률 기준으로 정렬
        sorted_emotions = sorted(
            detailed_analysis.items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )
        
        # 상위 N개 선택
        top_emotions = sorted_emotions[:top_n]
        
        ranking = {
            "top_emotions": [],
            "bottom_emotions": sorted_emotions[-top_n:] if len(sorted_emotions) > top_n else [],
            "total_emotions": len(sorted_emotions)
        }
        
        for i, (emotion, stats) in enumerate(top_emotions, 1):
            ranking["top_emotions"].append({
                "rank": i,
                "emotion": emotion,
                "level": stats["level"],
                "success_rate": stats["success_rate"],
                "total": stats["total"],
                "success": stats["success"],
                "fail": stats["fail"]
            })
        
        return ranking
    
    def generate_action_ranking(self, top_n: int = 5) -> Dict:
        """
        액션별 성공률 랭킹 생성
        
        Args:
            top_n (int): 상위 N개 액션
        
        Returns:
            Dict: 액션 랭킹
        """
        action_analysis = self.analyzer.get_action_analysis()
        
        # 성공률 기준으로 정렬
        sorted_actions = sorted(
            action_analysis.items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )
        
        ranking = {
            "top_actions": [],
            "total_actions": len(sorted_actions)
        }
        
        for i, (action, stats) in enumerate(sorted_actions[:top_n], 1):
            ranking["top_actions"].append({
                "rank": i,
                "action": action,
                "success_rate": stats["success_rate"],
                "total": stats["total"],
                "success": stats["success"],
                "fail": stats["fail"]
            })
        
        return ranking
    
    def save_report(self, report: Dict, output_path: str) -> bool:
        """
        보고서를 파일로 저장
        
        Args:
            report (Dict): 저장할 보고서
            output_path (str): 저장할 파일 경로
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            import os
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"보고서 저장 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"보고서 저장 실패: {e}")
            return False


def create_emotion_summary(stats_path: str, evolution_path: str) -> Dict:
    """
    감정 요약 분석 생성 (편의 함수)
    
    Args:
        stats_path (str): 액션 통계 파일 경로
        evolution_path (str): 진화 로그 파일 경로
    
    Returns:
        Dict: 감정 요약 분석 결과
    """
    from .summary_loader import load_and_validate_data
    
    # 데이터 로드 및 검증
    loader, errors = load_and_validate_data(stats_path, evolution_path)
    if not loader:
        return {"error": "데이터 로드 실패", "details": errors}
    
    # 분석기 생성
    analyzer = EmotionSummaryAnalyzer(
        loader.get_stats_data(),
        loader.get_evolution_data()
    )
    
    # 보고서 생성기 생성
    reporter = SummaryReporter(loader, analyzer)
    
    # 종합 보고서 생성
    return reporter.generate_summary_report()


if __name__ == "__main__":
    # 테스트 실행
    import sys
    
    if len(sys.argv) != 3:
        print("사용법: python summary_reporter.py <stats_path> <evolution_path>")
        sys.exit(1)
    
    stats_path = sys.argv[1]
    evolution_path = sys.argv[2]
    
    summary = create_emotion_summary(stats_path, evolution_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False)) 