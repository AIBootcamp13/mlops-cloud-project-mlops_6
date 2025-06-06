# 🎬 영화 평점 예측 서비스

<br>

## 💻 프로젝트 소개

### <프로젝트 목표>

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
|            [이상준](https://github.com/UpstageAILab)             |            [김두환](https://github.com/UpstageAILab)             |            [소재목](https://github.com/UpstageAILab)             |            [나주영](https://github.com/UpstageAILab)             |            [김재훈](https://github.com/UpstageAILab)             |
|                            팀장, 담당 역할                             |                            담당 역할                             |                            담당 역할                             |                            담당 역할                             |                            담당 역할                             |

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
├── code
│   ├── jupyter_notebooks
│   │   └── model_train.ipynb
│   └── train.py
├── docs
│   ├── pdf
│   │   └── (Template) [패스트캠퍼스] Upstage AI Lab 1기_그룹 스터디 .pptx
│   └── paper
└── input
    └── data
        ├── eval
        └── train
```

<br>

## 💻​ 구현 기능
### 기능1
- _작품에 대한 주요 기능을 작성해주세요_
### 기능2
- _작품에 대한 주요 기능을 작성해주세요_
### 기능3
- _작품에 대한 주요 기능을 작성해주세요_

<br>

## 🛠️ 작품 아키텍처(필수X)
- #### _아래 이미지는 예시입니다_
![이미지 설명](https://miro.medium.com/v2/resize:fit:4800/format:webp/1*ub_u88a4MB5Uj-9Eb60VNA.jpeg)

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
- [with https://www.perplexity.ai //Claude 4.0 Sonnet]
