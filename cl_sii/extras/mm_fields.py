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
