#!/bin/bash

# OpenSSH
mkdir -p ~/.ssh
# CLIENT_PUBKEYS are set via resin.io env vars (separated with '\n')
printf "$CLIENT_PUBKEYS" | tee -a ~/.ssh/authorized_keys

if [ -d "/data/ssh" ]; then
    # Restore keys from first openssh-server install
    cp /data/ssh/ssh_host_*_key* /etc/ssh/
else
    # Save keys from first openssh-server install
    mkdir /data/ssh
    cp /etc/ssh/ssh_host_*_key* /data/ssh/

fi

service ssh start

# Load resin.io env vars when running bash
echo ". <(xargs -0 bash -c 'printf \"export %q\n\" \"\$@\"' -- < /proc/1/environ)" >> /root/.bash_profile
