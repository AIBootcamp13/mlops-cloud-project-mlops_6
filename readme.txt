1. 설치 디렉토리로 이동
2. mkdir -p ./dags ./logs ./plugins ./config ./fastapi_app ./minio_data
3. echo -e "AIRFLOW_UID=$(id -u)" > .env
4. docker-compose up airflow-init
5. docker compose up --build -d