# cl-sii Python lib

[![PyPI package version](https://img.shields.io/pypi/v/cl-sii.svg)](https://pypi.python.org/pypi/cl-sii)
[![Python versions](https://img.shields.io/pypi/pyversions/cl-sii.svg)](https://pypi.python.org/pypi/cl-sii)
[![License](https://img.shields.io/pypi/l/cl-sii.svg)](https://pypi.python.org/pypi/cl-sii)

Python library for Servicio de Impuestos Internos (SII) of Chile.

## Documentation

The full documentation is at https://lib-cl-sii-python.readthedocs.io.

## Status

[![CI status](https://circleci.com/gh/fyntex/lib-cl-sii-python/tree/develop.svg?style=shield)](https://circleci.com/gh/fyntex/lib-cl-sii-python/tree/develop)
[![Code coverage](https://codecov.io/gh/fyntex/lib-cl-sii-python/branch/develop/graph/badge.svg)](https://codecov.io/gh/fyntex/lib-cl-sii-python)
[![Code Climate maintainability](https://api.codeclimate.com/v1/badges/c4e8a9b023310ff8c276/maintainability)](https://codeclimate.com/github/fyntex/lib-cl-sii-python/maintainability)
[![Documentation](https://readthedocs.org/projects/lib-cl-sii-python/badge/?version=latest)](https://lib-cl-sii-python.readthedocs.io/en/latest/?badge=latest)

## Supported Python versions

Only Python 3.7, 3.8 and 3.9. Python 3.6 and below will not work because we use some features
introduced in Python 3.7.

## Quickstart

Install package::

```sh
pip install cl-sii
```

And TODO

## Features

- TODO

### Tests

Requirements::

```sh
make install-dev
```

Run test suite for all supported Python versions and run tools for
code style analysis, static type check, etc::

```sh
make test-all
make lint
```

Check code coverage of tests::

```sh
make test-coverage
make test-coverage-report-console
```
