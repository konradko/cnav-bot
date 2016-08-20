#!/bin/bash

# Papertrail
echo "Setting up Papertrail"
mkdir -p /data/log/


sed -i -e "s/host:/host: $PAPERTRAIL_HOST/g" \
-e "s/port:/port: $PAPERTRAIL_PORT/g" \
-e "s#BOT_LOG_PATH#$BOT_LOG_PATH#g" /etc/log_files.yml
sed -i "s/host port/$PAPERTRAIL_HOST $PAPERTRAIL_PORT/g" /etc/systemd/system/papertrail.service

systemctl enable /etc/systemd/system/papertrail.service
echo "Starting Papertrail"
systemctl start papertrail.service
remote_syslog

# OpenSSH
echo "Setting up OpenSSH"
mkdir -p ~/.ssh
# CLIENT_PUBKEY is set via resin.io env vars
echo $CLIENT_PUBKEY | tee -a ~/.ssh/authorized_keys

if [ -d "/data/ssh" ]; then
    # Restore keys from first openssh-server install
    cp /data/ssh/ssh_host_*_key* /etc/ssh/
else
    # Save keys from first openssh-server install
    mkdir /data/ssh
    cp /etc/ssh/ssh_host_*_key* /data/ssh/

fi
echo "Starting OpenSSH"
service ssh start

# Picamera
echo "Enabling Picamera"
modprobe bcm2835-v4l2

# pi2go
echo "Enabling pi2go"
modprobe i2c-dev

# Bluetooth
echo "Enabling Bluetooth"
/usr/bin/hciattach /dev/ttyAMA0 bcm43xx 921600 noflow -
hciconfig hci0 up

# Prometheus
echo "Starting Prometheus"
bash /usr/src/app/config/prometheus/start.sh
