#!/bin/bash

# OpenSSH
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

service ssh start

# Papertrail
mkdir -p /data/log/
sed -i "s/host:/host: $PAPERTRAIL_HOST/" /etc/log_files.yml
sed -i "s/port:/port: $PAPERTRAIL_PORT/" /etc/log_files.yml
sed -i "s#BOT_LOG_PATH#$BOT_LOG_PATH#" /etc/log_files.yml
sed -i "s/host port/$PAPERTRAIL_HOST $PAPERTRAIL_PORT/" /etc/systemd/system/papertrail.service

systemctl enable /etc/systemd/system/papertrail.service
systemctl start papertrail.service
remote_syslog

# Picamera
modprobe bcm2835-v4l2

# pi2go
modprobe i2c-dev

# Bluetooth
/usr/bin/hciattach /dev/ttyAMA0 bcm43xx 921600 noflow -
hciconfig hci0 up

# prometheus
bash /prometheus/start.sh
