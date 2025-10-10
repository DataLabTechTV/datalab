#!/bin/sh

echo "Creating database: $DB_NAME"
docker exec datalab-postgres-1 \
    psql -c "CREATE DATABASE $DB_NAME"

echo "Granting all privileges to user: $DB_USER"
docker exec datalab-postgres-1 \
    psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo DB_NAME="$DB_NAME" > "$CI_PROJECT_DIR/credentials.env"
echo DB_USER="$DB_USER" >> "$CI_PROJECT_DIR/credentials.env"
echo DB_PASS="$DB_PASS" >> "$CI_PROJECT_DIR/credentials.env"
