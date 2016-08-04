SHELL := /bin/bash

build: clean install_test_requirements resin_cli

resin_cli:
	npm install --global --production resin-cli

clean:
	-find . -type f -name "*.pyc" -delete

setup_local_ssh_on_rpi:
	# Install openSSH server
	apt-get update && apt-get install -yq --no-install-recommends \
    openssh-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

	# Setup openSSH config
	mkdir /var/run/sshd \
    && echo "root:$PASSWD" | chpasswd \
    && sed -i "s/PermitRootLogin without-password/PermitRootLogin yes/" /etc/ssh/sshd_config \
    && sed -i "s/UsePAM yes/UsePAM no/" /etc/ssh/sshd_config

run_on_rpi: setup_local_ssh_on_rpi
	# init camera
	modprobe bcm2835-v4l2
	# init pi2go
	modprobe i2c-dev
	python cnavbot/main.py

test_in_docker:
	docker-compose -f docker-compose.test.yml build --pull
	docker-compose -f docker-compose.test.yml run test

install_test_requirements:
	pip install --upgrade pip
	pip install pip-tools
	pip-sync requirements/test.txt


update_requirements:
	pip-compile --output-file requirements/rpi.txt requirements/rpi.in
	pip-compile --output-file requirements/test.txt requirements/test.in

upgrade_requirements:
	pip-compile --upgrade --output-file requirements/rpi.txt requirements/rpi.in
	pip-compile --upgrade --output-file requirements/test.txt requirements/test.in

RESIN_SSH := resin ssh
# Set hashes according to resin.io app dashboard
resin_ssh_bot1:
	$(RESIN_SSH) e5eebce
resin_ssh_bot2:
	$(RESIN_SSH) e090bec
resin_ssh_bot3:
	$(RESIN_SSH) 9affe51

BOT1_IP := 192.168.1.18
BOT2_IP := 192.168.1.15
BOT3_IP := 192.168.1.132

# Set addresses according to resin.io app dashboard
ssh_bot1:
	ssh-keygen -R $(BOT1_IP)
	ssh root@$(BOT1_IP)
ssh_bot2:
	ssh-keygen -R $(BOT2_IP)
	ssh root@$(BOT2_IP)
ssh_bot3:
	ssh-keygen -R $(BOT3_IP)
	ssh root@$(BOT3_IP)

static_analysis: pep8 xenon

pep8:
	@echo "Running flake8 over codebase"
	flake8 --ignore=E501,W391,F999 cnavbot/

xenon:
	@echo "Running xenon over codebase"
	xenon --max-absolute B --max-modules B --max-average A cnavbot/

test: static_analysis
	py.test cnavbot --cov=cnavbot $(pytest_args)

deploy:
	git push resin master

.PHONY: build clean install_test_requirements test static_analysis pep8 xenon test_in_docker run_on_rpi update_requirements upgrade_requirements deploy ssh_bot1 ssh_bot2 ssh_bot3 resin_ssh_bot1 resin_ssh_bot2 resin_ssh_bot3 setup_local_ssh_on_rpi
