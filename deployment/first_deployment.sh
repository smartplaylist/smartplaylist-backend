#!/bin/bash

# `rabbitmq_mnesia_dir` should not exist

docker network create -d bridge smartplaylist_network
docker run -d --network smartplaylist_network --env-file .env --name db -v $(pwd)/pgdata:/pgdata -v $(pwd)/db_backup:/pg_backup postgres:14.1-alpine
docker run -d --network smartplaylist_network --env-file .env --name adminer adminer:4.8.1
docker run -d --network smartplaylist_network --env-file .env --name broker -v $(pwd)/rabbitmq_mnesia_dir:/var/lib/rabbitmq/mnesia rabbitmq:3.9.13-management-alpine
docker run -d --network smartplaylist_network --env-file .env --name api postgrest/postgrest:v10.0.0
docker run -d --network smartplaylist_network --env-file .env --name db_api_redis redis:7.0.5-alpine3.16

# docker run -d --network smartplaylist_network --env-file .env --name db_in_memory -v $(pwd):/db_backup -w /db_backup keinos/sqlite3

