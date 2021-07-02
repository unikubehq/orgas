FROM quay.io/blueshoe/python3.8-slim as base

FROM base as builder

ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y gcc python3-dev libpq-dev g++
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
COPY src/ /app
WORKDIR /app
