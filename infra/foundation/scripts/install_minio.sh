#!/bin/sh

# External configurations
. /root/config.envrc

# Internal configurations
USER=minio
GROUP=minio

# Install dependencies
apt-get update && apt-get install -y wget sudo

# Download MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio -O /usr/local/bin/minio
wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
chmod +x /usr/local/bin/minio /usr/local/bin/mc

# Create directories & user
id -u $USER 2>/dev/null || useradd -r -s /sbin/nologin $USER
mkdir -p $MINIO_DATA_DIR
chown -R $USER:$GROUP $MINIO_DATA_DIR

# Environment file
mkdir /etc/minio
chown -R $USER:$GROUP /etc/minio
echo "MINIO_ROOT_USER=$MINIO_ROOT_USER" > /etc/minio/minio.env
echo "MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD" >> /etc/minio/minio.env

# Systemd service
cat > /etc/systemd/system/minio.service <<EOF
[Unit]
Description=MinIO
After=network.target

[Service]
User=$USER
Group=$GROUP
EnvironmentFile=/etc/minio/minio.env
ExecStart=/usr/local/bin/minio server $MINIO_DATA_DIR --console-address ":9001"
Restart=always
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

# Enable & start MinIO
systemctl daemon-reload
systemctl enable --now minio

# Create default buckets
mc alias set local http://127.0.0.1:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
for bucket in $MINIO_DEFAULT_BUCKETS; do mc mb local/$bucket; done
