# jkulak/smartplaylist-api

FROM python:3.10.7-alpine3.16

RUN apk update && apk upgrade
RUN apk add --no-cache htop ncdu \
    && rm -rf /var/cache/apk/*

WORKDIR /api
COPY ./src/ ./
RUN pip install --no-cache-dir pipenv && \
    pipenv install
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "80"]
