#!/bin/sh

# 1. Run Docker
# 2. Run this script from the root of the project `./dev/setup_local_development.sh`

# After running this script you should be able to access:
# * Broker (Rabbit): http://localhost:15672/#/queues
# * Adminer: http://localhost:8080/?pgsql=db
# * API: http://localhost:8008/
# 
# * Then run the website from the separate repository to have it running on: http://localhost:3001/#

# Use the current working directory as the WORK_DIR
WORK_DIR=$(pwd)
NETWORK_NAME=smartplaylist_network
MNESIA_DIR="$WORK_DIR/rabbitmq_mnesia_dir"

if [ ! -f "$WORK_DIR/.env" ]
then
    echo "🙅🏽 File $WORK_DIR/.env does not exist." >&2
    exit 1
fi

# Check if rabbitmq_mnesia_dir exists
if [ -d "$MNESIA_DIR" ]; then
    echo "🙅🏽 The directory $MNESIA_DIR exists and it should most probably be deleted when running new Rabbit container."
    read -p "Do you want to delete it? (y/n): " yn
    case $yn in
        [Yy]* ) rm -rf "$MNESIA_DIR"; echo "$MNESIA_DIR has been deleted";;
        [Nn]* ) echo "Not deleting $MNESIA_DIR";;
        * ) echo "Please answer yes or no.";;
    esac
fi

# Run Postgres
docker run -d --rm --network $NETWORK_NAME --env-file $WORK_DIR/.env --name db \
    -v $WORK_DIR/pgdata:/pgdata postgres:14.1-alpine

# Run adminer
docker run -d --rm --network $NETWORK_NAME --env-file $WORK_DIR/.env --name adminer \
    -p 8080:8080 adminer:4.8.1

# Run message broker
docker run -d --network $NETWORK_NAME --env-file $WORK_DIR/.env --name broker \
    -v $WORK_DIR/rabbitmq_mnesia_dir:/var/lib/rabbitmq/mnesia -p 15672:15672 -p 5672:5672 rabbitmq:3.11.2-management-alpine

# Run API
## Build the container
docker build --no-cache -t smartplaylist/api $WORK_DIR/api
## Run the container
docker run -d --network $NETWORK_NAME --env-file $WORK_DIR/.env --name smartplaylist-api \
    -v $WORK_DIR/api/src:/api -p 8008:8008 smartplaylist/api

# Build app image
docker build --no-cache -t smartplaylist/app $WORK_DIR/app
