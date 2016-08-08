#!/bin/bash

# Setup client's public-key
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
