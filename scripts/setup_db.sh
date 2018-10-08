#!/bin/bash
echo Wait for servers to be up
sleep 10

HOSTPARAMS="--host db-1 --insecure"
SQL="/cockroach/cockroach.sh sql $HOSTPARAMS"

$SQL -e "CREATE DATABASE operations-api;"
$SQL -e "CREATE USER operations-api WITH ENCRYPTED PASSWORD 'operations-api';"
$SQL -e "GRANT ALL PRIVILEGES ON DATABASE operations-api TO operations-api;"
