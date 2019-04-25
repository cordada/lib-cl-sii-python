#!/usr/bin/env python
import os
import re
from typing import Sequence

from setuptools import find_packages, setup


def get_version(*file_paths: Sequence[str]) -> str:
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version('cl_sii', '__init__.py')

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

# TODO: add reasonable upper-bound for some of these packages?
requirements = [
    'cryptography>=2.6.1',
    'defusedxml>=0.5.0',
    'lxml>=4.2.6',
    'marshmallow>=2.16.3',
    'pyOpenSSL>=18.0.0',
    'pytz>=2018.7',
    'signxml>=2.6.0',
]

extras_requirements = {
    'django': ['Django>=2.1'],
    'djangorestframework': ['djangorestframework>=3.8.2'],
}

setup_requirements = [
]

test_requirements = [
    # note: include here only packages **imported** in test code (e.g. 'requests-mock'), NOT those
    #   like 'coverage' or 'tox'.
]

# note: the "typing information" of this project's packages is not made available to its users
#   automatically; it needs to be packaged and distributed. The way to do so is fairly new and
#   it is specified in PEP 561 - "Distributing and Packaging Type Information".
#   See:
#   - https://www.python.org/dev/peps/pep-0561/#packaging-type-information
#   - https://github.com/python/typing/issues/84
#   - https://github.com/python/mypy/issues/3930
# warning: remember to replicate this in the manifest file for source distribution ('MANIFEST.in').
_package_data = {
    'cl_sii': [
        # Indicates that the "typing information" of the package should be distributed.
        'py.typed',
        # Data files that are not in a sub-package.
        'data/ref/factura_electronica/schemas-xml/*.xsd',
    ],
}

setup(
    author='Fyndata (Fynpal SpA)',
    author_email='no-reply@fyndata.com',
    classifiers=[
        # See https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    description="""Python library for Servicio de Impuestos Internos (SII) of Chile.""",
    extras_require=extras_requirements,
    install_requires=requirements,
    license="MIT",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',  # for Markdown: 'text/markdown'
    include_package_data=True,
    name='cl-sii',
    package_data=_package_data,
    packages=find_packages(exclude=['docs', 'tests*']),
    python_requires='>=3.7, <3.8',
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/fyndata/lib-cl-sii-python',
    version=version,
    zip_safe=False,
)
