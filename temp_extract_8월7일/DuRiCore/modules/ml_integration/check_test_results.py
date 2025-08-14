#!/usr/bin/env python3
"""
Phase 1 테스트 결과 확인 스크립트
저장된 테스트 결과를 로드하고 분석
"""

import pickle
import sys
from pathlib import Path

def check_test_results():
    """테스트 결과 확인"""
    try:
        # 테스트 결과 파일 경로
        results_file = "phase1_test_results.pkl"
        
        if not Path(results_file).exists():
            print(f"❌ 테스트 결과 파일을 찾을 수 없습니다: {results_file}")
            return
        
        print("🔍 Phase 1 테스트 결과 분석 중...")
        
        # 결과 파일 로드
        with open(results_file, 'rb') as f:
            results_data = pickle.load(f)
        
        print("\n" + "="*60)
        print("🎯 PHASE 1 테스트 결과 요약")
        print("="*60)
        
        # 기본 정보
        if 'test_config' in results_data:
            config = results_data['test_config']
            print(f"📋 테스트 설정:")
            print(f"   - 성능 임계값: {config.get('performance_threshold', 'N/A')}")
            print(f"   - 교차 검증 폴드: {config.get('cross_validation_folds', 'N/A')}")
            print(f"   - 테스트 데이터 비율: {config.get('test_data_ratio', 'N/A')}")
        
        # 테스트 결과
        if 'test_results' in results_data:
            test_results = results_data['test_results']
            print(f"\n📊 테스트 결과:")
            print(f"   - 총 테스트 수: {len(test_results)}")
            
            for test_name, test_result in test_results.items():
                print(f"   - {test_name}: {'✅ 완료' if 'error' not in test_result else '❌ 실패'}")
        
        # 성능 비교
        if 'performance_comparison' in results_data:
            perf_comp = results_data['performance_comparison']
            print(f"\n📈 성능 비교:")
            print(f"   - 원본 vs 최적화: {'✅ 완료' if perf_comp else '❌ 없음'}")
        
        # 검증 메트릭
        if 'validation_metrics' in results_data:
            val_metrics = results_data['validation_metrics']
            print(f"\n🎯 검증 메트릭:")
            print(f"   - 총 메트릭 수: {len(val_metrics)}")
        
        # 파일 크기 정보
        file_size = Path(results_file).stat().st_size
        print(f"\n💾 파일 정보:")
        print(f"   - 파일 크기: {file_size} bytes")
        print(f"   - 파일 경로: {Path(results_file).absolute()}")
        
        print("\n" + "="*60)
        print("✅ 테스트 결과 확인 완료!")
        print("="*60)
        
        # 상세 결과 요약
        print("\n🔍 상세 결과 분석:")
        analyze_detailed_results(results_data)
        
    except Exception as e:
        print(f"❌ 테스트 결과 확인 실패: {e}")
        import traceback
        traceback.print_exc()

def analyze_detailed_results(results_data):
    """상세 결과 분석"""
    try:
        # 테스트 결과 상세 분석
        if 'test_results' in results_data:
            test_results = results_data['test_results']
            
            for test_name, test_result in test_results.items():
                print(f"\n📋 {test_name}:")
                
                if isinstance(test_result, dict):
                    if 'error' in test_result:
                        print(f"   ❌ 오류: {test_result['error']}")
                    else:
                        # 성공한 테스트의 주요 정보 추출
                        if 'optimization_results' in test_result:
                            opt_results = test_result['optimization_results']
                            if isinstance(opt_results, dict):
                                print(f"   ✅ 최적화 완료: {len(opt_results)}개 결과")
                        
                        if 'performance_improvement' in test_result:
                            improvement = test_result['performance_improvement']
                            if isinstance(improvement, dict):
                                avg_improvement = improvement.get('average_improvement', 0)
                                print(f"   📈 평균 성능 향상: {avg_improvement:.2f}%")
                        
                        if 'feature_optimization_analysis' in test_result:
                            feature_analysis = test_result['feature_optimization_analysis']
                            if isinstance(feature_analysis, dict):
                                reduction = feature_analysis.get('feature_reduction_percentage', 0)
                                new_features = feature_analysis.get('new_features_created', 0)
                                print(f"   🔧 특성 최적화: {reduction:.1f}% 감소, {new_features}개 새 특성")
                        
                        if 'ensemble_performance_analysis' in test_result:
                            ensemble_analysis = test_result['ensemble_performance_analysis']
                            if isinstance(ensemble_analysis, dict):
                                overall_perf = ensemble_analysis.get('overall_ensemble_performance', 0)
                                print(f"   🎯 앙상블 성능: {overall_perf:.3f}")
                else:
                    print(f"   📝 결과 타입: {type(test_result)}")
        
        # 성능 비교 상세 분석
        if 'performance_comparison' in results_data:
            perf_comp = results_data['performance_comparison']
            print(f"\n📊 성능 비교 상세:")
            
            if 'original_vs_optimized' in perf_comp:
                orig_vs_opt = perf_comp['original_vs_optimized']
                print(f"   - 원본 vs 최적화 비교: {len(orig_vs_opt)}개 모델")
            
            if 'optimization_effectiveness' in perf_comp:
                opt_effectiveness = perf_comp['optimization_effectiveness']
                print(f"   - 최적화 효과성: {opt_effectiveness}")
        
        # 검증 메트릭 상세 분석
        if 'validation_metrics' in results_data:
            val_metrics = results_data['validation_metrics']
            print(f"\n🎯 검증 메트릭 상세:")
            print(f"   - 총 메트릭 수: {len(val_metrics)}")
            
            for metric_name, metric_value in val_metrics.items():
                if isinstance(metric_value, (int, float)):
                    print(f"   - {metric_name}: {metric_value}")
                elif isinstance(metric_value, str):
                    print(f"   - {metric_name}: {metric_value}")
                else:
                    print(f"   - {metric_name}: {type(metric_value)}")
                    
    except Exception as e:
        print(f"❌ 상세 결과 분석 실패: {e}")

if __name__ == "__main__":
    check_test_results()
