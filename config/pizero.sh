#!/bin/bash
sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -s 169.254.0.0/16 -o eth0 -j MASQUERADE
# (replace eth0 in the second command with your internet-facing network device,
# e.g. wlan0 on a laptop)

# The Avahi-discovered hostname
ZERO_HOSTNAME=raspberrypi.local
# The SSH user
ZERO_USERNAME=pi
# The USB network device on the Zero-side (will always be usb0)
ZERO_DEV=usb0

# The USB network device on the PC-side (will probably be usb0)
PC_ZERO_DEV=usb0

# The internet-connected network device on the PC (will probably be eth0 or wlan0)
PC_INET_DEV=$(route | grep ^default | awk '{print $8}')
echo "PC_INET_DEV is $PC_INET_DEV"

ifconfig $PC_ZERO_DEV > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "PC_ZERO_DEV ($PC_ZERO_DEV) doesn't exist"
    exit 1
fi

ifconfig $PC_INET_DEV > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "PC_INET_DEV ($PC_INET_DEV) doesn't exist"
    exit 1
fi

DNS_SERVER=$(nmcli -t -f IP4 device list iface $PC_INET_DEV | grep DNS | head -1 | cut -d: -f2)
echo "DNS_SERVER is $DNS_SERVER"

# The IP address assigned to the PC-side of the USB network device
PC_ZERO_DEV_IP=$(ifconfig $PC_ZERO_DEV | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}')
echo "PC_ZERO_DEV_IP is $PC_ZERO_DEV_IP"
if [[ "$PC_ZERO_DEV_IP" != 169.254.* ]]; then
    echo "PC_ZERO_DEV_IP isn't in the link-local range"
    exit 1
fi

# The IP address assigned to Zero-side of the USB network device
ZERO_IP=$(ping -c1 $ZERO_HOSTNAME | grep $ZERO_HOSTNAME | head -1 | cut -d'(' -f2 | cut -d')' -f1)
echo "ZERO_IP is $ZERO_IP"
if [[ "$ZERO_IP" != 169.254.* ]]; then
    echo "ZERO_IP isn't in the link-local range"
    exit 1
fi

# Setup default route and DNS server on Zero
ssh $ZERO_USERNAME@$ZERO_HOSTNAME "sudo route add default gw $PC_ZERO_DEV_IP $ZERO_DEV; echo \"nameserver $DNS_SERVER\" | sudo resolvconf -a $ZERO_DEV"
