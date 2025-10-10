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
else
    echo "User found: $DB_USER"
fi

echo DB_USER="$DB_USER" > credentials.env
echo DB_PASS="$DB_PASS" >> credentials.env
