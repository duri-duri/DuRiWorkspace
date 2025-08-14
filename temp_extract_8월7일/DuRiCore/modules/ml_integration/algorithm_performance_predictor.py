"""
알고리즘 성능 예측 머신러닝 모델
Random Forest와 XGBoost를 사용하여 알고리즘 성능을 예측하는 시스템
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import pickle
import json

# 머신러닝 라이브러리
try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
    from sklearn.feature_extraction.text import TfidfVectorizer
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

class AlgorithmPerformancePredictor:
    """알고리즘 성능 예측 머신러닝 모델"""
    
    def __init__(self, knowledge_base: AlgorithmKnowledgeBase):
        self.knowledge_base = knowledge_base
        
        # 머신러닝 모델들
        self.success_rate_predictor = None      # 성공률 예측 (회귀)
        self.efficiency_predictor = None        # 효율성 예측 (회귀)
        self.complexity_classifier = None       # 복잡도 분류 (분류)
        self.performance_classifier = None      # 전반적 성능 분류 (분류)
        
        # 데이터 전처리기
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
        # 모델 성능 메트릭
        self.model_performance = {}
        
        # 학습 데이터
        self.training_data = []
        self.feature_names = []
        
        logger.info("알고리즘 성능 예측 모델 초기화 완료")
    
    def prepare_training_data(self) -> pd.DataFrame:
        """학습 데이터 준비"""
        try:
            training_records = []
            
            for algorithm in self.knowledge_base.algorithms.values():
                # 알고리즘 기본 특성
                record = {
                    'algorithm_id': algorithm.algorithm_id,
                    'category': algorithm.category,
                    'success_rate': algorithm.success_rate,
                    'efficiency_score': algorithm.efficiency_score,
                    'confidence_level': algorithm.confidence_level,
                    'usage_count': algorithm.usage_count,
                    'complexity': algorithm.complexity,
                    'input_patterns_count': len(algorithm.input_patterns),
                    'process_steps_count': len(algorithm.process_steps),
                    'output_patterns_count': len(algorithm.output_patterns),
                    'applicable_domains_count': len(algorithm.applicable_domains),
                    'prerequisites_count': len(algorithm.prerequisites),
                    'alternatives_count': len(algorithm.alternatives),
                }
                
                # 텍스트 특성 (TF-IDF 벡터화를 위해)
                text_content = f"{algorithm.name} {algorithm.description} {' '.join(algorithm.input_patterns)} {' '.join(algorithm.process_steps)}"
                record['text_content'] = text_content
                
                # 복잡도 수치화
                complexity_score = self._extract_complexity_score(algorithm.complexity)
                record['complexity_score'] = complexity_score
                
                # 카테고리 인코딩
                record['category_encoded'] = self._encode_category(algorithm.category)
                
                # 성능 등급 (분류를 위해)
                performance_grade = self._calculate_performance_grade(algorithm)
                record['performance_grade'] = performance_grade
                
                training_records.append(record)
            
            # DataFrame 생성
            df = pd.DataFrame(training_records)
            
            # 텍스트 특성 벡터화
            if len(df) > 0:
                text_vectors = self.tfidf_vectorizer.fit_transform(df['text_content'])
                text_df = pd.DataFrame(text_vectors.toarray(), 
                                     columns=[f'text_feature_{i}' for i in range(text_vectors.shape[1])])
                df = pd.concat([df, text_df], axis=1)
                df = df.drop('text_content', axis=1)
            
            self.training_data = df
            self.feature_names = [col for col in df.columns if col not in ['algorithm_id', 'success_rate', 'efficiency_score', 'performance_grade']]
            
            logger.info(f"학습 데이터 준비 완료: {len(df)}개 샘플, {len(self.feature_names)}개 특성")
            return df
            
        except Exception as e:
            logger.error(f"학습 데이터 준비 실패: {e}")
            return pd.DataFrame()
    
    def _extract_complexity_score(self, complexity: str) -> float:
        """복잡도를 수치로 변환"""
        complexity_mapping = {
            "O(1)": 1.0,
            "O(log n)": 2.0,
            "O(n)": 3.0,
            "O(n log n)": 4.0,
            "O(n^2)": 5.0,
            "O(n^3)": 6.0,
            "O(2^n)": 7.0
        }
        
        for pattern, score in complexity_mapping.items():
            if pattern in complexity:
                return score
        
        return 3.0  # 기본값
    
    def _encode_category(self, category: str) -> int:
        """카테고리를 숫자로 인코딩"""
        category_mapping = {
            "problem_solving": 0,
            "learning": 1,
            "decision_making": 2,
            "pattern_recognition": 3,
            "hybrid": 4,
            "adaptive": 5
        }
        
        return category_mapping.get(category, 0)
    
    def _calculate_performance_grade(self, algorithm: AlgorithmKnowledge) -> str:
        """성능 등급 계산"""
        avg_score = (algorithm.success_rate + algorithm.efficiency_score) / 2
        
        if avg_score >= 0.8:
            return "excellent"
        elif avg_score >= 0.6:
            return "good"
        elif avg_score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def train_models(self) -> bool:
        """모든 모델 학습"""
        try:
            if not ML_AVAILABLE:
                logger.error("머신러닝 라이브러리가 사용할 수 없습니다")
                return False
            
            # 학습 데이터 준비
            df = self.prepare_training_data()
            if df.empty:
                logger.error("학습 데이터가 없습니다")
                return False
            
            # 특성과 타겟 분리
            X = df[self.feature_names]
            y_success = df['success_rate']
            y_efficiency = df['efficiency_score']
            y_complexity = df['complexity_score']
            y_performance = df['performance_grade']
            
            # 데이터 분할
            X_train, X_test, y_success_train, y_success_test = train_test_split(
                X, y_success, test_size=0.2, random_state=42
            )
            _, _, y_efficiency_train, y_efficiency_test = train_test_split(
                X, y_efficiency, test_size=0.2, random_state=42
            )
            _, _, y_complexity_train, y_complexity_test = train_test_split(
                X, y_complexity, test_size=0.2, random_state=42
            )
            _, _, y_performance_train, y_performance_test = train_test_split(
                X, y_performance, test_size=0.2, random_state=42
            )
            
            # 특성 스케일링
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # 1. 성공률 예측 모델 (Random Forest)
            logger.info("성공률 예측 모델 학습 중...")
            self.success_rate_predictor = RandomForestRegressor(
                n_estimators=100, 
                max_depth=10, 
                random_state=42
            )
            self.success_rate_predictor.fit(X_train_scaled, y_success_train)
            
            # 성공률 모델 평가
            y_success_pred = self.success_rate_predictor.predict(X_test_scaled)
            success_mse = mean_squared_error(y_success_test, y_success_pred)
            success_r2 = self.success_rate_predictor.score(X_test_scaled, y_success_test)
            
            # 2. 효율성 예측 모델 (XGBoost)
            logger.info("효율성 예측 모델 학습 중...")
            self.efficiency_predictor = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            self.efficiency_predictor.fit(X_train_scaled, y_efficiency_train)
            
            # 효율성 모델 평가
            y_efficiency_pred = self.efficiency_predictor.predict(X_test_scaled)
            efficiency_mse = mean_squared_error(y_efficiency_test, y_efficiency_pred)
            efficiency_r2 = self.efficiency_predictor.score(X_test_scaled, y_efficiency_test)
            
            # 3. 복잡도 분류 모델 (Random Forest)
            logger.info("복잡도 분류 모델 학습 중...")
            self.complexity_classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                random_state=42
            )
            self.complexity_classifier.fit(X_train_scaled, y_complexity_train)
            
            # 복잡도 모델 평가
            y_complexity_pred = self.complexity_classifier.predict(X_test_scaled)
            complexity_accuracy = accuracy_score(y_complexity_test, y_complexity_pred)
            
            # 4. 성능 등급 분류 모델 (Random Forest)
            logger.info("성능 등급 분류 모델 학습 중...")
            self.performance_classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                random_state=42
            )
            self.performance_classifier.fit(X_train_scaled, y_performance_train)
            
            # 성능 등급 모델 평가
            y_performance_pred = self.performance_classifier.predict(X_test_scaled)
            performance_accuracy = accuracy_score(y_performance_test, y_performance_pred)
            
            # 모델 성능 저장
            self.model_performance = {
                'success_rate_predictor': {
                    'mse': success_mse,
                    'r2': success_r2,
                    'model_type': 'RandomForest'
                },
                'efficiency_predictor': {
                    'mse': efficiency_mse,
                    'r2': efficiency_r2,
                    'model_type': 'XGBoost'
                },
                'complexity_classifier': {
                    'accuracy': complexity_accuracy,
                    'model_type': 'RandomForest'
                },
                'performance_classifier': {
                    'accuracy': performance_accuracy,
                    'model_type': 'RandomForest'
                }
            }
            
            logger.info("모든 모델 학습 완료!")
            logger.info(f"성공률 예측 R²: {success_r2:.3f}")
            logger.info(f"효율성 예측 R²: {efficiency_r2:.3f}")
            logger.info(f"복잡도 분류 정확도: {complexity_accuracy:.3f}")
            logger.info(f"성능 등급 분류 정확도: {performance_accuracy:.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"모델 학습 실패: {e}")
            return False
    
    def predict_algorithm_performance(self, algorithm: AlgorithmKnowledge) -> Dict[str, Any]:
        """알고리즘 성능 예측"""
        try:
            if not all([self.success_rate_predictor, self.efficiency_predictor, 
                       self.complexity_classifier, self.performance_classifier]):
                logger.error("모델이 학습되지 않았습니다")
                return {}
            
            # 특성 추출
            features = self._extract_algorithm_features(algorithm)
            features_scaled = self.scaler.transform([features])
            
            # 예측 수행
            predicted_success_rate = self.success_rate_predictor.predict(features_scaled)[0]
            predicted_efficiency = self.efficiency_predictor.predict(features_scaled)[0]
            predicted_complexity_score = self.complexity_classifier.predict(features_scaled)[0]
            predicted_performance_grade = self.performance_classifier.predict(features_scaled)[0]
            
            # 복잡도 점수를 문자열로 변환
            complexity_mapping = {
                1.0: "O(1)", 2.0: "O(log n)", 3.0: "O(n)", 
                4.0: "O(n log n)", 5.0: "O(n^2)", 6.0: "O(n^3)", 7.0: "O(2^n)"
            }
            predicted_complexity = complexity_mapping.get(predicted_complexity_score, "O(n)")
            
            # 예측 신뢰도 계산
            confidence_scores = {
                'success_rate': self.success_rate_predictor.predict_proba(features_scaled).max() if hasattr(self.success_rate_predictor, 'predict_proba') else 0.8,
                'efficiency': 0.8,  # XGBoost는 기본적으로 높은 신뢰도
                'complexity': self.complexity_classifier.predict_proba(features_scaled).max(),
                'performance_grade': self.performance_classifier.predict_proba(features_scaled).max()
            }
            
            predictions = {
                'predicted_success_rate': max(0.0, min(1.0, predicted_success_rate)),
                'predicted_efficiency': max(0.0, min(1.0, predicted_efficiency)),
                'predicted_complexity': predicted_complexity,
                'predicted_performance_grade': predicted_performance_grade,
                'confidence_scores': confidence_scores,
                'prediction_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"알고리즘 성능 예측 완료: {algorithm.name}")
            return predictions
            
        except Exception as e:
            logger.error(f"성능 예측 실패: {e}")
            return {}
    
    def _extract_algorithm_features(self, algorithm: AlgorithmKnowledge) -> List[float]:
        """알고리즘에서 특성 추출"""
        features = [
            self._encode_category(algorithm.category),
            algorithm.confidence_level,
            algorithm.usage_count,
            self._extract_complexity_score(algorithm.complexity),
            len(algorithm.input_patterns),
            len(algorithm.process_steps),
            len(algorithm.output_patterns),
            len(algorithm.applicable_domains),
            len(algorithm.prerequisites),
            len(algorithm.alternatives)
        ]
        
        # 텍스트 특성 (기본값으로 0 채우기)
        text_features = [0.0] * 100  # TF-IDF 벡터 크기
        features.extend(text_features)
        
        return features
    
    def get_model_performance(self) -> Dict[str, Any]:
        """모델 성능 정보 반환"""
        return self.model_performance
    
    def save_models(self, filepath: str) -> bool:
        """학습된 모델들을 파일로 저장"""
        try:
            models_data = {
                'success_rate_predictor': self.success_rate_predictor,
                'efficiency_predictor': self.efficiency_predictor,
                'complexity_classifier': self.complexity_classifier,
                'performance_classifier': self.performance_classifier,
                'scaler': self.scaler,
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'feature_names': self.feature_names,
                'model_performance': self.model_performance,
                'training_data_shape': self.training_data.shape if hasattr(self, 'training_data') else None
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(models_data, f)
            
            logger.info(f"모델 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            return False
    
    def load_models(self, filepath: str) -> bool:
        """저장된 모델들을 파일에서 로드"""
        try:
            with open(filepath, 'rb') as f:
                models_data = pickle.load(f)
            
            self.success_rate_predictor = models_data['success_rate_predictor']
            self.efficiency_predictor = models_data['efficiency_predictor']
            self.complexity_classifier = models_data['complexity_classifier']
            self.performance_classifier = models_data['performance_classifier']
            self.scaler = models_data['scaler']
            self.tfidf_vectorizer = models_data['tfidf_vectorizer']
            self.feature_names = models_data['feature_names']
            self.model_performance = models_data['model_performance']
            
            logger.info(f"모델 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def get_feature_importance(self) -> Dict[str, List[Tuple[str, float]]]:
        """특성 중요도 분석"""
        try:
            feature_importance = {}
            
            if self.success_rate_predictor:
                importance = self.success_rate_predictor.feature_importances_
                feature_importance['success_rate'] = sorted(
                    zip(self.feature_names, importance), 
                    key=lambda x: x[1], reverse=True
                )[:10]
            
            if self.efficiency_predictor:
                importance = self.efficiency_predictor.feature_importances_
                feature_importance['efficiency'] = sorted(
                    zip(self.feature_names, importance), 
                    key=lambda x: x[1], reverse=True
                )[:10]
            
            if self.complexity_classifier:
                importance = self.complexity_classifier.feature_importances_
                feature_importance['complexity'] = sorted(
                    zip(self.feature_names, importance), 
                    key=lambda x: x[1], reverse=True
                )[:10]
            
            if self.performance_classifier:
                importance = self.performance_classifier.feature_importances_
                feature_importance['performance_grade'] = sorted(
                    zip(self.feature_names, importance), 
                    key=lambda x: x[1], reverse=True
                )[:10]
            
            return feature_importance
            
        except Exception as e:
            logger.error(f"특성 중요도 분석 실패: {e}")
            return {}
