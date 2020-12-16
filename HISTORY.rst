.. :changelog:

History
-------

0.11.1 (2020-12-15)
+++++++++++++++++++++++

* (PR #140, 2020-09-15) config: Make CI 'dist' job depend on 'test' jobs
* (PR #141, 2020-09-15) config: Update Python version used in CI jobs to 3.8.5
* (PR #137, 2020-09-15) build(deps): bump keyring from 21.2.0 to 21.4.0
* (PR #142, 2020-09-16) build(deps): bump mypy from 0.770 to 0.782
* (PR #145, 2020-09-21) build(deps): bump setuptools from 46.1.3 to 50.3.0
* (PR #146, 2020-09-23) build(deps): bump wheel from 0.34.2 to 0.35.1
* (PR #147, 2020-09-23) requirements: update 'eight' (dependency of 'signxml')
* (PR #149, 2020-09-24) build(deps): bump packaging from 20.3 to 20.4
* (PR #150, 2020-09-28) build(deps): bump virtualenv from 20.0.26 to 20.0.31
* (PR #157, 2020-11-12) requirements: Update 'flake8'
* (PR #158, 2020-11-12) requirements: Update 'signxml'
* (PR #161, 2020-12-15) Add support for Python 3.9
* (PR #160, 2020-12-15) build(deps): bump cryptography from 2.9 to 3.3.1
* (PR #162, 2020-12-15) config: Update Python 3.7 version to 3.7.9
* (PR #156, 2020-12-15) build(deps): bump attrs from 19.3.0 to 20.3.0
* (PR #151, 2020-12-15) build(deps): update djangorestframework requirement
  from <3.11,>=3.10.3 to >=3.10.3,<3.13
* (PR #163, 2020-12-15) requirements: update 'mypy' (test)
* (PR #164, 2020-12-15) requirements: update 'tox' (test)

0.11.0 (2020-09-15)
+++++++++++++++++++++++

* (PR #138, 2020-09-15) config: Add PyPI package uploading to CI
* (PR #135, 2020-09-15) rtc: Add constants
* (PR #129, 2020-09-14) build(deps): bump toml from 0.10.0 to 0.10.1
* (PR #133, 2020-09-14) build(deps): bump codecov from 2.0.22 to 2.1.9
* (PR #134, 2020-09-10) Add sub-package `rtc`
* (PR #131, 2020-07-22) requirements: update 'signxml'
* (PR #123, 2020-07-13) build(deps): bump six from 1.14.0 to 1.15.0
* (PR #126, 2020-07-10) build(deps): bump virtualenv from 20.0.16 to 20.0.26
* (PR #127, 2020-07-09) config: Verify Python dependency compatibility in CI
* (PR #124, 2020-07-07) build(deps): bump tox from 3.14.6 to 3.16.1
* (PR #122, 2020-07-07) config: Add configuration for GitHub Dependabot

0.10.1 (2020-06-08)
+++++++++++++++++++++++

* (PR #119, 2020-06-08) Add support for Python 3.8

0.10.0 (2020-04-14)
+++++++++++++++++++++++

0.10.0.a3
~~~~~~~~~~~~~~~~~~~~~~

* (PR #116, 2020-04-14) rcv.data_models: remove unnecessary fields
* (PR #114, 2020-04-14) rcv.parse_csv: remove param ``razon_social`` from parse functions

0.10.0.a2
~~~~~~~~~~~~~~~~~~~~~~

* (PR #112, 2020-04-14) data_models: make some fields optional

0.10.0.a1
~~~~~~~~~~~~~~~~~~~~~~

* (PR #110, 2020-04-13) rcv.data_models: move some fields to subclasses
* (PR #109, 2020-04-13) rcv.parse_csv: move code from 'fd-cl-data' in here
* (PR #108, 2020-04-13) dte.data_models: add 'DteXmlData'
* (PR #107, 2020-04-10) requirements: several updates

0.9.1 (2020-03-20)
+++++++++++++++++++++++

* Fix incorrect version used in the previous release's changelog.

0.9.0 (2020-03-20)
+++++++++++++++++++++++

* (PR #104, 2020-02-27) cte.f29.parser: Rename custom validator and deserializer parameters
* (PR #97, 2020-02-25) cte: Allow four digit Form 29 codes
* (PR #103, 2020-02-24) cte: Add custom validators and deserializers to parser

0.8.4 (2020-02-06)
+++++++++++++++++++++++

* (PR #100, 2020-02-06) Update everything for Fyntex, the new owner

0.8.3 (2020-02-06)
+++++++++++++++++++++++

* (PR #98, 2020-02-05) requirements: several updates (``cryptography``,
  ``lxml``, ``Django``, ``djangorestframework``)
* (PR #91, 2019-10-28) extras.mm_fields: add ``RcvPeriodoTributarioField``

0.8.2 (2019-10-28)
+++++++++++++++++++++++

* (PR #89, 2019-10-28) cte: Move JSON Schema of F29 'datos' object to 'data'
  directory and include it in the distribution packages
* (PR #87, 2019-10-25) cte: add data model, parser and more
* (PR #88, 2019-10-23) update config file for "deepsource"
* (PR #86, 2019-10-08) add config file for "deepsource"

0.8.1 (2019-09-25)
+++++++++++++++++++++++

* (PR #83, 2019-09-12) rcv.parse_csv: remove whitespace from "razon social"

0.8.0 (2019-09-03)
+++++++++++++++++++++++

* (PR #80, 2019-09-03) dte: Allow negative "monto total" when DTE type is "liquidación-factura
  electrónica"

0.7.4 (2019-08-08)
+++++++++++++++++++++++

* (PR #76, 2019-08-01) dte: misc data models and enum improvements

0.7.3 (2019-07-09)
+++++++++++++++++++++++

* (PR #74, 2019-07-09) requirements: update main packages

0.7.2 (2019-07-08)
+++++++++++++++++++++++

* (PR #72, 2019-07-08) extras: Handle ``str``-typed RUTs in Django ``RutField.get_prep_value()``
* (PR #70, 2019-07-05) rut: Add less-than and greater-than methods
* (PR #71, 2019-07-05) rut: Strip leading zeros from RUTs
* (PR #69, 2019-07-02) libs.tz_utils: Fix setting of time zone information in datetimes
* (PR #68, 2019-06-27) requirements: update all those for 'release' and 'test'

0.7.1 (2019-06-20)
+++++++++++++++++++++++

* (PR #66, 2019-06-20) rcv.parse_csv: detect invalid value of "razon social"

0.7.0 (2019-06-13)
+++++++++++++++++++++++

* (PR #63, 2019-06-13) rcv.parse_csv: significant changes to parse functions
* (PR #62, 2019-06-13) libs: add module ``io_utils``
* (PR #61, 2019-06-12) rcv: add data models, constants and more
* (PR #60, 2019-06-12) libs.tz_utils: misc
* (PR #59, 2019-05-31) rcv.parse_csv: add ``parse_rcv_compra_X_csv_file``

0.6.5 (2019-05-29)
+++++++++++++++++++++++

* (PR #57, 2019-05-29) libs.xml_utils: minor fix to ``verify_xml_signature``

0.6.4 (2019-05-29)
+++++++++++++++++++++++

* (PR #55, 2019-05-29) libs.xml_utils: add ``verify_xml_signature``
* (PR #54, 2019-05-28) libs: add module ``dataclass_utils``

0.6.3 (2019-05-24)
+++++++++++++++++++++++

* (PR #52, 2019-05-24) rcv: add module ``parse_csv``
* (PR #51, 2019-05-24) libs: add module ``rows_processing``
* (PR #50, 2019-05-24) libs: add module ``csv_utils``
* (PR #49, 2019-05-24) libs.mm_utils: add ``validate_no_unexpected_input_fields``
* (PR #48, 2019-05-24) dte.data_models: add ``DteDataL2.as_dte_data_l1``

0.6.2 (2019-05-15)
+++++++++++++++++++++++

* (PR #45, 2019-05-15) libs.encoding_utils: improve ``clean_base64``
* (PR #44, 2019-05-15) dte.parse: fix edge case in ``parse_dte_xml``

0.6.1 (2019-05-08)
+++++++++++++++++++++++

* (PR #40, 2019-05-08) dte.data_models: fix bug in ``DteDataL2``

0.6.0 (2019-05-08)
+++++++++++++++++++++++

Includes backwards-incompatible changes to data model ``DteDataL2``.

* (PR #38, 2019-05-08) dte.data_models: alter field ``DteDataL2.signature_x509_cert_pem``
* (PR #37, 2019-05-08) dte.data_models: alter field ``DteDataL2.firma_documento_dt_naive``
* (PR #36, 2019-05-08) libs.crypto_utils: add functions
* (PR #35, 2019-05-07) libs.tz_utils: minor improvements
* (PR #34, 2019-05-06) docs: Fix ``bumpversion`` command

0.5.1 (2019-05-03)
+++++++++++++++++++++++

* (PR #32, 2019-05-03) Requirements: updates and package upper-bounds

0.5.0 (2019-04-25)
+++++++++++++++++++++++

* (PR #29, 2019-04-25) dte.data_models: modify new fields of ``DteDataL2``
* (PR #28, 2019-04-25) libs: add module ``crypto_utils``
* (PR #27, 2019-04-25) libs: add module ``encoding_utils``
* (PR #26, 2019-04-25) test_data: add files
* (PR #25, 2019-04-25) libs.xml_utils: fix class alias ``XmlElementTree``
* (PR #24, 2019-04-25) requirements: add and update packages
* (PR #22, 2019-04-24) test_data: add files
* (PR #21, 2019-04-22) dte: many improvements
* (PR #20, 2019-04-22) libs.xml_utils: misc improvements
* (PR #19, 2019-04-22) test_data: fix and add real SII DTE & AEC XML files
* (PR #18, 2019-04-22) data.ref: add XML schemas for "Cesion" (RTC)

0.4.0 (2019-04-16)
+++++++++++++++++++++++

* (PR #16, 2019-04-16) dte.parse: change and improve ``clean_dte_xml``
* (PR #14, 2019-04-09) data.ref: merge XML schemas dirs
* (PR #13, 2019-04-09) extras: add Marshmallow field for a DTE's "tipo DTE"

0.3.0 (2019-04-05)
+++++++++++++++++++++++

* (PR #11, 2019-04-05) dte: add module ``parse``
* (PR #10, 2019-04-05) dte: add module ``data_models``
* (PR #9, 2019-04-05) libs: add module ``xml_utils``
* (PR #8, 2019-04-05) add sub-package ``rcv``

0.2.0 (2019-04-04)
+++++++++++++++++++++++

* (PR #6, 2019-04-04) data.ref: add XML schemas of "factura electrónica"
* (PR #5, 2019-04-04) extras: add 'RutField' for Django models, DRF and MM
* (PR #4, 2019-04-04) Config CircleCI

0.1.0 (2019-04-04)
+++++++++++++++++++++++

* (PR #2, 2019-04-04) Add class and constants for RUT
* (PR #1, 2019-04-04) Whole setup for a Python package/library
