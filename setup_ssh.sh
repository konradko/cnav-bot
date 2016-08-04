#!/bin/bash

# Setup client's public-key
mkdir -p ~/.ssh
# CLIENT_PUBKEY is set via resin.io env vars
echo $CLIENT_PUBKEY | tee -a ~/.ssh/authorized_keys

service ssh start
