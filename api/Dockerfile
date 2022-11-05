# jkulak/smartplaylist-api

FROM python:3.10.7-alpine3.16

RUN apk update && apk upgrade
RUN apk add --no-cache htop ncdu \
    && rm -rf /var/cache/apk/*

WORKDIR /api
COPY ./src/ ./
RUN pip install --no-cache-dir pipenv==v2022.10.25 && \
    pipenv install
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008", "--reload"]
