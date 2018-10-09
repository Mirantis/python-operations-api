#!/bin/bash

docker-compose -f keycloak_demo/docker-compose.auth.yml up -d --force-recreate
docker cp keycloak_demo/realm-export.json keycloakdemo_keycloak_1:/opt/jboss/keycloak

docker exec -it keycloakdemo_keycloak_1 bash -c \
'sleep 6; \
kcadm.sh config credentials --server http://localhost:8080/auth --realm master --user admin --password default &&
kcadm.sh create realms -f keycloak/realm-export.json &&
kcadm.sh create users -r demo -s username=test -s enabled=true -s emailVerified=false -s firstName=TestUser &&
ID=$(kcadm.sh get users -r demo --fields id | jq -r ".[].id") &&
kcadm.sh update users/$ID/reset-password -r demo -s type=password -s value=default -s temporary=false -n &&
kcadm.sh add-roles --uusername test --rolename user -r demo'
