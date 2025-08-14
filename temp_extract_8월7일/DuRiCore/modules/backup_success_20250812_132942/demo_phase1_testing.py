"""
Phase 1 테스트 및 검증 시스템 데모
실제 테스트 실행 및 결과 분석을 통한 Phase 1 완성도 검증
"""

import sys
import os
import logging
from pathlib import Path
import time
import json

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_demo_knowledge_base():
    """데모용 알고리즘 지식 베이스 생성"""
    try:
        from DuRiCore.modules.algorithm_knowledge.algorithm_knowledge_base import (
            AlgorithmKnowledge, ProblemPattern, AlgorithmKnowledgeBase
        )
        
        # 알고리즘 지식 베이스 초기화
        knowledge_base = AlgorithmKnowledgeBase()
        
        # 데모 알고리즘들 추가
        algorithms = [
            AlgorithmKnowledge(
                algorithm_id="sorting_quick",
                name="Quick Sort",
                description="분할 정복을 사용한 효율적인 정렬 알고리즘",
                category="sorting",
                complexity="O(n log n)",
                success_rate=0.95,
                efficiency_score=0.9,
                usage_count=150,
                confidence_level=0.95,
                input_patterns=["array", "list", "numbers"],
                process_steps=["pivot 선택", "분할", "재귀 정렬"],
                output_patterns=["정렬된 배열"],
                applicable_domains=["데이터 정렬", "알고리즘 교육"],
                prerequisites=["배열 이해", "재귀 개념"],
                alternatives=["Merge Sort", "Heap Sort"]
            ),
            AlgorithmKnowledge(
                algorithm_id="search_binary",
                name="Binary Search",
                description="정렬된 배열에서 효율적으로 검색하는 알고리즘",
                category="searching",
                complexity="O(log n)",
                success_rate=0.98,
                efficiency_score=0.95,
                usage_count=200,
                confidence_level=0.98,
                input_patterns=["정렬된 배열", "검색값"],
                process_steps=["중간값 계산", "비교", "범위 조정"],
                output_patterns=["검색 결과", "인덱스"],
                applicable_domains=["데이터 검색", "정렬된 데이터 처리"],
                prerequisites=["정렬된 배열", "비교 연산"],
                alternatives=["Linear Search", "Interpolation Search"]
            ),
            AlgorithmKnowledge(
                algorithm_id="graph_dfs",
                name="Depth-First Search",
                description="그래프를 깊이 우선으로 탐색하는 알고리즘",
                category="graph",
                complexity="O(V + E)",
                success_rate=0.92,
                efficiency_score=0.85,
                usage_count=80,
                confidence_level=0.92,
                input_patterns=["그래프", "시작 노드"],
                process_steps=["현재 노드 방문", "인접 노드 탐색", "재귀 호출"],
                output_patterns=["방문 순서", "탐색 트리"],
                applicable_domains=["그래프 탐색", "경로 찾기"],
                prerequisites=["그래프 개념", "재귀 이해"],
                alternatives=["Breadth-First Search", "A* Search"]
            ),
            AlgorithmKnowledge(
                algorithm_id="dp_fibonacci",
                name="Dynamic Programming Fibonacci",
                description="동적 프로그래밍을 사용한 피보나치 수열 계산",
                category="dynamic_programming",
                complexity="O(n)",
                success_rate=0.88,
                efficiency_score=0.8,
                usage_count=60,
                confidence_level=0.88,
                input_patterns=["정수 n", "피보나치 인덱스"],
                process_steps=["기본 케이스 정의", "메모이제이션", "상향식 계산"],
                output_patterns=["피보나치 수", "계산 과정"],
                applicable_domains=["수학 계산", "알고리즘 최적화"],
                prerequisites=["재귀 개념", "메모이제이션"],
                alternatives=["Recursive Fibonacci", "Matrix Exponentiation"]
            ),
            AlgorithmKnowledge(
                algorithm_id="ml_kmeans",
                name="K-Means Clustering",
                description="비지도 학습을 위한 클러스터링 알고리즘",
                category="machine_learning",
                complexity="O(nkd)",
                success_rate=0.85,
                efficiency_score=0.75,

                usage_count=45,
                confidence_level=0.85,
                input_patterns=["데이터 포인트", "클러스터 수 k"],
                process_steps=["중심점 초기화", "할당", "중심점 업데이트"],
                output_patterns=["클러스터 라벨", "중심점"],
                applicable_domains=["데이터 분석", "패턴 인식"],
                prerequisites=["선형대수", "통계 기초"],
                alternatives=["Hierarchical Clustering", "DBSCAN"]
            )
        ]
        
        # 알고리즘들을 지식 베이스에 추가
        for algorithm in algorithms:
            knowledge_base.add_algorithm(algorithm)
        
        logger.info(f"데모 알고리즘 지식 베이스 생성 완료: {len(algorithms)}개 알고리즘")
        return knowledge_base
        
    except Exception as e:
        logger.error(f"데모 지식 베이스 생성 실패: {e}")
        return None

