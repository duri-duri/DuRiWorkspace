"""
ML 통합 시스템 데모 스크립트
Phase 1의 모든 ML 모델을 테스트하고 통합 시스템의 성능을 시연
"""

import sys
import os
import logging
from pathlib import Path
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_demo_knowledge_base():
    """데모용 알고리즘 지식 베이스 생성"""
    from algorithm_knowledge.algorithm_knowledge_base import (
        AlgorithmKnowledge, 
        ProblemPattern,
        AlgorithmKnowledgeBase
    )
    
    # 데모 알고리즘들 생성
    algorithms = {}
    
    # 1. 문제 해결 알고리즘
    algorithms['binary_search'] = AlgorithmKnowledge(
        algorithm_id='binary_search',
        name='이진 탐색',
        description='정렬된 배열에서 특정 값을 효율적으로 찾는 알고리즘',
        category='problem_solving',
        input_patterns=['정렬된 배열', '찾을 값', '탐색 범위'],
        process_steps=['중간값 계산', '중간값과 목표값 비교', '범위 좁히기', '반복'],
        output_patterns=['찾은 값의 인덱스', '값이 없음을 나타내는 신호'],
        applicable_domains=['데이터 구조', '알고리즘', '검색'],
        prerequisites=['정렬된 배열', '비교 연산'],
        alternatives=['선형 탐색', '해시 테이블'],
        complexity='O(log n)',
        success_rate=0.95,
        efficiency_score=0.9,
        confidence_level=0.9,
        usage_count=150
    )
    
    # 2. 학습 알고리즘
    algorithms['gradient_descent'] = AlgorithmKnowledge(
        algorithm_id='gradient_descent',
        name='경사 하강법',
        description='함수의 최솟값을 찾기 위해 경사를 따라 내려가는 최적화 알고리즘',
        category='learning',
        input_patterns=['목적 함수', '초기값', '학습률', '반복 횟수'],
        process_steps=['현재 위치에서의 기울기 계산', '기울기 반대 방향으로 이동', '수렴 확인'],
        output_patterns=['최적해', '수렴 여부', '최종 함수값'],
        applicable_domains=['머신러닝', '최적화', '수학'],
        prerequisites=['미분 가능한 함수', '초기값 설정'],
        alternatives=['뉴턴법', 'Adam', 'RMSprop'],
        complexity='O(n)',
        success_rate=0.85,
        efficiency_score=0.8,
        confidence_level=0.85,
        usage_count=200
    )
    
    # 3. 의사결정 알고리즘
    algorithms['decision_tree'] = AlgorithmKnowledge(
        algorithm_id='decision_tree',
        name='의사결정 트리',
        description='데이터를 분류하거나 예측하기 위한 트리 구조의 모델',
        category='decision_making',
        input_patterns=['특성 데이터', '레이블', '분할 기준'],
        process_steps=['루트 노드 선택', '특성별 분할', '리프 노드 생성', '예측 수행'],
        output_patterns=['분류 결과', '예측값', '의사결정 경로'],
        applicable_domains=['머신러닝', '데이터 마이닝', '비즈니스 분석'],
        prerequisites=['특성 데이터', '레이블 데이터'],
        alternatives=['랜덤 포레스트', 'XGBoost', 'LightGBM'],
        complexity='O(n log n)',
        success_rate=0.8,
        efficiency_score=0.75,
        confidence_level=0.8,
        usage_count=180
    )
    
    # 4. 패턴 인식 알고리즘
    algorithms['kmeans'] = AlgorithmKnowledge(
        algorithm_id='kmeans',
        name='K-means 클러스터링',
        description='데이터를 K개의 그룹으로 자동으로 분류하는 비지도 학습 알고리즘',
        category='pattern_recognition',
        input_patterns=['데이터 포인트', '클러스터 수 K', '초기 중심점'],
        process_steps=['중심점 초기화', '포인트 할당', '중심점 재계산', '수렴 확인'],
        output_patterns=['클러스터 레이블', '중심점 좌표', '클러스터 크기'],
        applicable_domains=['데이터 마이닝', '이미지 처리', '고객 세분화'],
        prerequisites=['수치형 데이터', '유클리드 거리'],
        alternatives=['DBSCAN', '계층적 클러스터링', 'GMM'],
        complexity='O(nkd)',
        success_rate=0.75,
        efficiency_score=0.8,
        confidence_level=0.75,
        usage_count=120
    )
    
    # 5. 하이브리드 알고리즘
    algorithms['ensemble_method'] = AlgorithmKnowledge(
        algorithm_id='ensemble_method',
        name='앙상블 방법',
        description='여러 모델의 예측을 결합하여 성능을 향상시키는 방법',
        category='hybrid',
        input_patterns=['기본 모델들', '결합 방법', '가중치'],
        process_steps=['개별 모델 학습', '예측 수행', '결과 결합', '최종 예측'],
        output_patterns=['통합 예측값', '개별 모델 성능', '앙상블 정확도'],
        applicable_domains=['머신러닝', '예측 모델링', '분류'],
        prerequisites=['기본 모델들', '결합 전략'],
        alternatives=['단일 모델', '스태킹', '블렌딩'],
        complexity='O(nm)',
        success_rate=0.9,
        efficiency_score=0.7,
        confidence_level=0.9,
        usage_count=100
    )
    
    # 6. 적응형 알고리즘
    algorithms['adaptive_learning'] = AlgorithmKnowledge(
        algorithm_id='adaptive_learning',
        name='적응형 학습',
        description='학습자의 수준과 진행 상황에 따라 학습 내용을 동적으로 조정하는 방법',
        category='adaptive',
        input_patterns=['학습자 프로필', '학습 목표', '진행 상황', '성과 데이터'],
        process_steps=['현재 수준 평가', '학습 경로 생성', '학습 진행', '적응적 조정'],
        output_patterns=['개인화된 학습 계획', '학습 성과', '다음 단계'],
        applicable_domains=['교육', '온라인 학습', '기업 교육'],
        prerequisites=['학습자 데이터', '학습 콘텐츠', '평가 시스템'],
        alternatives=['표준화된 학습', '개별 지도', '그룹 학습'],
        complexity='O(n)',
        success_rate=0.85,
        efficiency_score=0.85,
        confidence_level=0.8,
        usage_count=80
    )
    
    # 지식 베이스 생성
    knowledge_base = AlgorithmKnowledgeBase()
    knowledge_base.algorithms = algorithms
    
    logger.info(f"데모 지식 베이스 생성 완료: {len(algorithms)}개 알고리즘")
    return knowledge_base

