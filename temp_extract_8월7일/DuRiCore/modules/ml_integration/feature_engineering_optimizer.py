"""
특성 선택 및 엔지니어링 최적화 시스템
Recursive Feature Elimination, 특성 상관관계 분석, 새로운 특성 생성을 통한 최적화
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Set
import logging
from datetime import datetime
import pickle
import json
import time
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# 머신러닝 라이브러리
try:
    from sklearn.feature_selection import RFE, SelectKBest, f_regression, f_classif, mutual_info_regression, mutual_info_classif
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.decomposition import PCA
    from sklearn.covariance import EllipticEnvelope
    from sklearn.manifold import TSNE
    from sklearn.cluster import KMeans
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

class FeatureEngineeringOptimizer:
    """특성 선택 및 엔지니어링 최적화 시스템"""
    
    def __init__(self, knowledge_base: AlgorithmKnowledgeBase):
        self.knowledge_base = knowledge_base
        
        # 최적화된 특성들
        self.optimized_features = {}
        
        # 특성 선택 결과
        self.feature_selection_results = {}
        
        # 새로운 특성들
        self.engineered_features = {}
        
        # 특성 중요도 분석
        self.feature_importance = {}
        
        # 특성 상관관계 분석
        self.feature_correlations = {}
        
        # 최적화 설정
        self.optimization_config = {
            'max_features': 50,
            'min_features': 5,
            'correlation_threshold': 0.8,
            'importance_threshold': 0.01,
            'polynomial_degree': 2,
            'n_clusters': 5
        }
        
        logger.info("특성 엔지니어링 최적화 시스템 초기화 완료")
    
    def optimize_all_features(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """모든 특성 최적화 수행"""
        try:
            if not ML_AVAILABLE:
                logger.error("머신러닝 라이브러리가 사용할 수 없습니다")
                return {'error': 'ML 라이브러리 없음'}
            
            logger.info("=== 특성 엔지니어링 최적화 시작 ===")
            
            start_time = time.time()
            optimization_results = {}
            
            # 1. 기존 특성 분석
            logger.info("기존 특성 분석 중...")
            feature_analysis = self._analyze_existing_features(training_data)
            optimization_results['feature_analysis'] = feature_analysis
            
            # 2. 특성 상관관계 분석
            logger.info("특성 상관관계 분석 중...")
            correlation_analysis = self._analyze_feature_correlations(training_data)
            optimization_results['correlation_analysis'] = correlation_analysis
            
            # 3. 특성 중요도 분석
            logger.info("특성 중요도 분석 중...")
            importance_analysis = self._analyze_feature_importance(training_data)
            optimization_results['importance_analysis'] = importance_analysis
            
            # 4. 새로운 특성 생성
            logger.info("새로운 특성 생성 중...")
            engineered_features = self._create_engineered_features(training_data)
            optimization_results['engineered_features'] = engineered_features
            
            # 5. 특성 선택 최적화
            logger.info("특성 선택 최적화 중...")
            feature_selection = self._optimize_feature_selection(training_data)
            optimization_results['feature_selection'] = feature_selection
            
            # 6. 최종 특성 세트 생성
            logger.info("최종 특성 세트 생성 중...")
            final_features = self._create_final_feature_set(training_data)
            optimization_results['final_features'] = final_features
            
            # 최적화 완료 시간 계산
            total_time = time.time() - start_time
            
            # 전체 결과 요약
            summary = {
                'total_optimization_time': total_time,
                'original_feature_count': len(training_data.columns),
                'final_feature_count': len(final_features['selected_features']),
                'feature_reduction_percentage': ((len(training_data.columns) - len(final_features['selected_features'])) / len(training_data.columns)) * 100,
                'optimization_results': optimization_results,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"=== 특성 엔지니어링 최적화 완료! "
                       f"특성 수: {len(training_data.columns)} → {len(final_features['selected_features'])} "
                       f"({summary['feature_reduction_percentage']:.1f}% 감소) ===")
            
            return summary
            
        except Exception as e:
            logger.error(f"특성 엔지니어링 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _analyze_existing_features(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """기존 특성 분석"""
        try:
            analysis = {
                'total_features': len(training_data.columns),
                'feature_types': {},
                'missing_values': {},
                'unique_values': {},
                'data_types': {}
            }
            
            for column in training_data.columns:
                # 데이터 타입 분석
                analysis['data_types'][column] = str(training_data[column].dtype)
                
                # 결측값 분석
                missing_count = training_data[column].isnull().sum()
                missing_percentage = (missing_count / len(training_data)) * 100
                analysis['missing_values'][column] = {
                    'count': missing_count,
                    'percentage': missing_percentage
                }
                
                # 고유값 분석
                unique_count = training_data[column].nunique()
                analysis['unique_values'][column] = unique_count
                
                # 특성 타입 분류
                if training_data[column].dtype in ['int64', 'float64']:
                    analysis['feature_types'][column] = 'numerical'
                else:
                    analysis['feature_types'][column] = 'categorical'
            
            logger.info(f"기존 특성 분석 완료: {len(training_data.columns)}개 특성")
            return analysis
            
        except Exception as e:
            logger.error(f"기존 특성 분석 실패: {e}")
            return {'error': str(e)}
    
    def _analyze_feature_correlations(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """특성 상관관계 분석"""
        try:
            # 수치형 특성만 선택
            numerical_features = training_data.select_dtypes(include=[np.number])
            
            if len(numerical_features.columns) < 2:
                return {'error': '수치형 특성이 부족합니다'}
            
            # 상관관계 계산
            correlation_matrix = numerical_features.corr()
            
            # 높은 상관관계 쌍 찾기
            high_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > self.optimization_config['correlation_threshold']:
                        high_correlations.append({
                            'feature1': correlation_matrix.columns[i],
                            'feature2': correlation_matrix.columns[j],
                            'correlation': corr_value
                        })
            
            # 상관관계 히트맵 생성
            plt.figure(figsize=(12, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('특성 상관관계 히트맵')
            plt.tight_layout()
            
            # 결과 저장
            analysis = {
                'correlation_matrix': correlation_matrix.to_dict(),
                'high_correlations': high_correlations,
                'correlation_threshold': self.optimization_config['correlation_threshold'],
                'total_correlations': len(high_correlations)
            }
            
            self.feature_correlations = analysis
            logger.info(f"특성 상관관계 분석 완료: {len(high_correlations)}개 높은 상관관계 발견")
            return analysis
            
        except Exception as e:
            logger.error(f"특성 상관관계 분석 실패: {e}")
            return {'error': str(e)}
    
    def _analyze_feature_importance(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """특성 중요도 분석"""
        try:
            # 타겟 변수들
            target_columns = ['success_rate', 'efficiency_score', 'complexity_score', 'category_encoded']
            available_targets = [col for col in target_columns if col in training_data.columns]
            
            importance_results = {}
            
            for target in available_targets:
                if target in training_data.columns:
                    # 특성과 타겟 분리
                    X = training_data.drop([target, 'algorithm_id', 'performance_grade'], axis=1, errors='ignore')
                    y = training_data[target]
                    
                    # 수치형 특성만 선택
                    X_numerical = X.select_dtypes(include=[np.number])
                    
                    if len(X_numerical.columns) == 0:
                        continue
                    
                    # 특성 중요도 계산 (Random Forest 사용)
                    if target in ['success_rate', 'efficiency_score', 'complexity_score']:
                        # 회귀 문제
                        model = RandomForestRegressor(n_estimators=100, random_state=42)
                        scoring_func = f_regression
                    else:
                        # 분류 문제
                        model = RandomForestClassifier(n_estimators=100, random_state=42)
                        scoring_func = f_classif
                    
                    # F-통계량 기반 중요도
                    f_scores, p_values = scoring_func(X_numerical, y)
                    
                    # 상호정보 기반 중요도
                    if target in ['success_rate', 'efficiency_score', 'complexity_score']:
                        mi_scores = mutual_info_regression(X_numerical, y, random_state=42)
                    else:
                        mi_scores = mutual_info_classif(X_numerical, y, random_state=42)
                    
                    # Random Forest 기반 중요도
                    model.fit(X_numerical, y)
                    rf_importance = model.feature_importances_
                    
                    # 중요도 점수 결합
                    feature_importance = pd.DataFrame({
                        'feature': X_numerical.columns,
                        'f_score': f_scores,
                        'p_value': p_values,
                        'mutual_info': mi_scores,
                        'rf_importance': rf_importance
                    })
                    
                    # 종합 중요도 점수 계산
                    feature_importance['combined_score'] = (
                        feature_importance['f_score'] / feature_importance['f_score'].max() +
                        feature_importance['mutual_info'] / feature_importance['mutual_info'].max() +
                        feature_importance['rf_importance'] / feature_importance['rf_importance'].max()
                    ) / 3
                    
                    # 중요도 기준으로 정렬
                    feature_importance = feature_importance.sort_values('combined_score', ascending=False)
                    
                    importance_results[target] = {
                        'feature_importance': feature_importance.to_dict('records'),
                        'top_features': feature_importance.head(10)['feature'].tolist(),
                        'importance_threshold': self.optimization_config['importance_threshold']
                    }
            
            self.feature_importance = importance_results
            logger.info(f"특성 중요도 분석 완료: {len(importance_results)}개 타겟에 대해 분석")
            return importance_results
            
        except Exception as e:
            logger.error(f"특성 중요도 분석 실패: {e}")
            return {'error': str(e)}
    
    def _create_engineered_features(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """새로운 특성 생성"""
        try:
            engineered_data = training_data.copy()
            new_features = {}
            
            # 1. 다항식 특성 생성
            logger.info("다항식 특성 생성 중...")
            numerical_features = engineered_data.select_dtypes(include=[np.number])
            numerical_features = numerical_features.drop(['success_rate', 'efficiency_score', 'complexity_score', 'category_encoded'], axis=1, errors='ignore')
            
            if len(numerical_features.columns) > 0:
                poly = PolynomialFeatures(degree=self.optimization_config['polynomial_degree'], 
                                        include_bias=False, interaction_only=True)
                poly_features = poly.fit_transform(numerical_features)
                
                # 새로운 특성 이름 생성
                feature_names = poly.get_feature_names_out(numerical_features.columns)
                
                # 원본 특성 제외하고 새로운 특성만 추가
                for i, name in enumerate(feature_names):
                    if name not in numerical_features.columns:
                        engineered_data[f'poly_{name}'] = poly_features[:, i]
                        new_features[f'poly_{name}'] = 'polynomial'
            
            # 2. 통계적 특성 생성
            logger.info("통계적 특성 생성 중...")
            if 'pattern_length' in engineered_data.columns and 'word_count' in engineered_data.columns:
                # 패턴 복잡도 지수
                engineered_data['pattern_complexity'] = (
                    engineered_data['pattern_length'] * engineered_data['word_count'] / 100
                )
                new_features['pattern_complexity'] = 'statistical'
                
                # 패턴 효율성
                engineered_data['pattern_efficiency'] = (
                    engineered_data['word_count'] / (engineered_data['pattern_length'] + 1)
                )
                new_features['pattern_efficiency'] = 'statistical'
            
            # 3. 도메인 지식 기반 특성
            logger.info("도메인 지식 기반 특성 생성 중...")
            if 'algorithm_category' in engineered_data.columns:
                # 카테고리별 특성
                category_dummies = pd.get_dummies(engineered_data['algorithm_category'], prefix='category')
                engineered_data = pd.concat([engineered_data, category_dummies], axis=1)
                
                for col in category_dummies.columns:
                    new_features[col] = 'domain_knowledge'
            
            # 4. 클러스터링 기반 특성
            logger.info("클러스터링 기반 특성 생성 중...")
            numerical_for_clustering = engineered_data.select_dtypes(include=[np.number])
            numerical_for_clustering = numerical_for_clustering.drop(['success_rate', 'efficiency_score', 'complexity_score', 'category_encoded'], axis=1, errors='ignore')
            
            if len(numerical_for_clustering.columns) > 0:
                # K-means 클러스터링
                kmeans = KMeans(n_clusters=self.optimization_config['n_clusters'], random_state=42)
                cluster_labels = kmeans.fit_predict(numerical_for_clustering)
                engineered_data['feature_cluster'] = cluster_labels
                new_features['feature_cluster'] = 'clustering'
                
                # 클러스터별 특성
                for i in range(self.optimization_config['n_clusters']):
                    engineered_data[f'cluster_{i}_indicator'] = (cluster_labels == i).astype(int)
                    new_features[f'cluster_{i}_indicator'] = 'clustering'
            
            # 5. 시계열/순서 특성
            logger.info("시계열/순서 특성 생성 중...")
            if 'usage_count' in engineered_data.columns:
                # 사용 빈도 등급
                engineered_data['usage_frequency'] = pd.qcut(
                    engineered_data['usage_count'], 
                    q=5, 
                    labels=['very_low', 'low', 'medium', 'high', 'very_high']
                )
                new_features['usage_frequency'] = 'ordinal'
                
                # 사용 빈도 원핫 인코딩
                usage_dummies = pd.get_dummies(engineered_data['usage_frequency'], prefix='usage')
                engineered_data = pd.concat([engineered_data, usage_dummies], axis=1)
                
                for col in usage_dummies.columns:
                    new_features[col] = 'ordinal'
            
            # 결과 저장
            self.engineered_features = new_features
            
            analysis = {
                'total_new_features': len(new_features),
                'feature_types': new_features,
                'feature_counts_by_type': {},
                'engineered_data_shape': engineered_data.shape
            }
            
            # 타입별 특성 수 계산
            for feature_type in new_features.values():
                if feature_type not in analysis['feature_counts_by_type']:
                    analysis['feature_counts_by_type'][feature_type] = 0
                analysis['feature_counts_by_type'][feature_type] += 1
            
            logger.info(f"새로운 특성 생성 완료: {len(new_features)}개 특성 추가")
            return analysis
            
        except Exception as e:
            logger.error(f"새로운 특성 생성 실패: {e}")
            return {'error': str(e)}
    
    def _optimize_feature_selection(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """특성 선택 최적화"""
        try:
            # 타겟 변수들
            target_columns = ['success_rate', 'efficiency_score', 'complexity_score', 'category_encoded']
            available_targets = [col for col in target_columns if col in training_data.columns]
            
            selection_results = {}
            
            for target in available_targets:
                if target in training_data.columns:
                    # 특성과 타겟 분리
                    X = training_data.drop([target, 'algorithm_id', 'performance_grade'], axis=1, errors='ignore')
                    y = training_data[target]
                    
                    # 수치형 특성만 선택
                    X_numerical = X.select_dtypes(include=[np.number])
                    
                    if len(X_numerical.columns) == 0:
                        continue
                    
                    # 1. SelectKBest (F-통계량 기반)
                    if target in ['success_rate', 'efficiency_score', 'complexity_score']:
                        selector_kbest = SelectKBest(score_func=f_regression, k=min(self.optimization_config['max_features'], len(X_numerical.columns)))
                    else:
                        selector_kbest = SelectKBest(score_func=f_classif, k=min(self.optimization_config['max_features'], len(X_numerical.columns)))
                    
                    X_kbest = selector_kbest.fit_transform(X_numerical, y)
                    selected_features_kbest = X_numerical.columns[selector_kbest.get_support()].tolist()
                    
                    # 2. RFE (Recursive Feature Elimination)
                    if target in ['success_rate', 'efficiency_score', 'complexity_score']:
                        estimator = RandomForestRegressor(n_estimators=100, random_state=42)
                    else:
                        estimator = RandomForestClassifier(n_estimators=100, random_state=42)
                    
                    selector_rfe = RFE(
                        estimator=estimator,
                        n_features_to_select=min(self.optimization_config['max_features'], len(X_numerical.columns))
                    )
                    
                    X_rfe = selector_rfe.fit_transform(X_numerical, y)
                    selected_features_rfe = X_numerical.columns[selector_rfe.get_support()].tolist()
                    
                    # 3. 상관관계 기반 선택
                    if target in self.feature_importance:
                        importance_df = pd.DataFrame(self.feature_importance[target]['feature_importance'])
                        selected_features_importance = importance_df[
                            importance_df['combined_score'] > self.optimization_config['importance_threshold']
                        ]['feature'].tolist()
                    else:
                        selected_features_importance = []
                    
                    # 4. 최종 특성 선택 (교집합 + 합집합)
                    all_selected = set(selected_features_kbest) | set(selected_features_rfe) | set(selected_features_importance)
                    final_selected = list(all_selected)[:self.optimization_config['max_features']]
                    
                    selection_results[target] = {
                        'kbest_features': selected_features_kbest,
                        'rfe_features': selected_features_rfe,
                        'importance_features': selected_features_importance,
                        'final_selected': final_selected,
                        'selection_methods': ['kbest', 'rfe', 'importance']
                    }
            
            self.feature_selection_results = selection_results
            logger.info(f"특성 선택 최적화 완료: {len(selection_results)}개 타겟에 대해 분석")
            return selection_results
            
        except Exception as e:
            logger.error(f"특성 선택 최적화 실패: {e}")
            return {'error': str(e)}
    
    def _create_final_feature_set(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """최종 특성 세트 생성"""
        try:
            # 모든 선택된 특성 통합
            all_selected_features = set()
            
            for target, selection_result in self.feature_selection_results.items():
                if 'final_selected' in selection_result:
                    all_selected_features.update(selection_result['final_selected'])
            
            # 기본 특성들 추가 (항상 필요한 특성들)
            essential_features = ['algorithm_id', 'success_rate', 'efficiency_score', 'complexity_score', 'performance_grade']
            for feature in essential_features:
                if feature in training_data.columns:
                    all_selected_features.add(feature)
            
            # 최종 특성 세트
            final_features = list(all_selected_features)
            
            # 특성 우선순위 설정
            feature_priority = {}
            
            # 1순위: 기본 특성
            for feature in essential_features:
                if feature in final_features:
                    feature_priority[feature] = 1
            
            # 2순위: 중요도 높은 특성
            for target, importance_result in self.feature_importance.items():
                if 'top_features' in importance_result:
                    for feature in importance_result['top_features'][:5]:  # 상위 5개
                        if feature in final_features:
                            feature_priority[feature] = 2
            
            # 3순위: 엔지니어링된 특성
            for feature in self.engineered_features:
                if feature in final_features:
                    feature_priority[feature] = 3
            
            # 4순위: 나머지 특성
            for feature in final_features:
                if feature not in feature_priority:
                    feature_priority[feature] = 4
            
            # 우선순위별로 정렬
            final_features_sorted = sorted(final_features, key=lambda x: feature_priority.get(x, 5))
            
            # 최종 특성 세트 생성
            final_feature_set = training_data[final_features_sorted]
            
            # 결과 저장
            final_result = {
                'selected_features': final_features_sorted,
                'feature_count': len(final_features_sorted),
                'feature_priority': feature_priority,
                'final_data_shape': final_feature_set.shape,
                'feature_categories': {
                    'essential': [f for f, p in feature_priority.items() if p == 1],
                    'high_importance': [f for f, p in feature_priority.items() if p == 2],
                    'engineered': [f for f, p in feature_priority.items() if p == 3],
                    'other': [f for f, p in feature_priority.items() if p == 4]
                }
            }
            
            # 최적화된 특성 저장
            self.optimized_features = final_result
            
            logger.info(f"최종 특성 세트 생성 완료: {len(final_features_sorted)}개 특성 선택")
            return final_result
            
        except Exception as e:
            logger.error(f"최종 특성 세트 생성 실패: {e}")
            return {'error': str(e)}
    
    def get_optimized_features(self) -> Dict[str, Any]:
        """최적화된 특성들 반환"""
        return self.optimized_features.copy()
    
    def save_optimization_results(self, filepath: str) -> bool:
        """최적화 결과 저장"""
        try:
            results_data = {
                'optimized_features': self.optimized_features,
                'feature_selection_results': self.feature_selection_results,
                'engineered_features': self.engineered_features,
                'feature_importance': self.feature_importance,
                'feature_correlations': self.feature_correlations,
                'optimization_config': self.optimization_config
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(results_data, f)
            
            logger.info(f"특성 엔지니어링 최적화 결과 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"결과 저장 실패: {e}")
            return False
    
    def load_optimization_results(self, filepath: str) -> bool:
        """저장된 최적화 결과 로드"""
        try:
            with open(filepath, 'rb') as f:
                results_data = pickle.load(f)
            
            self.optimized_features = results_data['optimized_features']
            self.feature_selection_results = results_data['feature_selection_results']
            self.engineered_features = results_data['engineered_features']
            self.feature_importance = results_data['feature_importance']
            self.feature_correlations = results_data['feature_correlations']
            self.optimization_config = results_data['optimization_config']
            
            logger.info(f"특성 엔지니어링 최적화 결과 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"결과 로드 실패: {e}")
            return False
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """최적화 결과 요약"""
        summary = {
            'total_engineered_features': len(self.engineered_features),
            'feature_selection_targets': list(self.feature_selection_results.keys()),
            'optimization_config': self.optimization_config
        }
        
        if self.optimized_features:
            summary.update({
                'final_feature_count': self.optimized_features.get('feature_count', 0),
                'feature_categories': self.optimized_features.get('feature_categories', {})
            })
        
        return summary
