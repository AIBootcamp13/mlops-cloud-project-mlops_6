FROM apache/airflow:2.10.5

USER root
RUN apt-get update && apt-get install -y libgomp1 && \
    apt-get autoremove -yqq --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
USER airflow

# 필요하다면 pip로 추가 파이썬 패키지 설치도 여기서 가능
RUN pip install --no-cache-dir numpy pandas koreanize-matplotlib python-dotenv fire wandb icecream tqdm lightgbm scikit-learn

# 애플리케이션 코드 복사
# COPY ./dags /opt/airflow/dags
