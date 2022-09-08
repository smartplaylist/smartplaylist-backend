#!/bin/bash

# `rabbitmq_mnesia_dir` should not exist

docker network create -d bridge my-bridge-network
docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_db -v $(pwd)/pgdata:/pgdata -v /home/www/db_backup:/pg_backup --name db postgres:14.1-alpine
docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_adminer -p 8081:8080 --name adminer adminer:4.8.1
docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_broker -v $(pwd)/rabbitmq_mnesia_dir:/var/lib/rabbitmq/mnesia -p 15672:15672 -p 5672:5672 --name broker rabbitmq:3.9.13-management-alpine
docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_api -p 3000:3000 --name api postgrest/postgrest:v10.0.0
