.PHONY: build install build publish publish-test docker-image docker-test clean test

all: build

venv: requirements.txt requirements-dev.txt 
	test -d venv || python3 -m virtualenv -p python3 venv --no-site-packages
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install -r requirements-dev.txt
	touch venv

install:
	test -n "$(VIRTUAL_ENV)"
	pip install -e .

clean:
	rm -vfr dist/ build/

test:
	tox

build: venv clean test
	test -n "$(VIRTUAL_ENV)"
	python3 setup.py sdist bdist_wheel

publish-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish: build
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

