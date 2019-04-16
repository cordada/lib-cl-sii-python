"""
cl_sii "extras" / Marshmallow fields.

(for serializers)

"""
try:
    import marshmallow
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'marshmallow' is required to use this module.") from exc

from typing import Optional

import marshmallow.fields

from cl_sii.dte.constants import TipoDteEnum
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

    default_error_messages = {
        'invalid': 'Not a syntactically valid RUT.'
    }

    def _serialize(self, value: Optional[object], attr: str, obj: object) -> Optional[str]:
        validated = self._validated(value)
        return validated.canonical if validated is not None else None

    def _deserialize(self, value: str, attr: str, data: dict) -> Optional[Rut]:
        return self._validated(value)

    def _validated(self, value: Optional[object]) -> Optional[Rut]:
        if value is None or isinstance(value, Rut):
            validated = value
        else:
            try:
                validated = Rut(value, validate_dv=False)  # type: ignore
            except TypeError:
                self.fail('type')
            except ValueError:
                self.fail('invalid')
        return validated


class TipoDteField(marshmallow.fields.Field):

    """
    Marshmallow field for a DTE's "tipo DTE".

    Data types:
    * native/primitive/internal/deserialized: :class:`TipoDteEnum`
    * representation/serialized: int, same as for Marshmallow field
      :class:`marshmallow.fields.Integer`

    The field performs some input value cleaning when it is an str;
    for example ``'  33 \t '`` is allowed and the resulting value
    is ``TipoDteEnum(33)``.

    Implementation almost identical to
    :class:`cl_sii.extras.mm_fields.RutField`.

    """

    default_error_messages = {
        'invalid': 'Not a valid Tipo DTE.'
    }

    def _serialize(self, value: Optional[object], attr: str, obj: object) -> Optional[int]:
        validated: Optional[TipoDteEnum] = self._validated(value)
        return validated.value if validated is not None else None

    def _deserialize(self, value: object, attr: str, data: dict) -> Optional[TipoDteEnum]:
        return self._validated(value)

    def _validated(self, value: Optional[object]) -> Optional[TipoDteEnum]:
        if value is None or isinstance(value, TipoDteEnum):
            validated = value
        else:
            if isinstance(value, bool):
                # is value is bool, `isinstance(value, int)` is True and `int(value)` works!
                self.fail('type')
            try:
                value = int(value)  # type: ignore
            except ValueError:
                # `int('x')` raises 'ValueError', not 'TypeError'
                self.fail('type')
            except TypeError:
                # `int(date(2018, 10, 10))` raises 'TypeError', unlike `int('x')`
                self.fail('type')

            try:
                validated = TipoDteEnum(value)  # type: ignore
            except ValueError:
                # TipoDteEnum('x') raises 'ValueError', not 'TypeError'
                self.fail('invalid')
        return validated