def run_phase1_comprehensive_testing():
    """Phase 1 포괄적 테스트 실행"""
    try:
        logger.info("=== Phase 1 포괄적 테스트 시작 ===")
        
        # 1. 데모 지식 베이스 생성
        knowledge_base = create_demo_knowledge_base()
        if not knowledge_base:
            logger.error("지식 베이스 생성 실패")
            return None
        
        # 2. Phase 1 테스트 시스템 초기화
        from DuRiCore.modules.ml_integration.phase1_testing_system import Phase1TestingSystem
        
        testing_system = Phase1TestingSystem(knowledge_base)
        
        # 3. 포괄적 테스트 실행
        logger.info("포괄적 테스트 실행 중...")
        comprehensive_results = testing_system.run_comprehensive_testing()
        
        if 'error' in comprehensive_results:
            logger.error(f"테스트 실행 실패: {comprehensive_results['error']}")
            return None
        
        # 4. 테스트 결과 분석
        logger.info("테스트 결과 분석 중...")
        analyze_test_results(comprehensive_results)
        
        # 5. 테스트 결과 저장
        results_file = "phase1_test_results.pkl"
        if testing_system.save_test_results(results_file):
            logger.info(f"테스트 결과 저장 완료: {results_file}")
        
        return comprehensive_results
        
    except Exception as e:
        logger.error(f"Phase 1 포괄적 테스트 실행 실패: {e}")
        return None

def analyze_test_results(test_results):
    """테스트 결과 분석 및 요약"""
    try:
        logger.info("=== Phase 1 테스트 결과 분석 ===")
        
        if 'comprehensive_results' not in test_results:
            logger.error("테스트 결과가 없습니다")
            return
        
        comprehensive_results = test_results['comprehensive_results']
        
        # 1. 원본 모델 성능
        if 'original_performance' in comprehensive_results:
            original_perf = comprehensive_results['original_performance']
            logger.info(f"원본 모델 성능: {original_perf}")
        
        # 2. 하이퍼파라미터 최적화 결과
        if 'hyperparameter_optimization' in comprehensive_results:
            hyper_opt = comprehensive_results['hyperparameter_optimization']
            if 'performance_improvement' in hyper_opt:
                improvement = hyper_opt['performance_improvement']
                logger.info(f"하이퍼파라미터 최적화 개선도: {improvement.get('average_improvement', 0):.2f}%")
        
        # 3. 특성 엔지니어링 결과
        if 'feature_engineering_optimization' in comprehensive_results:
            feature_opt = comprehensive_results['feature_engineering_optimization']
            if 'feature_optimization_analysis' in feature_opt:
                feature_analysis = feature_opt['feature_optimization_analysis']
                logger.info(f"특성 수 감소율: {feature_analysis.get('feature_reduction_percentage', 0):.1f}%")
                logger.info(f"새로 생성된 특성 수: {feature_analysis.get('new_features_created', 0)}")
        
        # 4. 앙상블 방법 결과
        if 'ensemble_optimization' in comprehensive_results:
            ensemble_opt = comprehensive_results['ensemble_optimization']
            if 'ensemble_performance_analysis' in ensemble_opt:
                ensemble_analysis = ensemble_opt['ensemble_performance_analysis']
                logger.info(f"전체 앙상블 성능: {ensemble_analysis.get('overall_ensemble_performance', 0):.3f}")
        
        # 5. 최종 검증 결과
        if 'final_validation' in comprehensive_results:
            final_validation = comprehensive_results['final_validation']
            completion_score = final_validation.get('phase1_completion_score', 0.0)
            overall_assessment = final_validation.get('overall_assessment', 'unknown')
            
            logger.info(f"Phase 1 완성도 점수: {completion_score:.1%}")
            logger.info(f"전체 평가: {overall_assessment}")
            
            # 다음 단계 권장사항
            if 'next_steps_recommendations' in final_validation:
                recommendations = final_validation['next_steps_recommendations']
                logger.info("다음 단계 권장사항:")
                for i, rec in enumerate(recommendations, 1):
                    logger.info(f"  {i}. {rec}")
        
        # 6. 전체 테스트 시간
        total_time = test_results.get('total_testing_time', 0)
        logger.info(f"전체 테스트 소요시간: {total_time:.2f}초")
        
    except Exception as e:
        logger.error(f"테스트 결과 분석 실패: {e}")

