#!/bin/bash

echo "Enabling Picamera"
modprobe bcm2835-v4l2

echo "Enabling pi2go"
modprobe i2c-dev

echo "Enabling bluetooth"
bash /usr/src/app/config/bluetooth.sh

case "$PAPERTRAIL_ON" in
 true) bash /usr/src/app/config/papertrail.sh ;;
    *) echo "Papertrail not enabled" ;;
esac

case "$LOCAL_SSH_ON" in
 true) bash /usr/src/app/config/openssh.sh ;;
    *) echo "Local SSH not enabled" ;;
esac

case "$PROMETHEUS_ON" in
 true) bash /usr/src/app/config/prometheus.sh ;;
    *) echo "Prometheus not enabled" ;;
esac

python cnavbot/main.py
