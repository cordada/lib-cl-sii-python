# cl-sii Python lib

[![PyPI Package Version](https://img.shields.io/pypi/v/cl-sii)](https://pypi.org/project/cl-sii/)
[![Python Versions](https://img.shields.io/pypi/pyversions/cl-sii)](https://pypi.org/project/cl-sii/)
[![License](https://img.shields.io/pypi/l/cl-sii)](https://pypi.org/project/cl-sii/)

Python library for Servicio de Impuestos Internos (SII) of Chile.

## Documentation

The full documentation is at <https://lib-cl-sii-python.readthedocs.io>.

## Dashboard

### Development

| VCS Branch | Deployment Environment | VCS Repository | CI/CD Status |
| ---------- | ---------------------- | -------------- | ------------ |
| `develop` | Staging | [GitHub](https://github.com/fyntex/lib-cl-sii-python/tree/develop) | [![GitHub Actions](https://github.com/fyntex/lib-cl-sii-python/actions/workflows/ci-cd.yaml/badge.svg?branch=develop)](https://github.com/fyntex/lib-cl-sii-python/actions/workflows/ci-cd.yaml?query=branch:develop) |
| `master` | Production | [GitHub](https://github.com/fyntex/lib-cl-sii-python/tree/master) | [![GitHub Actions](https://github.com/fyntex/lib-cl-sii-python/actions/workflows/ci-cd.yaml/badge.svg?branch=master)](https://github.com/fyntex/lib-cl-sii-python/actions/workflows/ci-cd.yaml?query=branch:master) |

| Code Coverage | Code Climate | Documentation | Project Analysis |
| ------------- | ------------ | ------------- | ---------------- |
| [![Codecov](https://codecov.io/gh/cordada/lib-cl-sii-python/graph/badge.svg?token=VdwPUEUzzQ)](https://codecov.io/gh/cordada/lib-cl-sii-python) | [![Maintainability](https://api.codeclimate.com/v1/badges/c4e8a9b023310ff8c276/maintainability)](https://codeclimate.com/github/fyntex/lib-cl-sii-python/maintainability) | [![Read the Docs](https://readthedocs.org/projects/lib-cl-sii-python/badge/)](https://readthedocs.org/projects/lib-cl-sii-python/) | [Open Source Insights](https://deps.dev/pypi/cl-sii) |

### Hosting

| Deployment Environment | Python Package Registry |
| ---------------------- | ----------------------- |
| Production | [PyPI](https://pypi.org/project/cl-sii/) |

## Supported Python versions

Only Python 3.9 and 3.10. Python 3.8 and below will not work because we use some features
introduced in Python 3.9.

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
