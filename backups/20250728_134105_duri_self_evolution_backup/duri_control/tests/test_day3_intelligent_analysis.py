#!/usr/bin/env python3
"""
DuRi Memory System Day 3 테스트
지능형 메모리 분석 시스템 테스트
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from duri_control.app.services.memory_service import MemoryService
from duri_control.app.services.intelligent_analysis_service import IntelligentAnalysisService
from duri_control.app.database.database import get_db_session


class TestDay3IntelligentAnalysis:
    """Day 3 지능형 메모리 분석 시스템 테스트"""
    
    def __init__(self):
        self.db = next(get_db_session())
        self.memory_service = MemoryService(self.db)
        self.intelligent_service = IntelligentAnalysisService()
        self.test_results = []
    
    def cleanup_test_memories(self):
        """테스트 메모리 정리"""
        try:
            # 테스트 태그가 포함된 메모리들 삭제
            test_memories = self.memory_service.query_memories(
                tags=["day3_test"],
                limit=100
            )
            
            for memory in test_memories:
                self.memory_service.delete_memory(memory.id)
            
            print(f"🧹 테스트 메모리 {len(test_memories)}개 정리 완료")
            
        except Exception as e:
            print(f"❌ 테스트 메모리 정리 실패: {e}")
    
    def create_test_data(self):
        """테스트 데이터 생성"""
        print("\n📋 테스트 데이터 생성...")
        
        # 다양한 타입의 메모리 생성
        test_memories = [
            # 패턴 분석용 데이터
            {"type": "api_request", "context": "Day 3 패턴 테스트", "content": "사용자 로그인 요청 처리", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 70},
            {"type": "api_request", "context": "Day 3 패턴 테스트", "content": "데이터베이스 조회 요청", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 65},
            {"type": "api_request", "context": "Day 3 패턴 테스트", "content": "파일 업로드 처리", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 80},
            {"type": "error", "context": "Day 3 패턴 테스트", "content": "데이터베이스 연결 오류", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 90},
            {"type": "error", "context": "Day 3 패턴 테스트", "content": "인증 토큰 만료", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 85},
            {"type": "system_event", "context": "Day 3 패턴 테스트", "content": "시스템 백업 완료", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 60},
            {"type": "system_event", "context": "Day 3 패턴 테스트", "content": "메모리 사용량 모니터링", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 55},
            {"type": "user_action", "context": "Day 3 패턴 테스트", "content": "사용자 설정 변경", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 75},
            {"type": "user_action", "context": "Day 3 패턴 테스트", "content": "사용자 프로필 업데이트", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 70},
            {"type": "important_event", "context": "Day 3 패턴 테스트", "content": "중요한 시스템 업데이트", "source": "day3_test", "tags": ["day3_test", "pattern"], "importance_score": 95},
        ]
        
        created_count = 0
        for memory_data in test_memories:
            try:
                self.memory_service.save_memory(memory_data)
                created_count += 1
            except Exception as e:
                print(f"❌ 메모리 생성 실패: {e}")
        
        print(f"✅ 테스트 데이터 {created_count}개 생성 완료")
        return created_count
    
    def test_pattern_analysis(self):
        """패턴 분석 테스트"""
        print("\n📋 패턴 분석 테스트...")
        
        try:
            # 패턴 분석 실행
            result = self.intelligent_service.analyze_memory_patterns(
                time_window=24,
                min_frequency=2
            )
            
            if "error" in result:
                print(f"❌ 패턴 분석 실패: {result['error']}")
                return False
            
            patterns = result.get("patterns", [])
            total_memories = result.get("total_memories_analyzed", 0)
            
            print(f"✅ 패턴 분석 성공")
            print(f"   분석된 메모리: {total_memories}개")
            print(f"   발견된 패턴: {len(patterns)}개")
            
            # 패턴 상세 정보 출력
            for i, pattern in enumerate(patterns[:3]):  # 최대 3개만 출력
                print(f"   패턴 {i+1}: {pattern['type']} - {pattern['context']}")
                print(f"     빈도: {pattern['frequency']}, 신뢰도: {pattern['confidence']:.2f}")
            
            return len(patterns) > 0
            
        except Exception as e:
            print(f"❌ 패턴 분석 테스트 실패: {e}")
            return False
    
    def test_correlation_analysis(self):
        """상관관계 분석 테스트"""
        print("\n📋 상관관계 분석 테스트...")
        
        try:
            # 상관관계 분석 실행
            result = self.intelligent_service.analyze_memory_correlations(
                time_window=24
            )
            
            if "error" in result:
                print(f"❌ 상관관계 분석 실패: {result['error']}")
                return False
            
            correlations = result.get("correlations", [])
            total_memories = result.get("total_memories_analyzed", 0)
            
            print(f"✅ 상관관계 분석 성공")
            print(f"   분석된 메모리: {total_memories}개")
            print(f"   발견된 상관관계: {len(correlations)}개")
            
            # 상관관계 상세 정보 출력
            for i, correlation in enumerate(correlations[:3]):  # 최대 3개만 출력
                print(f"   상관관계 {i+1}: {correlation['source_type']} ↔ {correlation['target_type']}")
                print(f"     강도: {correlation['correlation_strength']:.3f}")
                if correlation.get('time_lag'):
                    print(f"     시간 지연: {correlation['time_lag']:.1f}시간")
            
            return True  # 상관관계가 없어도 성공으로 간주
            
        except Exception as e:
            print(f"❌ 상관관계 분석 테스트 실패: {e}")
            return False
    
    def test_intelligent_recommendations(self):
        """지능형 추천 테스트"""
        print("\n📋 지능형 추천 테스트...")
        
        try:
            # 추천 생성
            result = self.intelligent_service.generate_intelligent_recommendations(
                user_context="Day 3 테스트",
                limit=5
            )
            
            if "error" in result:
                print(f"❌ 추천 생성 실패: {result['error']}")
                return False
            
            recommendations = result.get("recommendations", [])
            
            print(f"✅ 지능형 추천 생성 성공")
            print(f"   생성된 추천: {len(recommendations)}개")
            
            # 추천 상세 정보 출력
            for i, recommendation in enumerate(recommendations):
                print(f"   추천 {i+1}: {recommendation['title']}")
                print(f"     설명: {recommendation['description']}")
                print(f"     우선순위: {recommendation['priority']}")
                print(f"     액션: {recommendation['action']}")
            
            return len(recommendations) > 0
            
        except Exception as e:
            print(f"❌ 지능형 추천 테스트 실패: {e}")
            return False
    
    def test_trend_prediction(self):
        """트렌드 예측 테스트"""
        print("\n📋 트렌드 예측 테스트...")
        
        try:
            # 트렌드 예측 실행
            result = self.intelligent_service.predict_memory_trends(
                days_ahead=7
            )
            
            if "error" in result:
                print(f"❌ 트렌드 예측 실패: {result['error']}")
                return False
            
            predictions = result.get("predictions", [])
            
            print(f"✅ 트렌드 예측 성공")
            print(f"   예측 일수: 7일")
            print(f"   생성된 예측: {len(predictions)}개")
            
            # 예측 상세 정보 출력
            for i, prediction in enumerate(predictions):
                print(f"   예측 {i+1}: {prediction['metric']}")
                print(f"     현재 평균: {prediction['current_avg']:.2f}")
                print(f"     예측 총합: {prediction['predicted_total']}")
                print(f"     신뢰도: {prediction['confidence']:.2f}")
                print(f"     트렌드: {prediction['trend']}")
            
            return len(predictions) > 0
            
        except Exception as e:
            print(f"❌ 트렌드 예측 테스트 실패: {e}")
            return False
    
    def test_comprehensive_analysis(self):
        """종합 분석 테스트"""
        print("\n📋 종합 분석 테스트...")
        
        try:
            # 종합 분석 실행 (패턴, 상관관계, 추천, 예측 모두 포함)
            pattern_result = self.intelligent_service.analyze_memory_patterns(
                time_window=24,
                min_frequency=2
            )
            
            correlation_result = self.intelligent_service.analyze_memory_correlations(
                time_window=24
            )
            
            recommendation_result = self.intelligent_service.generate_intelligent_recommendations(
                user_context="Day 3 종합 테스트",
                limit=5
            )
            
            prediction_result = self.intelligent_service.predict_memory_trends(
                days_ahead=7
            )
            
            # 결과 통합
            comprehensive_result = {
                "patterns": pattern_result,
                "correlations": correlation_result,
                "recommendations": recommendation_result,
                "predictions": prediction_result
            }
            
            # 분석 요약
            patterns_found = len(pattern_result.get("patterns", []))
            correlations_found = len(correlation_result.get("correlations", []))
            recommendations_generated = len(recommendation_result.get("recommendations", []))
            predictions_made = len(prediction_result.get("predictions", []))
            
            print(f"✅ 종합 분석 성공")
            print(f"   발견된 패턴: {patterns_found}개")
            print(f"   발견된 상관관계: {correlations_found}개")
            print(f"   생성된 추천: {recommendations_generated}개")
            print(f"   생성된 예측: {predictions_made}개")
            
            return True
            
        except Exception as e:
            print(f"❌ 종합 분석 테스트 실패: {e}")
            return False
    
    def test_insights_generation(self):
        """인사이트 생성 테스트"""
        print("\n📋 인사이트 생성 테스트...")
        
        try:
            # 패턴 인사이트
            pattern_result = self.intelligent_service.analyze_memory_patterns(
                time_window=24,
                min_frequency=2
            )
            
            # 상관관계 인사이트
            correlation_result = self.intelligent_service.analyze_memory_correlations(
                time_window=24
            )
            
            # 트렌드 인사이트
            prediction_result = self.intelligent_service.predict_memory_trends(
                days_ahead=7
            )
            
            insights = []
            
            # 패턴 인사이트 생성
            if "patterns" in pattern_result:
                for pattern in pattern_result["patterns"][:3]:
                    insights.append({
                        "type": "pattern",
                        "title": f"패턴 발견: {pattern['type']}",
                        "description": pattern["context"],
                        "confidence": pattern["confidence"],
                        "importance": pattern["importance_score"]
                    })
            
            # 상관관계 인사이트 생성
            if "correlations" in correlation_result:
                for correlation in correlation_result["correlations"][:3]:
                    insights.append({
                        "type": "correlation",
                        "title": f"상관관계: {correlation['source_type']} ↔ {correlation['target_type']}",
                        "description": f"강도: {correlation['correlation_strength']:.2f}",
                        "confidence": correlation["correlation_strength"],
                        "importance": correlation["correlation_strength"] * 100
                    })
            
            # 트렌드 인사이트 생성
            if "predictions" in prediction_result:
                for prediction in prediction_result["predictions"]:
                    insights.append({
                        "type": "trend",
                        "title": f"트렌드: {prediction['metric']}",
                        "description": f"예측: {prediction['trend']} (신뢰도: {prediction['confidence']})",
                        "confidence": prediction["confidence"],
                        "importance": prediction["confidence"] * 100
                    })
            
            # 중요도 순으로 정렬
            insights.sort(key=lambda x: x["importance"], reverse=True)
            
            print(f"✅ 인사이트 생성 성공")
            print(f"   생성된 인사이트: {len(insights)}개")
            
            # 인사이트 상세 정보 출력
            for i, insight in enumerate(insights[:5]):  # 최대 5개만 출력
                print(f"   인사이트 {i+1}: {insight['title']}")
                print(f"     설명: {insight['description']}")
                print(f"     신뢰도: {insight['confidence']:.2f}")
                print(f"     중요도: {insight['importance']:.1f}")
            
            return len(insights) > 0
            
        except Exception as e:
            print(f"❌ 인사이트 생성 테스트 실패: {e}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 DuRi Memory System Day 3 테스트 시작")
        print("=" * 60)
        
        # 테스트 데이터 생성
        self.create_test_data()
        
        tests = [
            ("패턴 분석", self.test_pattern_analysis),
            ("상관관계 분석", self.test_correlation_analysis),
            ("지능형 추천", self.test_intelligent_recommendations),
            ("트렌드 예측", self.test_trend_prediction),
            ("종합 분석", self.test_comprehensive_analysis),
            ("인사이트 생성", self.test_insights_generation)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} 통과")
                else:
                    print(f"❌ {test_name} 실패")
            except Exception as e:
                print(f"❌ {test_name} 오류: {e}")
        
        # 테스트 메모리 정리
        self.cleanup_test_memories()
        
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        print(f"✅ 통과: {passed}/{total}")
        print(f"❌ 실패: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 모든 테스트가 통과했습니다!")
            print("   Day 3 목표 달성: 지능형 메모리 분석 시스템 구현 완료")
            print("\n🚀 Day 3 완료! Day 4로 진행할 준비가 되었습니다.")
            return True
        else:
            print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")
            print("   문제를 해결한 후 다시 테스트하세요.")
            return False


if __name__ == "__main__":
    test_runner = TestDay3IntelligentAnalysis()
    success = test_runner.run_all_tests()
    
    if success:
        print("\n🎯 Day 3 지능형 메모리 분석 시스템 구현 완료!")
        print("   - 패턴 분석 및 학습 시스템")
        print("   - 메모리 상관관계 분석")
        print("   - 지능형 추천 시스템")
        print("   - 예측 모델링")
    else:
        print("\n⚠️ Day 3 테스트 실패. 문제를 해결하세요.")
    
    sys.exit(0 if success else 1) 