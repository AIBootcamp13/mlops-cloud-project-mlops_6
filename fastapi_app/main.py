from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict


import os
import ast
from datetime import date
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import joblib

from movie_rating_predictor import  MovieRatingPredictor
from movie_rating import MovieRatingDataset

def init_model(checkpoint):
    model = MovieRatingPredictor(**checkpoint["model_params"])
    model.load_state_dict(checkpoint["model_state_dict"])
    scaler = checkpoint.get("scaler", None)
    label_encoders = checkpoint.get("label_encoders", None)
    mlb_genres = checkpoint.get("mlb_genres", None)
    mlb_keywords = checkpoint.get("mlb_keywords", None)
    return model, scaler, label_encoders, mlb_genres, mlb_keywords

def make_inference_df(data):
    """
    영화 추론을 위한 데이터프레임 생성
    data: 딕셔너리 또는 리스트 형태의 영화 데이터
    """
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = pd.DataFrame(data)
    
    # 리스트 컬럼 처리
    list_columns = ['genres', 'keywords', 'cast', 'crew']
    for col in list_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])
    
    # 기본값 설정
    if 'vote_average' not in df.columns:
        df['vote_average'] = 0  # 추론 시에는 실제 평점이 없으므로 0으로 설정
    
    return df


def download_from_minio(key: str, bucket_name: str, local_filename: str) -> None:
    """S3 버킷에서 로컬로 파일 다운로드 (boto3 사용)"""
    
    # 기존 파일이 있으면 스킵
    if os.path.exists(local_filename + key):
        #os.remove(local_filename + key)
        return

    # boto3 클라이언트 생성
    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio:9000',  # MinIO 엔드포인트
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        region_name='us-east-1',
    )

    try:
        # 파일 다운로드
        download_path = local_filename + key
        s3_client.download_file(
            Bucket=bucket_name, 
            Key=key, 
            Filename=download_path
        )
        print(f"Downloaded s3://{bucket_name}/{key} to {download_path}")
    except ClientError as e:
        print(f"Error downloading file: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


def get_data():

    current_date = date.today().strftime("%Y%m%d")
    movie_file_name = "TMDB_" + current_date + ".csv"
    model_file_name = "E1_T" + current_date + ".pkl"

    op_kwargs={
                'key': movie_file_name,
                'bucket_name': 'futurecraft',
                'local_filename': '/app/'  # 다운로드받을 경로
            }

    download_from_minio(**op_kwargs)

    op_kwargs={
                'key': model_file_name,
                'bucket_name': 'futurecraft',
                'local_filename': '/app/'  # 다운로드받을 경로
            }

    download_from_minio(**op_kwargs)

    # 영화데이타
    df = pd.read_csv('/app/'+movie_file_name) if os.path.exists('/app/'+movie_file_name) else pd.read_csv('/app/default.csv') 
    df = df.sort_values('vote_count', ascending=False).iloc[:20]
    df['poster_path'] = 'https://image.tmdb.org/t/p/w500' + df['poster_path']
    #df.rename(columns={'poster_path': 'poster'}, inplace=True)
    app.state.movies = df.to_dict(orient='records')    

    # 모델
    checkpoint = joblib.load('/app/'+model_file_name) if os.path.exists('/app/'+model_file_name) else joblib.load('/app/default.pkl') 
    app.state.model, app.state.scaler, app.state.label_encoders, app.state.mlb_genres, app.state.mlb_keywords = init_model(checkpoint)

def check_date_and_call_get_data():
    """날짜가 바뀌었는지 체크하고 바뀌었으면 get_data() 호출"""
    today =  date.today().strftime("%Y%m%d")
   
    if today != app.state.current_date:
        get_data()
    
@asynccontextmanager
async def lifespan(app: FastAPI):
   
    app.state.current_date =  date.today().strftime("%Y%m%d")
    get_data()    

    yield

app = FastAPI(lifespan=lifespan, title='영화 평점 예측 서비스')    


# 정적 파일과 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def convert_string_to_list(data):
    """문자열로 된 리스트를 실제 리스트로 변환"""
    for key in ['genres', 'keywords', 'cast', 'crew']:
        if key in data and isinstance(data[key], str):
            try:
                data[key] = ast.literal_eval(data[key])
            except Exception as e:
                print(f"Error converting {key}: {e}")
                data[key] = None
    return data

class MoviePredictionRequest(BaseModel):
    id: int
    title: str
    genres: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    cast: Optional[List[str]] = None
    crew: Optional[List[str]] = None
    release_date: Optional[str] = None
    runtime: Optional[int] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None

class MoviePredictionResponse(BaseModel):
    movie_id: int
    predicted_rating: float
    confidence: Optional[float] = None

@app.post("/predict", response_model=MoviePredictionResponse)
async def predict_movie_rating(request: dict):
    """
    영화 특성을 기반으로 예상 평점을 예측하는 API
    """
    try:
        # 문자열 리스트를 실제 리스트로 변환
        converted_data = convert_string_to_list(request.copy())
        
        # Pydantic 검증
        movie_data = MoviePredictionRequest(**converted_data)

        input_dict = movie_data.model_dump()  
        df = make_inference_df(input_dict)


        dataset = MovieRatingDataset(
            df, 
            scaler=app.state.scaler, 
            label_encoders=app.state.label_encoders,
            mlb_genres=app.state.mlb_genres,
            mlb_keywords=app.state.mlb_keywords
        )

        y_pred = app.state.model.model.predict(dataset.features)[0]
        predicted_rating = round(float(y_pred), 3)
       
        return MoviePredictionResponse(
            movie_id=movie_data.id,
            predicted_rating=predicted_rating,
            confidence=0.85
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    check_date_and_call_get_data()
    return templates.TemplateResponse("index.html", {"request": request, "movies": app.state.movies})

@app.get("/health")
def health_check():

    check_date_and_call_get_data()
    return {"status": "healthy"}