def run_ml_integration_demo():
    """ML 통합 시스템 데모 실행"""
    try:
        logger.info("=== ML 통합 시스템 데모 시작 ===")
        
        # 1. 데모 지식 베이스 생성
        knowledge_base = create_demo_knowledge_base()
        
        # 2. ML 통합 시스템 초기화
        from ml_integration.ml_integration_system import MLIntegrationSystem
        
        ml_system = MLIntegrationSystem(knowledge_base, models_directory="demo_ml_models")
        
        # 3. 모든 모델 학습
        logger.info("모든 ML 모델 학습 시작...")
        training_results = ml_system.train_all_models()
        
        logger.info("학습 결과:")
        for model_name, result in training_results.items():
            logger.info(f"  {model_name}: {result['status']}")
        
        # 4. 시스템 상태 확인
        system_status = ml_system.get_system_status()
        logger.info(f"시스템 전체 정확도: {system_status['system_status']['overall_accuracy']:.3f}")
        
        # 5. 통합 알고리즘 추천 데모
        logger.info("\n=== 통합 알고리즘 추천 데모 ===")
        
        # 데모 문제들
        demo_problems = [
            {
                'description': '대량의 데이터에서 특정 패턴을 찾고 싶습니다',
                'context': {
                    'domain': '데이터 마이닝',
                    'input_pattern': '대량 데이터 패턴 탐색',
                    'complexity_requirement': 'O(n log n)'
                }
            },
            {
                'description': '학습자의 수준에 맞는 개인화된 교육을 제공하고 싶습니다',
                'context': {
                    'domain': '교육',
                    'input_pattern': '개인화 학습',
                    'complexity_requirement': 'O(n)'
                }
            },
            {
                'description': '여러 모델의 예측을 결합하여 정확도를 높이고 싶습니다',
                'context': {
                    'domain': '머신러닝',
                    'input_pattern': '모델 결합',
                    'complexity_requirement': 'O(nm)'
                }
            }
        ]
        
        for i, problem in enumerate(demo_problems, 1):
            logger.info(f"\n--- 문제 {i}: {problem['description']} ---")
            
            recommendation = ml_system.integrated_algorithm_recommendation(
                problem['description'], 
                problem['context']
            )
            
            if 'error' not in recommendation:
                logger.info(f"추천된 알고리즘 수: {len(recommendation['recommendations'])}")
                
                # 상위 3개 추천 결과 출력
                for j, rec in enumerate(recommendation['recommendations'][:3], 1):
                    logger.info(f"  {j}위: {rec['algorithms'][0]['name']} "
                              f"(점수: {rec['overall_score']:.3f})")
                    
                    if 'individual_predictions' in rec:
                        for alg_id, pred in rec['individual_predictions'].items():
                            if 'predicted_success_rate' in pred:
                                logger.info(f"    예측 성공률: {pred['predicted_success_rate']:.3f}")
                                logger.info(f"    예측 효율성: {pred['predicted_efficiency']:.3f}")
            else:
                logger.error(f"추천 실패: {recommendation['error']}")
        
        # 6. 시스템 진단 실행
        logger.info("\n=== 시스템 진단 ===")
        diagnostics = ml_system.run_system_diagnostics()
        logger.info(f"시스템 상태: {diagnostics['system_health']}")
        
        if diagnostics['issues']:
            logger.info("발견된 문제점:")
            for issue in diagnostics['issues']:
                logger.info(f"  - {issue}")
        
        if diagnostics['recommendations']:
            logger.info("권장사항:")
            for rec in diagnostics['recommendations']:
                logger.info(f"  - {rec}")
        
        # 7. 모델 저장
        logger.info("\n모델 저장 중...")
        ml_system.save_all_models()
        
        # 8. 최종 통계
        final_metrics = ml_system.get_system_status()
        logger.info(f"\n=== 최종 통계 ===")
        logger.info(f"총 예측 수: {final_metrics['integrated_metrics']['total_predictions']}")
        logger.info(f"성공한 예측: {final_metrics['integrated_metrics']['successful_predictions']}")
        logger.info(f"평균 예측 신뢰도: {final_metrics['integrated_metrics']['average_prediction_confidence']:.3f}")
        logger.info(f"전체 시스템 정확도: {final_metrics['system_status']['overall_accuracy']:.3f}")
        
        logger.info("\n=== ML 통합 시스템 데모 완료 ===")
        
        return True
        
    except Exception as e:
        logger.error(f"데모 실행 실패: {e}")
        return False

