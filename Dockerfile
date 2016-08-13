# base resin image for python
FROM resin/raspberrypi3-python

# Set our working directory
WORKDIR /usr/src/app

# Install papertrail client
RUN wget https://github.com/papertrail/remote_syslog2/releases/download/v0.18/remote-syslog2_0.18_armhf.deb \
    && dpkg -i remote-syslog2_0.18_armhf.deb
COPY ./log_files.yml /etc/

# Install openSSH, remove the apt list to reduce the size of the image
RUN apt-get update && apt-get install -yq --no-install-recommends \
    openssh-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Only allow public-key based ssh login
RUN sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

# Copy requirements first for better cache on later pushes
COPY ./requirements/rpi.txt /requirements.txt

# pip install python deps from requirements.txt on the resin.io build server
RUN pip install -r /requirements.txt

# This will copy all files in our root to the working  directory in the container
COPY . ./

# Switch on systemd init system in container
ENV INITSYSTEM on

# make run_on_rpi will run when container starts up on the device
CMD ["make","run_on_rpi"]
