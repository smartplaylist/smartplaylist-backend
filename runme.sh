#!/bin/sh

NETWORK_NAME=smartplaylist_network
API_IMAGE_NAME=postgrest/postgrest:v10.0.0
API_PORT=3000

if [ $# -eq 1 ]
  then
    # docker build --no-cache -t $IMAGE_NAME .
    echo "One argument supplied"
fi

# run api
docker run \
    -d --rm \
    --network $NETWORK_NAME \
    --name api \
    --env-file .env \
    -p $API_PORT:$API_PORT \
    $API_IMAGE_NAME
