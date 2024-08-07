#!/usr/bin/env python
import os
import re
from typing import Sequence

from setuptools import find_packages, setup


def get_version(*file_paths: str) -> str:
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version('src', 'cl_sii', '__init__.py')

readme = open('README.md').read()
history = open('HISTORY.md').read()

requirements = [
    'cryptography>=38.0.0',
    'defusedxml>=0.6.0,<1',
    'jsonschema>=3.1.1',
    'lxml>=4.6.5,<6',
    'marshmallow>=3,<4',
    'pydantic>=2.3.0,!=1.7.*,!=1.8.*,!=1.9.*',
    'pyOpenSSL>=22.0.0',
    'pytz>=2019.3',
    'signxml>=3.1.0',
]

extras_requirements = {
    'django': ['Django>=2.2.24'],
    'django-filter': ['django-filter>=24.2'],
    'djangorestframework': ['djangorestframework>=3.10.3,<3.16'],
}

setup_requirements: Sequence[str] = []

test_requirements: Sequence[str] = [
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
        'data/cte/schemas-json/*.schema.json',
        'data/ref/factura_electronica/schemas-xml/*.xsd',
    ],
}

setup(
    author='Fyntex TI SpA',
    author_email='no-reply@fyntex.ai',
    classifiers=[
        # See https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="""Python library for Servicio de Impuestos Internos (SII) of Chile.""",
    extras_require=extras_requirements,
    install_requires=requirements,
    license="MIT",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',  # for reStructuredText: 'text/x-rst'
    include_package_data=True,
    name='cl-sii',
    package_data=_package_data,
    package_dir={'': 'src'},
    packages=find_packages(where='src', exclude=['scripts', 'tests*']),
    python_requires='>=3.8, <3.11',
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/fyntex/lib-cl-sii-python',
    version=version,
    zip_safe=False,
)
