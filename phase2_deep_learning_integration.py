"""
Phase 2: 딥러닝 통합 시스템
Phase 1의 전통적 ML과 딥러닝을 결합한 하이브리드 시스템
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import time
import traceback
import json

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

logger = logging.getLogger(__name__)

class DeepLearningModel(nn.Module):
    """딥러닝 신경망 모델"""
    
    def __init__(self, input_size: int, hidden_sizes: List[int] = None, dropout_rate: float = 0.2):
        super(DeepLearningModel, self).__init__()
        
        if hidden_sizes is None:
            hidden_sizes = [128, 64, 32]
        
        layers = []
        prev_size = input_size
        
        # 은닉층 구성
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_size = hidden_size
        
        # 출력층
        layers.append(nn.Linear(prev_size, 1))
        
        self.network = nn.Sequential(*layers)
        
        # 가중치 초기화
        self._initialize_weights()
    
    def _initialize_weights(self):
        """가중치 초기화"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, x):
        return self.network(x)

class AlgorithmDataset(Dataset):
    """알고리즘 데이터셋"""
    
    def __init__(self, features: np.ndarray, targets: np.ndarray):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]

class Phase2DeepLearningIntegration:
    """Phase 2: 딥러닝 통합 시스템"""
    
    def __init__(self, phase1_models: Dict[str, Any] = None):
        self.phase1_models = phase1_models or {}
        
        # 딥러닝 모델
        self.deep_learning_model = None
        self.deep_learning_scaler = None
        
        # 통합 시스템 설정
        self.integration_config = {
            'ensemble_weight_ml': 0.4,      # ML 모델 가중치
            'ensemble_weight_dl': 0.6,      # 딥러닝 모델 가중치
            'training_epochs': 100,         # 학습 에포크
            'learning_rate': 0.001,         # 학습률
            'batch_size': 32,               # 배치 크기
            'early_stopping_patience': 10   # 조기 종료 인내심
        }
        
        # 성능 메트릭
        self.performance_metrics = {}
        
        logger.info("Phase 2 딥러닝 통합 시스템 초기화 완료")
    
    def create_enhanced_test_data(self) -> pd.DataFrame:
        """향상된 테스트 데이터 생성"""
        try:
            np.random.seed(42)
            
            data = []
            for i in range(1000):  # 샘플 수 증가
                # 기본 특성들
                algorithm_complexity = np.random.uniform(1.0, 15.0)
                input_size = np.random.randint(10, 2000)
                memory_usage = np.random.uniform(0.1, 15.0)
                
                # 추가 특성들
                code_quality = np.random.uniform(0.1, 1.0)
                documentation_score = np.random.uniform(0.1, 1.0)
                test_coverage = np.random.uniform(0.1, 1.0)
                
                # 성공률 (더 복잡한 관계)
                base_success = 0.9 - (algorithm_complexity * 0.03) + (input_size * 0.00005)
                quality_bonus = (code_quality + documentation_score + test_coverage) * 0.1
                success_rate = max(0.1, min(1.0, base_success + quality_bonus + np.random.normal(0, 0.08)))
                
                # 효율성 점수
                efficiency_score = max(0.1, min(1.0,
                    success_rate * 0.7 + 
                    (1.0 - memory_usage * 0.05) + 
                    code_quality * 0.2 + 
                    np.random.normal(0, 0.1)
                ))
                
                data.append({
                    'algorithm_id': f'alg_{i}',
                    'algorithm_complexity': algorithm_complexity,
                    'input_size': input_size,
                    'memory_usage': memory_usage,
                    'code_lines': int(algorithm_complexity * 60 + np.random.normal(0, 15)),
                    'execution_time': algorithm_complexity * 0.08 + np.random.normal(0, 0.04),
                    'code_quality': code_quality,
                    'documentation_score': documentation_score,
                    'test_coverage': test_coverage,
                    'success_rate': success_rate,
                    'efficiency_score': efficiency_score
                })
            
            df = pd.DataFrame(data)
            logger.info(f"향상된 테스트 데이터 생성 완료: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"향상된 테스트 데이터 생성 실패: {e}")
            return pd.DataFrame()
    
    def train_deep_learning_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """딥러닝 모델 학습"""
        try:
            if not DEEP_LEARNING_AVAILABLE:
                return {'success': False, 'reason': '딥러닝 라이브러리 없음'}
            
            logger.info("딥러닝 모델 학습 시작...")
            
            # 특성과 타겟 분리
            feature_columns = ['algorithm_complexity', 'input_size', 'memory_usage', 
                              'code_lines', 'execution_time', 'code_quality', 
                              'documentation_score', 'test_coverage']
            
            X = training_data[feature_columns].values
            y = training_data['success_rate'].values
            
            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 특성 스케일링
            self.deep_learning_scaler = StandardScaler()
            X_train_scaled = self.deep_learning_scaler.fit_transform(X_train)
            X_test_scaled = self.deep_learning_scaler.transform(X_test)
            
            # 데이터셋 및 데이터로더 생성
            train_dataset = AlgorithmDataset(X_train_scaled, y_train)
            test_dataset = AlgorithmDataset(X_test_scaled, y_test)
            
            train_loader = DataLoader(train_dataset, batch_size=self.integration_config['batch_size'], shuffle=True)
            test_loader = DataLoader(test_dataset, batch_size=self.integration_config['batch_size'], shuffle=False)
            
            # 모델 초기화
            input_size = len(feature_columns)
            self.deep_learning_model = DeepLearningModel(
                input_size=input_size,
                hidden_sizes=[256, 128, 64, 32],
                dropout_rate=0.3
            )
            
            # 손실 함수 및 옵티마이저
            criterion = nn.MSELoss()
            optimizer = optim.Adam(
                self.deep_learning_model.parameters(), 
                lr=self.integration_config['learning_rate']
            )
            
            # 학습 루프
            best_loss = float('inf')
            patience_counter = 0
            training_history = []
            
            for epoch in range(self.integration_config['training_epochs']):
                # 학습 모드
                self.deep_learning_model.train()
                train_loss = 0.0
                
                for batch_features, batch_targets in train_loader:
                    optimizer.zero_grad()
                    outputs = self.deep_learning_model(batch_features).squeeze()
                    loss = criterion(outputs, batch_targets)
                    loss.backward()
                    optimizer.step()
                    train_loss += loss.item()
                
                # 검증 모드
                self.deep_learning_model.eval()
                val_loss = 0.0
                val_predictions = []
                val_targets = []
                
                with torch.no_grad():
                    for batch_features, batch_targets in test_loader:
                        outputs = self.deep_learning_model(batch_features).squeeze()
                        loss = criterion(outputs, batch_targets)
                        val_loss += loss.item()
                        val_predictions.extend(outputs.numpy())
                        val_targets.extend(batch_targets.numpy())
                
                # 평균 손실 계산
                avg_train_loss = train_loss / len(train_loader)
                avg_val_loss = val_loss / len(test_loader)
                
                training_history.append({
                    'epoch': epoch + 1,
                    'train_loss': avg_train_loss,
                    'val_loss': avg_val_loss
                })
                
                # 조기 종료 체크
                if avg_val_loss < best_loss:
                    best_loss = avg_val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                
                if patience_counter >= self.integration_config['early_stopping_patience']:
                    logger.info(f"조기 종료: 에포크 {epoch + 1}")
                    break
                
                if (epoch + 1) % 20 == 0:
                    logger.info(f"에포크 {epoch + 1}/{self.integration_config['training_epochs']}: "
                              f"Train Loss: {avg_train_loss:.6f}, Val Loss: {avg_val_loss:.6f}")
            
            # 최종 성능 평가
            val_r2 = r2_score(val_targets, val_predictions)
            val_mse = mean_squared_error(val_targets, val_predictions)
            
            # 교차 검증
            cv_scores = self._cross_validate_deep_learning(X_train_scaled, y_train)
            
            performance_metrics = {
                'r2_score': val_r2,
                'mse': val_mse,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'training_history': training_history,
                'best_epoch': len(training_history) - patience_counter
            }
            
            self.performance_metrics['deep_learning'] = performance_metrics
            
            logger.info(f"딥러닝 모델 학습 완료: R²={val_r2:.3f}, MSE={val_mse:.6f}")
            
            return {
                'success': True,
                'performance': performance_metrics
            }
            
        except Exception as e:
            logger.error(f"딥러닝 모델 학습 실패: {e}")
            return {'success': False, 'reason': str(e)}
    
    def _cross_validate_deep_learning(self, X: np.ndarray, y: np.ndarray, cv_folds: int = 5) -> np.ndarray:
        """딥러닝 모델 교차 검증"""
        try:
            cv_scores = []
            
            for fold in range(cv_folds):
                # 데이터 분할
                fold_size = len(X) // cv_folds
                start_idx = fold * fold_size
                end_idx = start_idx + fold_size if fold < cv_folds - 1 else len(X)
                
                X_val = X[start_idx:end_idx]
                y_val = y[start_idx:end_idx]
                X_train = np.concatenate([X[:start_idx], X[end_idx:]])
                y_train = np.concatenate([y[:start_idx], y[end_idx:]])
                
                # 모델 학습
                model = DeepLearningModel(input_size=X.shape[1], hidden_sizes=[128, 64])
                criterion = nn.MSELoss()
                optimizer = optim.Adam(model.parameters(), lr=0.001)
                
                # 간단한 학습 (빠른 교차 검증을 위해)
                for epoch in range(20):
                    model.train()
                    optimizer.zero_grad()
                    outputs = model(torch.FloatTensor(X_train)).squeeze()
                    loss = criterion(outputs, torch.FloatTensor(y_train))
                    loss.backward()
                    optimizer.step()
                
                # 검증
                model.eval()
                with torch.no_grad():
                    val_outputs = model(torch.FloatTensor(X_val)).squeeze()
                    val_r2 = r2_score(y_val, val_outputs.numpy())
                    cv_scores.append(val_r2)
            
            return np.array(cv_scores)
            
        except Exception as e:
            logger.error(f"교차 검증 실패: {e}")
            return np.array([0.0])
    
    def create_hybrid_system(self) -> Dict[str, Any]:
        """하이브리드 시스템 생성 (ML + 딥러닝)"""
        try:
            logger.info("하이브리드 시스템 생성 시작...")
            
            if not self.deep_learning_model:
                return {'success': False, 'reason': '딥러닝 모델이 학습되지 않음'}
            
            # 향상된 테스트 데이터 생성
            test_data = self.create_enhanced_test_data()
            if test_data.empty:
                return {'success': False, 'reason': '테스트 데이터 생성 실패'}
            
            # 특성 선택
            feature_columns = ['algorithm_complexity', 'input_size', 'memory_usage', 
                              'code_lines', 'execution_time', 'code_quality', 
                              'documentation_score', 'test_coverage']
            
            X = test_data[feature_columns].values
            y = test_data['success_rate'].values
            
            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 1. 딥러닝 모델 예측
            X_test_scaled = self.deep_learning_scaler.transform(X_test)
            self.deep_learning_model.eval()
            
            with torch.no_grad():
                dl_predictions = self.deep_learning_model(torch.FloatTensor(X_test_scaled)).squeeze().numpy()
            
            # 2. Phase 1 모델들 예측 (간단한 구현)
            # 실제로는 phase1_models에서 가져와야 함
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X_train, y_train)
            rf_predictions = rf_model.predict(X_test)
            
            xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42)
            xgb_model.fit(X_train, y_train)
            xgb_predictions = xgb_model.predict(X_test)
            
            # 3. 앙상블 예측
            ensemble_predictions = (
                rf_predictions * 0.2 +
                xgb_predictions * 0.2 +
                dl_predictions * 0.6
            )
            
            # 4. 성능 비교
            performance_comparison = {
                'random_forest': {
                    'r2': r2_score(y_test, rf_predictions),
                    'mse': mean_squared_error(y_test, rf_predictions)
                },
                'xgboost': {
                    'r2': r2_score(y_test, xgb_predictions),
                    'mse': mean_squared_error(y_test, xgb_predictions)
                },
                'deep_learning': {
                    'r2': r2_score(y_test, dl_predictions),
                    'mse': mean_squared_error(y_test, dl_predictions)
                },
                'ensemble': {
                    'r2': r2_score(y_test, ensemble_predictions),
                    'mse': mean_squared_error(y_test, ensemble_predictions)
                }
            }
            
            # 5. 개선 효과 분석
            best_individual = max(
                performance_comparison.items(),
                key=lambda x: x[1]['r2']
            )
            
            ensemble_improvement = {
                'best_individual_model': best_individual[0],
                'best_individual_r2': best_individual[1]['r2'],
                'ensemble_r2': performance_comparison['ensemble']['r2'],
                'improvement': performance_comparison['ensemble']['r2'] - best_individual[1]['r2'],
                'improvement_percentage': ((performance_comparison['ensemble']['r2'] - best_individual[1]['r2']) / best_individual[1]['r2']) * 100 if best_individual[1]['r2'] != 0 else 0
            }
            
            hybrid_system_info = {
                'success': True,
                'performance_comparison': performance_comparison,
                'ensemble_improvement': ensemble_improvement,
                'feature_importance': {
                    'random_forest': dict(zip(feature_columns, rf_model.feature_importances_)),
                    'xgboost': dict(zip(feature_columns, xgb_model.feature_importances_))
                }
            }
            
            logger.info("하이브리드 시스템 생성 완료")
            return hybrid_system_info
            
        except Exception as e:
            logger.error(f"하이브리드 시스템 생성 실패: {e}")
            return {'success': False, 'reason': str(e)}
    
    def get_system_summary(self) -> Dict[str, Any]:
        """시스템 요약 정보"""
        summary = {
            'phase1_status': 'completed' if self.phase1_models else 'not_available',
            'deep_learning_status': 'completed' if self.deep_learning_model else 'not_trained',
            'hybrid_system_status': 'available' if self.deep_learning_model else 'not_available',
            'performance_metrics': self.performance_metrics.copy()
        }
        
        return summary
    
    def save_models(self, save_path: str) -> bool:
        """모델 저장"""
        try:
            if self.deep_learning_model:
                torch.save({
                    'model_state_dict': self.deep_learning_model.state_dict(),
                    'scaler': self.deep_learning_scaler,
                    'performance_metrics': self.performance_metrics,
                    'integration_config': self.integration_config
                }, f"{save_path}/phase2_deep_learning_model.pth")
                
                logger.info(f"딥러닝 모델 저장 완료: {save_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            return False
    
    def load_models(self, load_path: str) -> bool:
        """모델 로드"""
        try:
            checkpoint = torch.load(f"{load_path}/phase2_deep_learning_model.pth")
            
            # 모델 상태 복원
            if 'model_state_dict' in checkpoint:
                input_size = 8  # 기본 특성 수
                self.deep_learning_model = DeepLearningModel(input_size=input_size)
                self.deep_learning_model.load_state_dict(checkpoint['model_state_dict'])
            
            # 스케일러 및 설정 복원
            if 'scaler' in checkpoint:
                self.deep_learning_scaler = checkpoint['scaler']
            
            if 'performance_metrics' in checkpoint:
                self.performance_metrics = checkpoint['performance_metrics']
            
            if 'integration_config' in checkpoint:
                self.integration_config.update(checkpoint['integration_config'])
            
            logger.info(f"딥러닝 모델 로드 완료: {load_path}")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
