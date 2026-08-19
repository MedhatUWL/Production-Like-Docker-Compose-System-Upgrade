#!/bin/sh
set -eu
while true; do
  timestamp=$(date -u +%Y-%m-%dT%H-%M-%SZ)
  mysqldump --single-transaction --host="$MYSQL_HOST" --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" "$MYSQL_DATABASE" > "/backups/backup-$timestamp.sql"
  find /backups -type f -name '*.sql' -mtime +7 -delete
  sleep 21600
done
