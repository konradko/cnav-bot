#!/bin/bash

/usr/bin/hciattach /dev/ttyAMA0 bcm43xx 921600 noflow -
hciconfig hci0 up
