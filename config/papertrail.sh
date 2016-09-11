#!/bin/bash
echo "Starting Papertrail"

sed -i "s/PAPERTRAIL_HOST PAPERTRAIL_PORT/$PAPERTRAIL_HOST $PAPERTRAIL_PORT/" /etc/systemd/system/papertrail.service

systemctl enable /etc/systemd/system/papertrail.service
systemctl start papertrail.service
