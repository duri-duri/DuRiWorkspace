"""
ML 모델 하이퍼파라미터 자동 최적화 시스템
GridSearchCV, RandomizedSearchCV를 사용하여 모든 ML 모델의 성능을 최적화
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import pickle
import json
import time
from pathlib import Path

# 머신러닝 라이브러리
try:
    from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.naive_bayes import GaussianNB
    from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
    from sklearn.preprocessing import StandardScaler
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("머신러닝 라이브러리가 설치되지 않았습니다. pip install scikit-learn xgboost")

from ..algorithm_knowledge.algorithm_knowledge_base import (
    AlgorithmKnowledge, 
    ProblemPattern,
    AlgorithmKnowledgeBase
)

logger = logging.getLogger(__name__)

class MLHyperparameterOptimizer:
    """ML 모델 하이퍼파라미터 자동 최적화 시스템"""
    
    def __init__(self, knowledge_base: AlgorithmKnowledgeBase):
        self.knowledge_base = knowledge_base
        
        # 최적화된 모델들
        self.optimized_models = {}
        
        # 최적화 결과 히스토리
        self.optimization_history = {}
        
        # 하이퍼파라미터 검색 공간
        self.parameter_grids = self._define_parameter_grids()
        
        # 최적화 설정
        self.optimization_config = {
            'cv_folds': 5,
            'n_jobs': -1,  # 모든 CPU 코어 사용
            'random_state': 42,
            'verbose': 1
        }
        
        # 성능 향상 메트릭
        self.improvement_metrics = {
            'before_optimization': {},
            'after_optimization': {},
            'improvement_percentage': {}
        }
        
        logger.info("ML 하이퍼파라미터 최적화 시스템 초기화 완료")
    
    def _define_parameter_grids(self) -> Dict[str, Dict[str, Any]]:
        """각 모델별 하이퍼파라미터 검색 공간 정의"""
        return {
            'random_forest_regressor': {
                'n_estimators': [50, 100, 200, 300],
                'max_depth': [5, 10, 15, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'max_features': ['sqrt', 'log2', None],
                'bootstrap': [True, False]
            },
            'random_forest_classifier': {
                'n_estimators': [50, 100, 200, 300],
                'max_depth': [5, 10, 15, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'max_features': ['sqrt', 'log2', None],
                'criterion': ['gini', 'entropy']
            },
            'xgboost_regressor': {
                'n_estimators': [50, 100, 200, 300],
                'max_depth': [3, 6, 9, 12],
                'learning_rate': [0.01, 0.1, 0.2, 0.3],
                'subsample': [0.8, 0.9, 1.0],
                'colsample_bytree': [0.8, 0.9, 1.0],
                'reg_alpha': [0, 0.1, 1.0],
                'reg_lambda': [0, 0.1, 1.0]
            },
            'svm_classifier': {
                'C': [0.1, 1, 10, 100],
                'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
                'kernel': ['rbf', 'linear', 'poly'],
                'degree': [2, 3, 4],
                'class_weight': ['balanced', None]
            },
            'gaussian_nb': {
                'var_smoothing': [1e-9, 1e-8, 1e-7, 1e-6, 1e-5]
            }
        }
    
    def optimize_all_models(self, training_data: pd.DataFrame, 
                           force_retrain: bool = False) -> Dict[str, Any]:
        """모든 ML 모델의 하이퍼파라미터 최적화"""
        try:
            if not ML_AVAILABLE:
                logger.error("머신러닝 라이브러리가 사용할 수 없습니다")
                return {'error': 'ML 라이브러리 없음'}
            
            logger.info("=== 모든 ML 모델 하이퍼파라미터 최적화 시작 ===")
            
            optimization_results = {}
            start_time = time.time()
            
            # 1. 성공률 예측 모델 (Random Forest) 최적화
            logger.info("성공률 예측 모델 최적화 중...")
            success_rate_result = self._optimize_random_forest_regressor(
                training_data, 'success_rate', 'random_forest_regressor'
            )
            optimization_results['success_rate_predictor'] = success_rate_result
            
            # 2. 효율성 예측 모델 (XGBoost) 최적화
            logger.info("효율성 예측 모델 최적화 중...")
            efficiency_result = self._optimize_xgboost_regressor(
                training_data, 'efficiency_score', 'xgboost_regressor'
            )
            optimization_results['efficiency_predictor'] = efficiency_result
            
            # 3. 복잡도 분류 모델 (Random Forest) 최적화
            logger.info("복잡도 분류 모델 최적화 중...")
            complexity_result = self._optimize_random_forest_classifier(
                training_data, 'complexity_score', 'random_forest_classifier'
            )
            optimization_results['complexity_classifier'] = complexity_result
            
            # 4. 성능 등급 분류 모델 (Random Forest) 최적화
            logger.info("성능 등급 분류 모델 최적화 중...")
            performance_result = self._optimize_random_forest_classifier(
                training_data, 'performance_grade', 'random_forest_classifier'
            )
            optimization_results['performance_classifier'] = performance_result
            
            # 5. SVM 분류기 최적화
            logger.info("SVM 분류기 최적화 중...")
            svm_result = self._optimize_svm_classifier(
                training_data, 'category_encoded', 'svm_classifier'
            )
            optimization_results['svm_classifier'] = svm_result
            
            # 6. Naive Bayes 분류기 최적화
            logger.info("Naive Bayes 분류기 최적화 중...")
            nb_result = self._optimize_naive_bayes_classifier(
                training_data, 'category_encoded', 'gaussian_nb'
            )
            optimization_results['naive_bayes_classifier'] = nb_result
            
            # 최적화 완료 시간 계산
            total_time = time.time() - start_time
            
            # 전체 결과 요약
            summary = {
                'total_optimization_time': total_time,
                'models_optimized': len(optimization_results),
                'optimization_results': optimization_results,
                'timestamp': datetime.now().isoformat()
            }
            
            # 성능 향상 분석
            self._analyze_performance_improvement()
            
            logger.info(f"=== 모든 모델 최적화 완료! 총 소요시간: {total_time:.2f}초 ===")
            return summary
            
        except Exception as e:
            logger.error(f"모든 모델 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _optimize_random_forest_regressor(self, training_data: pd.DataFrame, 
                                        target_column: str, 
                                        model_type: str) -> Dict[str, Any]:
        """Random Forest 회귀 모델 최적화"""
        try:
            # 특성과 타겟 분리
            X = training_data.drop([target_column, 'algorithm_id', 'performance_grade'], axis=1, errors='ignore')
            y = training_data[target_column]
            
            # 데이터 분할
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 특성 스케일링
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 기본 모델 성능 측정
            base_model = RandomForestRegressor(random_state=42)
            base_model.fit(X_train_scaled, y_train)
            base_score = base_model.score(X_test_scaled, y_test)
            
            # GridSearchCV를 통한 최적화
            grid_search = GridSearchCV(
                RandomForestRegressor(random_state=42),
                self.parameter_grids[model_type],
                cv=self.optimization_config['cv_folds'],
                n_jobs=self.optimization_config['n_jobs'],
                verbose=self.optimization_config['verbose'],
                scoring='r2'
            )
            
            grid_search.fit(X_train_scaled, y_train)
            
            # 최적화된 모델
            best_model = grid_search.best_estimator_
            best_score = best_model.score(X_test_scaled, y_test)
            
            # 결과 저장
            result = {
                'model_type': 'RandomForestRegressor',
                'best_parameters': grid_search.best_params_,
                'best_score': best_score,
                'base_score': base_score,
                'improvement': best_score - base_score,
                'improvement_percentage': ((best_score - base_score) / base_score) * 100 if base_score != 0 else 0,
                'cv_results': grid_search.cv_results_,
                'best_model': best_model,
                'scaler': scaler
            }
            
            # 모델 저장
            self.optimized_models[f'{target_column}_predictor'] = {
                'model': best_model,
                'scaler': scaler,
                'feature_names': X.columns.tolist()
            }
            
            logger.info(f"{target_column} 예측 모델 최적화 완료: "
                       f"기본 점수 {base_score:.3f} → 최적 점수 {best_score:.3f} "
                       f"(향상: {result['improvement_percentage']:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"{target_column} 예측 모델 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _optimize_random_forest_classifier(self, training_data: pd.DataFrame, 
                                         target_column: str, 
                                         model_type: str) -> Dict[str, Any]:
        """Random Forest 분류 모델 최적화"""
        try:
            # 특성과 타겟 분리
            X = training_data.drop([target_column, 'algorithm_id', 'performance_grade'], axis=1, errors='ignore')
            y = training_data[target_column]
            
            # 데이터 분할
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # 특성 스케일링
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 기본 모델 성능 측정
            base_model = RandomForestClassifier(random_state=42)
            base_model.fit(X_train_scaled, y_train)
            base_score = base_model.score(X_test_scaled, y_test)
            
            # GridSearchCV를 통한 최적화
            grid_search = GridSearchCV(
                RandomForestClassifier(random_state=42),
                self.parameter_grids[model_type],
                cv=self.optimization_config['cv_folds'],
                n_jobs=self.optimization_config['n_jobs'],
                verbose=self.optimization_config['verbose'],
                scoring='accuracy'
            )
            
            grid_search.fit(X_train_scaled, y_train)
            
            # 최적화된 모델
            best_model = grid_search.best_estimator_
            best_score = best_model.score(X_test_scaled, y_test)
            
            # 결과 저장
            result = {
                'model_type': 'RandomForestClassifier',
                'best_parameters': grid_search.best_params_,
                'best_score': best_score,
                'base_score': base_score,
                'improvement': best_score - base_score,
                'improvement_percentage': ((best_score - base_score) / base_score) * 100 if base_score != 0 else 0,
                'cv_results': grid_search.cv_results_,
                'best_model': best_model,
                'scaler': scaler
            }
            
            # 모델 저장
            model_key = f'{target_column}_classifier'
            self.optimized_models[model_key] = {
                'model': best_model,
                'scaler': scaler,
                'feature_names': X.columns.tolist()
            }
            
            logger.info(f"{target_column} 분류 모델 최적화 완료: "
                       f"기본 정확도 {base_score:.3f} → 최적 정확도 {best_score:.3f} "
                       f"(향상: {result['improvement_percentage']:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"{target_column} 분류 모델 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _optimize_xgboost_regressor(self, training_data: pd.DataFrame, 
                                   target_column: str, 
                                   model_type: str) -> Dict[str, Any]:
        """XGBoost 회귀 모델 최적화"""
        try:
            # 특성과 타겟 분리
            X = training_data.drop([target_column, 'algorithm_id', 'performance_grade'], axis=1, errors='ignore')
            y = training_data[target_column]
            
            # 데이터 분할
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # 특성 스케일링
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 기본 모델 성능 측정
            base_model = xgb.XGBRegressor(random_state=42)
            base_model.fit(X_train_scaled, y_train)
            base_score = base_model.score(X_test_scaled, y_test)
            
            # RandomizedSearchCV를 통한 최적화 (XGBoost는 파라미터가 많아서)
            random_search = RandomizedSearchCV(
                xgb.XGBRegressor(random_state=42),
                self.parameter_grids[model_type],
                n_iter=50,  # 50번 랜덤 시도
                cv=self.optimization_config['cv_folds'],
                n_jobs=self.optimization_config['n_jobs'],
                verbose=self.optimization_config['verbose'],
                scoring='r2',
                random_state=42
            )
            
            random_search.fit(X_train_scaled, y_train)
            
            # 최적화된 모델
            best_model = random_search.best_estimator_
            best_score = best_model.score(X_test_scaled, y_test)
            
            # 결과 저장
            result = {
                'model_type': 'XGBRegressor',
                'best_parameters': random_search.best_params_,
                'best_score': best_score,
                'base_score': base_score,
                'improvement': best_score - base_score,
                'improvement_percentage': ((best_score - base_score) / base_score) * 100 if base_score != 0 else 0,
                'cv_results': random_search.cv_results_,
                'best_model': best_model,
                'scaler': scaler
            }
            
            # 모델 저장
            self.optimized_models[f'{target_column}_predictor'] = {
                'model': best_model,
                'scaler': scaler,
                'feature_names': X.columns.tolist()
            }
            
            logger.info(f"{target_column} 예측 모델 최적화 완료: "
                       f"기본 점수 {base_score:.3f} → 최적 점수 {best_score:.3f} "
                       f"(향상: {result['improvement_percentage']:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"{target_column} 예측 모델 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _optimize_svm_classifier(self, training_data: pd.DataFrame, 
                                target_column: str, 
                                model_type: str) -> Dict[str, Any]:
        """SVM 분류 모델 최적화"""
        try:
            # 특성과 타겟 분리
            X = training_data.drop([target_column, 'algorithm_id', 'performance_grade'], axis=1, errors='ignore')
            y = training_data[target_column]
            
            # 데이터 분할
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # 특성 스케일링
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 기본 모델 성능 측정
            base_model = SVC(random_state=42, probability=True)
            base_model.fit(X_train_scaled, y_train)
            base_score = base_model.score(X_test_scaled, y_test)
            
            # GridSearchCV를 통한 최적화
            grid_search = GridSearchCV(
                SVC(random_state=42, probability=True),
                self.parameter_grids[model_type],
                cv=self.optimization_config['cv_folds'],
                n_jobs=self.optimization_config['n_jobs'],
                verbose=self.optimization_config['verbose'],
                scoring='accuracy'
            )
            
            grid_search.fit(X_train_scaled, y_train)
            
            # 최적화된 모델
            best_model = grid_search.best_estimator_
            best_score = best_model.score(X_test_scaled, y_test)
            
            # 결과 저장
            result = {
                'model_type': 'SVC',
                'best_parameters': grid_search.best_params_,
                'best_score': best_score,
                'base_score': base_score,
                'improvement': best_score - base_score,
                'improvement_percentage': ((best_score - base_score) / base_score) * 100 if base_score != 0 else 0,
                'cv_results': grid_search.cv_results_,
                'best_model': best_model,
                'scaler': scaler
            }
            
            # 모델 저장
            self.optimized_models['svm_classifier'] = {
                'model': best_model,
                'scaler': scaler,
                'feature_names': X.columns.tolist()
            }
            
            logger.info(f"SVM 분류기 최적화 완료: "
                       f"기본 정확도 {base_score:.3f} → 최적 정확도 {best_score:.3f} "
                       f"(향상: {result['improvement_percentage']:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"SVM 분류기 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _optimize_naive_bayes_classifier(self, training_data: pd.DataFrame, 
                                        target_column: str, 
                                        model_type: str) -> Dict[str, Any]:
        """Naive Bayes 분류 모델 최적화"""
        try:
            # 특성과 타겟 분리
            X = training_data.drop([target_column, 'algorithm_id', 'performance_grade'], axis=1, errors='ignore')
            y = training_data[target_column]
            
            # 데이터 분할
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # 특성 스케일링
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 기본 모델 성능 측정
            base_model = GaussianNB()
            base_model.fit(X_train_scaled, y_train)
            base_score = base_model.score(X_test_scaled, y_test)
            
            # GridSearchCV를 통한 최적화
            grid_search = GridSearchCV(
                GaussianNB(),
                self.parameter_grids[model_type],
                cv=self.optimization_config['cv_folds'],
                n_jobs=self.optimization_config['n_jobs'],
                verbose=self.optimization_config['verbose'],
                scoring='accuracy'
            )
            
            grid_search.fit(X_train_scaled, y_train)
            
            # 최적화된 모델
            best_model = grid_search.best_estimator_
            best_score = best_model.score(X_test_scaled, y_test)
            
            # 결과 저장
            result = {
                'model_type': 'GaussianNB',
                'best_parameters': grid_search.best_params_,
                'best_score': best_score,
                'base_score': base_score,
                'improvement': best_score - base_score,
                'improvement_percentage': ((best_score - base_score) / base_score) * 100 if base_score != 0 else 0,
                'cv_results': grid_search.cv_results_,
                'best_model': best_model,
                'scaler': scaler
            }
            
            # 모델 저장
            self.optimized_models['naive_bayes_classifier'] = {
                'model': best_model,
                'scaler': scaler,
                'feature_names': X.columns.tolist()
            }
            
            logger.info(f"Naive Bayes 분류기 최적화 완료: "
                       f"기본 정확도 {base_score:.3f} → 최적 정확도 {best_score:.3f} "
                       f"(향상: {result['improvement_percentage']:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Naive Bayes 분류기 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _analyze_performance_improvement(self):
        """성능 향상 분석"""
        try:
            total_improvement = 0.0
            model_count = 0
            
            for model_name, model_data in self.optimized_models.items():
                if 'model' in model_data:
                    # 모델 성능 메트릭 계산
                    if hasattr(model_data['model'], 'score'):
                        # 실제 성능 측정은 별도 데이터로 해야 함
                        pass
                    model_count += 1
            
            logger.info(f"총 {model_count}개 모델 최적화 완료")
            
        except Exception as e:
            logger.error(f"성능 향상 분석 실패: {e}")
    
    def get_optimized_models(self) -> Dict[str, Any]:
        """최적화된 모델들 반환"""
        return self.optimized_models.copy()
    
    def save_optimized_models(self, filepath: str) -> bool:
        """최적화된 모델들을 파일로 저장"""
        try:
            models_data = {
                'optimized_models': self.optimized_models,
                'optimization_history': self.optimization_history,
                'improvement_metrics': self.improvement_metrics,
                'parameter_grids': self.parameter_grids
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(models_data, f)
            
            logger.info(f"최적화된 모델 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            return False
    
    def load_optimized_models(self, filepath: str) -> bool:
        """저장된 최적화 모델들을 파일에서 로드"""
        try:
            with open(filepath, 'rb') as f:
                models_data = pickle.load(f)
            
            self.optimized_models = models_data['optimized_models']
            self.optimization_history = models_data['optimization_history']
            self.improvement_metrics = models_data['improvement_metrics']
            self.parameter_grids = models_data['parameter_grids']
            
            logger.info(f"최적화된 모델 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """최적화 결과 요약"""
        summary = {
            'total_models': len(self.optimized_models),
            'model_types': list(self.optimized_models.keys()),
            'parameter_grids': self.parameter_grids,
            'optimization_config': self.optimization_config
        }
        return summary
