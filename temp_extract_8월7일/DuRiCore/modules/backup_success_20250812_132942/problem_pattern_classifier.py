"""
문제 패턴 분류 머신러닝 모델
SVM과 Naive Bayes를 사용하여 문제 패턴을 자동으로 분류하는 시스템
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
    from sklearn.svm import SVC
    from sklearn.naive_bayes import MultinomialNB, GaussianNB
    from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.pipeline import Pipeline
    from sklearn.ensemble import VotingClassifier
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("머신러닝 라이브러리가 설치되지 않았습니다. pip install scikit-learn")

from ..algorithm_knowledge.algorithm_knowledge_base import (
    AlgorithmKnowledge, 
    ProblemPattern,
    AlgorithmKnowledgeBase
)

logger = logging.getLogger(__name__)

class ProblemPatternClassifier:
    """문제 패턴 분류 머신러닝 모델"""
    
    def __init__(self, knowledge_base: AlgorithmKnowledgeBase):
        self.knowledge_base = knowledge_base
        
        # 분류 모델들
        self.svm_classifier = None           # SVM 분류기
        self.naive_bayes_classifier = None   # Naive Bayes 분류기
        self.ensemble_classifier = None      # 앙상블 분류기
        
        # 데이터 전처리기
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=200, stop_words='english')
        self.count_vectorizer = CountVectorizer(max_features=200, stop_words='english')
        
        # 모델 성능 메트릭
        self.model_performance = {}
        
        # 학습 데이터
        self.training_data = []
        self.feature_names = []
        self.pattern_categories = []
        
        logger.info("문제 패턴 분류 모델 초기화 완료")
    
    def prepare_training_data(self) -> pd.DataFrame:
        """학습 데이터 준비"""
        try:
            training_records = []
            
            # 문제 패턴 데이터 수집
            for algorithm in self.knowledge_base.algorithms.values():
                for pattern in algorithm.input_patterns:
                    record = {
                        'pattern_text': pattern,
                        'algorithm_category': algorithm.category,
                        'algorithm_success_rate': algorithm.success_rate,
                        'algorithm_efficiency': algorithm.efficiency_score,
                        'pattern_length': len(pattern),
                        'word_count': len(pattern.split()),
                        'has_numbers': any(char.isdigit() for char in pattern),
                        'has_special_chars': any(not char.isalnum() and char != ' ' for char in pattern),
                        'is_question': pattern.strip().endswith('?'),
                        'is_command': pattern.strip().endswith('!') or pattern.strip().startswith(('해결', '찾기', '계산', '분석')),
                        'algorithm_id': algorithm.algorithm_id
                    }
                    training_records.append(record)
            
            # DataFrame 생성
            df = pd.DataFrame(training_records)
            
            if df.empty:
                logger.warning("학습 데이터가 없습니다")
                return df
            
            # 패턴 카테고리 인코딩
            df['category_encoded'] = self.label_encoder.fit_transform(df['algorithm_category'])
            self.pattern_categories = self.label_encoder.classes_.tolist()
            
            # 텍스트 특성 벡터화
            text_vectors = self.tfidf_vectorizer.fit_transform(df['pattern_text'])
            text_df = pd.DataFrame(text_vectors.toarray(), 
                                 columns=[f'tfidf_{i}' for i in range(text_vectors.shape[1])])
            
            # 카운트 벡터화
            count_vectors = self.count_vectorizer.fit_transform(df['pattern_text'])
            count_df = pd.DataFrame(count_vectors.toarray(), 
                                  columns=[f'count_{i}' for i in range(count_vectors.shape[1])])
            
            # 특성 결합
            df = pd.concat([df, text_df, count_df], axis=1)
            
            # 특성 이름 저장
            self.feature_names = [col for col in df.columns if col not in [
                'pattern_text', 'algorithm_category', 'algorithm_id', 'category_encoded'
            ]]
            
            self.training_data = df
            logger.info(f"학습 데이터 준비 완료: {len(df)}개 샘플, {len(self.feature_names)}개 특성")
            return df
            
        except Exception as e:
            logger.error(f"학습 데이터 준비 실패: {e}")
            return pd.DataFrame()
    
    def train_models(self) -> bool:
        """모든 분류 모델 학습"""
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
            y = df['category_encoded']
            
            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # 특성 스케일링
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # 1. SVM 분류기 학습
            logger.info("SVM 분류기 학습 중...")
            self.svm_classifier = SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42
            )
            self.svm_classifier.fit(X_train_scaled, y_train)
            
            # SVM 성능 평가
            y_svm_pred = self.svm_classifier.predict(X_test_scaled)
            svm_accuracy = accuracy_score(y_test, y_svm_pred)
            svm_report = classification_report(y_test, y_svm_pred, target_names=self.pattern_categories)
            
            # 2. Naive Bayes 분류기 학습
            logger.info("Naive Bayes 분류기 학습 중...")
            # 가우시안 NB (연속형 특성에 적합)
            self.naive_bayes_classifier = GaussianNB()
            self.naive_bayes_classifier.fit(X_train_scaled, y_train)
            
            # Naive Bayes 성능 평가
            y_nb_pred = self.naive_bayes_classifier.predict(X_test_scaled)
            nb_accuracy = accuracy_score(y_test, y_nb_pred)
            nb_report = classification_report(y_test, y_nb_pred, target_names=self.pattern_categories)
            
            # 3. 앙상블 분류기 학습
            logger.info("앙상블 분류기 학습 중...")
            self.ensemble_classifier = VotingClassifier(
                estimators=[
                    ('svm', self.svm_classifier),
                    ('nb', self.naive_bayes_classifier)
                ],
                voting='soft'
            )
            self.ensemble_classifier.fit(X_train_scaled, y_train)
            
            # 앙상블 성능 평가
            y_ensemble_pred = self.ensemble_classifier.predict(X_test_scaled)
            ensemble_accuracy = accuracy_score(y_test, y_ensemble_pred)
            ensemble_report = classification_report(y_test, y_ensemble_pred, target_names=self.pattern_categories)
            
            # 모델 성능 저장
            self.model_performance = {
                'svm_classifier': {
                    'accuracy': svm_accuracy,
                    'classification_report': svm_report,
                    'model_type': 'SVM'
                },
                'naive_bayes_classifier': {
                    'accuracy': nb_accuracy,
                    'classification_report': nb_report,
                    'model_type': 'GaussianNB'
                },
                'ensemble_classifier': {
                    'accuracy': ensemble_accuracy,
                    'classification_report': ensemble_report,
                    'model_type': 'VotingClassifier'
                },
                'pattern_categories': self.pattern_categories,
                'feature_count': len(self.feature_names),
                'training_samples': len(self.training_data)
            }
            
            logger.info("모든 분류 모델 학습 완료!")
            logger.info(f"SVM 정확도: {svm_accuracy:.3f}")
            logger.info(f"Naive Bayes 정확도: {nb_accuracy:.3f}")
            logger.info(f"앙상블 정확도: {ensemble_accuracy:.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"모델 학습 실패: {e}")
            return False
    
    def classify_problem_pattern(self, pattern_text: str) -> Dict[str, Any]:
        """문제 패턴 분류"""
        try:
            if not all([self.svm_classifier, self.naive_bayes_classifier, self.ensemble_classifier]):
                logger.error("모델이 학습되지 않았습니다")
                return {}
            
            # 특성 추출
            features = self._extract_pattern_features(pattern_text)
            features_scaled = self.scaler.transform([features])
            
            # 각 모델로 예측
            svm_pred = self.svm_classifier.predict(features_scaled)[0]
            nb_pred = self.naive_bayes_classifier.predict(features_scaled)[0]
            ensemble_pred = self.ensemble_classifier.predict(features_scaled)[0]
            
            # 확률 점수
            svm_proba = self.svm_classifier.predict_proba(features_scaled)[0]
            nb_proba = self.naive_bayes_classifier.predict_proba(features_scaled)[0]
            ensemble_proba = self.ensemble_classifier.predict_proba(features_scaled)[0]
            
            # 카테고리 이름으로 변환
            svm_category = self.pattern_categories[svm_pred]
            nb_category = self.pattern_categories[nb_pred]
            ensemble_category = self.pattern_categories[ensemble_pred]
            
            # 신뢰도 계산
            svm_confidence = svm_proba.max()
            nb_confidence = nb_proba.max()
            ensemble_confidence = ensemble_proba.max()
            
            # 최종 분류 결과
            final_category = ensemble_category  # 앙상블 결과를 최종 결과로 사용
            final_confidence = ensemble_confidence
            
            classification_result = {
                'pattern_text': pattern_text,
                'final_classification': {
                    'category': final_category,
                    'confidence': final_confidence
                },
                'individual_predictions': {
                    'svm': {
                        'category': svm_category,
                        'confidence': svm_confidence
                    },
                    'naive_bayes': {
                        'category': nb_category,
                        'confidence': nb_confidence
                    },
                    'ensemble': {
                        'category': ensemble_category,
                        'confidence': ensemble_confidence
                    }
                },
                'all_probabilities': {
                    'svm': dict(zip(self.pattern_categories, svm_proba)),
                    'naive_bayes': dict(zip(self.pattern_categories, nb_proba)),
                    'ensemble': dict(zip(self.pattern_categories, ensemble_proba))
                },
                'classification_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"문제 패턴 분류 완료: '{pattern_text}' -> {final_category} (신뢰도: {final_confidence:.3f})")
            return classification_result
            
        except Exception as e:
            logger.error(f"문제 패턴 분류 실패: {e}")
            return {}
    
    def _extract_pattern_features(self, pattern_text: str) -> List[float]:
        """패턴에서 특성 추출"""
        features = [
            len(pattern_text),  # 패턴 길이
            len(pattern_text.split()),  # 단어 수
            float(any(char.isdigit() for char in pattern_text)),  # 숫자 포함 여부
            float(any(not char.isalnum() and char != ' ' for char in pattern_text)),  # 특수문자 포함 여부
            float(pattern_text.strip().endswith('?')),  # 질문 여부
            float(pattern_text.strip().endswith('!') or pattern_text.strip().startswith(('해결', '찾기', '계산', '분석')))  # 명령어 여부
        ]
        
        # TF-IDF 특성
        tfidf_vector = self.tfidf_vectorizer.transform([pattern_text])
        tfidf_features = tfidf_vector.toarray()[0].tolist()
        features.extend(tfidf_features)
        
        # 카운트 벡터 특성
        count_vector = self.count_vectorizer.transform([pattern_text])
        count_features = count_vector.toarray()[0].tolist()
        features.extend(count_features)
        
        return features
    
    def get_model_performance(self) -> Dict[str, Any]:
        """모델 성능 정보 반환"""
        return self.model_performance
    
    def save_models(self, filepath: str) -> bool:
        """학습된 모델들을 파일로 저장"""
        try:
            models_data = {
                'svm_classifier': self.svm_classifier,
                'naive_bayes_classifier': self.naive_bayes_classifier,
                'ensemble_classifier': self.ensemble_classifier,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'count_vectorizer': self.count_vectorizer,
                'feature_names': self.feature_names,
                'pattern_categories': self.pattern_categories,
                'model_performance': self.model_performance
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
            
            self.svm_classifier = models_data['svm_classifier']
            self.naive_bayes_classifier = models_data['naive_bayes_classifier']
            self.ensemble_classifier = models_data['ensemble_classifier']
            self.scaler = models_data['scaler']
            self.label_encoder = models_data['label_encoder']
            self.tfidf_vectorizer = models_data['tfidf_vectorizer']
            self.count_vectorizer = models_data['count_vectorizer']
            self.feature_names = models_data['feature_names']
            self.pattern_categories = models_data['pattern_categories']
            self.model_performance = models_data['model_performance']
            
            logger.info(f"모델 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def get_pattern_categories(self) -> List[str]:
        """패턴 카테고리 목록 반환"""
        return self.pattern_categories
    
    def analyze_pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """두 패턴 간의 유사도 분석"""
        try:
            features1 = self._extract_pattern_features(pattern1)
            features2 = self._extract_pattern_features(pattern2)
            
            # 코사인 유사도 계산
            features1 = np.array(features1)
            features2 = np.array(features2)
            
            dot_product = np.dot(features1, features2)
            norm1 = np.linalg.norm(features1)
            norm2 = np.linalg.norm(features2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"패턴 유사도 분석 실패: {e}")
            return 0.0
