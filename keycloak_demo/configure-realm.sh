kcadm.sh  config credentials --server http://localhost:8080/auth --realm master --user admin --password default
kcadm.sh create realms -f keycloak/realm-export.json
kcadm.sh  create users -r demo -s username=test2 -s enabled=true -s emailVerified=false -s firstName=TestUser
ID=$(kcadm.sh get users -r demo --fields id | jq -r ".[].id")
kcadm.sh update users/$ID/reset-password -r demo -s type=password -s value=default -s temporary=false -n
kcadm.sh add-roles --uusername test --rolename user -r demo



---
./keycloak/bin/kcadm.sh create realms -f keycloak/realm-export.json && \
./keycloak/bin/kcadm.sh  create users -r demo -s username=test2 -s enabled=true -s emailVerified=false -s firstName=TestUser && \
ID=$(./keycloak/bin/kcadm.sh get users -r demo --fields id | jq -r ".[].id") && \
./keycloak/bin/kcadm.sh update users/$ID/reset-password -r demo -s type=password -s value=default -s temporary=false -n && \
./keycloak/bin/kcadm.sh add-roles --uusername test --rolename user -r demo"
