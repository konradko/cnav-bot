#!/bin/bash
echo "Starting Papertrail"

mkdir -p /data/log/

sed -i -e "s/PAPERTRAIL_HOST/$PAPERTRAIL_HOST/" \
-e "s/PAPERTRAIL_PORT/$PAPERTRAIL_PORT/" \
-e "s#BOT_LOG_PATH#$BOT_LOG_PATH#" /etc/log_files.yml
sed -i "s/PAPERTRAIL_HOST PAPERTRAIL_PORT/$PAPERTRAIL_HOST $PAPERTRAIL_PORT/" /etc/systemd/system/papertrail.service

systemctl enable /etc/systemd/system/papertrail.service
systemctl start papertrail.service
remote_syslog
