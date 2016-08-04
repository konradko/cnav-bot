# base resin image for python
FROM resin/raspberrypi3-python

# Set our working directory
WORKDIR /usr/src/app

# Copy requirements first for better cache on later pushes
COPY ./requirements/rpi.txt /requirements.txt

# pip install python deps from requirements.txt on the resin.io build server
RUN pip install -r /requirements.txt

# This will copy all files in our root to the working  directory in the container
COPY . ./

# Switch on systemd init system in container
ENV INITSYSTEM on

# Install openSSH server
RUN apt-get update && apt-get install -yq --no-install-recommends \
    openssh-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Setup openSSH config
RUN mkdir /var/run/sshd \
    && echo 'root:$PASSWD' | chpasswd \
    && sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

# make run_on_rpi will run when container starts up on the device
CMD ["make","run_on_rpi"]
