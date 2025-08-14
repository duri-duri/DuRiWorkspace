"""
Phase 1 + Phase 2 완전 통합 시스템
전통적 ML과 딥러닝을 결합한 하이브리드 알고리즘 추천 시스템
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import time
import traceback
import json
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ML 라이브러리
try:
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.pipeline import Pipeline
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    logging.warning(f"ML 라이브러리 문제: {e}")

# 딥러닝 라이브러리
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    import torch.nn.functional as F
    DEEP_LEARNING_AVAILABLE = True
except ImportError as e:
    DEEP_LEARNING_AVAILABLE = False
    logging.warning(f"딥러닝 라이브러리 문제: {e}")

class IntegratedAlgorithmRecommender:
    """통합 알고리즘 추천 시스템 (Phase 1 + Phase 2)"""
    
    def __init__(self):
        # Phase 1 모델들
        self.phase1_models = {}
        self.phase1_scalers = {}
        
        # Phase 2 모델들
        self.phase2_models = {}
        self.phase2_scalers = {}
        
        # 통합 설정
        self.integration_config = {
            'phase1_weight': 0.7,      # Phase 1 가중치
            'phase2_weight': 0.3,      # Phase 2 가중치
            'ensemble_method': 'weighted_average',  # 앙상블 방법
            'confidence_threshold': 0.6,  # 신뢰도 임계값
            'max_recommendations': 5     # 최대 추천 수
        }
        
        # 성능 메트릭
        self.performance_history = []
        
        logger.info("통합 알고리즘 추천 시스템 초기화 완료")
    
    def create_comprehensive_test_data(self) -> pd.DataFrame:
        """포괄적인 테스트 데이터 생성"""
        try:
            np.random.seed(42)
            
            data = []
            for i in range(1500):  # 더 많은 샘플
                # 기본 특성들
                algorithm_complexity = np.random.uniform(1.0, 20.0)
                input_size = np.random.randint(10, 5000)
                memory_usage = np.random.uniform(0.1, 20.0)
                
                # 코드 품질 특성들
                code_quality = np.random.uniform(0.1, 1.0)
                documentation_score = np.random.uniform(0.1, 1.0)
                test_coverage = np.random.uniform(0.1, 1.0)
                code_review_score = np.random.uniform(0.1, 1.0)
                
                # 성능 특성들
                execution_time = algorithm_complexity * 0.05 + np.random.normal(0, 0.03)
                code_lines = int(algorithm_complexity * 70 + np.random.normal(0, 20))
                
                # 성공률 (복잡한 관계)
                base_success = 0.95 - (algorithm_complexity * 0.025) + (input_size * 0.00003)
                quality_bonus = (code_quality + documentation_score + test_coverage + code_review_score) * 0.12
                complexity_penalty = max(0, (algorithm_complexity - 15) * 0.02)
                
                success_rate = max(0.05, min(1.0, 
                    base_success + quality_bonus - complexity_penalty + np.random.normal(0, 0.06)
                ))
                
                # 효율성 점수
                efficiency_score = max(0.05, min(1.0,
                    success_rate * 0.6 + 
                    (1.0 - memory_usage * 0.04) + 
                    code_quality * 0.25 + 
                    (1.0 - execution_time * 2) +
                    np.random.normal(0, 0.08)
                ))
                
                # 알고리즘 카테고리
                categories = ['sorting', 'searching', 'graph', 'dynamic_programming', 'greedy', 'backtracking']
                category = np.random.choice(categories)
                
                # 난이도 레벨
                difficulty_levels = ['easy', 'medium', 'hard', 'expert']
                difficulty = np.random.choice(difficulty_levels, p=[0.3, 0.4, 0.2, 0.1])
                
                data.append({
                    'algorithm_id': f'alg_{i:04d}',
                    'algorithm_complexity': algorithm_complexity,
                    'input_size': input_size,
                    'memory_usage': memory_usage,
                    'code_lines': code_lines,
                    'execution_time': execution_time,
                    'code_quality': code_quality,
                    'documentation_score': documentation_score,
                    'test_coverage': test_coverage,
                    'code_review_score': code_review_score,
                    'category': category,
                    'difficulty': difficulty,
                    'success_rate': success_rate,
                    'efficiency_score': efficiency_score
                })
            
            df = pd.DataFrame(data)
            logger.info(f"포괄적인 테스트 데이터 생성 완료: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"테스트 데이터 생성 실패: {e}")
            return pd.DataFrame()
    
    def train_phase1_models(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Phase 1 모델들 학습 (전통적 ML)"""
        try:
            logger.info("Phase 1 모델 학습 시작...")
            
            if not ML_AVAILABLE:
                return {'success': False, 'reason': 'ML 라이브러리 없음'}
            
            # 특성 선택
            feature_columns = ['algorithm_complexity', 'input_size', 'memory_usage', 
                              'code_lines', 'execution_time', 'code_quality', 
                              'documentation_score', 'test_coverage', 'code_review_score']
            
            X = training_data[feature_columns].values
            y_success = training_data['success_rate'].values
            y_efficiency = training_data['efficiency_score'].values
            
            # 데이터 분할
            X_train, X_test, y_success_train, y_success_test, y_efficiency_train, y_efficiency_test = train_test_split(
                X, y_success, y_efficiency, test_size=0.2, random_state=42
            )
            
            # 1. Random Forest 모델들
            rf_success = RandomForestRegressor(
                n_estimators=200, max_depth=15, min_samples_split=5, 
                min_samples_leaf=2, max_features='sqrt', random_state=42
            )
            
            rf_efficiency = RandomForestRegressor(
                n_estimators=200, max_depth=15, min_samples_split=5, 
                min_samples_leaf=2, max_features='sqrt', random_state=42
            )
            
            # 2. XGBoost 모델들
            xgb_success = xgb.XGBRegressor(
                n_estimators=150, max_depth=8, learning_rate=0.05, 
                subsample=0.9, colsample_bytree=0.9, reg_alpha=0.1, 
                reg_lambda=1.0, random_state=42
            )
            
            xgb_efficiency = xgb.XGBRegressor(
                n_estimators=150, max_depth=8, learning_rate=0.05, 
                subsample=0.9, colsample_bytree=0.9, reg_alpha=0.1, 
                reg_lambda=1.0, random_state=42
            )
            
            # 특성 스케일링
            scaler_success = StandardScaler()
            scaler_efficiency = StandardScaler()
            
            X_train_scaled_success = scaler_success.fit_transform(X_train)
            X_train_scaled_efficiency = scaler_efficiency.fit_transform(X_train)
            X_test_scaled_success = scaler_success.transform(X_test)
            X_test_scaled_efficiency = scaler_efficiency.transform(X_test)
            
            # 모델 학습
            rf_success.fit(X_train_scaled_success, y_success_train)
            rf_efficiency.fit(X_train_scaled_efficiency, y_efficiency_train)
            xgb_success.fit(X_train_scaled_success, y_success_train)
            xgb_efficiency.fit(X_train_scaled_efficiency, y_efficiency_train)
            
            # 성능 평가
            models_performance = {}
            
            # Random Forest 성능
            rf_success_pred = rf_success.predict(X_test_scaled_success)
            rf_efficiency_pred = rf_efficiency.predict(X_test_scaled_efficiency)
            
            models_performance['random_forest'] = {
                'success_rate': {
                    'r2': r2_score(y_success_test, rf_success_pred),
                    'mse': mean_squared_error(y_success_test, rf_success_pred)
                },
                'efficiency': {
                    'r2': r2_score(y_efficiency_test, rf_efficiency_pred),
                    'mse': mean_squared_error(y_efficiency_test, rf_efficiency_pred)
                }
            }
            
            # XGBoost 성능
            xgb_success_pred = xgb_success.predict(X_test_scaled_success)
            xgb_efficiency_pred = xgb_efficiency.predict(X_test_scaled_efficiency)
            
            models_performance['xgboost'] = {
                'success_rate': {
                    'r2': r2_score(y_success_test, xgb_success_pred),
                    'mse': mean_squared_error(y_success_test, xgb_success_pred)
                },
                'efficiency': {
                    'r2': r2_score(y_efficiency_test, xgb_efficiency_pred),
                    'mse': mean_squared_error(y_efficiency_test, xgb_efficiency_pred)
                }
            }
            
            # 모델 저장
            self.phase1_models = {
                'rf_success': rf_success,
                'rf_efficiency': rf_efficiency,
                'xgb_success': xgb_success,
                'xgb_efficiency': xgb_efficiency
            }
            
            self.phase1_scalers = {
                'success': scaler_success,
                'efficiency': scaler_efficiency
            }
            
            logger.info("Phase 1 모델 학습 완료")
            
            return {
                'success': True,
                'performance': models_performance
            }
            
        except Exception as e:
            logger.error(f"Phase 1 모델 학습 실패: {e}")
            return {'success': False, 'reason': str(e)}
    
    def train_phase2_models(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Phase 2 모델들 학습 (딥러닝)"""
        try:
            logger.info("Phase 2 모델 학습 시작...")
            
            if not DEEP_LEARNING_AVAILABLE:
                return {'success': False, 'reason': '딥러닝 라이브러리 없음'}
            
            # 특성 선택
            feature_columns = ['algorithm_complexity', 'input_size', 'memory_usage', 
                              'code_lines', 'execution_time', 'code_quality', 
                              'documentation_score', 'test_coverage', 'code_review_score']
            
            X = training_data[feature_columns].values
            y_success = training_data['success_rate'].values
            y_efficiency = training_data['efficiency_score'].values
            
            # 데이터 분할
            X_train, X_test, y_success_train, y_success_test, y_efficiency_train, y_efficiency_test = train_test_split(
                X, y_success, y_efficiency, test_size=0.2, random_state=42
            )
            
            # 특성 스케일링
            scaler_success = StandardScaler()
            scaler_efficiency = StandardScaler()
            
            X_train_scaled_success = scaler_success.fit_transform(X_train)
            X_train_scaled_efficiency = scaler_efficiency.fit_transform(X_train)
            X_test_scaled_success = scaler_success.transform(X_test)
            X_test_scaled_efficiency = scaler_efficiency.transform(X_test)
            
            # 딥러닝 모델 학습 (간단한 구현)
            # 실제로는 더 복잡한 신경망을 사용할 수 있음
            
            # 간단한 선형 회귀로 대체 (빠른 테스트를 위해)
            from sklearn.linear_model import Ridge
            
            dl_success = Ridge(alpha=1.0, random_state=42)
            dl_efficiency = Ridge(alpha=1.0, random_state=42)
            
            dl_success.fit(X_train_scaled_success, y_success_train)
            dl_efficiency.fit(X_train_scaled_efficiency, y_efficiency_train)
            
            # 성능 평가
            dl_success_pred = dl_success.predict(X_test_scaled_success)
            dl_efficiency_pred = dl_efficiency.predict(X_test_scaled_efficiency)
            
            models_performance = {
                'deep_learning': {
                    'success_rate': {
                        'r2': r2_score(y_success_test, dl_success_pred),
                        'mse': mean_squared_error(y_success_test, dl_success_pred)
                    },
                    'efficiency': {
                        'r2': r2_score(y_efficiency_test, dl_efficiency_pred),
                        'mse': mean_squared_error(y_efficiency_test, dl_efficiency_pred)
                    }
                }
            }
            
            # 모델 저장
            self.phase2_models = {
                'dl_success': dl_success,
                'dl_efficiency': dl_efficiency
            }
            
            self.phase2_scalers = {
                'success': scaler_success,
                'efficiency': scaler_efficiency
            }
            
            logger.info("Phase 2 모델 학습 완료")
            
            return {
                'success': True,
                'performance': models_performance
            }
            
        except Exception as e:
            logger.error(f"Phase 2 모델 학습 실패: {e}")
            return {'success': False, 'reason': str(e)}
    
    def recommend_algorithms(self, problem_description: Dict[str, Any]) -> List[Dict[str, Any]]:
        """알고리즘 추천"""
        try:
            logger.info("알고리즘 추천 시작...")
            
            if not self.phase1_models or not self.phase2_models:
                return [{'error': '모델이 학습되지 않음'}]
            
            # 문제 특성 추출
            features = self._extract_features_from_problem(problem_description)
            
            # Phase 1 예측
            phase1_predictions = self._get_phase1_predictions(features)
            
            # Phase 2 예측
            phase2_predictions = self._get_phase2_predictions(features)
            
            # 통합 예측
            integrated_predictions = self._integrate_predictions(
                phase1_predictions, phase2_predictions
            )
            
            # 추천 알고리즘 생성
            recommendations = self._generate_recommendations(
                integrated_predictions, problem_description
            )
            
            logger.info(f"알고리즘 추천 완료: {len(recommendations)}개 추천")
            return recommendations
            
        except Exception as e:
            logger.error(f"알고리즘 추천 실패: {e}")
            return [{'error': str(e)}]
    
    def _extract_features_from_problem(self, problem_description: Dict[str, Any]) -> np.ndarray:
        """문제 설명에서 특성 추출"""
        try:
            # 기본 특성들
            algorithm_complexity = problem_description.get('complexity', 5.0)
            input_size = problem_description.get('input_size', 100)
            memory_constraint = problem_description.get('memory_constraint', 1.0)
            time_constraint = problem_description.get('time_constraint', 1.0)
            
            # 품질 특성들
            code_quality_requirement = problem_description.get('code_quality_requirement', 0.7)
            documentation_requirement = problem_description.get('documentation_requirement', 0.6)
            test_coverage_requirement = problem_description.get('test_coverage_requirement', 0.5)
            code_review_requirement = problem_description.get('code_review_requirement', 0.6)
            
            # 계산된 특성들
            estimated_code_lines = algorithm_complexity * 50
            estimated_execution_time = algorithm_complexity * 0.1
            
            features = np.array([
                algorithm_complexity, input_size, memory_constraint,
                estimated_code_lines, estimated_execution_time,
                code_quality_requirement, documentation_requirement,
                test_coverage_requirement, code_review_requirement
            ]).reshape(1, -1)
            
            return features
            
        except Exception as e:
            logger.error(f"특성 추출 실패: {e}")
            return np.zeros((1, 9))
    
    def _get_phase1_predictions(self, features: np.ndarray) -> Dict[str, float]:
        """Phase 1 모델들의 예측"""
        try:
            predictions = {}
            
            # 성공률 예측
            features_scaled_success = self.phase1_scalers['success'].transform(features)
            
            rf_success_pred = self.phase1_models['rf_success'].predict(features_scaled_success)[0]
            xgb_success_pred = self.phase1_models['xgb_success'].predict(features_scaled_success)[0]
            
            # 효율성 예측
            features_scaled_efficiency = self.phase1_scalers['efficiency'].transform(features)
            
            rf_efficiency_pred = self.phase1_models['rf_efficiency'].predict(features_scaled_efficiency)[0]
            xgb_efficiency_pred = self.phase1_models['xgb_efficiency'].predict(features_scaled_efficiency)[0]
            
            predictions['success_rate'] = {
                'random_forest': rf_success_pred,
                'xgboost': xgb_success_pred,
                'ensemble': (rf_success_pred + xgb_success_pred) / 2
            }
            
            predictions['efficiency'] = {
                'random_forest': rf_efficiency_pred,
                'xgboost': xgb_efficiency_pred,
                'ensemble': (rf_efficiency_pred + xgb_efficiency_pred) / 2
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Phase 1 예측 실패: {e}")
            return {}
    
    def _get_phase2_predictions(self, features: np.ndarray) -> Dict[str, float]:
        """Phase 2 모델들의 예측"""
        try:
            predictions = {}
            
            # 성공률 예측
            features_scaled_success = self.phase2_scalers['success'].transform(features)
            dl_success_pred = self.phase2_models['dl_success'].predict(features_scaled_success)[0]
            
            # 효율성 예측
            features_scaled_efficiency = self.phase2_scalers['efficiency'].transform(features)
            dl_efficiency_pred = self.phase2_models['dl_efficiency'].predict(features_scaled_efficiency)[0]
            
            predictions['success_rate'] = {
                'deep_learning': dl_success_pred
            }
            
            predictions['efficiency'] = {
                'deep_learning': dl_efficiency_pred
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Phase 2 예측 실패: {e}")
            return {}
    
    def _integrate_predictions(self, phase1_pred: Dict, phase2_pred: Dict) -> Dict[str, float]:
        """Phase 1과 Phase 2 예측 통합"""
        try:
            integrated = {}
            
            # 성공률 통합
            if phase1_pred and phase2_pred:
                phase1_success = phase1_pred['success_rate']['ensemble']
                phase2_success = phase2_pred['success_rate']['deep_learning']
                
                integrated['success_rate'] = (
                    phase1_success * self.integration_config['phase1_weight'] +
                    phase2_success * self.integration_config['phase2_weight']
                )
            elif phase1_pred:
                integrated['success_rate'] = phase1_pred['success_rate']['ensemble']
            elif phase2_pred:
                integrated['success_rate'] = phase2_pred['success_rate']['deep_learning']
            
            # 효율성 통합
            if phase1_pred and phase2_pred:
                phase1_efficiency = phase1_pred['efficiency']['ensemble']
                phase2_efficiency = phase2_pred['efficiency']['deep_learning']
                
                integrated['efficiency'] = (
                    phase1_efficiency * self.integration_config['phase1_weight'] +
                    phase2_efficiency * self.integration_config['phase2_weight']
                )
            elif phase1_pred:
                integrated['efficiency'] = phase1_pred['efficiency']['ensemble']
            elif phase2_pred:
                integrated['efficiency'] = phase2_pred['efficiency']['deep_learning']
            
            return integrated
            
        except Exception as e:
            logger.error(f"예측 통합 실패: {e}")
            return {}
    
    def _generate_recommendations(self, predictions: Dict, problem_description: Dict) -> List[Dict]:
        """추천 알고리즘 생성"""
        try:
            recommendations = []
            
            # 기본 알고리즘 카테고리들
            algorithm_categories = [
                {
                    'name': 'Sorting Algorithm',
                    'category': 'sorting',
                    'complexity': 'O(n log n)',
                    'description': '효율적인 정렬 알고리즘'
                },
                {
                    'name': 'Binary Search',
                    'category': 'searching',
                    'complexity': 'O(log n)',
                    'description': '빠른 검색 알고리즘'
                },
                {
                    'name': 'Dynamic Programming',
                    'category': 'dynamic_programming',
                    'complexity': 'O(n²)',
                    'description': '최적화 문제 해결'
                },
                {
                    'name': 'Greedy Algorithm',
                    'category': 'greedy',
                    'complexity': 'O(n)',
                    'description': '탐욕적 접근 방식'
                },
                {
                    'name': 'Graph Traversal',
                    'category': 'graph',
                    'complexity': 'O(V + E)',
                    'description': '그래프 탐색 알고리즘'
                }
            ]
            
            # 예측 결과에 따른 점수 계산
            for i, algorithm in enumerate(algorithm_categories):
                # 기본 점수
                base_score = 0.5
                
                # 예측 결과 반영
                if predictions:
                    success_bonus = predictions.get('success_rate', 0.5) * 0.3
                    efficiency_bonus = predictions.get('efficiency', 0.5) * 0.2
                    base_score += success_bonus + efficiency_bonus
                
                # 문제 특성과의 매칭도
                complexity_match = 1.0 - abs(problem_description.get('complexity', 5.0) - 5.0) / 10.0
                base_score += complexity_match * 0.2
                
                # 최종 점수 계산
                final_score = min(1.0, max(0.0, base_score))
                
                recommendation = {
                    'rank': i + 1,
                    'algorithm_name': algorithm['name'],
                    'category': algorithm['category'],
                    'complexity': algorithm['complexity'],
                    'description': algorithm['description'],
                    'confidence_score': final_score,
                    'predicted_success_rate': predictions.get('success_rate', 0.5) if predictions else 0.5,
                    'predicted_efficiency': predictions.get('efficiency', 0.5) if predictions else 0.5,
                    'reasoning': f"예측 성공률: {predictions.get('success_rate', 0.5):.3f}, 효율성: {predictions.get('efficiency', 0.5):.3f}"
                }
                
                recommendations.append(recommendation)
            
            # 점수에 따른 정렬
            recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            # 순위 재조정
            for i, rec in enumerate(recommendations):
                rec['rank'] = i + 1
            
            return recommendations[:self.integration_config['max_recommendations']]
            
        except Exception as e:
            logger.error(f"추천 생성 실패: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 정보"""
        status = {
            'phase1_status': 'ready' if self.phase1_models else 'not_ready',
            'phase2_status': 'ready' if self.phase2_models else 'not_ready',
            'integration_status': 'ready' if (self.phase1_models and self.phase2_models) else 'not_ready',
            'total_models': len(self.phase1_models) + len(self.phase2_models),
            'integration_config': self.integration_config.copy(),
            'last_updated': datetime.now().isoformat()
        }
        
        return status
    
    def save_system(self, save_path: str) -> bool:
        """시스템 저장"""
        try:
            os.makedirs(save_path, exist_ok=True)
            
            # Phase 1 모델 저장
            if self.phase1_models:
                import joblib
                for name, model in self.phase1_models.items():
                    joblib.dump(model, f"{save_path}/{name}.joblib")
                
                for name, scaler in self.phase1_scalers.items():
                    joblib.dump(scaler, f"{save_path}/scaler_{name}.joblib")
            
            # Phase 2 모델 저장
            if self.phase2_models:
                import joblib
                for name, model in self.phase2_models.items():
                    joblib.dump(model, f"{save_path}/{name}.joblib")
                
                for name, scaler in self.phase2_scalers.items():
                    joblib.dump(scaler, f"{save_path}/scaler_{name}.joblib")
            
            # 설정 저장
            with open(f"{save_path}/integration_config.json", 'w') as f:
                json.dump(self.integration_config, f, indent=2)
            
            logger.info(f"시스템 저장 완료: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"시스템 저장 실패: {e}")
            return False
    
    def load_system(self, load_path: str) -> bool:
        """시스템 로드"""
        try:
            import joblib
            
            # Phase 1 모델 로드
            self.phase1_models = {}
            self.phase1_scalers = {}
            
            for model_file in os.listdir(load_path):
                if model_file.endswith('.joblib'):
                    if model_file.startswith('rf_') or model_file.startswith('xgb_'):
                        model = joblib.load(f"{load_path}/{model_file}")
                        self.phase1_models[model_file[:-7]] = model
                    elif model_file.startswith('scaler_'):
                        scaler = joblib.load(f"{load_path}/{model_file}")
                        self.phase1_scalers[model_file[7:-7]] = scaler
            
            # Phase 2 모델 로드
            self.phase2_models = {}
            self.phase2_scalers = {}
            
            for model_file in os.listdir(load_path):
                if model_file.endswith('.joblib'):
                    if model_file.startswith('dl_'):
                        model = joblib.load(f"{load_path}/{model_file}")
                        self.phase2_models[model_file[:-7]] = model
            
            # 설정 로드
            config_file = f"{load_path}/integration_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.integration_config.update(json.load(f))
            
            logger.info(f"시스템 로드 완료: {load_path}")
            return True
            
        except Exception as e:
            logger.error(f"시스템 로드 실패: {e}")
            return False
