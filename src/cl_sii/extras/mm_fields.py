"""
cl_sii "extras" / Marshmallow fields.

(for serializers)

"""

from __future__ import annotations


try:
    import marshmallow
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'marshmallow' is required to use this module.") from exc

import datetime
import decimal
import numbers
from typing import Any, ClassVar, Mapping, Optional

import marshmallow.fields
import marshmallow.validate

from cl_sii.dte.constants import DTE_FOLIO_FIELD_MAX_VALUE, DTE_FOLIO_FIELD_MIN_VALUE, TipoDte
from cl_sii.rcv.constants import RcvTipoDocto
from cl_sii.rcv.data_models import PeriodoTributario as RcvPeriodoTributario
from cl_sii.rut import Rut


class RutField(marshmallow.fields.Field):
    """
    Marshmallow field for RUT.

    Data types:
    * native/primitive/internal/deserialized: :class:`cl_sii.rut.Rut`
    * representation/serialized: str, same as for Marshmallow field
      :class:`marshmallow.fields.String`

    It verifies only that the input is syntactically valid; it does NOT check
    that the value is within boundaries deemed acceptable by the SII.

    The field performs some input value cleaning when it is an str;
    for example ``' 1.111.111-k \t '`` is allowed and the resulting value
    is ``Rut('1111111-K')``.

    .. seealso::
        :class:`.dj_model_fields.RutField` and :class:`.drf_fields.RutField`

    Implementation partially inspired in :class:`marshmallow.fields.UUID`.

    """

    validate_dv: bool
    validate_dv_by_default: ClassVar[bool] = False

    default_error_messages = {
        'invalid': 'Not a syntactically valid RUT.',
        'invalid_dv': """RUT's "digito verificador" is incorrect.""",
        'type': 'Invalid type.',
    }

    def __init__(
        self,
        *,
        validate_dv: bool = validate_dv_by_default,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.validate_dv = validate_dv

    def _serialize(
        self, value: Optional[object], attr: str | None, obj: object, **kwargs: Any
    ) -> Optional[str]:
        validated = self._validated(value)
        return validated.canonical if validated is not None else None

    def _deserialize(
        self, value: str, attr: str | None, data: Mapping[str, Any] | None, **kwargs: Any
    ) -> Optional[Rut]:
        return self._validated(value)

    def _validated(self, value: Optional[object]) -> Optional[Rut]:
        if value is None or isinstance(value, Rut):
            validated = value
        else:
            try:
                validated = Rut(value, validate_dv=False)  # type: ignore
            except TypeError as exc:
                raise self.make_error('type') from exc
            except ValueError as exc:
                raise self.make_error('invalid') from exc

        if self.validate_dv and validated is not None:
            try:
                validated.validate_dv(raise_exception=True)
            except ValueError as exc:
                raise self.make_error('invalid_dv') from exc

        return validated


class TipoDteField(marshmallow.fields.Field):
    """
    Marshmallow field for a DTE's "tipo DTE".

    Data types:
    * native/primitive/internal/deserialized: :class:`TipoDte`
    * representation/serialized: int, same as for Marshmallow field
      :class:`marshmallow.fields.Integer`

    The field performs some input value cleaning when it is an str;
    for example ``'  33 \t '`` is allowed and the resulting value
    is ``TipoDte(33)``.

    Implementation almost identical to
    :class:`cl_sii.extras.mm_fields.RutField`.

    """

    default_error_messages = {
        'invalid': 'Not a valid Tipo DTE.',
        'type': 'Invalid type.',
    }

    def _serialize(
        self, value: Optional[object], attr: str | None, obj: object, **kwargs: Any
    ) -> Optional[int]:
        validated: Optional[TipoDte] = self._validated(value)
        return validated.value if validated is not None else None

    def _deserialize(
        self, value: object, attr: str | None, data: Mapping[str, Any] | None, **kwargs: Any
    ) -> Optional[TipoDte]:
        return self._validated(value)

    def _validated(self, value: Optional[object]) -> Optional[TipoDte]:
        if value is None or isinstance(value, TipoDte):
            validated = value
        else:
            if isinstance(value, bool):
                # is value is bool, `isinstance(value, int)` is True and `int(value)` works!
                raise self.make_error('type')
            try:
                value = int(value)  # type: ignore
            except ValueError as exc:
                # `int('x')` raises 'ValueError', not 'TypeError'
                raise self.make_error('type') from exc
            except TypeError as exc:
                # `int(date(2018, 10, 10))` raises 'TypeError', unlike `int('x')`
                raise self.make_error('type') from exc

            try:
                validated = TipoDte(value)  # type: ignore
            except ValueError as exc:
                # TipoDte('x') raises 'ValueError', not 'TypeError'
                raise self.make_error('invalid') from exc
        return validated


class RcvTipoDoctoField(marshmallow.fields.Field):
    """
    Marshmallow field for RCV's "tipo documento".

    Data types:
    * native/primitive/internal/deserialized: :class:`RcvTipoDocto`
    * representation/serialized: int, same as for Marshmallow field
      :class:`marshmallow.fields.Integer`

    The field performs some input value cleaning when it is an str;
    for example ``'  33 \t '`` is allowed and the resulting value
    is ``RcvTipoDocto(33)``.

    Implementation almost identical to :class:`TipoDteField`.

    """

    default_error_messages = {
        'invalid': "Not a valid RCV's Tipo de Documento.",
        'type': "Invalid type.",
    }

    def _serialize(
        self, value: Optional[object], attr: str | None, obj: object, **kwargs: Any
    ) -> Optional[int]:
        validated: Optional[RcvTipoDocto] = self._validated(value)
        return validated.value if validated is not None else None

    def _deserialize(
        self, value: object, attr: str | None, data: Mapping[str, Any] | None, **kwargs: Any
    ) -> Optional[RcvTipoDocto]:
        return self._validated(value)

    def _validated(self, value: Optional[object]) -> Optional[RcvTipoDocto]:
        if value is None or isinstance(value, RcvTipoDocto):
            validated = value
        else:
            if isinstance(value, bool):
                # is value is bool, `isinstance(value, int)` is True and `int(value)` works!
                raise self.make_error('type')
            try:
                value = int(value)  # type: ignore
            except ValueError as exc:
                # `int('x')` raises 'ValueError', not 'TypeError'
                raise self.make_error('type') from exc
            except TypeError as exc:
                # `int(date(2018, 10, 10))` raises 'TypeError', unlike `int('x')`
                raise self.make_error('type') from exc

            try:
                validated = RcvTipoDocto(value)  # type: ignore
            except ValueError as exc:
                # RcvTipoDocto('x') raises 'ValueError', not 'TypeError'
                raise self.make_error('invalid') from exc
        return validated


class RcvPeriodoTributarioField(marshmallow.fields.Field):
    """
    Marshmallow field for RCV's "periodo tributario".

    Data types:
    * native/primitive/internal/deserialized: :class:`RcvPeriodoTributario`
    * representation/serialized: str
    """

    default_error_messages = {
        'invalid': "Not a valid RCV Periodo Tributario.",
        'type': "Invalid type.",
    }
    _string_format = '%Y-%m'  # Example: '2019-12'

    def _serialize(
        self, value: Optional[object], attr: str | None, obj: object, **kwargs: Any
    ) -> Optional[str]:
        validated: Optional[RcvPeriodoTributario] = self._validated(value)
        return validated.as_date().strftime(self._string_format) if validated is not None else None

    def _deserialize(
        self, value: object, attr: str | None, data: Mapping[str, Any] | None, **kwargs: Any
    ) -> Optional[RcvPeriodoTributario]:
        return self._validated(value)

    def _validated(self, value: Optional[object]) -> Optional[RcvPeriodoTributario]:
        if value is None or isinstance(value, RcvPeriodoTributario):
            validated = value
        else:
            try:
                value = datetime.datetime.strptime(value, self._string_format)  # type: ignore
                value = value.date()
            except ValueError as exc:
                raise self.make_error('invalid') from exc
            except TypeError as exc:
                raise self.make_error('type') from exc

            validated = RcvPeriodoTributario.from_date(value)

        return validated


class DteFolioField(marshmallow.fields.Integer):
    """
    Marshmallow field for a DTE's "folio".

    Data types:
    * native/primitive/internal/deserialized: :class:`int`
    * representation/serialized: int, same as for Marshmallow field
      :class:`marshmallow.fields.Integer`

    By default, the value must be within the range of valid values for a
    DTE's "folio", i.e. between
    :data:`cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE` and
    :data:`cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE`. A different range
    can be set with the field options ``min_value`` and ``max_value``.

    Unlike :class:`marshmallow.fields.Integer`, which truncates a number with
    a fractional part (e.g. ``1.5`` becomes ``1``), this field rejects it.
    A number without a fractional part (e.g. ``1.0``) and a string (e.g.
    ``'1'``) are accepted, unless the field option ``strict`` is enabled.

    The field's metadata includes ``format`` ``int64``, because the range of
    valid values exceeds that of a 32-bit integer.

    .. seealso::
        :class:`.dj_model_fields.DteFolioField`, :class:`.drf_fields.DteFolioField`
        and :data:`.pydantic_types.DteFolio`
    """

    def __init__(
        self,
        *,
        min_value: int = DTE_FOLIO_FIELD_MIN_VALUE,
        max_value: int = DTE_FOLIO_FIELD_MAX_VALUE,
        **kwargs: Any,
    ) -> None:
        validators: list[Any] = [marshmallow.validate.Range(min=min_value, max=max_value)]
        validate = kwargs.pop('validate', None)
        if callable(validate):
            validators.append(validate)
        elif validate is not None:
            validators.extend(validate)

        metadata = {'format': 'int64', **(kwargs.pop('metadata', None) or {})}

        super().__init__(validate=validators, metadata=metadata, **kwargs)

    def _deserialize(
        self, value: Any, attr: str | None, data: Mapping[str, Any] | None, **kwargs: Any
    ) -> int:
        if isinstance(value, numbers.Number) and not isinstance(value, numbers.Integral):
            try:
                is_integral_value = value == int(value)  # type: ignore[call-overload]
            except (TypeError, ValueError, OverflowError, decimal.InvalidOperation) as exc:
                raise self.make_error('invalid', input=value) from exc
            if not is_integral_value:
                raise self.make_error('invalid', input=value)

        return super()._deserialize(value, attr, data, **kwargs)
