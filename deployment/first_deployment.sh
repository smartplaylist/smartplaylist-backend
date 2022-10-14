#!/bin/bash

# `rabbitmq_mnesia_dir` should not exist

docker network create -d bridge smartplaylist_network
docker run -d --network smartplaylist_network --env-file .env --name db-v /home/www/pgdata:/pgdata -v /home/www/db_backup:/pg_backup postgres:14.1-alpine
docker run -d --network smartplaylist_network --env-file .env --name adminer adminer:4.8.1
docker run -d --network smartplaylist_network --env-file .env --name broker -v $(pwd)/rabbitmq_mnesia_dir:/var/lib/rabbitmq/mnesia rabbitmq:3.9.13-management-alpine
docker run -d --network smartplaylist_network --env-file .env --name api postgrest/postgrest:v10.0.0
# dodac reverse-proxy (z oddzielnego repozytorium)
