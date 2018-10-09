#!/bin/bash

echo "[ Waiting for CockroachDB servers ]"
sleep 15

HOSTPARAMS="--host cockroach-db-1 --insecure"
SQL="/cockroach/cockroach.sh sql $HOSTPARAMS"

echo -e "\n[ Creating user oapi ]"
$SQL -e "CREATE USER oapi;"

echo -e "\n[ Creating database oapi ]"
$SQL -e "CREATE DATABASE oapi;"

echo -e "\n[ Granting ALL permissions to user oapi on database oapi ]"
$SQL -e "GRANT ALL ON DATABASE oapi TO oapi;"

echo -e "\nDatabase initialization successful!"
