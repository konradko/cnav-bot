build: clean virtualenv local_settings resin_cli

local_settings:
	[ ! -f src/cnavbot/settings/local.py ] && cp src/cnavbot/settings/local.example.py src/cnavbot/settings/local.py || true

resin_cli:
	npm install --global --production resin-cli

clean:
	-find . -type f -name "*.pyc" -delete

virtualenv:
	pip install --upgrade pip
	pip install pip-tools
	pip-sync requirements/test.txt

run_on_rpi:
	# init camera
	modprobe bcm2835-v4l2
	python src/cnavbot/main.py

test_in_docker:
	docker-compose -f docker-compose.test.yml build --pull
	docker-compose -f docker-compose.test.yml run sut

update_requirements:
	pip-compile --output-file requirements/common.txt requirements/common.in
	pip-compile --output-file requirements/test.txt requirements/test.in

upgrade_requirements:
	pip-compile --upgrade --output-file requirements/common.txt requirements/common.in
	pip-compile --upgrade --output-file requirements/test.txt requirements/test.in
test:
	py.test src/cnavbot $(pytest_args)

coverage:
	py.test src/cnavbot --cov=src/cnavbot $(pytest_args)

deploy:
	git push resin master

ssh_bot1:
	resin ssh e5eebce

static_analysis: pep8 xenon

pep8:
	@echo "Running flake8 over codebase"
	flake8 --ignore=E501,W391,F999 etl/

xenon:
	@echo "Running xenon over codebase"
	xenon --max-absolute B --max-modules B --max-average A src/cnavbot

.PHONY: build clean virtualenv test coverage static_analysis pep8 xenon test_in_docker run_on_rpi
