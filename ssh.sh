#!/bin/bash

if [[ "$1" != "" ]]; then
    # Hostname is the first command line argument
    HOST="$1"
    ssh root@$HOST
else
    echo "Usage: ./ssh.sh <hostname>"
fi
