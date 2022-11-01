#!/bin/bash

NOW=$(date '+%Y-%m-%d-%H%M%S')
FILENAME="-smartplaylist-backup.psql"

echo $NOW "Running backup"

docker exec db pg_dump --username=postgres --no-password --format=custom --compress=9 --dbname=spotify -f /pg_backup/$NOW$FILENAME

NOW=$(date '+%Y-%m-%d-%H%M%S')
echo $NOW "Finished backup"
