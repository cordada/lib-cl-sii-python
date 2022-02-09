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
            and Rut.calc_dv(converted_value.digits) != converted_value.dv
        ):
            raise django.core.exceptions.ValidationError(
                self.error_messages['invalid_dv'],
                code='invalid_dv',
            )

        return converted_value
