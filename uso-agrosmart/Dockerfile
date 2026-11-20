FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir kafka-python==2.0.2 requests==2.32.3
COPY producer/ /app/producer/
COPY consumer/ /app/consumer/
