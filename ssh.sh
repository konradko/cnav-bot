#!/bin/bash

if [[ "$1" != "" ]]; then
    # Hostname is the first command line argument
    HOST="$1"
    # Host key changes on every deployment, thus removing it from known hosts
    ssh-keygen -R $HOST
    ssh root@$HOST
else
    echo "Usage: ./ssh.sh <hostname>"
fi
