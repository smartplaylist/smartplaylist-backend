#!/bin/sh

WORKING_DIR=/home/www/smartplaylist_api
IMAGE_NAME=jkulak/smartplaylist-api:latest

docker pull $IMAGE_NAME
docker tag $IMAGE_NAME api:current
docker stop api
docker rm api
docker run -d --network smartplaylist_network --name api api:current
docker rmi $IMAGE_NAME
