#!/bin/sh

BACKUP_FILENAME=2023-11-05-041701-smartplaylist-backup.psql
LOCAL_BACKUP_DIRECTORY=/your_local_backup_directory

# Copy file to images pgdata directory if it does not exist
if [ ! -f $LOCAL_PGDATA/$BACKUP_FILENAME ]
then
    echo "Copying $BACKUP_FILENAME to $LOCAL_PGDATA"
    cp $LOCAL_BACKUP_DIRECTORY/$BACKUP_FILENAME $LOCAL_PGDATA
fi
echo "Moved $BACKUP_FILENAME to pgdata directory."

# Restore database
# The database must exist, can be empty
docker exec -ti db pg_restore --username=postgres --dbname=smartplaylist_restore --clean --if-exists --verbose /pgdata/$BACKUP_FILENAME
