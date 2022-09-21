#!/bin/sh

WORKING_DIR=/home/www/spotify-grabtrack/

docker stop www
docker rmi jkulak/grabtrack-www:latest
docker run -d --rm --network my-bridge-network --env-file $WORKING_DIR.env --hostname gt_www -p 3001:3001 --name www jkulak/grabtrack-www:latest
