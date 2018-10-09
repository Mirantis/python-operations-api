#!/bin/bash

set -e

if [[ $# -eq 0 ]] ; then
    echo "Usage: $0 [up|down]"
    exit 1
fi

command -v docker >/dev/null 2>&1 || { echo >&2 "bootstrap_env requires docker but it's not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo >&2 "bootstrap_env requires docker-compose but it's not installed. Aborting."; exit 1; }

COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.database.yml -f docker-compose.auth.yml"
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

if [ "$1" = "up" ]; then
    echo -e "${GREEN}[ Starting backend services ]${NC}"
    $COMPOSE up -d
    echo -e "${GREEN}[ Waiting for init containers ]${NC}"
    COUNTER=0
    KC_ID=$(docker-compose -f docker-compose.yml -f docker-compose.database.yml -f docker-compose.auth.yml ps -q keycloak-init)
    CR_ID=$(docker-compose -f docker-compose.yml -f docker-compose.database.yml -f docker-compose.auth.yml ps -q cockroach-init)
    while [  $COUNTER -lt 20 ]; do
        echo -ne "."
        KC_STATE=$(docker inspect -f '{{.State.Running}}' $KC_ID)
        CR_STATE=$(docker inspect -f '{{.State.Running}}' $CR_ID)
        if [ "$KC_STATE" = false ] && [ "$CR_STATE" = false ]; then
            echo ""
            KC_EXIT=$(docker inspect $KC_ID --format='{{.State.ExitCode}}')
            CR_EXIT=$(docker inspect $CR_ID --format='{{.State.ExitCode}}')
            if [ "$KC_EXIT" -eq "0" ] && [ "$CR_EXIT" -eq "0" ]; then
                echo -e "${GREEN}[ All services started ]${NC}"
                exit 0
            else
                echo -e "${RED}[ Init containers failed, aborting ]${NC}"
                echo -e "\nKeycloak init container:\n"
                docker logs $KC_ID
                echo -e "\nCockroachDB init container:\n"
                docker logs $CR_ID
                exit 1
            fi
        fi
        sleep 6
        let COUNTER=COUNTER+1 
    done
    echo ""
    echo -e "${RED}[ Init containers unresponsive, aborting ]${NC}"
    echo -e "\nKeycloak init container:\n"
    docker logs $KC_ID
    echo -e "\nCockroachDB init container:\n"
    docker logs $CR_ID
    exit 1
elif [ "$1" = "down" ]; then
    echo -e "${GREEN}[ Stopping backend services ]${NC}"
    $COMPOSE down -v
    echo -e "${GREEN}[ Removing local DB ]${NC}"
    rm -rf cockroach_data
    echo -e "${GREEN}[ All services stopped ]${NC}"
fi
