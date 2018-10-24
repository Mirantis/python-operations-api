#!/bin/bash

if jq -e . >/dev/null 2>&1 <<< "$OAPI_OIDC_CLIENT_SECRETS_OVERRIDE"; then
    echo "Overriding client_secrets.json with env string into: /tmp/client_secrets.json"
    echo $OAPI_OIDC_CLIENT_SECRETS_OVERRIDE > /tmp/client_secrets.json
    export OAPI_OIDC_CLIENT_SECRETS="/tmp/client_secrets.json"
fi

exec gunicorn --config operations_api/gunicorn.py operations_api.wsgi
