#!/bin/bash

NOW=$(date '+%Y-%m-%d-%H%M%S')
FILENAME="-grabtrack-backup.psql"

ECHO $NOW "Running backup"

docker exec db pg_dump -U postgres -w -F c spotify -f /pg_backup/$NOW$FILENAME
