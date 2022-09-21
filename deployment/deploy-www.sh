#!/bin/sh

WORKING_DIR=/home/www/spotify-grabtrack/

docker pull jkulak/grabtrack-www:latest
docker tag jkulak/grabtrack-www:latest www:current
docker stop www
docker run -d --rm --network my-bridge-network --env-file $WORKING_DIR.env --hostname gt_www -p 3001:3001 --name www www:current
docker rmi jkulak/grabtrack-www:latest
