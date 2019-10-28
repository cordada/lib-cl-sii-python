.. :changelog:

History
-------

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
