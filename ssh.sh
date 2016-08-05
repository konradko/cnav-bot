#!/bin/bash

if [[ "$1" != "" ]]; then
    # Hostname is the first command line argument
    HOST="$1"
    # Host key changes on every deployment, thus removing the old one from known hosts
    echo "Removing old key from the known hosts"
    ssh-keygen -R $HOST
    # Adding the new host key. Use with caution, this makes man-in-the-middle attack possible
    echo "Adding new key to the known hosts"
    ssh-keyscan -H $HOST >> ~/.ssh/known_hosts
    ssh root@$HOST
else
    echo "Usage: ./ssh.sh <hostname>"
fi
