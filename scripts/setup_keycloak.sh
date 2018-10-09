#!/bin/bash

echo "[ Waiting for Keycloak server ]"
until $(curl --output /dev/null --silent --head --fail http://keycloak:8080); do
    sleep 2
done

KCADM="/opt/jboss/keycloak/bin/kcadm.sh"

echo -e "\n[ Log into Keycloak ]"
$KCADM config credentials --server http://keycloak:8080/auth --realm master --user admin --password default

echo -e "\n[ Create realms ]"
$KCADM create realms -f /scripts/realms.json

echo -e "\n[ Create and configure user demo ]"
$KCADM create users -r demo -s username=test -s enabled=true -s emailVerified=false -s firstName=TestUser
ID=$($KCADM get users -r demo --fields id | jq -r ".[].id")
$KCADM update users/$ID/reset-password -r demo -s type=password -s value=default -s temporary=false -n
$KCADM add-roles --uusername test --rolename user -r demo

echo -e "Keycloak initialization successful!"
