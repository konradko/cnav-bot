# Install openSSH server
apt-get update && apt-get install -yq --no-install-recommends \
openssh-server && \
apt-get clean && rm -rf /var/lib/apt/lists/*

# Setup openSSH config
echo "root:$PASSWD" | chpasswd \
&& sed -i "s/PermitRootLogin without-password/PermitRootLogin yes/" /etc/ssh/sshd_config \
&& sed -i "s/UsePAM yes/UsePAM no/" /etc/ssh/sshd_config

service ssh start
