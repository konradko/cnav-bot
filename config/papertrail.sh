#!/bin/bash

mkdir -p /data/log/

sed -i -e "s/host:/host: $PAPERTRAIL_HOST/g" \
-e "s/port:/port: $PAPERTRAIL_PORT/g" \
-e "s#BOT_LOG_PATH#$BOT_LOG_PATH#g" /etc/log_files.yml
sed -i "s/host port/$PAPERTRAIL_HOST $PAPERTRAIL_PORT/g" /etc/systemd/system/papertrail.service

systemctl enable /etc/systemd/system/papertrail.service
systemctl start papertrail.service
remote_syslog
