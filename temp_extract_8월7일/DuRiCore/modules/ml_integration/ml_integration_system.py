"""
Phase 1: 머신러닝 통합 시스템
알고리즘 성능 예측, 문제 패턴 분류, 알고리즘 조합 최적화를 통합한 시스템
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import pickle
import json
import os
from pathlib import Path

# ML 통합 모델들
from .algorithm_performance_predictor import AlgorithmPerformancePredictor
from .problem_pattern_classifier import ProblemPatternClassifier
from .algorithm_combination_optimizer import AlgorithmCombinationOptimizer

from ..algorithm_knowledge.algorithm_knowledge_base import (
    AlgorithmKnowledge, 
    ProblemPattern,
    AlgorithmKnowledgeBase
)

logger = logging.getLogger(__name__)

class MLIntegrationSystem:
    """Phase 1: 머신러닝 통합 시스템"""
    
    def __init__(self, knowledge_base: AlgorithmKnowledgeBase, 
                 models_directory: str = "ml_models"):
        self.knowledge_base = knowledge_base
        self.models_directory = Path(models_directory)
        self.models_directory.mkdir(exist_ok=True)
        
        # ML 모델들
        self.performance_predictor = None
        self.pattern_classifier = None
        self.combination_optimizer = None
        
        # 시스템 상태
        self.system_status = {
            'performance_predictor_trained': False,
            'pattern_classifier_trained': False,
            'combination_optimizer_initialized': False,
            'last_training_timestamp': None,
            'overall_accuracy': 0.0
        }
        
        # 통합 성능 메트릭
        self.integrated_metrics = {
            'total_predictions': 0,
            'successful_predictions': 0,
            'average_prediction_confidence': 0.0,
            'system_uptime': datetime.now().isoformat()
        }
        
        logger.info("ML 통합 시스템 초기화 완료")
    
    def initialize_all_models(self) -> bool:
        """모든 ML 모델 초기화"""
        try:
            logger.info("모든 ML 모델 초기화 시작...")
            
            # 1. 알고리즘 성능 예측 모델
            self.performance_predictor = AlgorithmPerformancePredictor(self.knowledge_base)
            
            # 2. 문제 패턴 분류 모델
            self.pattern_classifier = ProblemPatternClassifier(self.knowledge_base)
            
            # 3. 알고리즘 조합 최적화 모델
            self.combination_optimizer = AlgorithmCombinationOptimizer(self.knowledge_base)
            
            logger.info("모든 ML 모델 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"ML 모델 초기화 실패: {e}")
            return False
    
    def train_all_models(self, force_retrain: bool = False) -> Dict[str, Any]:
        """모든 ML 모델 학습"""
        try:
            if not all([self.performance_predictor, self.pattern_classifier, self.combination_optimizer]):
                self.initialize_all_models()
            
            training_results = {}
            
            # 1. 알고리즘 성능 예측 모델 학습
            logger.info("=== 알고리즘 성능 예측 모델 학습 시작 ===")
            if force_retrain or not self.system_status['performance_predictor_trained']:
                success = self.performance_predictor.train_models()
                if success:
                    self.system_status['performance_predictor_trained'] = True
                    training_results['performance_predictor'] = {
                        'status': 'success',
                        'performance': self.performance_predictor.get_model_performance()
                    }
                    logger.info("성능 예측 모델 학습 성공")
                else:
                    training_results['performance_predictor'] = {'status': 'failed'}
                    logger.error("성능 예측 모델 학습 실패")
            else:
                training_results['performance_predictor'] = {'status': 'already_trained'}
                logger.info("성능 예측 모델 이미 학습됨")
            
            # 2. 문제 패턴 분류 모델 학습
            logger.info("=== 문제 패턴 분류 모델 학습 시작 ===")
            if force_retrain or not self.system_status['pattern_classifier_trained']:
                success = self.pattern_classifier.train_models()
                if success:
                    self.system_status['pattern_classifier_trained'] = True
                    training_results['pattern_classifier'] = {
                        'status': 'success',
                        'performance': self.pattern_classifier.get_model_performance()
                    }
                    logger.info("패턴 분류 모델 학습 성공")
                else:
                    training_results['pattern_classifier'] = {'status': 'failed'}
                    logger.error("패턴 분류 모델 학습 실패")
            else:
                training_results['pattern_classifier'] = {'status': 'already_trained'}
                logger.info("패턴 분류 모델 이미 학습됨")
            
            # 3. 알고리즘 조합 최적화 모델 초기화
            logger.info("=== 알고리즘 조합 최적화 모델 초기화 ===")
            self.combination_optimizer.initialize_optimization_models()
            self.system_status['combination_optimizer_initialized'] = True
            training_results['combination_optimizer'] = {'status': 'initialized'}
            logger.info("조합 최적화 모델 초기화 완료")
            
            # 시스템 상태 업데이트
            self.system_status['last_training_timestamp'] = datetime.now().isoformat()
            
            # 전체 정확도 계산
            self._calculate_overall_accuracy()
            
            logger.info("=== 모든 ML 모델 학습 완료 ===")
            return training_results
            
        except Exception as e:
            logger.error(f"모든 모델 학습 실패: {e}")
            return {'error': str(e)}
    
    def _calculate_overall_accuracy(self):
        """전체 시스템 정확도 계산"""
        try:
            total_accuracy = 0.0
            model_count = 0
            
            if self.performance_predictor and self.system_status['performance_predictor_trained']:
                perf_metrics = self.performance_predictor.get_model_performance()
                if 'success_rate_predictor' in perf_metrics:
                    total_accuracy += perf_metrics['success_rate_predictor'].get('r2', 0.0)
                    model_count += 1
                if 'efficiency_predictor' in perf_metrics:
                    total_accuracy += perf_metrics['efficiency_predictor'].get('r2', 0.0)
                    model_count += 1
            
            if self.pattern_classifier and self.system_status['pattern_classifier_trained']:
                pattern_metrics = self.pattern_classifier.get_model_performance()
                if 'ensemble_classifier' in pattern_metrics:
                    total_accuracy += pattern_metrics['ensemble_classifier'].get('accuracy', 0.0)
                    model_count += 1
            
            if model_count > 0:
                self.system_status['overall_accuracy'] = total_accuracy / model_count
            else:
                self.system_status['overall_accuracy'] = 0.0
                
        except Exception as e:
            logger.error(f"전체 정확도 계산 실패: {e}")
            self.system_status['overall_accuracy'] = 0.0
    
    def integrated_algorithm_recommendation(self, problem_description: str, 
                                          problem_context: Dict[str, Any]) -> Dict[str, Any]:
        """통합 알고리즘 추천 시스템"""
        try:
            if not self._check_models_ready():
                return {'error': '모델이 준비되지 않았습니다'}
            
            recommendation_result = {
                'problem_description': problem_description,
                'problem_context': problem_context,
                'recommendation_timestamp': datetime.now().isoformat(),
                'recommendations': []
            }
            
            # 1. 문제 패턴 분류
            pattern_classification = self.pattern_classifier.classify_problem_pattern(problem_description)
            if pattern_classification:
                recommendation_result['pattern_classification'] = pattern_classification
                
                # 분류된 카테고리 기반으로 알고리즘 필터링
                problem_category = pattern_classification['final_classification']['category']
                filtered_algorithms = self._filter_algorithms_by_category(problem_category)
            else:
                filtered_algorithms = list(self.knowledge_base.algorithms.keys())
            
            # 2. 개별 알고리즘 성능 예측
            algorithm_predictions = {}
            for alg_id in filtered_algorithms[:10]:  # 상위 10개만
                if alg_id in self.knowledge_base.algorithms:
                    alg = self.knowledge_base.algorithms[alg_id]
                    prediction = self.performance_predictor.predict_algorithm_performance(alg)
                    if prediction:
                        algorithm_predictions[alg_id] = prediction
            
            # 3. 알고리즘 조합 최적화
            combination_recommendations = self.combination_optimizer.get_recommended_combinations(
                problem_context, top_k=3
            )
            
            # 4. 통합 추천 결과 생성
            for i, combination_rec in enumerate(combination_recommendations):
                recommendation = {
                    'rank': i + 1,
                    'combination_type': 'optimized_combination',
                    'algorithms': combination_rec['algorithms'],
                    'overall_score': combination_rec['score'],
                    'individual_predictions': {}
                }
                
                # 개별 알고리즘 예측 결과 추가
                for alg_info in combination_rec['algorithms']:
                    alg_id = alg_info['id']
                    if alg_id in algorithm_predictions:
                        recommendation['individual_predictions'][alg_id] = algorithm_predictions[alg_id]
                
                recommendation_result['recommendations'].append(recommendation)
            
            # 5. 단일 알고리즘 추천 (고성능 개별 알고리즘)
            top_individual_algorithms = self._get_top_individual_algorithms(
                algorithm_predictions, top_k=3
            )
            
            for i, (alg_id, prediction) in enumerate(top_individual_algorithms):
                if alg_id in self.knowledge_base.algorithms:
                    alg = self.knowledge_base.algorithms[alg_id]
                    recommendation = {
                        'rank': len(recommendation_result['recommendations']) + i + 1,
                        'combination_type': 'individual_algorithm',
                        'algorithms': [{
                            'id': alg_id,
                            'name': alg.name,
                            'category': alg.category,
                            'success_rate': alg.success_rate,
                            'efficiency_score': alg.efficiency_score
                        }],
                        'overall_score': (prediction.get('predicted_success_rate', 0.0) + 
                                        prediction.get('predicted_efficiency', 0.0)) / 2,
                        'individual_predictions': {alg_id: prediction}
                    }
                    recommendation_result['recommendations'].append(recommendation)
            
            # 추천 결과 정렬
            recommendation_result['recommendations'].sort(key=lambda x: x['overall_score'], reverse=True)
            
            # 통합 메트릭 업데이트
            self._update_integrated_metrics(recommendation_result)
            
            logger.info(f"통합 알고리즘 추천 완료: {len(recommendation_result['recommendations'])}개 추천")
            return recommendation_result
            
        except Exception as e:
            logger.error(f"통합 알고리즘 추천 실패: {e}")
            return {'error': str(e)}
    
    def _check_models_ready(self) -> bool:
        """모든 모델이 준비되었는지 확인"""
        return (self.system_status['performance_predictor_trained'] and
                self.system_status['pattern_classifier_trained'] and
                self.system_status['combination_optimizer_initialized'])
    
    def _filter_algorithms_by_category(self, category: str) -> List[str]:
        """카테고리별 알고리즘 필터링"""
        try:
            filtered_ids = []
            for alg_id, algorithm in self.knowledge_base.algorithms.items():
                if algorithm.category == category:
                    filtered_ids.append(alg_id)
            return filtered_ids
        except Exception as e:
            logger.error(f"카테고리별 필터링 실패: {e}")
            return list(self.knowledge_base.algorithms.keys())
    
    def _get_top_individual_algorithms(self, predictions: Dict[str, Any], 
                                     top_k: int = 3) -> List[Tuple[str, Any]]:
        """상위 개별 알고리즘 선택"""
        try:
            # 성능 점수 계산
            algorithm_scores = []
            for alg_id, prediction in predictions.items():
                success_rate = prediction.get('predicted_success_rate', 0.0)
                efficiency = prediction.get('predicted_efficiency', 0.0)
                overall_score = (success_rate + efficiency) / 2
                algorithm_scores.append((alg_id, prediction, overall_score))
            
            # 점수 기준 정렬
            algorithm_scores.sort(key=lambda x: x[2], reverse=True)
            
            # 상위 K개 반환
            return [(alg_id, prediction) for alg_id, prediction, _ in algorithm_scores[:top_k]]
            
        except Exception as e:
            logger.error(f"상위 알고리즘 선택 실패: {e}")
            return []
    
    def _update_integrated_metrics(self, recommendation_result: Dict[str, Any]):
        """통합 메트릭 업데이트"""
        try:
            self.integrated_metrics['total_predictions'] += 1
            
            if 'recommendations' in recommendation_result and recommendation_result['recommendations']:
                self.integrated_metrics['successful_predictions'] += 1
                
                # 평균 신뢰도 계산
                total_confidence = 0.0
                confidence_count = 0
                
                for rec in recommendation_result['recommendations']:
                    for alg_id, prediction in rec.get('individual_predictions', {}).items():
                        if 'confidence_scores' in prediction:
                            conf_scores = prediction['confidence_scores']
                            avg_conf = sum(conf_scores.values()) / len(conf_scores)
                            total_confidence += avg_conf
                            confidence_count += 1
                
                if confidence_count > 0:
                    current_avg = self.integrated_metrics['average_prediction_confidence']
                    new_avg = total_confidence / confidence_count
                    # 이동 평균 업데이트
                    self.integrated_metrics['average_prediction_confidence'] = (
                        (current_avg * (self.integrated_metrics['total_predictions'] - 1) + new_avg) / 
                        self.integrated_metrics['total_predictions']
                    )
                    
        except Exception as e:
            logger.error(f"통합 메트릭 업데이트 실패: {e}")
    
    def save_all_models(self) -> bool:
        """모든 모델 저장"""
        try:
            if not self.models_directory.exists():
                self.models_directory.mkdir(parents=True)
            
            # 1. 성능 예측 모델 저장
            if self.performance_predictor and self.system_status['performance_predictor_trained']:
                perf_model_path = self.models_directory / "performance_predictor.pkl"
                self.performance_predictor.save_models(str(perf_model_path))
            
            # 2. 패턴 분류 모델 저장
            if self.pattern_classifier and self.system_status['pattern_classifier_trained']:
                pattern_model_path = self.models_directory / "pattern_classifier.pkl"
                self.pattern_classifier.save_models(str(pattern_model_path))
            
            # 3. 조합 최적화 모델 저장
            if self.combination_optimizer and self.system_status['combination_optimizer_initialized']:
                combo_model_path = self.models_directory / "combination_optimizer.pkl"
                self.combination_optimizer.save_optimization_state(str(combo_model_path))
            
            # 4. 시스템 상태 저장
            system_state_path = self.models_directory / "system_state.json"
            with open(system_state_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'system_status': self.system_status,
                    'integrated_metrics': self.integrated_metrics
                }, f, ensure_ascii=False, indent=2)
            
            logger.info("모든 모델 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            return False
    
    def load_all_models(self) -> bool:
        """모든 모델 로드"""
        try:
            if not self.models_directory.exists():
                logger.warning("모델 디렉토리가 존재하지 않습니다")
                return False
            
            # 1. 성능 예측 모델 로드
            perf_model_path = self.models_directory / "performance_predictor.pkl"
            if perf_model_path.exists():
                self.performance_predictor = AlgorithmPerformancePredictor(self.knowledge_base)
                if self.performance_predictor.load_models(str(perf_model_path)):
                    self.system_status['performance_predictor_trained'] = True
                    logger.info("성능 예측 모델 로드 완료")
            
            # 2. 패턴 분류 모델 로드
            pattern_model_path = self.models_directory / "pattern_classifier.pkl"
            if pattern_model_path.exists():
                self.pattern_classifier = ProblemPatternClassifier(self.knowledge_base)
                if self.pattern_classifier.load_models(str(pattern_model_path)):
                    self.system_status['pattern_classifier_trained'] = True
                    logger.info("패턴 분류 모델 로드 완료")
            
            # 3. 조합 최적화 모델 로드
            combo_model_path = self.models_directory / "combination_optimizer.pkl"
            if combo_model_path.exists():
                self.combination_optimizer = AlgorithmCombinationOptimizer(self.knowledge_base)
                if self.combination_optimizer.load_optimization_state(str(combo_model_path)):
                    self.system_status['combination_optimizer_initialized'] = True
                    logger.info("조합 최적화 모델 로드 완료")
            
            # 4. 시스템 상태 로드
            system_state_path = self.models_directory / "system_state.json"
            if system_state_path.exists():
                with open(system_state_path, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    self.system_status.update(state_data.get('system_status', {}))
                    self.integrated_metrics.update(state_data.get('integrated_metrics', {}))
            
            logger.info("모든 모델 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            'system_status': self.system_status.copy(),
            'integrated_metrics': self.integrated_metrics.copy(),
            'models_directory': str(self.models_directory),
            'knowledge_base_size': len(self.knowledge_base.algorithms) if self.knowledge_base else 0
        }
    
    def run_system_diagnostics(self) -> Dict[str, Any]:
        """시스템 진단 실행"""
        try:
            diagnostics = {
                'timestamp': datetime.now().isoformat(),
                'system_health': 'healthy',
                'issues': [],
                'recommendations': []
            }
            
            # 모델 상태 확인
            if not self.system_status['performance_predictor_trained']:
                diagnostics['issues'].append('성능 예측 모델이 학습되지 않음')
                diagnostics['recommendations'].append('모델 학습을 실행하세요')
            
            if not self.system_status['pattern_classifier_trained']:
                diagnostics['issues'].append('패턴 분류 모델이 학습되지 않음')
                diagnostics['recommendations'].append('모델 학습을 실행하세요')
            
            if not self.system_status['combination_optimizer_initialized']:
                diagnostics['issues'].append('조합 최적화 모델이 초기화되지 않음')
                diagnostics['recommendations'].append('모델 초기화를 실행하세요')
            
            # 성능 확인
            if self.system_status['overall_accuracy'] < 0.7:
                diagnostics['issues'].append('전체 정확도가 낮음')
                diagnostics['recommendations'].append('모델 재학습을 고려하세요')
            
            # 시스템 상태 결정
            if diagnostics['issues']:
                diagnostics['system_health'] = 'needs_attention'
            elif self.system_status['overall_accuracy'] < 0.8:
                diagnostics['system_health'] = 'warning'
            
            return diagnostics
            
        except Exception as e:
            logger.error(f"시스템 진단 실패: {e}")
            return {'error': str(e), 'system_health': 'error'}
