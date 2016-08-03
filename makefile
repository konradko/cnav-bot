build: clean local_requirements resin_cli

resin_cli:
	npm install --global --production resin-cli

clean:
	-find . -type f -name "*.pyc" -delete

run_on_rpi:
	# init camera
	modprobe bcm2835-v4l2
	python src/cnavbot/main.py

test_in_docker:
	docker-compose -f docker-compose.test.yml build --pull
	docker-compose -f docker-compose.test.yml run sut

local_requirements:
	pip install --upgrade pip
	pip install pip-tools
	pip install --no-deps -e git+https://git@github.com/konradko/pi2go.git@master#egg=pi2go
	pip-sync requirements/test.txt


update_requirements:
	pip-compile --output-file requirements/prod.txt requirements/prod.in
	pip-compile --output-file requirements/test.txt requirements/test.in

upgrade_requirements:
	pip-compile --upgrade --output-file requirements/prod.txt requirements/prod.in
	pip-compile --upgrade --output-file requirements/test.txt requirements/test.in

test:
	py.test src/cnavbot $(pytest_args)

coverage:
	py.test src/cnavbot --cov=src/cnavbot $(pytest_args)

deploy:
	git push resin master

RESIN_SSH := resin ssh

ssh_bot1:
	$(RESIN_SSH) e5eebce

ssh_bot2:
	$(RESIN_SSH) e090bec

ssh_bot3:
	$(RESIN_SSH) 9affe51

static_analysis: pep8 xenon

pep8:
	@echo "Running flake8 over codebase"
	flake8 --ignore=E501,W391,F999 etl/

xenon:
	@echo "Running xenon over codebase"
	xenon --max-absolute B --max-modules B --max-average A src/cnavbot

.PHONY: build clean local_requirements test coverage static_analysis pep8 xenon test_in_docker run_on_rpi update_requirements upgrade_requirements deploy ssh_bot1 ssh_bot2 ssh_bot3
