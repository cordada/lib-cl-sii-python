"""
cl_sii "extras" / Django REST Framework (DRF) fields.

(for serializers)

"""
try:
    import rest_framework
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'djangorestframework' is required to use this module.") from exc

import rest_framework.fields

from cl_sii.rut import Rut


class RutField(rest_framework.fields.CharField):

    """
    DRF field for RUT.

    Data types:
    * native/primitive/internal/deserialized: :class:`cl_sii.rut.Rut`
    * representation/serialized: str, same as for DRF field
      :class:`rest_framework.fields.CharField`

    It verifies only that the input is syntactically valid; it does NOT check
    that the value is within boundaries deemed acceptable by the SII.

    The field performs some input value cleaning when it is an str;
    for example ``' 1.111.111-k \t '`` is allowed and the resulting value
    is ``Rut('1111111-K')``.

    .. seealso::
        :class:`.dj_model_fields.RutField` and :class:`.mm_fields.RutField`

    Implementation partially inspired in
    :class:`rest_framework.fields.UUIDField`.

    """

    default_error_messages = {
        'invalid': "'{value}' is not a syntactically valid RUT.",
    }

    def to_internal_value(self, data: object) -> Rut:
        """
        Deserialize.

        > Restore a primitive datatype into its internal python representation.

        :raises rest_framework.exceptions.ValidationError:
            if the data can't be converted

        """
        if isinstance(data, Rut):
            converted_data = data
        else:
            try:
                if isinstance(data, str):
                    converted_data = Rut(data, validate_dv=False)
                else:
                    self.fail('invalid', value=data)
            except (AttributeError, TypeError, ValueError):
                self.fail('invalid', value=data)

        return converted_data

    def to_representation(self, value: Rut) -> str:
        """
        Serialize.

        > Convert the initial datatype into a primitive, serializable datatype.

        """
        return value.canonical
