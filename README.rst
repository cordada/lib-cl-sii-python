=================
cl-sii Python lib
=================

.. image:: https://img.shields.io/pypi/v/cl-sii.svg
    :target: https://pypi.python.org/pypi/cl-sii
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/cl-sii.svg
    :target: https://pypi.python.org/pypi/cl-sii
    :alt: Python versions

.. image:: https://img.shields.io/pypi/l/cl-sii.svg
    :target: https://pypi.python.org/pypi/cl-sii
    :alt: License

Python library for Servicio de Impuestos Internos (SII) of Chile.

Documentation
-------------

The full documentation is at https://lib-cl-sii-python.readthedocs.io.

Status
-------------

.. image:: https://circleci.com/gh/fyndata/lib-cl-sii-python/tree/develop.svg?style=shield
    :target: https://circleci.com/gh/fyndata/lib-cl-sii-python/tree/develop
    :alt: CI status

.. image:: https://codecov.io/gh/fyndata/lib-cl-sii-python/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/fyndata/lib-cl-sii-python
    :alt: Code coverage

.. image:: https://api.codeclimate.com/v1/badges/74408e5f8811f750ff3f/maintainability
    :target: https://codeclimate.com/github/fyndata/lib-cl-sii-python/maintainability
    :alt: Code Climate maintainability

.. image:: https://readthedocs.org/projects/lib-cl-sii-python/badge/?version=latest
    :target: https://lib-cl-sii-python.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation

Supported Python versions
-------------------------

Only Python 3.7. Python 3.6 and below will not work because we use some features introduced in
Python 3.7.

Quickstart
----------

Install package::

    pip install cl-sii

And TODO

Features
--------

* TODO

Tests
+++++

Requirements::

    pip install -r requirements/test.txt

Run test suite for all supported Python versions and run tools for
code style analysis, static type check, etc::

    make test-all
    make lint

Check code coverage of tests::

    make test-coverage
    make test-coverage-report-console
