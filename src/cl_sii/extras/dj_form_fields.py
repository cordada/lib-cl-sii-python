"""
cl_sii "extras" / Django form fields.

"""

try:
    import django
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'Django' is required to use this module.") from exc

from typing import Any, Optional

import django.core.exceptions
import django.forms
from django.utils.translation import gettext_lazy as _

from cl_sii.dte.constants import TipoDte
from cl_sii.extras.dj_model_fields import TipoDteChoices
from cl_sii.rut import Rut


class RutField(django.forms.CharField):
    """
    Django form field for RUT.

    * Python data type: :class:`cl_sii.rut.Rut`

    .. seealso::
        :class:`.dj_model_fields.RutField`

    """

    default_error_messages = {
        'invalid': _('Enter a valid RUT.'),
        'invalid_dv': _('RUT\'s "digito verificador" is incorrect.'),
    }

    def __init__(self, *, validate_dv: bool = False, **kwargs: Any) -> None:
        """
        :param validate_dv: Boolean that specifies whether to validate that
            the RUT's "digito verificador" is correct. False by default.
        """

        self.validate_dv = validate_dv
        super().__init__(strip=True, **kwargs)

    def to_python(self, value: Optional[object]) -> Optional[Rut]:
        """
        Validate that the input can be converted to a Python object (:class:`Rut`).

        :raises django.core.exceptions.ValidationError:
            if the input can't be converted
        """

        if value in self.empty_values:
            converted_value = None
        elif isinstance(value, Rut):
            converted_value = value
        else:
            try:
                converted_value = Rut(value)  # type: ignore[arg-type]
            except (AttributeError, TypeError, ValueError):
                raise django.core.exceptions.ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                )

        if (
            converted_value is not None
            and self.validate_dv
            and not converted_value.validate_dv(raise_exception=False)
        ):
            raise django.core.exceptions.ValidationError(
                self.error_messages['invalid_dv'],
                code='invalid_dv',
            )

        return converted_value


class TipoDteField(django.forms.TypedChoiceField):
    """
    Django form field for "Tipo de DTE".

    * Python data type: :class:`cl_sii.dte.constants.TipoDte`

    By default, the choices are all the members of :class:`TipoDte`, as in
    :data:`.dj_model_fields.TipoDteChoices`. A different set of choices can be
    set with the field option ``choices``; a value that is not among them is
    rejected.

    .. seealso::
        - :class:`.dj_model_fields.TipoDteField`
        - :class:`.drf_fields.TipoDteField`
        - :class:`.mm_fields.TipoDteField`
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault('choices', TipoDteChoices.choices)
        kwargs.setdefault('coerce', self._to_tipo_dte)
        kwargs.setdefault('empty_value', None)
        super().__init__(**kwargs)

    # note: before Python 3.11, `str()` of an `IntEnum` member is its name, not its value, which
    #   would make `ChoiceField` reject an instance of `TipoDte`, and the widget not select it.

    def prepare_value(self, value: Optional[object]) -> object:
        if isinstance(value, TipoDte):
            value = value.value
        return super().prepare_value(value)

    def to_python(self, value: Optional[object]) -> str:
        if isinstance(value, TipoDte):
            value = value.value
        converted_value: str = super().to_python(value)
        return converted_value

    @staticmethod
    def _to_tipo_dte(value: object) -> TipoDte:
        return TipoDte(int(value))  # type: ignore[call-overload]
