FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR false
ENV DOCKER_PIPENV_VERSION 2021.11.23

WORKDIR /src

RUN apt-get update \
    && apt-get install -y gcc python3-dev --no-install-recommends

COPY Pipfile Pipfile.lock  /

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pipenv==${DOCKER_PIPENV_VERSION} && \
    pipenv install --deploy --system --clear

COPY ./src /src
