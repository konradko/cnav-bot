#!/bin/bash

# Special procedure invoked only on rpi3 revision
REV=`cat /proc/cmdline | awk -v RS=" " -F= '/boardrev/ { print $2 }'`
if [ "$REV" = "0xa02082" ]
  then
    if ! /usr/bin/hciattach /dev/ttyAMA0 bcm43xx 921600 noflow -; then
        /usr/bin/hciattach /dev/ttyAMA0 bcm43xx 921600 noflow - || true
    fi
fi
hciconfig hci0 up || true

