#!/bin/bash

DB_BACKUP_DIR=/home/www/db_backup
REVERSE_PROXY_DIR=/home/www/smartplaylist-reverseproxy
ENV_FILE_DIR=/home/www/spotify-grabtrack
DEPLOYMENT_SCRIPT_DIR=/home/www/deployment

# `rabbitmq_mnesia_dir` should not exist
rm -rf ENV_FILE_DIR/rabbitmq_mnesia_dir

docker network create -d bridge smartplaylist_network
docker run -d --network smartplaylist_network --env-file $ENV_FILE_DIR/.env --name db $ENV_FILE_DIR/pgdata:/pgdata -v $DB_BACKUP_DIR:/pg_backup postgres:14.1-alpine
docker run -d --network smartplaylist_network --env-file $ENV_FILE_DIR/.env --name adminer adminer:4.8.1
docker run -d --network smartplaylist_network --env-file $ENV_FILE_DIR/.env --name broker -v $(pwd)/rabbitmq_mnesia_dir:/var/lib/rabbitmq/mnesia rabbitmq:3.9.13-management-alpine
docker run -d --network smartplaylist_network --env-file $ENV_FILE_DIR/.env --name api postgrest/postgrest:v10.0.0
docker run -d --network smartplaylist_network --env-file $ENV_FILE_DIR/.env --name fastapi jkulak/smartplaylist-api

# Deploy www
$DEPLOYMENT_SCRIPT_DIR/deploy_www.sh

# Run reverseproxy (this is why ports are not needed for above containers)
docker run -d --name reverseproxy --network smartplaylist_network -p 80:80 -p 443:443 -v $REVERSE_PROXY_DIR/certbot/www:/etc/nginx/ssl/live/smartplaylist.me/:ro -v $REVERSE_PROXY_DIR/nginx/conf/:/etc/nginx/conf.d/:ro nginx:1.23-alpine

# Deploy app
$DEPLOYMENT_SCRIPT_DIR/deploy_app.sh
