import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, MultiLabelBinarizer
from ast import literal_eval

from src.utils import config

class MovieRatingDataset:
    def __init__(self, df, scaler=None, label_encoders=None, mlb_genres=None, mlb_keywords=None):
        self.df = df
        self.features = None
        self.labels = None
        self.scaler = scaler
        self.label_encoders = label_encoders
        self.mlb_genres = mlb_genres
        self.mlb_keywords = mlb_keywords
        self._preprocessing()

    def _preprocessing(self):
        target_nm = 'vote_average'
        
        # 타겟 정의 (영화 평점)
        self.labels = self.df[target_nm].to_numpy()
        
        # 피처 정의
        feature_df = self.df.drop(columns=[target_nm], axis=1)
        
        # 수치형 피처
        numerical_features = feature_df[['runtime', 'vote_count', 'popularity']].fillna(0)
        
        # 날짜 피처 처리 (연도 추출)
        feature_df['release_year'] = pd.to_datetime(feature_df['release_date'], errors='coerce').dt.year.fillna(0)
        numerical_features['release_year'] = feature_df['release_year']
        
        # 장르 원-핫 인코딩
        if self.mlb_genres:
            # 추론 시에는 학습 데이터에 없던 장르는 무시
            filtered_genres = []
            for genres in feature_df['genres']:
                filtered = [g for g in genres if g in self.mlb_genres.classes_]
                filtered_genres.append(filtered)
            genres_encoded = self.mlb_genres.transform(filtered_genres)
        else:
            self.mlb_genres = MultiLabelBinarizer()
            genres_encoded = self.mlb_genres.fit_transform(feature_df['genres'])
        
        # 키워드 원-핫 인코딩 (상위 100개만 사용)
        if self.mlb_keywords:
            # 추론 시에는 학습 데이터에 없던 키워드는 무시
            filtered_keywords = []
            for keywords in feature_df['keywords']:
                filtered = [k for k in keywords if k in self.mlb_keywords.classes_]
                filtered_keywords.append(filtered)
            keywords_encoded = self.mlb_keywords.transform(filtered_keywords)
        else:
            # 키워드 빈도 계산하여 상위 100개만 선택
            all_keywords = []
            for keywords in feature_df['keywords']:
                all_keywords.extend(keywords)
            
            from collections import Counter
            keyword_counts = Counter(all_keywords)
            top_keywords = [k for k, _ in keyword_counts.most_common(100)]
            
            self.mlb_keywords = MultiLabelBinarizer(classes=top_keywords)
            keywords_encoded = self.mlb_keywords.fit_transform(feature_df['keywords'])
        
        # 출연진/제작진 수 계산
        feature_df['cast_count'] = feature_df['cast'].apply(len)
        feature_df['crew_count'] = feature_df['crew'].apply(len)
        
        numerical_features['cast_count'] = feature_df['cast_count']
        numerical_features['crew_count'] = feature_df['crew_count']
        
        # 모든 피처 결합
        features = np.hstack([
            numerical_features.to_numpy(),
            genres_encoded,
            keywords_encoded
        ])
        
        # 피처 스케일링
        if self.scaler:
            self.features = self.scaler.transform(features)
        else:
            self.scaler = StandardScaler()
            self.features = self.scaler.fit_transform(features)

    @property
    def features_dim(self):
        return self.features.shape[1]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]


def read_dataset(filePath):
    # 영화 데이터 CSV 파일 읽기
    df = pd.read_csv(filePath)
    
    # 문자열로 저장된 리스트 컬럼들을 실제 리스트로 변환
    list_columns = ['genres', 'keywords', 'cast', 'crew', 'similar_ids']
    
    for col in list_columns:
        df[col] = df[col].apply(lambda x: literal_eval(x) if pd.notna(x) and x != '' else [])
    
    # vote_average가 0이거나 결측치인 데이터 제거
    df = df[(df['vote_average'] > 0) & (df['vote_count'] > 0)]
    
    return df


def preprocess_dataset(df):
    """
    데이터 전처리 및 피처 엔지니어링
    """
    # 필요한 컬럼만 선택
    columns_to_keep = [
        'id', 'title', 'genres', 'keywords', 'cast', 'crew',
        'release_date', 'runtime', 'vote_average', 'vote_count', 'popularity'
    ]
    
    df = df[columns_to_keep].copy()
    
    # 결측치 처리
    df['runtime'] = df['runtime'].fillna(df['runtime'].median())
    df['popularity'] = df['popularity'].fillna(0)
    
    return df


def split_dataset(df):
    """
    데이터셋을 train, validation, test로 분할
    """
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)
    
    return train_df, val_df, test_df


def get_datasets(filePath=None, scaler=None, label_encoders=None, mlb_genres=None, mlb_keywords=None):
    """
    전체 데이터셋 준비 프로세스
    """
    # 1. 데이터 읽기
    df = read_dataset(filePath)
    
    # 2. 전처리
    df = preprocess_dataset(df)
    
    # 3. 데이터 분할
    train_df, val_df, test_df = split_dataset(df)
    
    # 4. 데이터셋 객체 생성
    train_dataset = MovieRatingDataset(train_df, scaler, label_encoders, mlb_genres, mlb_keywords)
    val_dataset = MovieRatingDataset(
        val_df, 
        scaler=train_dataset.scaler, 
        label_encoders=train_dataset.label_encoders,
        mlb_genres=train_dataset.mlb_genres,
        mlb_keywords=train_dataset.mlb_keywords
    )
    test_dataset = MovieRatingDataset(
        test_df, 
        scaler=train_dataset.scaler, 
        label_encoders=train_dataset.label_encoders,
        mlb_genres=train_dataset.mlb_genres,
        mlb_keywords=train_dataset.mlb_keywords
    )
    
    return train_dataset, val_dataset, test_dataset