#!/bin/sh

if [ -z "$DB_PASS" ]; then
    DB_PASS=$(openssl rand -base64 12)
    echo "Creating user: $DB_USER"

    docker exec datalab-postgres-1 psql -c "
        DO
        \$\$
        BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
            CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
        END IF;
        END
        \$\$;
    "

    echo "Updating CI/CD variable: PSQL_SECRETS"

    PSQL_SECRETS=${PSQL_SECRETS:-"{}"}
    PSQL_SECRETS=$(echo "$PSQL_SECRETS" | jq -c '. + { "$DB_USER": "$DB_PASS" }')

    curl \
        -X POST \
        -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        -d "key=PSQL_SECRETS" \
        -d "value=$PSQL_SECRETS" \
        -d "protected=false" \
        -d "raw=true" \
        -d "hidden=true" \
        -d "masked=true" \
        "$CI_API_V4_URL/projects/$CI_PROJECT_ID/variables"
else
    echo "User found: $DB_USER"
fi

echo DB_USER="$DB_USER" > credentials.env
echo DB_PASS="$DB_PASS" >> credentials.env
