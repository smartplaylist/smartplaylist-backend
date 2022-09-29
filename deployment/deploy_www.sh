#!/bin/sh

WORKING_DIR=/home/www/deployment

docker pull jkulak/grabtrack-www:latest
docker tag jkulak/grabtrack-www:latest www:current
docker stop www
docker run -d --env SERVER_CONFIG_FILE=/config.toml -v $WORKING_DIR/sws_config.toml:/config.toml --hostname gt_www -p 8787:80 --name www www:current
docker rmi jkulak/grabtrack-www:latest
