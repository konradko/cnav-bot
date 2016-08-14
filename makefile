SHELL := /bin/bash

build: clean install_test_requirements resin_cli

resin_cli:
	npm install --global --production resin-cli

clean:
	-find . -type f -name "*.pyc" -delete

run_on_rpi:
	# Initialise hardware and deamons
	./init.sh
	python cnavbot/main.py

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
	$(RESIN_SSH) $(CNAV_BOT1_ID)
resin_ssh_bot2:
	$(RESIN_SSH) $(CNAV_BOT2_ID)
resin_ssh_bot3:
	$(RESIN_SSH) $(CNAV_BOT3_ID)

# Set addresses as env vars according to resin.io app dashboard
ssh_bot1:
	ssh root@$(CNAV_BOT1_IP)
ssh_bot2:
	ssh root@$(CNAV_BOT2_IP)
ssh_bot3:
	ssh root@$(CNAV_BOT3_IP)

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

.PHONY: build clean install_test_requirements test static_analysis pep8 xenon test_in_docker run_on_rpi update_requirements upgrade_requirements deploy ssh_bot1 ssh_bot2 ssh_bot3