def run_individual_optimization_tests():
    """개별 최적화 시스템 테스트"""
    try:
        logger.info("=== 개별 최적화 시스템 테스트 시작 ===")
        
        # 1. 데모 지식 베이스 생성
        knowledge_base = create_demo_knowledge_base()
        if not knowledge_base:
            return None
        
        # 2. 하이퍼파라미터 최적화 테스트
        logger.info("하이퍼파라미터 최적화 테스트...")
        from DuRiCore.modules.ml_integration.ml_hyperparameter_optimizer import MLHyperparameterOptimizer
        
        hyper_optimizer = MLHyperparameterOptimizer(knowledge_base)
        training_data = create_demo_training_data()
        
        if not training_data.empty:
            hyper_results = hyper_optimizer.optimize_all_models(training_data)
            logger.info(f"하이퍼파라미터 최적화 완료: {len(hyper_results.get('optimization_results', {}))}개 모델")
        
        # 3. 특성 엔지니어링 최적화 테스트
        logger.info("특성 엔지니어링 최적화 테스트...")
        from DuRiCore.modules.ml_integration.feature_engineering_optimizer import FeatureEngineeringOptimizer
        
        feature_optimizer = FeatureEngineeringOptimizer(knowledge_base)
        if not training_data.empty:
            feature_results = feature_optimizer.optimize_all_features(training_data)
            logger.info(f"특성 엔지니어링 최적화 완료: {feature_results.get('final_features', {}).get('feature_count', 0)}개 특성")
        
        # 4. 앙상블 방법 최적화 테스트
        logger.info("앙상블 방법 최적화 테스트...")
        from DuRiCore.modules.ml_integration.ensemble_method_optimizer import EnsembleMethodOptimizer
        
        ensemble_optimizer = EnsembleMethodOptimizer(knowledge_base)
        if not training_data.empty:
            ensemble_optimizer.create_base_models(training_data)
            target_columns = ['success_rate', 'efficiency_score', 'complexity_score']
            ensemble_results = ensemble_optimizer.create_ensemble_methods(training_data, target_columns)
            logger.info(f"앙상블 방법 최적화 완료: {len(ensemble_results)}개 타겟")
        
        logger.info("개별 최적화 시스템 테스트 완료")
        
    except Exception as e:
        logger.error(f"개별 최적화 시스템 테스트 실패: {e}")

def create_demo_training_data():
    """데모용 학습 데이터 생성"""
    try:
        import pandas as pd
        import numpy as np
        
        # 간단한 테스트용 데이터 생성
        data = []
        for i in range(200):
            data.append({
                'algorithm_id': f'alg_{i}',
                'category_encoded': i % 6,
                'confidence_level': np.random.uniform(0.5, 1.0),
                'usage_count': np.random.randint(1, 100),
                'complexity_score': np.random.uniform(1.0, 7.0),
                'input_patterns_count': np.random.randint(1, 10),
                'process_steps_count': np.random.randint(1, 15),
                'output_patterns_count': np.random.randint(1, 8),
                'applicable_domains_count': np.random.randint(1, 5),
                'prerequisites_count': np.random.randint(0, 5),
                'alternatives_count': np.random.randint(0, 3),
                'success_rate': np.random.uniform(0.3, 1.0),
                'efficiency_score': np.random.uniform(0.3, 1.0),
                'performance_grade': np.random.choice(['poor', 'fair', 'good', 'excellent'])
            })
        
        # TF-IDF 특성 추가 (50개)
        for i in range(200):
            for j in range(50):
                data[i][f'text_feature_{j}'] = np.random.uniform(0, 1)
        
        df = pd.DataFrame(data)
        logger.info(f"데모 학습 데이터 생성 완료: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"데모 학습 데이터 생성 실패: {e}")
        return pd.DataFrame()

def main():
    """메인 실행 함수"""
    try:
        logger.info("=== Phase 1 테스트 및 검증 시스템 데모 시작 ===")
        
        # 사용자 선택
        print("\nPhase 1 테스트 옵션을 선택하세요:")
        print("1. 포괄적 테스트 실행 (전체 시스템)")
        print("2. 개별 최적화 시스템 테스트")
        print("3. 테스트 결과만 확인")
        
        choice = input("선택 (1-3): ").strip()
        
        if choice == "1":
            # 포괄적 테스트 실행
            results = run_phase1_comprehensive_testing()
            if results:
                logger.info("포괄적 테스트 완료!")
            else:
                logger.error("포괄적 테스트 실패")
        
        elif choice == "2":
            # 개별 최적화 시스템 테스트
            run_individual_optimization_tests()
        
        elif choice == "3":
            # 저장된 테스트 결과 확인
            results_file = "phase1_test_results.pkl"
            if os.path.exists(results_file):
                from DuRiCore.modules.ml_integration.phase1_testing_system import Phase1TestingSystem
                testing_system = Phase1TestingSystem(None)
                if testing_system.load_test_results(results_file):
                    analyze_test_results(testing_system.get_test_summary())
                else:
                    logger.error("테스트 결과 로드 실패")
            else:
                logger.error("저장된 테스트 결과가 없습니다")
        
        else:
            logger.error("잘못된 선택입니다")
        
        logger.info("=== Phase 1 테스트 및 검증 시스템 데모 완료 ===")
        
    except Exception as e:
        logger.error(f"메인 실행 실패: {e}")

if __name__ == "__main__":
    main()
