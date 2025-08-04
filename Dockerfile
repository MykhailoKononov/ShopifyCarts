FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install -y postgresql-client

COPY ./requirements.txt .
RUN pip install -r requirements.txt