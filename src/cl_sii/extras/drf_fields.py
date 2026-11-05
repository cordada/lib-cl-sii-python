"""
cl_sii "extras" / Django REST Framework (DRF) fields.

(for serializers)

"""

try:
    import rest_framework
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'djangorestframework' is required to use this module.") from exc

from typing import Any, ClassVar

import rest_framework.fields

import cl_sii.dte.constants
from cl_sii.dte.constants import TipoDte
from cl_sii.extras.dj_model_fields import TipoDteChoices
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

    validate_dv: bool
    validate_dv_by_default: ClassVar[bool] = False

    default_error_messages = {
        'invalid': "'{value}' is not a syntactically valid RUT.",
        'invalid_dv': '''"digito verificador" of RUT '{value}' is incorrect.''',
    }

    def __init__(
        self,
        *,
        validate_dv: bool = validate_dv_by_default,
        **kwargs: Any,
    ) -> None:
        self.validate_dv = validate_dv

        super().__init__(**kwargs)

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

        if self.validate_dv and not converted_data.validate_dv(raise_exception=False):
            self.fail('invalid_dv', value=data)

        return converted_data

    def to_representation(self, value: Rut) -> str:
        """
        Serialize.

        > Convert the initial datatype into a primitive, serializable datatype.

        """
        return value.canonical


class TipoDteField(rest_framework.fields.ChoiceField):
    """
    DRF field for "Tipo de DTE".

    Data types:
    * native/primitive/internal/deserialized: :class:`cl_sii.dte.constants.TipoDte`
    * representation/serialized: int, the value of the :class:`TipoDte` member

    By default, the choices are all the members of :class:`TipoDte`, as in
    :data:`.dj_model_fields.TipoDteChoices`. A different set of choices can be
    set with the field option ``choices``; a value that is not among them is
    rejected, and so is a choice that is not a member of :class:`TipoDte`.

    As for DRF field :class:`rest_framework.fields.ChoiceField`, the input can
    be an int or its str; for example ``33`` and ``'33'`` are allowed and the
    resulting value is ``TipoDte(33)``.

    .. seealso::
        - :class:`.dj_form_fields.TipoDteField`
        - :class:`.dj_model_fields.TipoDteField`
        - :class:`.mm_fields.TipoDteField`
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault('choices', TipoDteChoices.choices)
        super().__init__(**kwargs)

    def to_internal_value(self, data: object) -> TipoDte:
        """
        Deserialize.

        > Restore a primitive datatype into its internal python representation.

        :raises rest_framework.exceptions.ValidationError:
            if the data can't be converted
        """
        if isinstance(data, TipoDte):
            data = data.value
        value = super().to_internal_value(data)
        try:
            converted_data = TipoDte(value)
        except ValueError:
            self.fail('invalid_choice', input=data)

        return converted_data

    def to_representation(self, value: TipoDte | int) -> int:
        """
        Serialize.

        > Convert the initial datatype into a primitive, serializable datatype.
        """
        return int(value)


class DteFolioField(rest_framework.fields.IntegerField):
    """
    DRF field for a DTE's "folio".

    Data types:
    * native/primitive/internal/deserialized: :class:`int`
    * representation/serialized: int, same as for DRF field
      :class:`rest_framework.fields.IntegerField`

    By default, the value must be within the range of valid values for a
    DTE's "folio", i.e. between
    :data:`cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE` and
    :data:`cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE`. A different range
    can be set with the field options ``min_value`` and ``max_value``.

    .. note::
        OpenAPI schema generators, such as DRF's (as of version 3.16) and
        drf-spectacular's, declare format ``int64`` for an integer field whose
        range exceeds that of a 32-bit integer, as this field's default range
        does.

    .. seealso::
        :class:`.dj_model_fields.DteFolioField`, :class:`.mm_fields.DteFolioField`
        and :data:`.pydantic_types.DteFolio`
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault('min_value', cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE)
        kwargs.setdefault('max_value', cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE)
        super().__init__(**kwargs)
