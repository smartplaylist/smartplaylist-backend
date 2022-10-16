#!/bin/bash

backup_path="/home/www/db_backup"

# delete all but 4 recent database backups (files having .sql extension) in backup folder.
find $backup_path -maxdepth 1 -name "*.psql" -type f | xargs -x ls -t | awk 'NR>4' | xargs -L1 rm -f