def run_individual_model_tests():
    """개별 모델 테스트"""
    try:
        logger.info("=== 개별 모델 테스트 시작 ===")
        
        # 지식 베이스 생성
        knowledge_base = create_demo_knowledge_base()
        
        # 1. 성능 예측 모델 테스트
        logger.info("\n--- 알고리즘 성능 예측 모델 테스트 ---")
        from ml_integration.algorithm_performance_predictor import AlgorithmPerformancePredictor
        
        perf_predictor = AlgorithmPerformancePredictor(knowledge_base)
        if perf_predictor.train_models():
            logger.info("성능 예측 모델 학습 성공")
            
            # 예측 테스트
            test_algorithm = list(knowledge_base.algorithms.values())[0]
            prediction = perf_predictor.predict_algorithm_performance(test_algorithm)
            if prediction:
                logger.info(f"예측 결과: 성공률 {prediction['predicted_success_rate']:.3f}, "
                          f"효율성 {prediction['predicted_efficiency']:.3f}")
        
        # 2. 패턴 분류 모델 테스트
        logger.info("\n--- 문제 패턴 분류 모델 테스트 ---")
        from ml_integration.problem_pattern_classifier import ProblemPatternClassifier
        
        pattern_classifier = ProblemPatternClassifier(knowledge_base)
        if pattern_classifier.train_models():
            logger.info("패턴 분류 모델 학습 성공")
            
            # 분류 테스트
            test_pattern = "정렬된 배열에서 값을 찾고 싶습니다"
            classification = pattern_classifier.classify_problem_pattern(test_pattern)
            if classification:
                logger.info(f"패턴 분류 결과: {classification['final_classification']['category']} "
                          f"(신뢰도: {classification['final_classification']['confidence']:.3f})")
        
        # 3. 조합 최적화 모델 테스트
        logger.info("\n--- 알고리즘 조합 최적화 모델 테스트 ---")
        from ml_integration.algorithm_combination_optimizer import AlgorithmCombinationOptimizer
        
        combo_optimizer = AlgorithmCombinationOptimizer(knowledge_base)
        combo_optimizer.initialize_optimization_models()
        
        # 최적화 테스트
        problem_context = {
            'domain': '머신러닝',
            'input_pattern': '데이터 분석',
            'complexity_requirement': 'O(n log n)'
        }
        
        optimization_result = combo_optimizer.optimize_combination(problem_context, iterations=50)
        if optimization_result:
            logger.info(f"최적화 완료: 최고 점수 {optimization_result['best_score']:.3f}")
            logger.info(f"최적 조합: {optimization_result['best_combination']}")
        
        logger.info("\n=== 개별 모델 테스트 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"개별 모델 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("DuRi ML 통합 시스템 데모")
    print("=" * 50)
    
    # 개별 모델 테스트
    print("\n1. 개별 모델 테스트 실행...")
    if run_individual_model_tests():
        print("✅ 개별 모델 테스트 성공")
    else:
        print("❌ 개별 모델 테스트 실패")
    
    # 통합 시스템 데모
    print("\n2. 통합 시스템 데모 실행...")
    if run_ml_integration_demo():
        print("✅ 통합 시스템 데모 성공")
    else:
        print("❌ 통합 시스템 데모 실패")
    
    print("\n데모 완료!")
