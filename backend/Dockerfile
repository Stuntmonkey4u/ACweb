# FastAPI Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y pkg-config default-libmysqlclient-dev gcc && \
    pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
