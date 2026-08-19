#!/bin/sh
set -eu

mysql_root() {
  mysql --protocol=tcp --host="$1" --user=root --password="$MYSQL_ROOT_PASSWORD" "$2"
}

mysql_root mysql-primary <<SQL
CREATE USER IF NOT EXISTS 'replicator'@'%' IDENTIFIED BY '${REPLICATION_PASSWORD}';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replicator'@'%';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
SQL

mysql_root mysql-replica <<SQL
STOP REPLICA;
RESET REPLICA ALL;
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='mysql-primary',
  SOURCE_USER='replicator',
  SOURCE_PASSWORD='${REPLICATION_PASSWORD}',
  SOURCE_AUTO_POSITION=1;
START REPLICA;
SQL
