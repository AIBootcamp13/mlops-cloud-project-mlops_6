import os
import pickle
import datetime

import numpy as np
import pandas as pd
import lightgbm as lgbm

class MovieRatingPredictor:
    name = "movie_rating_predictor"  

    def __init__(self, input_dim=None, num_classes=None, hidden_dim=None, train_dataset=None, val_dataset=None, test_dataset=None):
        
        self.model = lgbm.LGBMRegressor(
                boosting_type='gbdt',
                colsample_bytree=0.8219308825575806,
                learning_rate=0.1,  # 영화 데이터에 맞게 조정
                max_bin=255,
                min_child_samples=20,  # 영화 데이터에 맞게 조정
                n_estimators=2000,  # 영화 데이터에 맞게 조정
                n_jobs=-1,
                num_leaves=31,  # 영화 데이터에 맞게 조정
                reg_alpha=0.5,  # 정규화 파라미터 조정
                reg_lambda=0.5,  # 정규화 파라미터 조정
                verbose=-1, 
                device='cpu',  # CPU 사용으로 변경
                metric='rmse',  # 평점 예측에 적합한 메트릭
                objective='regression'
        )
    
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.test_dataset = test_dataset

    def load_state_dict(self, state_dict):
        self.model = state_dict   

    def train_lgbm(self):
        dataset = self.train_dataset
        val_dataset = self.val_dataset
        evals_result_history = {}

        self.model.fit(
            dataset.features, 
            dataset.labels,
            eval_set=[(dataset.features, dataset.labels), (val_dataset.features, val_dataset.labels)], 
            eval_names=['train', 'valid'],
            eval_metric='rmse',  # RMSE는 평점 예측에 더 적합
            callbacks=[
                lgbm.early_stopping(stopping_rounds=100),  # 조기 종료 라운드 증가
                lgbm.log_evaluation(period=50, show_stdv=True),
                lgbm.record_evaluation(evals_result_history)
            ]
        )
        
        # 훈련 과정의 마지막 RMSE 반환
        train_rmse_history = evals_result_history.get('train', {}).get('rmse', [])
        val_rmse_history = evals_result_history.get('valid', {}).get('rmse', [])
        
        print(f"Final Train RMSE: {train_rmse_history[-1]:.4f}")
        print(f"Final Valid RMSE: {val_rmse_history[-1]:.4f}")
        
        return train_rmse_history[-1]


    def evaluate(self, dataset=None):
        
        dataset = self.val_dataset if dataset is None else dataset

        # 검증 데이터 예측
        predictions = self.model.predict(dataset.features)
        
        # 평점 범위로 클리핑 (0~10)
        predictions = np.clip(predictions, 0, 10)
        
        # RMSE 계산
        rmse = np.sqrt(np.mean((predictions - dataset.labels) ** 2))
        
        # MAE 계산 (추가 메트릭)
        mae = np.mean(np.abs(predictions - dataset.labels))
        
        print(f"Validation RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        
        return rmse, predictions

    def test(self, dataset=None):

        dataset = self.test_dataset if dataset is None else dataset

        # 테스트 데이터 예측
        predictions = self.model.predict(dataset.features)
        
        # 평점 범위로 클리핑 (0~10)
        predictions = np.clip(predictions, 0, 10)
        
        # RMSE 계산
        rmse = np.sqrt(np.mean((predictions - dataset.labels) ** 2))
        
        # MAE 계산
        mae = np.mean(np.abs(predictions - dataset.labels))
        
        print(f"Test RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        
        return rmse, predictions
    
    def get_feature_importance(self):
        """피처 중요도 반환"""
        importance = self.model.feature_importances_
        feature_names = self.get_feature_names()
        
        feature_importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return feature_importance_df
    
    def get_feature_names(self):
        """피처 이름 생성"""
        # 기본 수치형 피처
        feature_names = ['runtime', 'vote_count', 'popularity', 'release_year', 'cast_count', 'crew_count']
        
        # 장르 피처
        if hasattr(self.train_dataset, 'mlb_genres'):
            feature_names.extend([f'genre_{g}' for g in self.train_dataset.mlb_genres.classes_])
        
        # 키워드 피처
        if hasattr(self.train_dataset, 'mlb_keywords'):
            feature_names.extend([f'keyword_{k}' for k in self.train_dataset.mlb_keywords.classes_])
        
        return feature_names