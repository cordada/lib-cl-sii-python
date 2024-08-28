SHELL = /usr/bin/env bash

# Sources Root
SOURCES_ROOT = $(CURDIR)/src

# Python
PYTHON = python3
PYTHON_PIP = $(PYTHON) -m pip
PYTHON_PIP_VERSION_SPECIFIER = $(shell \
	grep -E '^pip==.+' --no-filename --only-matching --no-messages -- requirements{,-dev}.{txt,in} \
	| head -n 1 | sed 's/^pip//' \
)
PYTHON_SETUPTOOLS_VERSION_SPECIFIER = $(shell \
	grep -E '^setuptools==.+' --no-filename --only-matching --no-messages -- requirements{,-dev}.{txt,in} \
	| head -n 1 | sed 's/^setuptools//' \
)
PYTHON_VIRTUALENV_DIR = venv
PYTHON_PIP_TOOLS_VERSION_SPECIFIER = $(shell \
	grep -E '^pip-tools==.+' --no-filename --only-matching --no-messages -- requirements{,-dev}.{txt,in} \
	| head -n 1 | sed 's/^pip-tools//' \
)
PYTHON_PIP_TOOLS_SRC_FILES = requirements.in requirements-dev.in
PYTHON_PIP_TOOLS_COMPILE_ARGS = --allow-unsafe --strip-extras --quiet

# Black
BLACK = black --config .black.cfg.toml

# Tox
TOXENV ?= py310

.DEFAULT_GOAL := help
.PHONY: help
.PHONY: clean clean-build clean-pyc clean-test
.PHONY: install-dev install-deps-dev
.PHONY: lint lint-fix test test-all test-coverage
.PHONY: test-coverage-report test-coverage-report-console test-coverage-report-xml test-coverage-report-html
.PHONY: build dist deploy upload-release
.PHONE: python-virtualenv
.PHONY: python-deps-compile python-deps-sync-check python-pip-tools-install
.PHONY: python-pip-install python-setuptools-install

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

install-deps-dev: python-pip-install python-setuptools-install
install-deps-dev: python-pip-tools-install
install-deps-dev: ## Install dependencies for development
	python -m pip install -r requirements.txt
	python -m pip check

	python -m pip install -r requirements-dev.txt
	python -m pip check

lint: FLAKE8_FILES = *.py "$(SOURCES_ROOT)"
lint: ISORT_FILES = *.py "$(SOURCES_ROOT)"
lint: BLACK_SRC = *.py "$(SOURCES_ROOT)"
lint: ## run tools for code style analysis, static type check, etc
	flake8 $(FLAKE8_FILES)
	mypy
	isort --check-only $(ISORT_FILES)
	$(BLACK) --check $(BLACK_SRC)

lint-fix: BLACK_SRC = *.py "$(SOURCES_ROOT)"
lint-fix: ISORT_FILES = *.py "$(SOURCES_ROOT)"
lint-fix: ## Fix lint errors
	$(BLACK) $(BLACK_SRC)
	isort $(ISORT_FILES)

test: ## run tests quickly with the default Tox Python
	tox -e "$(TOXENV)"

test-all: ## run tests on every Python version with tox
	tox

test-coverage: ## run tests and record test coverage
	coverage run --rcfile=.coveragerc.test.ini -m unittest discover -v -c -b -s src -t src

test-coverage-report: test-coverage-report-console
test-coverage-report: test-coverage-report-xml
test-coverage-report: test-coverage-report-html
test-coverage-report: ## Run tests, measure code coverage, and generate reports

test-coverage-report-console: ## print test coverage summary
	coverage report --rcfile=.coveragerc.test.ini -m

test-coverage-report-xml: ## Generate test coverage XML report
	coverage xml --rcfile=.coveragerc.test.ini

test-coverage-report-html: ## generate test coverage HTML report
	coverage html --rcfile=.coveragerc.test.ini

build: ## Build Python package
	$(PYTHON) setup.py build

dist: build ## builds source and wheel package
	python -m build --sdist
	python -m build --wheel
	twine check --strict dist/*
	ls -l dist

upload-release: ## upload dist packages
	python -m twine upload 'dist/*'

deploy: upload-release
deploy: ## Deploy or publish

python-virtualenv: ## Create virtual Python environment
	$(PYTHON) -m venv "$(PYTHON_VIRTUALENV_DIR)"

python-pip-install: ## Install Pip
	$(PYTHON_PIP) install 'pip$(PYTHON_PIP_VERSION_SPECIFIER)'

python-setuptools-install: ## Install Setuptools
	$(PYTHON_PIP) install 'setuptools$(PYTHON_SETUPTOOLS_VERSION_SPECIFIER)'

python-deps-compile: $(patsubst %,python-deps-compile-%,$(PYTHON_PIP_TOOLS_SRC_FILES))
python-deps-compile: ## Compile Python dependency manifests

python-deps-compile-%:
	pip-compile $(PYTHON_PIP_TOOLS_COMPILE_ARGS) "$(*)"

python-deps-sync-check: $(patsubst %,python-deps-sync-check-%,$(PYTHON_PIP_TOOLS_SRC_FILES))
python-deps-sync-check: ## Check that compiled Python dependency manifests are up-to-date with their sources

python-deps-sync-check-%: python-deps-compile-%
	@# Replace file extension of source Python dependency manifest (.in)
	@# with file extension of compiled Python dependency manifest (.txt).
	git diff --exit-code -- "$(*:.in=.txt)"

python-pip-tools-install: ## Install Pip Tools
	$(PYTHON_PIP) install 'pip-tools$(PYTHON_PIP_TOOLS_VERSION_SPECIFIER)'
