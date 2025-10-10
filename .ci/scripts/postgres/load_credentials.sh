#!/bin/sh

PSQL_SECRETS=${PSQL_SECRETS:-{}}
DB_PASS="$(echo $PSQL_SECRETS | jq -r '.["$[[ inputs.db_user ]]"]')"

echo DB_USER="$DB_USER" > credentials.env
echo DB_PASS="$DB_PASS" >> credentials.env
