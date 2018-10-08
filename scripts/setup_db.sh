#!/bin/bash -x
echo "Waiting for CockroachDB servers ..."
sleep 10

HOSTPARAMS="--host db-1 --insecure"
SQL="/cockroach/cockroach.sh sql $HOSTPARAMS"

echo -e "\nCreating user oapi ..."
$SQL -e "CREATE USER oapi;"

echo -e "\nCreating database oapi ..."
$SQL -e "CREATE DATABASE oapi;"

echo -e "\nGranting ALL permissions to user oapi on database oapi ..."
$SQL -e "GRANT ALL ON DATABASE oapi TO oapi;"

echo -e "\nDatabase initialization successful!"
