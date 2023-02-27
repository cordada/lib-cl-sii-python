SHELL = /usr/bin/env bash

# Python
PYTHON = python3
PYTHON_PIP = $(PYTHON) -m pip
PYTHON_PIP_VERSION_SPECIFIER = ==22.3.1
PYTHON_SETUPTOOLS_VERSION_SPECIFIER = ==58.1.0
PYTHON_WHEEL_VERSION_SPECIFIER = ==0.38.4
PYTHON_VIRTUALENV_DIR = venv
PYTHON_PIP_TOOLS_VERSION_SPECIFIER = ~=6.8.0
PYTHON_PIP_TOOLS_SRC_FILES = requirements.in requirements-dev.in

# Black
BLACK = black --config .black.cfg.toml

.DEFAULT_GOAL := help
.PHONY: help
.PHONY: clean clean-build clean-pyc clean-test
.PHONY: install-dev install-deps-dev
.PHONY: lint lint-fix test test-all test-coverage test-coverage-report-console test-coverage-report-html
.PHONY: dist upload-release
.PHONE: python-virtualenv
.PHONY: python-deps-compile python-deps-sync-check python-pip-tools-install
.PHONY: python-pip-install python-setuptools-install python-wheel-install

help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc clean-test ## remove all build, test, lint, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -rf .eggs/
	rm -rf build/
	rm -rf dist/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test: ## remove test, lint and coverage artifacts
	rm -rf .cache/
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf test-reports/
	rm -rf .mypy_cache/

install-dev: install-deps-dev
install-dev: ## Install for development
	python -m pip install --editable .
	python -m pip check

install-deps-dev: python-pip-install python-setuptools-install python-wheel-install
install-deps-dev: python-pip-tools-install
install-deps-dev: ## Install dependencies for development
	python -m pip install -r requirements.txt
	python -m pip check

	python -m pip install -r requirements-dev.txt
	python -m pip check

lint: ## run tools for code style analysis, static type check, etc
	flake8 --config=setup.cfg  cl_sii  scripts  tests
	mypy
	isort --check-only .
	$(BLACK) --check .

lint-fix: ## Fix lint errors
	$(BLACK) .
	isort .

test: ## run tests quickly with the default Python
	python setup.py test

test-all: ## run tests on every Python version with tox
	tox

test-coverage: ## run tests and record test coverage
	coverage run --rcfile=setup.cfg setup.py test

test-coverage-report-console: ## print test coverage summary
	coverage report --rcfile=setup.cfg -m

test-coverage-report-html: ## generate test coverage HTML report
	coverage html --rcfile=setup.cfg

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	twine check dist/*
	ls -l dist

upload-release: ## upload dist packages
	python -m twine upload 'dist/*'

python-virtualenv: ## Create virtual Python environment
	$(PYTHON) -m venv "$(PYTHON_VIRTUALENV_DIR)"

python-pip-install: ## Install Pip
	$(PYTHON_PIP) install 'pip$(PYTHON_PIP_VERSION_SPECIFIER)'

python-setuptools-install: ## Install Setuptools
	$(PYTHON_PIP) install 'setuptools$(PYTHON_SETUPTOOLS_VERSION_SPECIFIER)'

python-wheel-install: ## Install Wheel
	$(PYTHON_PIP) install 'wheel$(PYTHON_WHEEL_VERSION_SPECIFIER)'

python-deps-compile: $(patsubst %,python-deps-compile-%,$(PYTHON_PIP_TOOLS_SRC_FILES))
python-deps-compile: ## Compile Python dependency manifests

python-deps-compile-%:
	pip-compile --strip-extras --quiet "$(*)"

python-deps-sync-check: $(patsubst %,python-deps-sync-check-%,$(PYTHON_PIP_TOOLS_SRC_FILES))
python-deps-sync-check: ## Check that compiled Python dependency manifests are up-to-date with their sources

python-deps-sync-check-%: python-deps-compile-%
	@# Replace file extension of source Python dependency manifest (.in)
	@# with file extension of compiled Python dependency manifest (.txt).
	git diff --exit-code -- "$(*:.in=.txt)"

python-pip-tools-install: ## Install Pip Tools
	$(PYTHON_PIP) install 'pip-tools$(PYTHON_PIP_TOOLS_VERSION_SPECIFIER)'
