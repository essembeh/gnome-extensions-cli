.PHONY: clean test build install publish publish-test 

all: build

clean:
	rm -vfr \
		dist/ build/ \
		.coverage 

venv: requirements.txt requirements-dev.txt 
	test -d venv || python3 -m virtualenv -p python3 venv --no-site-packages
	bash -c "source venv/bin/activate && \
		pip install -r requirements.txt -r requirements-dev.txt"
	touch venv

install: venv
	bash -c "source venv/bin/activate && \
		pip install -e ."

test: clean install
	bash -c "source venv/bin/activate && \
		coverage run --parallel-mode --source src/ --module pytest src/ && \
		coverage combine --append && \
		coverage report -m"
	bash -c "source venv/bin/activate && \
		flake8 src/"

build: test
	bash -c "source venv/bin/activate && \
		python3 setup.py sdist bdist_wheel"

publish-test: build
	bash -c "source venv/bin/activate && \
		twine upload --repository-url https://test.pypi.org/legacy/ dist/*"

publish: build
	bash -c "source venv/bin/activate && \
		twine upload --repository-url https://upload.pypi.org/legacy/ dist/*"

