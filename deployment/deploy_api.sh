#!/bin/sh

WORKING_DIR=/home/www/smartplaylist_api
IMAGE_NAME=jkulak/smartplaylist-api:latest
NETWORK_NAME=my-bridge-network
ENV_FILE=/home/www/spotify-grabtrack/.env

docker pull $IMAGE_NAME
docker tag $IMAGE_NAME api:current
docker stop fastapi
docker rm fastapi
docker run -d --network $NETWORK_NAME -p 8008:8008 --env-file $ENV_FILE --name fastapi api:current
docker rmi $IMAGE_NAME
