FROM python:3.10.2-bullseye

WORKDIR /db

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=example
ENV POSTGRES_DB=spotify
ENV POSTGRES_HOST=db

RUN pip install alembic psycopg2
