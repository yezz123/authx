FROM python:3.10.0

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.dev.txt


ENV PYTHONPATH=/app
EXPOSE 8000 8000
