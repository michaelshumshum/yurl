FROM alpine:latest

RUN apk add --no-cache python3 py3-pip

COPY app /app
COPY gunicorn.config.py /gunicorn.config.py
COPY .env.example /app/.env
COPY .env /app/.env
COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt --break-system-packages

WORKDIR /