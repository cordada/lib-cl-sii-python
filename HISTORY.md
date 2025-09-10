# History

## 0.55.0 (2025-09-10)

- (PR #878, 2025-09-10) extras: Improve Django filter for `Rut`
- (PR #879, 2025-09-10) chore(deps): Bump the github-actions-production group with 2 updates

## 0.54.0 (2025-09-09)

- (PR #871, 2025-09-09) rut: Use class variables for exception messages raised by `Rut`
- (PR #873, 2025-09-09) chore(deps): Bump the python-development group across 1 directory with 2 updates
- (PR #874, 2025-09-09) extras: Add option to validate RUT DV to Django model field `RutField`
- (PR #875, 2025-09-09) extras: Refactor `dj_form_fields.RutField.to_python()`
- (PR #872, 2025-09-09) chore(deps): Bump django from 4.2.23 to 4.2.24

## 0.53.0 (2025-09-02)

- (PR #862, 2025-08-28) chore(deps): Bump the github-actions-production group with 5 updates
- (PR #864, 2025-08-28) rcv: Expand "RCV Compras" CSV schemas and update field mappings
- (PR #867, 2025-09-02) rcv: Update RCV CSV typing and RCV Ventas preprocessing

## 0.52.0 (2025-08-28)

- (PR #850, 2025-08-21) chore(deps): Bump the python-development group across 1 directory with 6 updates
- (PR #856, 2025-08-26) Update Dependabot configuration
- (PR #847, 2025-08-26) chore(deps): Bump jsonschema from 4.24.0 to 4.25.0
- (PR #857, 2025-08-26) Minor improvement of CI workflow
- (PR #858, 2025-08-26) rut: Constant `RUT_DIGITS_MIN_VALUE` should be for the whole range of RUTs
- (PR #859, 2025-08-27) rcv: Enhance "RCV Ventas" CSV parsing and add schema fields

## 0.51.0 (2025-08-21)

- (PR #852, 2025-08-21) rcv: Add RvTipoVenta enum to represent "Tipo de Venta" in RCV
- (PR #853, 2025-08-21) rcv: Extend RcTipoCompra enum with new purchase types

## 0.50.0 (2025-08-20)

- (PR #843, 2025-07-30) chore(task): Update editorconfig checker
- (PR #844, 2025-08-01) Pin GitHub Action `codecov/codecov-action` to commit hash
- (PR #848, 2025-08-20) rcv: Add RcTipoCompra enum to represent "Tipo de Compra" in RCV

## 0.49.0 (2025-07-08)

- (PR #837, 2025-07-02) dte: Customize range of random folio in `DteNaturalKey.random()`
- (PR #838, 2025-07-07) rcv: Improve CSV parsing preprocessing and logging
- (PR #836, 2025-07-07) chore(deps): Bump cryptography from 44.0.3 to 45.0.4
- (PR #839, 2025-07-07) deps: Install Python package `setuptools`
- (PR #840, 2025-07-07) deps: Uninstall Python package `wheel`
- (PR #834, 2025-07-07) chore(deps): Bump signxml from 4.0.3 to 4.1.0

## 0.48.0 (2025-06-30)

- (PR #823, 2025-06-30) chore(deps): Bump typing-extensions from 4.12.2 to 4.14.0
- (PR #829, 2025-06-30) deps: Update `requests-toolbelt` from 0.9.1 to 1.0.0
- (PR #830, 2025-06-30) chore(deps): Bump setuptools from 78.1.1 to 80.9.0
- (PR #831, 2025-06-30) chore(deps): Bump django from 4.2.22 to 4.2.23

## 0.47.0 (2025-06-30)

- (PR #809, 2025-05-22) Trigger GitHub Dependency Review when draft pull request is ready for review
- (PR #817, 2025-06-11) chore(deps): Bump django from 4.2.21 to 4.2.22
- (PR #818, 2025-06-11) chore(deps): Bump requests from 2.32.2 to 2.32.4
- (PR #820, 2025-06-30) dte: Generate random `DteNaturalKeys`
- (PR #819, 2025-06-30) chore(deps): Bump urllib3 from 1.26.19 to 2.5.0
- (PR #821, 2025-06-30) Update Dependabot configuration
- (PR #822, 2025-06-30) deps: Update `signxml` from 4.0.3 to 4.0.5
- (PR #812, 2025-06-30) chore(deps): Bump jsonschema from 4.23.0 to 4.24.0
- (PR #814, 2025-06-30) chore(deps): Bump pyopenssl from 25.0.0 to 25.1.0
- (PR #813, 2025-06-30) chore(deps): Bump pydantic from 2.11.2 to 2.11.5
- (PR #826, 2025-06-30) chore(deps): Bump the github-actions-production group with 2 updates
- (PR #824, 2025-06-30) deps: Bump the development-dependencies group across 1 directory with 7 updates
- (PR #825, 2025-06-30) chore(deps): Bump pydantic from 2.11.2 to 2.11.7

## 0.46.0 (2025-05-22)

- (PR #790, 2025-03-26) Add GitHub Actions workflow to release and deploy; Etc.
- (PR #792, 2025-04-02) deps: Bump the development-dependencies group with 5 updates
- (PR #794, 2025-04-02) chore(deps): Bump setuptools from 75.3.0 to 78.1.0
- (PR #797, 2025-04-03) chore: Bump the production-dependencies group with 5 updates
- (PR #793, 2025-04-04) chore(deps): Bump djangorestframework from 3.15.2 to 3.16.0
- (PR #795, 2025-04-07) chore(deps): Bump pytz from 2025.1 to 2025.2
- (PR #796, 2025-04-07) chore(deps): Bump pydantic from 2.10.6 to 2.11.2
- (PR #798, 2025-05-06) chore: Bump the production-dependencies group with 3 updates
- (PR #804, 2025-05-14) chore: Bump django from 4.2.20 to 4.2.21
- (PR #805, 2025-05-19) chore: Bump setuptools from 78.1.0 to 78.1.1
- (PR #802, 2025-05-19) chore(deps): Bump importlib-metadata from 8.6.1 to 8.7.0
- (PR #799, 2025-05-22) chore(deps): Bump djangorestframework from 3.15.2 to 3.16.0
- (PR #803, 2025-05-22) chore(deps): Bump lxml from 5.3.1 to 5.4.0
- (PR #806, 2025-05-22) deps: Uninstall Python package `types-pyOpenSSL`
- (PR #801, 2025-05-22) chore(deps): Bump cryptography from 44.0.1 to 44.0.3

## 0.45.0 (2025-03-24)

- (PR #784, 2025-03-13) chore(deps): Bump the development-dependencies group with 8 updates
- (PR #773, 2025-03-13) chore(deps): Bump django-filter from 24.3 to 25.1
- (PR #774, 2025-03-17) chore(deps): Bump marshmallow from 3.22.0 to 3.26.1
- (PR #776, 2025-03-17) chore(deps): Bump importlib-metadata from 8.5.0 to 8.6.1
- (PR #787, 2025-03-24) Require Python ≥3.9

## 0.44.0 (2025-03-13)

- (PR #783, 2025-03-13) deps: Update `packaging` from 24.1 to 24.2

## 0.43.0 (2025-03-12)

- (PR #764, 2025-01-28) Python dependency sync check is never executed in CI/CD workflow
- (PR #765, 2025-02-03) chore: Bump the production-dependencies group with 3 updates
- (PR #766, 2025-02-03) chore(deps-dev): Bump twine from 6.0.1 to 6.1.0 in the
  development-dependencies group
- (PR #767, 2025-02-07) chore(deps): Bump pydantic from 2.10.4 to 2.10.6
- (PR #769, 2025-02-18) chore(deps): Bump pyopenssl from 24.3.0 to 25.0.0
- (PR #768, 2025-02-18) chore(deps): Bump pytz from 2024.2 to 2025.1
- (PR #770, 2025-02-18) chore(deps): Bump cryptography from 44.0.0 to 44.0.1 in the pip group
- (PR #777, 2025-03-06) chore: Bump the production-dependencies group with 4 updates
- (PR #779, 2025-03-07) libs: Add utility to get X.509 certificate from PKCS12 (PFX) file
- (PR #778, 2025-03-07) chore(deps): Bump django from 4.2.18 to 4.2.20
- (PR #775, 2025-03-07) chore(deps): Bump lxml from 5.3.0 to 5.3.1
- (PR #771, 2025-03-11) Drop support for Python 3.8

## 0.42.0 (2025-01-28)

- (PR #758, 2025-01-15) Enable `warn_unused_ignores` in Mypy configuration
- (PR #759, 2025-01-28) Annotate method return types with `typing.Self` where appropriate
- (PR #761, 2025-01-28) deps: Increase minimum version of Python package `Django` to 4.2
- (PR #760, 2025-01-28) rut: Add constant with lowest RUT for personas jurídicas

## 0.41.0 (2025-01-08)

- (PR #753, 2025-01-08) Exclude only individual test files in Mypy configuration
- (PR #755, 2025-01-08) Improve Make tasks `clean-build`, `clean-pyc`, and `clean-test`

## 0.40.0 (2025-01-08)

- (PR #748, 2025-01-06) Use most recent patch version of Python in CI/CD configuration
- (PR #750, 2025-01-08) Really use latest patch version of Python in CI/CD configuration
- (PR #751, 2025-01-08) Improve dependency caching in CI/CD configuration
- (PR #749, 2025-01-08) deps: Update dependency constraints of Python package `cl-sii`
- (PR #747, 2025-01-08) chore: Bump the production-dependencies group with 3 updates
- (PR #737, 2025-01-08) chore(deps): Bump setuptools from 70.3.0 to 75.3.0
- (PR #745, 2025-01-08) chore(deps): Bump pydantic from 2.10.3 to 2.10.4
- (PR #746, 2025-01-08) chore(deps): Bump the development-dependencies group with 6 updates

## 0.39.0 (2024-12-12)

- (PR #729, 2024-10-30) extras: Fix serialization of `None` in Pydantic `Rut` type
- (PR #730, 2024-11-19) chore: Bump the production-dependencies group with 6 updates
- (PR #733, 2024-11-20) chore: Bump the development-dependencies group across 1 directory with 5 updates
- (PR #734, 2024-12-05) chore: Bump the production-dependencies group with 2 updates
- (PR #732, 2024-12-05) chore(deps): Bump cryptography from 43.0.1 to 43.0.3
- (PR #739, 2024-12-09) chore(deps): Bump pydantic from 2.9.2 to 2.10.3
- (PR #740, 2024-12-09) chore(deps): Bump django from 4.2.16 to 4.2.17
- (PR #736, 2024-12-12) chore(deps): Bump signxml from 3.2.2 to 4.0.3
- (PR #742, 2024-12-12) deps: Update  cryptography to 44.0.0 and pyopenssl to 24.3.0

## 0.38.0 (2024-10-28)

- (PR #725, 2024-10-28) extras: Fix generation of JSON Schema for Pydantic `Rut` type
- (PR #726, 2024-10-28) chore(deps): Update `mypy` from 1.11.2 to 1.13.0

## 0.37.0 (2024-10-25)

- (PR #721, 2024-10-11) rut: Improve type annotation; Add method to validate DV
- (PR #720, 2024-10-11) chore(deps): Bump django from 4.2.15 to 4.2.16
- (PR #722, 2024-10-25) extras: Pydantic `Rut` type regex is not compliant with JSON Schema

## 0.36.0 (2024-10-03)

- (PR #715, 2024-10-01) chore: Bump actions/checkout from 4.1.7 to 4.2.0 in production-deps group
- (PR #717, 2024-10-01) Refactor `cryptography.hazmat.*` Python imports
- (PR #716, 2024-10-02) Update cleaning regex to match RUTs with non-numeric digits
- (PR #710, 2024-10-03) chore: Bump tox from 4.20.0 to 4.21.0 in the development-dependencies group
- (PR #711, 2024-10-03) chore(deps): Bump django-filter from 24.2 to 24.3
- (PR #714, 2024-10-03) chore(deps): Bump pytz from 2024.1 to 2024.2
- (PR #712, 2024-10-03) chore(deps): Bump importlib-metadata from 8.4.0 to 8.5.0

## 0.35.0 (2024-09-26)

- (PR #706, 2024-09-26) Improvements and fixes related to validation of trusted inputs
- (PR #582, 2024-09-26) Add configuration for ignoring revisions in Git Blame
- (PR #707, 2024-09-26) Make file `setup.py` executable again

## 0.34.0 (2024-09-26)

- (PR #690, 2024-09-25) chore(deps): Bump lxml from 5.2.2 to 5.3.0
- (PR #691, 2024-09-25) chore(deps): Bump marshmallow from 3.21.3 to 3.22.0
- (PR #701, 2024-09-25) Enable type checking for `setuptools`
- (PR #702, 2024-09-25) Enable type checking for `lxml`
- (PR #703, 2024-09-26) Relax some validations for trusted inputs

## 0.33.0 (2024-09-24)

- (PR #689, 2024-09-24) chore(deps): Bump pydantic from 2.7.2 to 2.8.2
- (PR #694, 2024-09-24) deps: Bump the development-dependencies group with 4 updates
- (PR #695, 2024-09-24) deps: Update `pydantic` from 2.8.2 to 2.9.2
- (PR #693, 2024-09-24) chore(deps): Bump cryptography from 42.0.8 to 43.0.1
- (PR #696, 2024-09-24) extras: Add Pydantic type for `Rut`
- (PR #687, 2024-09-24) chore: Bump the production-dependencies group with 2 updates
- (PR #697, 2024-09-24) cte: Close file object in `f29.parse_datos_obj`

## 0.32.0 (2024-08-28)

- (PR #660, 2024-08-23) chore: Bump setuptools from 65.5.1 to 70.3.0
- (PR #672, 2024-08-23) chore: Bump django from 4.2.14 to 4.2.15
- (PR #676, 2024-08-23) chore(deps): Update `pip` from 23.3 to 24.2
- (PR #677, 2024-08-23) chore(deps): Update `wheel` from ≤0.43.0 to 0.44.0
- (PR #675, 2024-08-23) Replace Setuptools Configuration with Python Project Configuration
- (PR #670, 2024-08-23) chore: Bump jsonschema from 4.22.0 to 4.23.0
- (PR #678, 2024-08-23) chore: Bump the development-dependencies group across 1 directory with 7 updates
- (PR #679, 2024-08-23) chore: Bump the production-dependencies group across 1 directory with 2 updates
- (PR #680, 2024-08-23) Test coverage broken by migration from `setup.py` to `pyproject.toml`
- (PR #668, 2024-08-23) chore: Bump pyopenssl from 24.1.0 to 24.2.1
- (PR #673, 2024-08-23) chore(deps): Bump importlib-metadata from 7.1.0 to 8.4.0
- (PR #681, 2024-08-28) Move Flake8 configuration from `setup.cfg` to its own file
- (PR #682, 2024-08-28) Move Coverage.py configuration from `setup.cfg` to its own file
- (PR #683, 2024-08-28) Replace `setup.py sdist` and `bdist_wheel` with `build`
- (PR #684, 2024-08-28) When running `twine check`, fail on warnings

## 0.31.0 (2024-07-17)

- (PR #661, 2024-07-17) extras: Add `RutFilter` for Django views and DRF views
- (PR #662, 2024-07-17) extras: Add Django URL path converter for RUT and Tipo DTE
- (PR #663, 2024-07-17) extras: Add mapping of Django model fields to DRF serializer fields
- (PR #664, 2024-07-17) extras: Reformat source code of `.dj_filters`

## 0.30.0 (2024-07-11)

- (PR #640, 2024-05-20) chore: Bump the production-dependencies group across 1 directory with 5 updates
- (PR #643, 2024-05-30) chore: Bump requests from 2.31.0 to 2.32.2
- (PR #642, 2024-05-30) chore: Bump pydantic from 2.6.4 to 2.7.2
- (PR #644, 2024-05-30) chore: Bump the development-dependencies group across 1 directory with 6 updates
- (PR #633, 2024-05-30) chore: Bump jsonschema from 4.21.1 to 4.22.0
- (PR #648, 2024-06-11) Replace hardcoded versions of Pip and others in Make variables
- (PR #649, 2024-06-11) chore: Bump cryptography from 42.0.5 to 42.0.8
- (PR #651, 2024-07-10) chore: Bump urllib3 from 1.26.18 to 1.26.19
- (PR #652, 2024-07-10) chore: Bump djangorestframework from 3.15.1 to 3.15.2
- (PR #655, 2024-07-10) chore(deps): Update package `zipp` from 3.8.1 to 3.19.2
- (PR #650, 2024-07-11) chore: Bump marshmallow from 3.21.1 to 3.21.3
- (PR #646, 2024-07-11) chore: Bump lxml from 5.2.1 to 5.2.2
- (PR #656, 2024-07-11) chore: Bump the development-dependencies group across 1 directory with 6 updates
- (PR #657, 2024-07-11) chore: Bump the production-dependencies group across 1 directory with 6 updates

## 0.29.0 (2024-05-15)

- (PR #614, 2024-03-26) chore: Bump the production-dependencies group with 4 updates
- (PR #617, 2024-03-27) chore: Bump black from 24.1.1 to 24.3.0
- (PR #619, 2024-03-27) chore: Bump pydantic from 2.6.1 to 2.6.4
- (PR #618, 2024-03-27) chore: Bump marshmallow from 3.20.2 to 3.21.1
- (PR #616, 2024-03-27) chore: Bump django from 3.2.24 to 3.2.25
- (PR #615, 2024-03-27) chore: Bump cryptography from 42.0.4 to 42.0.5
- (PR #620, 2024-03-27) chore: Bump the development-dependencies group with 7 updates
- (PR #621, 2024-04-04) chore: Bump the production-dependencies group with 6 updates
- (PR #628, 2024-04-16) chore: Bump sqlparse from 0.4.4 to 0.5.0
- (PR #627, 2024-04-16) chore: Bump idna from 2.10 to 3.7
- (PR #624, 2024-04-16) chore: Bump pyopenssl from 24.0.0 to 24.1.0
- (PR #629, 2024-04-16) chore: Bump lxml from 5.1.0 to 5.2.1
- (PR #626, 2024-04-18) chore: Bump importlib-metadata from 6.1.0 to 7.1.0
- (PR #631, 2024-04-18) chore(deps): Bump the development-dependencies group with 4 updates
- (PR #625, 2024-04-18) chore: Bump djangorestframework from 3.14.0 to 3.15.1
- (PR #636, 2024-05-15) Disallow implicit re-exports of imported values in Python modules

## 0.28.0 (2024-02-26)

- (PR #606, 2024-02-14) fix: Add default value for missing codes in SII CTE Form 29
- (PR #607, 2024-02-19) chore: Bump cryptography from 41.0.7 to 42.0.2
- (PR #605, 2024-02-19) chore: Bump django from 3.2.23 to 3.2.24
- (PR #608, 2024-02-26) chore: Bump cryptography from 42.0.2 to 42.0.4

## 0.27.0 (2024-02-07)

- (PR #593, 2024-02-01) chore: Bump pydantic from 2.5.3 to 2.6.0
- (PR #592, 2024-02-05) chore: Bump lxml from 4.9.2 to 4.9.4
- (PR #595, 2024-02-05) chore: Bump the development-dependencies group with 6 updates
- (PR #596, 2024-02-05) chore: Bump the production-dependencies group with 5 updates
- (PR #599, 2024-02-07) chore: Bump signxml from 3.2.1 to 3.2.2
- (PR #598, 2024-02-07) chore: Bump pydantic from 2.6.0 to 2.6.1
- (PR #600, 2024-02-07) chore: Bump pyopenssl from 23.2.0 to 24.0.0
- (PR #597, 2024-02-07) chore: Bump pytz from 2023.3.post1 to 2024.1
- (PR #601, 2024-02-07) chore: Bump marshmallow from 3.20.1 to 3.20.2
- (PR #602, 2024-02-07) chore(deps): Update `lxml` from 4.9.4 to 5.1.0

## 0.26.0 (2024-01-30)

- (PR #586, 2024-01-30) fix: Add default value for missing code `098` in SII CTE Form 29
- (PR #577, 2024-01-30) chore: Bump cryptography from 41.0.4 to 41.0.7
- (PR #587, 2024-01-30) chore: Bump jsonschema from 4.19.2 to 4.21.1

## 0.25.0 (2024-10-01)

- (PR #581, 2024-01-03) chore: Bump the production-dependencies group with 4 updates
- (PR #571, 2024-01-03) chore: Bump cryptography from 41.0.4 to 41.0.6
- (PR #580, 2024-01-09) chore: Bump the development-dependencies group with 7 updates
- (PR #583, 2024-01-10) dte: Allow gaps when validating order of `DteXmlData.referencias`
- (PR #579, 2024-01-10) chore: Bump pydantic from 2.4.2 to 2.5.3

## 0.24.0 (2023-11-09)

- (PR #555, 2023-10-23) Fix GitHub code scanning alerts 'Clear-text logging of sensitive info'
- (PR #562, 2023-11-03) chore: Bump the production-dependencies group with 2 updates
- (PR #509, 2023-11-06) chore: Bump marshmallow from 3.19.0 to 3.20.1
- (PR #563, 2023-11-06) chore: Bump django from 3.2.20 to 3.2.23
- (PR #561, 2023-11-06) chore: Bump jsonschema from 4.17.3 to 4.19.2
- (PR #558, 2023-11-06) chore: Bump the development-dependencies group with 5 updates
- (PR #559, 2023-11-06) chore: Bump signxml from 3.2.0 to 3.2.1
- (PR #560, 2023-11-06) chore: Bump pytz from 2023.3 to 2023.3.post1
- (PR #557, 2023-11-08) dte: Improve validation error message in `DteXmlData.referencias`
- (PR #564, 2023-11-08) Remove Make task `python-wheel-install`
- (PR #566, 2023-11-08) Add Python project configuration
- (PR #565, 2023-11-09) chore(deps): Update `pip-tools` from 6.14.0 to 7.3.0
- (PR #568, 2023-11-09) chore: Bump setuptools from 58.1.0 to 65.5.1
- (PR #567, 2023-11-09) chore: Bump pip from 22.3.1 to 23.3

## 0.23.4 (2023-10-23)

- (PR #547, 2023-10-02) chore: Bump pydantic from 2.3.0 to 2.4.2
- (PR #544, 2023-10-23) Migrate to `pydantic==2.4.2`
- (PR #545, 2023-10-23) chore: Bump the production-dependencies group with 4 updates
- (PR #549, 2023-10-23) chore: Bump the development-dependencies group with 5 updates
- (PR #553, 2023-10-23) Improve CI/CD workflows
- (PR #554, 2023-10-23) Enable GHA secrets inheritance so that Codecov token can be passed
- (PR #543, 2023-10-23) chore: Bump cryptography from 41.0.3 to 41.0.4
- (PR #551, 2023-10-23) chore: Bump urllib3 from 1.26.12 to 1.26.18

## 0.23.3 (2023-09-14)

- (PR #530, 2023-09-05) chore: Bump the development-dependencies group with 9 updates
- (PR #536, 2023-09-05) chore(deps): Update `typing-extensions` from 4.3.0 to 4.7.1
- (PR #538, 2023-09-06) Fix errors reported by EditorConfig-Checker
- (PR #537, 2023-09-06) Change Python project structure from Flat layout to Src layout
- (PR #539, 2023-09-07) Add Codecov repository upload token; update Codecov status badge
- (PR #540, 2023-09-14) Update pydantic from 1.10.12 to 2.3.0

## 0.23.2 (2023-09-05)

- (PR #522, 2023-08-07) Enable Editor Configuration validation in Super-Linter
- (PR #523, 2023-08-08) chore(deps): Update `pydantic` from 1.10.4 to 1.10.12
- (PR #524, 2023-08-10) Fix type checking of Setuptools configuration
- (PR #521, 2023-08-10) chore: Bump cryptography from 41.0.2 to 41.0.3
- (PR #525, 2023-08-28) Add dependency groups to Dependabot configuration
- (PR #526, 2023-08-28) chore: Bump the production-dependencies group with 2 updates

## 0.23.1 (2023-07-26)

- (PR #478, 2023-04-05) Fix Git alias `lg-github-pr-summary` in Contributing Guidelines
- (PR #479, 2023-04-05) Update code owners for Python dependencies
- (PR #467, 2023-04-10) chore(deps): Bump importlib-metadata from 6.0.0 to 6.1.0
- (PR #483, 2023-04-18) Add Codecov to CI workflow
- (PR #466, 2023-04-18) chore: Bump actions/cache from 3.2.6 to 3.3.1
- (PR #465, 2023-04-18) chore: Bump actions/dependency-review-action from 3.0.3 to 3.0.4
- (PR #481, 2023-04-24) chore: Bump actions/checkout from 3.3.0 to 3.5.2
- (PR #480, 2023-04-24) chore(deps-dev): Bump mypy from 1.0.1 to 1.2.0
- (PR #473, 2023-04-24) chore(deps-dev): Bump types-pytz from 2022.7.1.2 to 2023.3.0.0
- (PR #471, 2023-04-24) chore(deps): Bump pytz from 2022.7.1 to 2023.3
- (PR #468, 2023-04-24) chore(deps): Bump cryptography from 39.0.1 to 39.0.2
- (PR #486, 2023-05-05) chore: Bump codecov/codecov-action from 3.1.2 to 3.1.3
- (PR #484, 2023-05-09) chore: Bump sqlparse from 0.4.2 to 0.4.4
- (PR #499, 2023-06-22) chore(deps): Update `black` from 23.1.0 to 23.3.0
- (PR #501, 2023-07-03) chore: Bump actions/checkout from 3.5.2 to 3.5.3
- (PR #502, 2023-07-03) chore(deps): Update `pip-tools` from 6.8.0 to 6.14.0
- (PR #504, 2023-07-19) chore: Bump actions/setup-python from 4.5.0 to 4.7.0
- (PR #495, 2023-07-20) chore: Bump actions/dependency-review-action from 3.0.4 to 3.0.6
- (PR #494, 2023-07-21) chore: Bump codecov/codecov-action from 3.1.3 to 3.1.4
- (PR #497, 2023-07-25) chore: Bump pyopenssl from 23.0.0 to 23.2.0
- (PR #505, 2023-07-25) chore: Bump pygments from 2.13.0 to 2.15.0
- (PR #492, 2023-07-25) chore: Bump requests from 2.25.1 to 2.31.0
- (PR #512, 2023-07-25) chore: Bump cryptography from 39.0.2 to 41.0.2
- (PR #513, 2023-07-25) chore(deps): Update `django` from 3.2.17 to 3.2.20
- (PR #490, 2023-07-25) chore(deps): Bump signxml from 3.1.0 to 3.2.0
- (PR #514, 2023-07-25) chore(deps): Update `tox` from 3.25.1 to 4.6.4
- (PR #506, 2023-07-25) chore: Bump types-pyopenssl from 23.0.0.4 to 23.2.0.2
- (PR #498, 2023-07-25) chore: Bump coverage from 7.1.0 to 7.2.7
- (PR #515, 2023-07-25) chore(deps): Update `certifi` from 2022.6.15 to 2023.7.22
- (PR #516, 2023-07-25) Update code owners
- (PR #511, 2023-07-25) chore: Bump wheel from 0.38.4 to 0.41.0

## 0.23.0 (2023-04-05)

- (PR #443, 2023-03-13) chore(deps-dev): Bump types-pytz from 2022.7.1.0 to 2022.7.1.2
- (PR #445, 2023-03-13) chore(deps-dev): Bump types-jsonschema from 4.17.0.3 to 4.17.0.6
- (PR #428, 2023-03-13) chore(deps): Bump signxml from 2.10.1 to 3.1.0
- (PR #444, 2023-03-13) chore(deps-dev): Bump types-pyopenssl from 23.0.0.2 to 23.0.0.4
- (PR #462, 2023-03-14) Update minimum version of `signxml` to `3.1.0`
- (PR #429, 2023-03-14) chore(deps): Bump importlib-metadata from 1.6.0 to 6.0.0
- (PR #463, 2023-03-29) Decrease Dependabot's open pull request limit to 5
- (PR #475, 2023-04-03) Update Editor Configuration
- (PR #474, 2023-04-04) Update Super-Linter configuration
- (PR #218, 2023-04-04)  Add data model for DTE Referencia
- (PR #461, 2023-04-04) Add contributing guidelines

## 0.22.3 (2023-03-13)

- (PR #432, 2023-03-13) chore(deps-dev): Bump isort from 5.10.1 to 5.12.0
- (PR #430, 2023-03-13) chore(deps-dev): Bump flake8 from 4.0.1 to 6.0.0
- (PR #458, 2023-03-13) fix(data.cte): Add missing code `8020` to file used by schema validator

## 0.22.2 (2023-03-10)

- (PR #427, 2023-03-10) chore(deps-dev): Bump black from 22.12.0 to 23.1.0
- (PR #455, 2023-03-10) fix(data.cte): Add missing codes to files used by schema validator

## 0.22.1 (2023-03-09)

- (PR #452, 2023-03-09) fix(data.cte): Add JSON files to MANIFEST.in

## 0.22.0 (2023-03-09)

- (PR #446, 2023-03-07) chore(deps-dev): Bump mypy from 0.991 to 1.0.1
- (PR #449, 2023-03-08) Drop support for Python 3.7
- (PR #442, 2023-03-09) chore: Bump actions/cache from 3.2.5 to 3.2.6
- (PR #440, 2023-03-09) fix(cte): Add default values for known missing codes in SII CTE Form 29

## 0.21.0 (2023-02-28)

- (PR #441, 2023-03-01) Switch CI/CD from CircleCI to GitHub Actions

## 0.20.0 (2023-02-10)

- (PR #403, 2023-01-05) chore(deps): Bump pyopenssl from 22.0.0 to 22.1.0
- (PR #406, 2023-01-05) chore(deps-dev): Bump mypy from 0.982 to 0.991
- (PR #405, 2023-01-23) chore(deps): Bump jsonschema from 4.16.0 to 4.17.3
- (PR #422, 2023-01-26) Add GitHub Dependency Review
- (PR #423, 2023-01-26) Improve GitHub Dependency Review
- (PR #411, 2023-01-26) chore(deps-dev): Bump black from 22.10.0 to 22.12.0
- (PR #425, 2023-01-27) Update Markdownlint configuration
- (PR #410, 2023-02-03) chore(deps): Bump pydantic from 1.10.2 to 1.10.4
- (PR #433, 2023-02-03) Improve type checking
- (PR #434, 2023-02-03) Improve type checking
- (PR #424, 2023-02-06) chore(deps-dev): Bump coverage from 6.5.0 to 7.1.0
- (PR #414, 2023-02-06) chore(deps): Bump lxml from 4.9.1 to 4.9.2
- (PR #420, 2023-02-06) chore(deps): Bump pytz from 2022.6 to 2022.7.1
- (PR #431, 2023-02-06) chore(deps): Bump pyopenssl from 22.1.0 to 23.0.0
- (PR #436, 2023-02-08) chore(deps): Bump cryptography from 38.0.4 to 39.0.1
- (PR #435, 2023-02-08) chore(deps): Bump django from 3.2.16 to 3.2.17
- (PR #426, 2023-02-08) chore(deps): Bump marshmallow from 2.21.0 to 3.19.0

## 0.19.0 (2023-01-05)

- (PR #398, 2022-11-23) fix: Fix Dependabot error pip.….Error: Constraints cannot have extras
- (PR #399, 2022-11-23) chore(deps): Bump cryptography from 38.0.1 to 38.0.3
- (PR #400, 2022-12-05) chore(deps-dev): Bump wheel from 0.37.1 to 0.38.4
- (PR #407, 2022-12-05) chore(deps): Bump cryptography from 38.0.3 to 38.0.4
- (PR #408, 2022-12-06) Enable Python dependency sync check for Python 3.7
- (PR #409, 2022-12-29) chore: Add support for Python 3.10

## 0.18.3 (2022-11-07)

- (PR #346, 2022-09-28) chore(deps-dev): bump mypy from 0.790 to 0.971
- (PR #385, 2022-10-14) chore(deps-dev): Bump mypy from 0.971 to 0.981
- (PR #389, 2022-10-14) chore(deps-dev): Bump coverage from 6.4.4 to 6.5.0
- (PR #386, 2022-10-19) chore(deps): Bump djangorestframework from 3.13.1 to 3.14.0
- (PR #391, 2022-10-19) chore(deps): Bump django from 3.2.15 to 3.2.16
- (PR #394, 2022-11-03) chore(deps-dev): Bump mypy from 0.981 to 0.982
- (PR #395, 2022-11-07) chore(deps): Bump pytz from 2022.2.1 to 2022.6
- (PR #396, 2022-11-07) chore(deps-dev): Bump black from 22.8.0 to 22.10.0
- (PR #375, 2022-11-07) chore(deps): Bump signxml from 2.9.0 to 2.10.1
- (PR #376, 2022-11-07) chore(deps): Bump cryptography from 37.0.4 to 38.0.1

## 0.18.2 (2022-09-26)

- (PR #370, 2022-09-14) chore(deps): Bump pyopenssl from 18.0.0 to 20.0.1
- (PR #373, 2022-09-14) Manage Python dependencies with Pip Tools
- (PR #381, 2022-09-14) fix(deps): Remove Python version constraint for `importlib-metadata`
- (PR #382, 2022-09-14) fix(deps): Workaround for CI issues related to `python-deps-sync-check`
- (PR #380, 2022-09-14) chore(deps): Bump pydantic from 1.10.1 to 1.10.2
- (PR #371, 2022-09-23) chore(deps): Bump jsonschema from 3.2.0 to 4.16.0
- (PR #374, 2022-09-23) chore(deps): Bump defusedxml from 0.6.0 to 0.7.1
- (PR #377, 2022-09-23) chore(deps-dev): Bump codecov from 2.1.11 to 2.1.12
- (PR #378, 2022-09-23) chore(deps-dev): Bump black from 22.1.0 to 22.8.0
- (PR #379, 2022-09-23) chore(deps-dev): Bump coverage from 5.3 to 6.4.4

## 0.18.1 (2022-09-01)

- (PR #362, 2022-08-29) Add information dashboard to readme
- (PR #358, 2022-08-29) chore(deps): bump pytz from 2019.3 to 2022.2.1
- (PR #364, 2022-08-31) chore(deps): bump typing-extensions from 4.0.1 to 4.3.0
- (PR #367, 2022-08-31) chore(deps): Update 'pydantic' from version 1.6.2 to 1.10.1
- (PR #368, 2022-09-01) Add Super-Linter

## 0.18.0 (2022-08-26)

- (PR #343, 2022-07-08) chore: Update Dependabot configuration
- (PR #281, 2022-07-21) build(deps): bump six from 1.15.0 to 1.16.0
- (PR #340, 2022-07-21) build(deps): bump lxml from 4.6.5 to 4.9.1
- (PR #334, 2022-07-22) build(deps): bump certifi from 2020.12.5 to 2022.6.15
- (PR #350, 2022-08-11) chore: Add code owners
- (PR #352, 2022-08-18) chore: Change Dependabot schedule interval from `weekly` to `monthly`
- (PR #338, 2022-08-22) build(deps-dev): bump tox from 3.20.1 to 3.25.1
- (PR #342, 2022-08-22) chore(deps): Bump cryptography from 3.3.2 to 37.0.4
- (PR #286, 2022-08-24) build(deps): bump eight from 1.0.0 to 1.0.1
- (PR #355, 2022-08-24) chore: Add Make tasks for installation
- (PR #332, 2022-08-24) build(deps-dev): bump pkginfo from 1.7.0 to 1.8.3
- (PR #288, 2022-08-24) build(deps): bump pluggy from 0.13.1 to 1.0.0
- (PR #287, 2022-08-25) build(deps): bump wheel from 0.35.1 to 0.37.1
- (PR #356, 2022-08-25) chore(deps): bump marshmallow from 2.19.5 to 2.21.0
- (PR #339, 2022-08-25) build(deps): bump cffi from 1.14.0 to 1.15.1
- (PR #312, 2022-08-25) build(deps-dev): bump tqdm from 4.45.0 to 4.64.0
- (PR #359, 2022-08-25) chore: Add Git commit linter
- (PR #360, 2022-08-26) Update files for Git commit linter

## 0.17.3 (2022-07-04)

- (PR #326, 2022-05-25) chore(requirements-dev): Update package `readme-renderer` to 35.0
- (PR #325, 2022-05-25) chore: Update Python to version 3.8.13

## 0.17.2 (2022-03-31)

- (PR #309, 2022-03-31) fix(rut): `AttributeError` for `GeneralName` object without `type_id`

## 0.17.1 (2022-02-16)

- (PR #269, 2022-02-03) chore: Add tool to automatically sort Python imports
- (PR #274, 2022-02-08) chore: Increase Dependabot's open pull request limit for `pip`
- (PR #273, 2022-02-08) requirements: Update 'Flake8'
- (PR #292, 2022-02-08) chore: Increase Django REST Framework required maximum version to 3.13.x
- (PR #294, 2022-02-09) chore: Simplify organization of Python dependency manifests
- (PR #272, 2022-02-10) Add 'Black' Python code formatter

## 0.17.0 (2022-01-27)

- (PR #251, 2022-01-14) rcv: Convert stdlib dataclasses into pydantic dataclasses
- (PR #267, 2022-01-27) cl_sii.rut: Add method to get the RUT of the certificate holder

## 0.16.1 (2022-01-13)

- (PR #264, 2022-01-13) rtc.xml_utils: Add method to verify signature of AEC XML document

## 0.16.0 (2021-12-24)

- (PR #261, 2021-12-24) chore(rtc.parse): Disable validation that AEC signature cert is loadable
- (PR #253, 2021-12-24) Rename of the enum class for `TipoDte` object

## 0.15.2 (2021-12-23)

- (PR #258, 2021-12-22) chore: Increase lxml lower bound constraint
- (PR #259, 2021-12-23) requirements: Update 'signxml'

## 0.15.1 (2021-12-21)

- (PR #255, 2021-12-21) build(deps): bump lxml from 4.6.3 to 4.6.5

## 0.15.0 (2021-10-20)

- (PR #242, 2021-10-12) rtc: Verify outermost XML signature of SII AECs
- (PR #247, 2021-10-19) config: Update Python version used in CI jobs to 3.8.12
- (PR #245, 2021-10-20) rtc.parse_aec: Convert to `None` the empty optional values in the Caratula

## 0.14.1 (2021-10-12)

- (PR #238, 2021-09-08) rut: Fix RUT clean method to accept '0-0' value
- (PR #241, 2021-09-16) rtc: Make AEC field 'nombre persona autorizada cedente' optional

## 0.14.0 (2021-08-17)

- (PR #234, 2021-08-09) dte: Convert stdlib dataclasses into pydantic dataclasses
- (PR #236, 2021-08-09) DteXmlData: Restore mistakenly deleted regression tests

## 0.13.0 (2021-07-14)

- (PR #228, 2021-06-29) config: Update Python version used in CI jobs to 3.8.10
- (PR #230, 2021-07-09) dte: Convert stdlib dataclass `DteXmlData` into pydantic dataclass

## 0.12.5 (2021-06-15)

- (PR #226, 2021-06-15) requirements: Remove Django upper bound constraint
- (PR #224, 2021-06-15) requirements: Upgrade 'Django'
- (PR #223, 2021-06-08) requirements: Upgrade 'Django'
- (PR #221, 2021-05-14) requirements: Upgrade Pydantic
- (PR #216, 2021-04-22) docs: Add creation of release branch to instructions for new releases
- (PR #213, 2021-04-21) build(deps): bump toml from 0.10.1 to 0.10.2

## 0.12.4 (2021-04-15)

- (PR #195, 2021-04-15) build(deps): bump requests from 2.23.0 to 2.25.1
- (PR #212, 2021-04-14) config: Update Python version used in CI jobs to 3.8.9
- (PR #210, 2021-04-13) rtc.data_models_aec: remove validation for the progression of
  'monto_cesion' across the 'cesiones'
- (PR #207, 2021-04-08) build(deps): bump virtualenv from 20.0.31 to 20.4.3
- (PR #208, 2021-04-08) rtc.data_models_aec: remove match validation for 'fecha_firma_dt' and
  'fecha_cesion_dt'
- (PR #205, 2021-03-26) build(deps): bump lxml from 4.6.2 to 4.6.3
- (PR #204, 2021-03-24) requirements: Upgrade 'Django'

## 0.12.3 (2021-02-26)

- (PR #193, 2021-02-16) requirements: Update dependency graph of base requirements
- (PR #197, 2021-02-26) extras: add 'RutField' for Django forms

## 0.12.2 (2021-02-16)

- (PR #177, 2021-02-16) build(deps): bump lxml from 4.5.0 to 4.6.2
- (PR #188, 2021-02-16) build(deps): bump cryptography from 3.3.1 to 3.3.2
- (PR #176, 2021-02-16) build(deps): bump zipp from 3.1.0 to 3.4.0
- (PR #167, 2021-02-16) build(deps): bump py from 1.8.1 to 1.10.0
- (PR #189, 2021-02-16) build(deps): bump certifi from 2020.4.5.1 to 2020.12.5
- (PR #185, 2021-02-16) build(deps): bump pkginfo from 1.5.0.1 to 1.7.0
- (PR #191, 2021-02-16) build(deps): bump pyrsistent from 0.16.0 to 0.17.3
- (PR #190, 2021-02-16) build(deps): bump typed-ast from 1.4.1 to 1.4.2

## 0.12.1 (2021-02-09)

- (PR #186, 2021-02-09) rtc: Add methods to build CesionL2, CesionL1, and CesionL0 from other data
  models

## 0.12.0 (2021-01-17)

- (PR #179, 2021-01-13) rtc: Add data models for "cesión"
- (PR #181, 2021-01-14) rtc.data_models: Clean up configuration leftovers from tests
- (PR #180, 2021-01-15) rtc: Add data models and parser for AECs

## 0.11.2 (2021-01-11)

- (PR #166, 2020-12-15) requirements: Update 'cryptography'
- (PR #169, 2020-12-16) build(deps): bump coverage from 4.5.3 to 5.3
- (PR #172, 2020-12-22) rtc: Add data model for "Cesiones Periodo" entries
- (PR #173, 2021-01-05) requirements: Add 'pydantic'
- (PR #175, 2021-01-06) libs.tz_utils: Add checks to validate_dt_tz
- (PR #174, 2021-01-07) rtc: Add constants and "cesión" natural keys
- (PR #171, 2021-01-07) build(deps): bump codecov from 2.1.9 to 2.1.11

## 0.11.1 (2020-12-15)

- (PR #140, 2020-09-15) config: Make CI 'dist' job depend on 'test' jobs
- (PR #141, 2020-09-15) config: Update Python version used in CI jobs to 3.8.5
- (PR #137, 2020-09-15) build(deps): bump keyring from 21.2.0 to 21.4.0
- (PR #142, 2020-09-16) build(deps): bump mypy from 0.770 to 0.782
- (PR #145, 2020-09-21) build(deps): bump setuptools from 46.1.3 to 50.3.0
- (PR #146, 2020-09-23) build(deps): bump wheel from 0.34.2 to 0.35.1
- (PR #147, 2020-09-23) requirements: update 'eight' (dependency of 'signxml')
- (PR #149, 2020-09-24) build(deps): bump packaging from 20.3 to 20.4
- (PR #150, 2020-09-28) build(deps): bump virtualenv from 20.0.26 to 20.0.31
- (PR #157, 2020-11-12) requirements: Update 'flake8'
- (PR #158, 2020-11-12) requirements: Update 'signxml'
- (PR #161, 2020-12-15) Add support for Python 3.9
- (PR #160, 2020-12-15) build(deps): bump cryptography from 2.9 to 3.3.1
- (PR #162, 2020-12-15) config: Update Python 3.7 version to 3.7.9
- (PR #156, 2020-12-15) build(deps): bump attrs from 19.3.0 to 20.3.0
- (PR #151, 2020-12-15) build(deps): update djangorestframework requirement
  from <3.11,>=3.10.3 to >=3.10.3,<3.13
- (PR #163, 2020-12-15) requirements: update 'mypy' (test)
- (PR #164, 2020-12-15) requirements: update 'tox' (test)

## 0.11.0 (2020-09-15)

- (PR #138, 2020-09-15) config: Add PyPI package uploading to CI
- (PR #135, 2020-09-15) rtc: Add constants
- (PR #129, 2020-09-14) build(deps): bump toml from 0.10.0 to 0.10.1
- (PR #133, 2020-09-14) build(deps): bump codecov from 2.0.22 to 2.1.9
- (PR #134, 2020-09-10) Add sub-package `rtc`
- (PR #131, 2020-07-22) requirements: update 'signxml'
- (PR #123, 2020-07-13) build(deps): bump six from 1.14.0 to 1.15.0
- (PR #126, 2020-07-10) build(deps): bump virtualenv from 20.0.16 to 20.0.26
- (PR #127, 2020-07-09) config: Verify Python dependency compatibility in CI
- (PR #124, 2020-07-07) build(deps): bump tox from 3.14.6 to 3.16.1
- (PR #122, 2020-07-07) config: Add configuration for GitHub Dependabot

## 0.10.1 (2020-06-08)

- (PR #119, 2020-06-08) Add support for Python 3.8

## 0.10.0 (2020-04-14)

### 0.10.0.a3

- (PR #116, 2020-04-14) rcv.data_models: remove unnecessary fields
- (PR #114, 2020-04-14) rcv.parse_csv: remove param `razon_social` from parse functions

### 0.10.0.a2

- (PR #112, 2020-04-14) data_models: make some fields optional

### 0.10.0.a1

- (PR #110, 2020-04-13) rcv.data_models: move some fields to subclasses
- (PR #109, 2020-04-13) rcv.parse_csv: move code from 'fd-cl-data' in here
- (PR #108, 2020-04-13) dte.data_models: add 'DteXmlData'
- (PR #107, 2020-04-10) requirements: several updates

## 0.9.1 (2020-03-20)

- Fix incorrect version used in the previous release's changelog.

## 0.9.0 (2020-03-20)

- (PR #104, 2020-02-27) cte.f29.parser: Rename custom validator and deserializer parameters
- (PR #97, 2020-02-25) cte: Allow four digit Form 29 codes
- (PR #103, 2020-02-24) cte: Add custom validators and deserializers to parser

## 0.8.4 (2020-02-06)

- (PR #100, 2020-02-06) Update everything for Fyntex, the new owner

## 0.8.3 (2020-02-06)

- (PR #98, 2020-02-05) requirements: several updates (`cryptography`,
  `lxml`, `Django`, `djangorestframework`)
- (PR #91, 2019-10-28) extras.mm_fields: add `RcvPeriodoTributarioField`

## 0.8.2 (2019-10-28)

- (PR #89, 2019-10-28) cte: Move JSON Schema of F29 'datos' object to 'data'
  directory and include it in the distribution packages
- (PR #87, 2019-10-25) cte: add data model, parser and more
- (PR #88, 2019-10-23) update config file for "deepsource"
- (PR #86, 2019-10-08) add config file for "deepsource"

## 0.8.1 (2019-09-25)

- (PR #83, 2019-09-12) rcv.parse_csv: remove whitespace from "razon social"

## 0.8.0 (2019-09-03)

- (PR #80, 2019-09-03) dte: Allow negative "monto total" when DTE type is "liquidación-factura
  electrónica"

## 0.7.4 (2019-08-08)

- (PR #76, 2019-08-01) dte: misc data models and enum improvements

## 0.7.3 (2019-07-09)

- (PR #74, 2019-07-09) requirements: update main packages

## 0.7.2 (2019-07-08)

- (PR #72, 2019-07-08) extras: Handle `str`-typed RUTs in Django `RutField.get_prep_value()`
- (PR #70, 2019-07-05) rut: Add less-than and greater-than methods
- (PR #71, 2019-07-05) rut: Strip leading zeros from RUTs
- (PR #69, 2019-07-02) libs.tz_utils: Fix setting of time zone information in datetimes
- (PR #68, 2019-06-27) requirements: update all those for 'release' and 'test'

## 0.7.1 (2019-06-20)

- (PR #66, 2019-06-20) rcv.parse_csv: detect invalid value of "razon social"

## 0.7.0 (2019-06-13)

- (PR #63, 2019-06-13) rcv.parse_csv: significant changes to parse functions
- (PR #62, 2019-06-13) libs: add module `io_utils`
- (PR #61, 2019-06-12) rcv: add data models, constants and more
- (PR #60, 2019-06-12) libs.tz_utils: misc
- (PR #59, 2019-05-31) rcv.parse_csv: add `parse_rcv_compra_X_csv_file`

## 0.6.5 (2019-05-29)

- (PR #57, 2019-05-29) libs.xml_utils: minor fix to `verify_xml_signature`

## 0.6.4 (2019-05-29)

- (PR #55, 2019-05-29) libs.xml_utils: add `verify_xml_signature`
- (PR #54, 2019-05-28) libs: add module `dataclass_utils`

## 0.6.3 (2019-05-24)

- (PR #52, 2019-05-24) rcv: add module `parse_csv`
- (PR #51, 2019-05-24) libs: add module `rows_processing`
- (PR #50, 2019-05-24) libs: add module `csv_utils`
- (PR #49, 2019-05-24) libs.mm_utils: add `validate_no_unexpected_input_fields`
- (PR #48, 2019-05-24) dte.data_models: add `DteDataL2.as_dte_data_l1`

## 0.6.2 (2019-05-15)

- (PR #45, 2019-05-15) libs.encoding_utils: improve `clean_base64`
- (PR #44, 2019-05-15) dte.parse: fix edge case in `parse_dte_xml`

## 0.6.1 (2019-05-08)

- (PR #40, 2019-05-08) dte.data_models: fix bug in `DteDataL2`

## 0.6.0 (2019-05-08)

Includes backwards-incompatible changes to data model `DteDataL2`.

- (PR #38, 2019-05-08) dte.data_models: alter field `DteDataL2.signature_x509_cert_pem`
- (PR #37, 2019-05-08) dte.data_models: alter field `DteDataL2.firma_documento_dt_naive`
- (PR #36, 2019-05-08) libs.crypto_utils: add functions
- (PR #35, 2019-05-07) libs.tz_utils: minor improvements
- (PR #34, 2019-05-06) docs: Fix `bumpversion` command

## 0.5.1 (2019-05-03)

- (PR #32, 2019-05-03) Requirements: updates and package upper-bounds

## 0.5.0 (2019-04-25)

- (PR #29, 2019-04-25) dte.data_models: modify new fields of `DteDataL2`
- (PR #28, 2019-04-25) libs: add module `crypto_utils`
- (PR #27, 2019-04-25) libs: add module `encoding_utils`
- (PR #26, 2019-04-25) test_data: add files
- (PR #25, 2019-04-25) libs.xml_utils: fix class alias `XmlElementTree`
- (PR #24, 2019-04-25) requirements: add and update packages
- (PR #22, 2019-04-24) test_data: add files
- (PR #21, 2019-04-22) dte: many improvements
- (PR #20, 2019-04-22) libs.xml_utils: misc improvements
- (PR #19, 2019-04-22) test_data: fix and add real SII DTE & AEC XML files
- (PR #18, 2019-04-22) data.ref: add XML schemas for "Cesion" (RTC)

## 0.4.0 (2019-04-16)

- (PR #16, 2019-04-16) dte.parse: change and improve `clean_dte_xml`
- (PR #14, 2019-04-09) data.ref: merge XML schemas dirs
- (PR #13, 2019-04-09) extras: add Marshmallow field for a DTE's "tipo DTE"

## 0.3.0 (2019-04-05)

- (PR #11, 2019-04-05) dte: add module `parse`
- (PR #10, 2019-04-05) dte: add module `data_models`
- (PR #9, 2019-04-05) libs: add module `xml_utils`
- (PR #8, 2019-04-05) add sub-package `rcv`

## 0.2.0 (2019-04-04)

- (PR #6, 2019-04-04) data.ref: add XML schemas of "factura electrónica"
- (PR #5, 2019-04-04) extras: add 'RutField' for Django models, DRF and MM
- (PR #4, 2019-04-04) Config CircleCI

## 0.1.0 (2019-04-04)

- (PR #2, 2019-04-04) Add class and constants for RUT
- (PR #1, 2019-04-04) Whole setup for a Python package/library
