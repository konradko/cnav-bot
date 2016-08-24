#!/bin/bash

echo "Starting Papertrail"
bash /usr/src/app/config/papertrail.sh

echo "Starting OpenSSH"
bash /usr/src/app/config/openssh.sh

echo "Enabling Picamera"
modprobe bcm2835-v4l2

echo "Enabling pi2go"
modprobe i2c-dev

echo "Enabling bluetooth"
hciconfig hci0 up

echo "Starting Prometheus"
bash /usr/src/app/config/prometheus.sh
