#!/bin/sh

WORKING_DIR=/home/www/smartplaylist_api
IMAGE_NAME=jkulak/smartplaylist-api:latest
NETWORK_NAME=smartplaylist_network

docker pull $IMAGE_NAME
docker tag $IMAGE_NAME api:current
docker stop fastapi
docker rm fastapi
docker run -d --network $NETWORK_NAME --name fastapi api:current
docker rmi $IMAGE_NAME
