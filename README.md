## 💻 프로젝트 소개

### 🎬 영화 평점 예측 서비스
- 영화 포스터와 메타데이터를 활용하여 AI 기반 평점 예측 서비스를 제공하는 영화 추천 플랫폼입니다. 사용자가 포스터를 클릭하면 영화의 상세 정보와 함께 머신러닝 모델이 예측한 평점을 실시간으로 확인할 수 있습니다. 장르, 출연진, 제작진, 개봉일 등의 다양한 영화 메타데이터를 FastAPI로 처리하여 정확한 평점 예측을 제공하며, 직관적인 갤러리 인터페이스로 영화 탐색 경험을 향상시킵니다.
  
### 🎯 프로젝트 목표

- MLOps 자동화를 통한 영화 평점 예측 서비스 개발
- TMDB API를 호출하여 데이터 수집및 갱신
- MINIO 레지스트리에 저장한 영화정보와 모델정보 공유및 갱신
- Airflow 을 이용한 전체 워크플로의 제어
- FastAPI를 통한 영화정보및 영화평점 예측모델 서비스
- Docker compose 를 통한 전체 컨테이너 서비스 환경구성 자동화

<br>

## 👨‍👩‍👦‍👦 팀 구성원

| ![박패캠](https://avatars.githubusercontent.com/u/156163982?v=4) | ![이패캠](https://avatars.githubusercontent.com/u/156163982?v=4) | ![최패캠](https://avatars.githubusercontent.com/u/156163982?v=4) | ![김패캠](https://avatars.githubusercontent.com/u/156163982?v=4) | ![오패캠](https://avatars.githubusercontent.com/u/156163982?v=4) |
| :--------------------------------------------------------------: | :--------------------------------------------------------------: | :--------------------------------------------------------------: | :--------------------------------------------------------------: | :--------------------------------------------------------------: |
|            [김두환](https://github.com/UpstageAILab)             |            [소재목](https://github.com/UpstageAILab)             |            [나주영](https://github.com/UpstageAILab)             |            [김재훈](https://github.com/UpstageAILab)             |
|                            팀장 및 MLOps 총괄                             |                            모델링 방향 논의                             |                            자료 정리 및 발표                             |                            분석 흐름 검토                             |

<br>

## 🔨 개발 환경 및 기술 스택

- **주 언어**: Python 3.10
- **데이터 소스**: TMDB API
- **데이터 저장소**: MINIO(s3 호환)
- **워크플로우 관리**: Apache Airflow 2.10.5
- **API 서버**: FastAPI
- **컨테이너화**: Docker, docker-compose
- **버전 및 이슈 관리**: GitHub

## 📁 프로젝트 구조

```
├── airflow/                    # Airflow 관련 파일
│   └── dags/                   # Airflow DAGs
│        └── pipeline.py        # 워크플로 제어 DAGs
├── src/                        # 프로세스 
│   ├── dataset/                # 데이터셋 관련 패키지
│   ├── inference/              # 평가 관련 패키지
│   ├── model/                  # 모델 관련 패키지
│   ├── preprocessing/          # 데이터 수집/전처리 관련 패키지
│   └── utils/                  # 유틸리티 패키지
├── fastapi_app/                # 프론트단
│   ├── templates/              # html 파일 패키지
│   └── main.py                 # web api
├── .env                        # 환경 변수
├── .dockerignore               # Docker ignore 파일
├── .gitignore                  # Git ignore 파일
├── docker-compose.yml          # Docker Compose file
├── Dockerfile                  # 메인 도커파일
├── Dockerfiil.fastapi          # fastapi 용 도커파일
├── readme.txt                  # 설치 설명서
├── requirements.txt            # 라이브러리 설치파일
└── README.md                   # 프로젝트 README
```

<br>

## 💻​ 구현 기능
### 데이터 수집 및 자동화
- _TMDB API를 활용하여 영화 데이터 수집_
- _Airflow DAG를 통해 주기적으로 데이터를 크롤링 및 수집 수행하게 설정_
- _수집된 데이터를 MinIO에 저장하여 모델 학습 및 API 호출에 사용_
### 영화 평점 예측 모델 학습 및 제공
- _수집된 데이터를 전처리하고 모델 학습 수행_
- _모델은 입력된 데이터를 기반으로 평점을 예측_
- _학습된 모델은 MinIO에 저장되며 FastAPI를 통해 REST API로 배포됨_
### 실시간 API 기반 예측 서비
- _FastAPI 서버를 통해 /predict 엔드포인트 제공_
- _외부 요청이 들어오면 MinIO에서 예측 결과 반환_
- _HTML 기반의 갤러리 UI로 사용자 인터랙션 제공_

<br>

## 🛠️ 작품 아키텍처(필수X)

-아키텍처 사진 혹은 텍스트-

<br>

## 🚨​ 트러블 슈팅
### 1. OOO 에러 발견

#### 설명
- _프로젝트 진행 중 발생한 트러블에 대해 작성해주세요_

#### 해결
- _프로젝트 진행 중 발생한 트러블 해결방법 대해 작성해주세요_

<br>

## 📌 프로젝트 회고
### 박패캠
- _프로젝트 회고를 작성해주세요_

<br>

## 📰​ 참고자료
- [Airflow Tutorial for Beginners - Full Course in 2 Hours 2022](https://www.youtube.com/watch?v=K9AnJ9_ZAXE&list=PLwFJcsJ61oujAqYpMp1kdUBcPG0sE0QMT)
- [https://www.perplexity.ai](https://www.perplexity.ai)
