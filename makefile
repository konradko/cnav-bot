build: clean virtualenv local_settings

local_settings:
	[ ! -f src/cnavbot/settings/local.py ] && cp src/cnavbot/settings/local.example.py src/cnavbot/settings/local.py || true

clean:
	-find . -type f -name "*.pyc" -delete

virtualenv:
	pip install --upgrade pip
	pip install pip-tools
	pip install -r requirements/test.txt

run_on_rpi:
	modprobe bcm2835-v4l2
	python src/cnavbot/main.py

test_in_docker:
	docker-compose -f docker-compose.test.yml build --pull
	docker-compose -f docker-compose.test.yml run sut

test:
	py.test src/cnavbot $(pytest_args)

coverage:
	py.test src/cnavbot --cov=src/cnavbot $(pytest_args)

static_analysis: pep8 xenon

pep8:
	@echo "Running flake8 over codebase"
	flake8 --ignore=E501,W391,F999 etl/

xenon:
	@echo "Running xenon over codebase"
	xenon --max-absolute B --max-modules B --max-average A src/cnavbot

.PHONY: build clean virtualenv test coverage static_analysis pep8 xenon test_in_docker
