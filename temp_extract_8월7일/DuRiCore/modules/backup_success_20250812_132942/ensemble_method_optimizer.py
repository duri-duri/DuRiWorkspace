"""
앙상블 방법 최적화 시스템
Stacking, Blending, 가중 앙상블을 통한 고급 앙상블 전략 구현
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
import logging
from datetime import datetime
import pickle
import json
import time
from pathlib import Path

# 머신러닝 라이브러리
try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, VotingRegressor, VotingClassifier
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.svm import SVC
    from sklearn.naive_bayes import GaussianNB
    from sklearn.model_selection import cross_val_predict, KFold, StratifiedKFold
    from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, r2_score
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

class EnsembleMethodOptimizer:
    """앙상블 방법 최적화 시스템"""
    
    def __init__(self, knowledge_base: AlgorithmKnowledgeBase):
        self.knowledge_base = knowledge_base
        
        # 앙상블 모델들
        self.ensemble_models = {}
        
        # 앙상블 성능 메트릭
        self.ensemble_performance = {}
        
        # 앙상블 설정
        self.ensemble_config = {
            'cv_folds': 5,
            'random_state': 42,
            'test_size': 0.2,
            'meta_learner_type': 'linear',  # 'linear', 'rf', 'svm'
            'stacking_method': 'cv',  # 'cv', 'holdout'
            'blending_ratio': 0.3,  # 검증 세트 비율
            'weight_optimization': True
        }
        
        # 기본 모델들
        self.base_models = {}
        
        # 메타 모델들
        self.meta_models = {}
        
        logger.info("앙상블 방법 최적화 시스템 초기화 완료")
    
    def create_base_models(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """기본 모델들 생성"""
        try:
            logger.info("기본 모델들 생성 중...")
            
            base_models = {}
            
            # 1. Random Forest 모델들
            base_models['rf_regressor'] = RandomForestRegressor(
                n_estimators=100, max_depth=10, random_state=42
            )
            base_models['rf_classifier'] = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42
            )
            
            # 2. XGBoost 모델들
            base_models['xgb_regressor'] = xgb.XGBRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
            )
            base_models['xgb_classifier'] = xgb.XGBClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
            )
            
            # 3. SVM 모델
            base_models['svm_classifier'] = SVC(
                kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42
            )
            
            # 4. Naive Bayes 모델
            base_models['nb_classifier'] = GaussianNB()
            
            # 5. 선형 모델들
            base_models['linear_regressor'] = LinearRegression()
            base_models['logistic_classifier'] = LogisticRegression(random_state=42)
            
            self.base_models = base_models
            
            logger.info(f"기본 모델 {len(base_models)}개 생성 완료")
            return {'status': 'success', 'model_count': len(base_models)}
            
        except Exception as e:
            logger.error(f"기본 모델 생성 실패: {e}")
            return {'error': str(e)}
    
    def create_ensemble_methods(self, training_data: pd.DataFrame, 
                               target_columns: List[str]) -> Dict[str, Any]:
        """다양한 앙상블 방법 생성"""
        try:
            logger.info("앙상블 방법 생성 시작...")
            
            ensemble_results = {}
            
            for target in target_columns:
                if target in training_data.columns:
                    logger.info(f"{target}에 대한 앙상블 방법 생성 중...")
                    
                    # 특성과 타겟 분리
                    X = training_data.drop([target, 'algorithm_id', 'performance_grade'], axis=1, errors='ignore')
                    y = training_data[target]
                    
                    # 수치형 특성만 선택
                    X_numerical = X.select_dtypes(include=[np.number])
                    
                    if len(X_numerical.columns) == 0:
                        continue
                    
                    # 데이터 분할
                    from sklearn.model_selection import train_test_split
                    X_train, X_test, y_train, y_test = train_test_split(
                        X_numerical, y, test_size=self.ensemble_config['test_size'], 
                        random_state=self.ensemble_config['random_state'],
                        stratify=y if target not in ['success_rate', 'efficiency_score', 'complexity_score'] else None
                    )
                    
                    # 특성 스케일링
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    # 타겟 타입에 따른 앙상블 방법 생성
                    if target in ['success_rate', 'efficiency_score', 'complexity_score']:
                        # 회귀 문제
                        ensemble_methods = self._create_regression_ensembles(
                            X_train_scaled, y_train, X_test_scaled, y_test, target
                        )
                    else:
                        # 분류 문제
                        ensemble_methods = self._create_classification_ensembles(
                            X_train_scaled, y_train, X_test_scaled, y_test, target
                        )
                    
                    ensemble_results[target] = ensemble_methods
            
            self.ensemble_models = ensemble_results
            
            logger.info(f"앙상블 방법 생성 완료: {len(ensemble_results)}개 타겟에 대해 생성")
            return ensemble_results
            
        except Exception as e:
            logger.error(f"앙상블 방법 생성 실패: {e}")
            return {'error': str(e)}
    
    def _create_regression_ensembles(self, X_train: np.ndarray, y_train: np.ndarray,
                                   X_test: np.ndarray, y_test: np.ndarray,
                                   target: str) -> Dict[str, Any]:
        """회귀 문제를 위한 앙상블 방법 생성"""
        try:
            ensembles = {}
            
            # 1. Voting Regressor (하드 보팅)
            voting_regressor = VotingRegressor([
                ('rf', self.base_models['rf_regressor']),
                ('xgb', self.base_models['xgb_regressor']),
                ('linear', self.base_models['linear_regressor'])
            ])
            
            voting_regressor.fit(X_train, y_train)
            voting_score = voting_regressor.score(X_test, y_test)
            
            ensembles['voting_regressor'] = {
                'model': voting_regressor,
                'score': voting_score,
                'type': 'voting'
            }
            
            # 2. Stacking (Cross-Validation 기반)
            stacking_result = self._create_stacking_regressor(X_train, y_train, X_test, y_test)
            ensembles['stacking_regressor'] = stacking_result
            
            # 3. Blending
            blending_result = self._create_blending_regressor(X_train, y_train, X_test, y_test)
            ensembles['blending_regressor'] = blending_result
            
            # 4. 가중 앙상블
            weighted_result = self._create_weighted_regressor(X_train, y_train, X_test, y_test)
            ensembles['weighted_regressor'] = weighted_result
            
            # 5. 성능 비교
            performance_comparison = self._compare_regression_ensembles(ensembles, X_test, y_test)
            ensembles['performance_comparison'] = performance_comparison
            
            return ensembles
            
        except Exception as e:
            logger.error(f"회귀 앙상블 생성 실패: {e}")
            return {'error': str(e)}
    
    def _create_classification_ensembles(self, X_train: np.ndarray, y_train: np.ndarray,
                                       X_test: np.ndarray, y_test: np.ndarray,
                                       target: str) -> Dict[str, Any]:
        """분류 문제를 위한 앙상블 방법 생성"""
        try:
            ensembles = {}
            
            # 1. Voting Classifier (소프트 보팅)
            voting_classifier = VotingClassifier([
                ('rf', self.base_models['rf_classifier']),
                ('xgb', self.base_models['xgb_classifier']),
                ('svm', self.base_models['svm_classifier']),
                ('nb', self.base_models['nb_classifier'])
            ], voting='soft')
            
            voting_classifier.fit(X_train, y_train)
            voting_score = voting_classifier.score(X_test, y_test)
            
            ensembles['voting_classifier'] = {
                'model': voting_classifier,
                'score': voting_score,
                'type': 'voting'
            }
            
            # 2. Stacking (Cross-Validation 기반)
            stacking_result = self._create_stacking_classifier(X_train, y_train, X_test, y_test)
            ensembles['stacking_classifier'] = stacking_result
            
            # 3. Blending
            blending_result = self._create_blending_classifier(X_train, y_train, X_test, y_test)
            ensembles['blending_classifier'] = blending_result
            
            # 4. 가중 앙상블
            weighted_result = self._create_weighted_classifier(X_train, y_train, X_test, y_test)
            ensembles['weighted_classifier'] = weighted_result
            
            # 5. 성능 비교
            performance_comparison = self._compare_classification_ensembles(ensembles, X_test, y_test)
            ensembles['performance_comparison'] = performance_comparison
            
            return ensembles
            
        except Exception as e:
            logger.error(f"분류 앙상블 생성 실패: {e}")
            return {'error': str(e)}
    
    def _create_stacking_regressor(self, X_train: np.ndarray, y_train: np.ndarray,
                                 X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Stacking 회귀 모델 생성"""
        try:
            # 1단계: 기본 모델들의 교차 검증 예측
            base_predictions = {}
            
            # Random Forest
            rf_cv_pred = cross_val_predict(
                self.base_models['rf_regressor'], X_train, y_train, 
                cv=self.ensemble_config['cv_folds']
            )
            base_predictions['rf'] = rf_cv_pred
            
            # XGBoost
            xgb_cv_pred = cross_val_predict(
                self.base_models['xgb_regressor'], X_train, y_train, 
                cv=self.ensemble_config['cv_folds']
            )
            base_predictions['xgb'] = xgb_cv_pred
            
            # Linear Regression
            linear_cv_pred = cross_val_predict(
                self.base_models['linear_regressor'], X_train, y_train, 
                cv=self.ensemble_config['cv_folds']
            )
            base_predictions['linear'] = linear_cv_pred
            
            # 메타 특성 생성
            meta_features = np.column_stack([
                base_predictions['rf'],
                base_predictions['xgb'],
                base_predictions['linear']
            ])
            
            # 2단계: 메타 모델 학습
            meta_learner = self._get_meta_learner('regression')
            meta_learner.fit(meta_features, y_train)
            
            # 3단계: 테스트 세트에 대한 예측
            # 기본 모델들을 전체 훈련 데이터로 학습
            self.base_models['rf_regressor'].fit(X_train, y_train)
            self.base_models['xgb_regressor'].fit(X_train, y_train)
            self.base_models['linear_regressor'].fit(X_train, y_train)
            
            # 테스트 세트 예측
            rf_test_pred = self.base_models['rf_regressor'].predict(X_test)
            xgb_test_pred = self.base_models['xgb_regressor'].predict(X_test)
            linear_test_pred = self.base_models['linear_regressor'].predict(X_test)
            
            # 메타 특성 생성
            meta_test_features = np.column_stack([rf_test_pred, xgb_test_pred, linear_test_pred])
            
            # 최종 예측
            final_prediction = meta_learner.predict(meta_test_features)
            final_score = r2_score(y_test, final_prediction)
            
            result = {
                'model': meta_learner,
                'score': final_score,
                'type': 'stacking',
                'base_predictions': base_predictions,
                'meta_features': meta_features,
                'final_prediction': final_prediction
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Stacking 회귀 모델 생성 실패: {e}")
            return {'error': str(e)}
    
    def _create_stacking_classifier(self, X_train: np.ndarray, y_train: np.ndarray,
                                  X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Stacking 분류 모델 생성"""
        try:
            # 1단계: 기본 모델들의 교차 검증 예측
            base_predictions = {}
            
            # Random Forest
            rf_cv_pred = cross_val_predict(
                self.base_models['rf_classifier'], X_train, y_train, 
                cv=self.ensemble_config['cv_folds']
            )
            base_predictions['rf'] = rf_cv_pred
            
            # XGBoost
            xgb_cv_pred = cross_val_predict(
                self.base_models['xgb_classifier'], X_train, y_train, 
                cv=self.ensemble_config['cv_folds']
            )
            base_predictions['xgb'] = xgb_cv_pred
            
            # SVM
            svm_cv_pred = cross_val_predict(
                self.base_models['svm_classifier'], X_train, y_train, 
                cv=self.ensemble_config['cv_folds']
            )
            base_predictions['svm'] = svm_cv_pred
            
            # Naive Bayes
            nb_cv_pred = cross_val_predict(
                self.base_models['nb_classifier'], X_train, y_train, 
                cv=self.ensemble_config['cv_folds']
            )
            base_predictions['nb'] = nb_cv_pred
            
            # 메타 특성 생성
            meta_features = np.column_stack([
                base_predictions['rf'],
                base_predictions['xgb'],
                base_predictions['svm'],
                base_predictions['nb']
            ])
            
            # 2단계: 메타 모델 학습
            meta_learner = self._get_meta_learner('classification')
            meta_learner.fit(meta_features, y_train)
            
            # 3단계: 테스트 세트에 대한 예측
            # 기본 모델들을 전체 훈련 데이터로 학습
            self.base_models['rf_classifier'].fit(X_train, y_train)
            self.base_models['xgb_classifier'].fit(X_train, y_train)
            self.base_models['svm_classifier'].fit(X_train, y_train)
            self.base_models['nb_classifier'].fit(X_train, y_train)
            
            # 테스트 세트 예측
            rf_test_pred = self.base_models['rf_classifier'].predict(X_test)
            xgb_test_pred = self.base_models['xgb_classifier'].predict(X_test)
            svm_test_pred = self.base_models['svm_classifier'].predict(X_test)
            nb_test_pred = self.base_models['nb_classifier'].predict(X_test)
            
            # 메타 특성 생성
            meta_test_features = np.column_stack([rf_test_pred, xgb_test_pred, svm_test_pred, nb_test_pred])
            
            # 최종 예측
            final_prediction = meta_learner.predict(meta_test_features)
            final_score = accuracy_score(y_test, final_prediction)
            
            result = {
                'model': meta_learner,
                'score': final_score,
                'type': 'stacking',
                'base_predictions': base_predictions,
                'meta_features': meta_features,
                'final_prediction': final_prediction
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Stacking 분류 모델 생성 실패: {e}")
            return {'error': str(e)}
    
    def _create_blending_regressor(self, X_train: np.ndarray, y_train: np.ndarray,
                                 X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Blending 회귀 모델 생성"""
        try:
            # 훈련 데이터를 두 부분으로 분할
            split_point = int(len(X_train) * (1 - self.ensemble_config['blending_ratio']))
            
            X_train_base = X_train[:split_point]
            y_train_base = y_train[:split_point]
            X_train_meta = X_train[split_point:]
            y_train_meta = y_train[split_point:]
            
            # 1단계: 기본 모델들을 첫 번째 부분으로 학습
            self.base_models['rf_regressor'].fit(X_train_base, y_train_base)
            self.base_models['xgb_regressor'].fit(X_train_base, y_train_base)
            self.base_models['linear_regressor'].fit(X_train_base, y_train_base)
            
            # 2단계: 두 번째 부분에 대한 예측
            rf_pred = self.base_models['rf_regressor'].predict(X_train_meta)
            xgb_pred = self.base_models['xgb_regressor'].predict(X_train_meta)
            linear_pred = self.base_models['linear_regressor'].predict(X_train_meta)
            
            # 메타 특성 생성
            meta_features = np.column_stack([rf_pred, xgb_pred, linear_pred])
            
            # 3단계: 메타 모델 학습
            meta_learner = self._get_meta_learner('regression')
            meta_learner.fit(meta_features, y_train_meta)
            
            # 4단계: 테스트 세트에 대한 예측
            # 기본 모델들을 전체 훈련 데이터로 재학습
            self.base_models['rf_regressor'].fit(X_train, y_train)
            self.base_models['xgb_regressor'].fit(X_train, y_train)
            self.base_models['linear_regressor'].fit(X_train, y_train)
            
            # 테스트 세트 예측
            rf_test_pred = self.base_models['rf_regressor'].predict(X_test)
            xgb_test_pred = self.base_models['xgb_regressor'].predict(X_test)
            linear_test_pred = self.base_models['linear_regressor'].predict(X_test)
            
            # 메타 특성 생성
            meta_test_features = np.column_stack([rf_test_pred, xgb_test_pred, linear_test_pred])
            
            # 최종 예측
            final_prediction = meta_learner.predict(meta_test_features)
            final_score = r2_score(y_test, final_prediction)
            
            result = {
                'model': meta_learner,
                'score': final_score,
                'type': 'blending',
                'blending_ratio': self.ensemble_config['blending_ratio'],
                'final_prediction': final_prediction
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Blending 회귀 모델 생성 실패: {e}")
            return {'error': str(e)}
    
    def _create_blending_classifier(self, X_train: np.ndarray, y_train: np.ndarray,
                                  X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Blending 분류 모델 생성"""
        try:
            # 훈련 데이터를 두 부분으로 분할
            split_point = int(len(X_train) * (1 - self.ensemble_config['blending_ratio']))
            
            X_train_base = X_train[:split_point]
            y_train_base = y_train[:split_point]
            X_train_meta = X_train[split_point:]
            y_train_meta = y_train[split_point:]
            
            # 1단계: 기본 모델들을 첫 번째 부분으로 학습
            self.base_models['rf_classifier'].fit(X_train_base, y_train_base)
            self.base_models['xgb_classifier'].fit(X_train_base, y_train_base)
            self.base_models['svm_classifier'].fit(X_train_base, y_train_base)
            self.base_models['nb_classifier'].fit(X_train_base, y_train_base)
            
            # 2단계: 두 번째 부분에 대한 예측
            rf_pred = self.base_models['rf_classifier'].predict(X_train_meta)
            xgb_pred = self.base_models['xgb_classifier'].predict(X_train_meta)
            svm_pred = self.base_models['svm_classifier'].predict(X_train_meta)
            nb_pred = self.base_models['nb_classifier'].predict(X_train_meta)
            
            # 메타 특성 생성
            meta_features = np.column_stack([rf_pred, xgb_pred, svm_pred, nb_pred])
            
            # 3단계: 메타 모델 학습
            meta_learner = self._get_meta_learner('classification')
            meta_learner.fit(meta_features, y_train_meta)
            
            # 4단계: 테스트 세트에 대한 예측
            # 기본 모델들을 전체 훈련 데이터로 재학습
            self.base_models['rf_classifier'].fit(X_train, y_train)
            self.base_models['xgb_classifier'].fit(X_train, y_train)
            self.base_models['svm_classifier'].fit(X_train, y_train)
            self.base_models['nb_classifier'].fit(X_train, y_train)
            
            # 테스트 세트 예측
            rf_test_pred = self.base_models['rf_classifier'].predict(X_test)
            xgb_test_pred = self.base_models['xgb_classifier'].predict(X_test)
            svm_test_pred = self.base_models['svm_classifier'].predict(X_test)
            nb_test_pred = self.base_models['nb_classifier'].predict(X_test)
            
            # 메타 특성 생성
            meta_test_features = np.column_stack([rf_test_pred, xgb_test_pred, svm_test_pred, nb_test_pred])
            
            # 최종 예측
            final_prediction = meta_learner.predict(meta_test_features)
            final_score = accuracy_score(y_test, final_prediction)
            
            result = {
                'model': meta_learner,
                'score': final_score,
                'type': 'blending',
                'blending_ratio': self.ensemble_config['blending_ratio'],
                'final_prediction': final_prediction
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Blending 분류 모델 생성 실패: {e}")
            return {'error': str(e)}
    
    def _create_weighted_regressor(self, X_train: np.ndarray, y_train: np.ndarray,
                                 X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """가중 앙상블 회귀 모델 생성"""
        try:
            # 기본 모델들을 훈련
            self.base_models['rf_regressor'].fit(X_train, y_train)
            self.base_models['xgb_regressor'].fit(X_train, y_train)
            self.base_models['linear_regressor'].fit(X_train, y_train)
            
            # 교차 검증을 통한 성능 평가
            rf_score = np.mean(cross_val_score(self.base_models['rf_regressor'], X_train, y_train, cv=5))
            xgb_score = np.mean(cross_val_score(self.base_models['xgb_regressor'], X_train, y_train, cv=5))
            linear_score = np.mean(cross_val_score(self.base_models['linear_regressor'], X_train, y_train, cv=5))
            
            # 성능 기반 가중치 계산
            total_score = rf_score + xgb_score + linear_score
            weights = {
                'rf': rf_score / total_score,
                'xgb': xgb_score / total_score,
                'linear': linear_score / total_score
            }
            
            # 테스트 세트에 대한 예측
            rf_pred = self.base_models['rf_regressor'].predict(X_test)
            xgb_pred = self.base_models['xgb_regressor'].predict(X_test)
            linear_pred = self.base_models['linear_regressor'].predict(X_test)
            
            # 가중 평균 예측
            weighted_prediction = (
                weights['rf'] * rf_pred +
                weights['xgb'] * xgb_pred +
                weights['linear'] * linear_pred
            )
            
            final_score = r2_score(y_test, weighted_prediction)
            
            result = {
                'weights': weights,
                'score': final_score,
                'type': 'weighted',
                'final_prediction': weighted_prediction,
                'individual_scores': {
                    'rf': rf_score,
                    'xgb': xgb_score,
                    'linear': linear_score
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"가중 앙상블 회귀 모델 생성 실패: {e}")
            return {'error': str(e)}
    
    def _create_weighted_classifier(self, X_train: np.ndarray, y_train: np.ndarray,
                                  X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """가중 앙상블 분류 모델 생성"""
        try:
            # 기본 모델들을 훈련
            self.base_models['rf_classifier'].fit(X_train, y_train)
            self.base_models['xgb_classifier'].fit(X_train, y_train)
            self.base_models['svm_classifier'].fit(X_train, y_train)
            self.base_models['nb_classifier'].fit(X_train, y_train)
            
            # 교차 검증을 통한 성능 평가
            rf_score = np.mean(cross_val_score(self.base_models['rf_classifier'], X_train, y_train, cv=5))
            xgb_score = np.mean(cross_val_score(self.base_models['xgb_classifier'], X_train, y_train, cv=5))
            svm_score = np.mean(cross_val_score(self.base_models['svm_classifier'], X_train, y_train, cv=5))
            nb_score = np.mean(cross_val_score(self.base_models['nb_classifier'], X_train, y_train, cv=5))
            
            # 성능 기반 가중치 계산
            total_score = rf_score + xgb_score + svm_score + nb_score
            weights = {
                'rf': rf_score / total_score,
                'xgb': xgb_score / total_score,
                'svm': svm_score / total_score,
                'nb': nb_score / total_score
            }
            
            # 테스트 세트에 대한 예측
            rf_pred = self.base_models['rf_classifier'].predict(X_test)
            xgb_pred = self.base_models['xgb_classifier'].predict(X_test)
            svm_pred = self.base_models['svm_classifier'].predict(X_test)
            nb_pred = self.base_models['nb_classifier'].predict(X_test)
            
            # 가중 평균 예측 (확률 기반)
            weighted_prediction = (
                weights['rf'] * rf_pred +
                weights['xgb'] * xgb_pred +
                weights['svm'] * svm_pred +
                weights['nb'] * nb_pred
            )
            
            # 클래스 예측으로 변환
            final_prediction = np.round(weighted_prediction).astype(int)
            final_score = accuracy_score(y_test, final_prediction)
            
            result = {
                'weights': weights,
                'score': final_score,
                'type': 'weighted',
                'final_prediction': final_prediction,
                'individual_scores': {
                    'rf': rf_score,
                    'xgb': xgb_score,
                    'svm': svm_score,
                    'nb': nb_score
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"가중 앙상블 분류 모델 생성 실패: {e}")
            return {'error': str(e)}
    
    def _get_meta_learner(self, problem_type: str):
        """메타 학습기 반환"""
        if self.ensemble_config['meta_learner_type'] == 'linear':
            if problem_type == 'regression':
                return LinearRegression()
            else:
                return LogisticRegression(random_state=42)
        elif self.ensemble_config['meta_learner_type'] == 'rf':
            if problem_type == 'regression':
                return RandomForestRegressor(n_estimators=50, random_state=42)
            else:
                return RandomForestClassifier(n_estimators=50, random_state=42)
        elif self.ensemble_config['meta_learner_type'] == 'svm':
            if problem_type == 'regression':
                return SVR(kernel='rbf')
            else:
                return SVC(kernel='rbf', probability=True, random_state=42)
        else:
            # 기본값: 선형 모델
            if problem_type == 'regression':
                return LinearRegression()
            else:
                return LogisticRegression(random_state=42)
    
    def _compare_regression_ensembles(self, ensembles: Dict[str, Any], 
                                    X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """회귀 앙상블 방법들 비교"""
        try:
            comparison = {}
            
            for method_name, ensemble_data in ensembles.items():
                if 'score' in ensemble_data:
                    comparison[method_name] = {
                        'score': ensemble_data['score'],
                        'type': ensemble_data['type']
                    }
            
            # 성능 순위 결정
            sorted_methods = sorted(comparison.items(), key=lambda x: x[1]['score'], reverse=True)
            
            comparison['ranking'] = [method[0] for method in sorted_methods]
            comparison['best_method'] = sorted_methods[0][0] if sorted_methods else None
            comparison['best_score'] = sorted_methods[0][1]['score'] if sorted_methods else 0.0
            
            return comparison
            
        except Exception as e:
            logger.error(f"회귀 앙상블 비교 실패: {e}")
            return {'error': str(e)}
    
    def _compare_classification_ensembles(self, ensembles: Dict[str, Any], 
                                        X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """분류 앙상블 방법들 비교"""
        try:
            comparison = {}
            
            for method_name, ensemble_data in ensembles.items():
                if 'score' in ensemble_data:
                    comparison[method_name] = {
                        'score': ensemble_data['score'],
                        'type': ensemble_data['type']
                    }
            
            # 성능 순위 결정
            sorted_methods = sorted(comparison.items(), key=lambda x: x[1]['score'], reverse=True)
            
            comparison['ranking'] = [method[0] for method in sorted_methods]
            comparison['best_method'] = sorted_methods[0][0] if sorted_methods else None
            comparison['best_score'] = sorted_methods[0][1]['score'] if sorted_methods else 0.0
            
            return comparison
            
        except Exception as e:
            logger.error(f"분류 앙상블 비교 실패: {e}")
            return {'error': str(e)}
    
    def get_ensemble_summary(self) -> Dict[str, Any]:
        """앙상블 결과 요약"""
        summary = {
            'total_targets': len(self.ensemble_models),
            'ensemble_methods': ['voting', 'stacking', 'blending', 'weighted'],
            'base_models': list(self.base_models.keys()),
            'meta_learner_type': self.ensemble_config['meta_learner_type']
        }
        
        if self.ensemble_models:
            summary['targets'] = list(self.ensemble_models.keys())
            
            # 각 타겟별 최고 성능 방법
            best_methods = {}
            for target, methods in self.ensemble_models.items():
                if 'performance_comparison' in methods:
                    best_method = methods['performance_comparison'].get('best_method')
                    best_score = methods['performance_comparison'].get('best_score', 0.0)
                    best_methods[target] = {
                        'best_method': best_method,
                        'best_score': best_score
                    }
            
            summary['best_methods_by_target'] = best_methods
        
        return summary
    
    def save_ensemble_models(self, filepath: str) -> bool:
        """앙상블 모델들 저장"""
        try:
            models_data = {
                'ensemble_models': self.ensemble_models,
                'base_models': self.base_models,
                'meta_models': self.meta_models,
                'ensemble_config': self.ensemble_config
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(models_data, f)
            
            logger.info(f"앙상블 모델들 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"앙상블 모델 저장 실패: {e}")
            return False
    
    def load_ensemble_models(self, filepath: str) -> bool:
        """저장된 앙상블 모델들 로드"""
        try:
            with open(filepath, 'rb') as f:
                models_data = pickle.load(f)
            
            self.ensemble_models = models_data['ensemble_models']
            self.base_models = models_data['base_models']
            self.meta_models = models_data['meta_models']
            self.ensemble_config = models_data['ensemble_config']
            
            logger.info(f"앙상블 모델들 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"앙상블 모델 로드 실패: {e}")
            return False
