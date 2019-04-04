"""
cl_sii "extras" / Django model fields.

"""
try:
    import django
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'Django' is required to use this module.") from exc

from typing import Any, Optional, Tuple

import django.core.exceptions
import django.db.models
import django.db.models.fields

import cl_sii.rut.constants
from cl_sii.rut import Rut


class RutField(django.db.models.Field):

    """
    Django model field for RUT.

    * Python data type: :class:`cl_sii.rut.Rut`
    * DB type: ``varchar``, the same one as the one for model field
      :class:`django.db.models.CharField`

    It verifies only that the input is syntactically valid; it does NOT check
    that the value is within boundaries deemed acceptable by the SII.

    The field performs some input value cleaning when it is an str;
    for example ``' 1.111.111-k \t '`` is allowed and the resulting value
    is ``Rut('1111111-K')``.

    .. seealso::
        :class:`.drf_fields.RutField` and :class:`.mm_fields.RutField`

    Implementation partially inspired in
    :class:`django.db.models.fields.UUIDField`.

    """

    # TODO: add option to validate that "digito verificador" is correct.
    # TODO: implement method 'formfield'. Probably a copy of 'CharField.formfield' is fine.

    description = 'RUT for SII (Chile)'
    default_error_messages = {
        'invalid': "'%(value)s' is not a syntactically valid RUT.",
        'invalid_dv': "\"digito verificador\" of RUT '%(value)s' is incorrect.",
    }
    empty_strings_allowed = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # note: the value saved to the DB will always be in canonical format.
        db_column_max_length = cl_sii.rut.constants.RUT_CANONICAL_MAX_LENGTH

        # note: for some reason, even though the kwarg 'max_length' was not set explicitly in
        #   a model, some Django magic caused it was set automatically (perhaps consecutive calls
        #   or something like that?).
        if 'max_length' in kwargs and kwargs['max_length'] != db_column_max_length:
            raise ValueError("This field does not allow customization of 'max_length'.")

        kwargs['max_length'] = db_column_max_length
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> Tuple[str, str, Any, Any]:
        """
        Return a 4-tuple with enough information to recreate the field.
        """
        # note: this override is necessary because we have a custom constructor.

        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']

        return name, path, args, kwargs

    def get_internal_type(self) -> str:
        # Emulate built-in model field type 'CharField' i.e. the underlying DB type is the same.
        #   https://docs.djangoproject.com/en/2.1/howto/custom-model-fields/#emulating-built-in-field-types
        return 'CharField'

    def from_db_value(
        self,
        value: Optional[str],
        expression: object,
        connection: object,
    ) -> Optional[Rut]:
        """
        Convert a value as returned by the database to a Python object.

        > It is the reverse of :meth:`get_prep_value`.

        > If present for the field subclass, :meth:`from_db_value` will be
        > called in all circumstances when the data is loaded from the
        > database, including in aggregates and ``values()`` calls.

        It needs to be able to process ``None``.

        .. seealso::
            https://docs.djangoproject.com/en/2.1/howto/custom-model-fields/#converting-values-to-python-objects
            https://docs.djangoproject.com/en/2.1/ref/models/fields/#django.db.models.Field.from_db_value

        """
        # note: there is no parent implementation, for performance reasons.
        return self.to_python(value)

    def get_prep_value(self, value: Optional[Rut]) -> Optional[str]:
        """
        Convert the model's attribute value to a format suitable for the DB.

        i.e. prepared for use as a parameter in a query.
        It is the reverse of :meth:`from_db_value`.

        However, these are preliminary non-DB specific value checks and
        conversions (otherwise customize :meth:`get_db_prep_value`).

        """
        value = super().get_prep_value(value)
        return value if value is None else value.canonical

    def to_python(self, value: Optional[object]) -> Optional[Rut]:
        """
        Convert the input value to the correct Python object (:class:`Rut`).

        > It acts as the reverse of :meth:`value_to_string`, and is also
        called in :meth`clean`.

        It needs to be able to process ``None``.

        .. seealso::
            https://docs.djangoproject.com/en/2.1/howto/custom-model-fields/#converting-values-to-python-objects
            https://docs.djangoproject.com/en/2.1/ref/models/fields/#django.db.models.Field.to_python

        :raises django.core.exceptions.ValidationError:
            if the data can't be converted

        """
        if value is None or isinstance(value, Rut):
            converted_value = value
        else:
            try:
                converted_value = Rut(value, validate_dv=False)  # type: ignore
            except (AttributeError, TypeError, ValueError):
                raise django.core.exceptions.ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value},
                )

        return converted_value

    def value_to_string(self, obj: django.db.models.Model) -> str:
        """
        Convert to a string the field value of model instance``obj``.

        Used to serialize the value of the field.

        .. seealso::
            https://docs.djangoproject.com/en/2.1/howto/custom-model-fields/#converting-field-data-for-serialization

        """
        # note: according to official docs, 'value_from_object' is the
        #   "best way to get the field's value prior to serialization".
        value: Optional[Rut] = self.value_from_object(obj)

        return '' if value is None else value.canonical
