"""
cl_sii "extras" / Django model fields.

"""

try:
    import django
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'Django' is required to use this module.") from exc

from typing import Any, ClassVar, Optional, Tuple

import django.core.exceptions
import django.core.validators
import django.db.models
import django.db.models.fields
import django.forms

import cl_sii.rut.constants
from cl_sii.base.constants import TipoDocumento
from cl_sii.dte.constants import DTE_FOLIO_FIELD_MAX_VALUE, DTE_FOLIO_FIELD_MIN_VALUE, TipoDte
from cl_sii.rcv.constants import RcvTipoDocto
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

    # TODO: implement method 'formfield'. Probably a copy of 'CharField.formfield' is fine.

    description = 'RUT for SII (Chile)'
    default_error_messages = {
        'invalid': "'%(value)s' is not a syntactically valid RUT.",
        'invalid_dv': "\"digito verificador\" of RUT '%(value)s' is incorrect.",
    }
    empty_strings_allowed = False
    validate_dv_by_default: ClassVar[bool] = False

    def __init__(
        self,
        verbose_name: Optional[str] = None,
        name: Optional[str] = None,
        validate_dv: bool = validate_dv_by_default,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.validate_dv = validate_dv

        # note: the value saved to the DB will always be in canonical format.
        db_column_max_length = cl_sii.rut.constants.RUT_CANONICAL_MAX_LENGTH

        # note: for some reason, even though the kwarg 'max_length' was not set explicitly in
        #   a model, some Django magic caused it was set automatically (perhaps consecutive calls
        #   or something like that?).
        if 'max_length' in kwargs and kwargs['max_length'] != db_column_max_length:
            raise ValueError("This field does not allow customization of 'max_length'.")

        kwargs['max_length'] = db_column_max_length
        super().__init__(verbose_name, name, *args, **kwargs)

    def deconstruct(self) -> Tuple[str, str, Any, Any]:
        """
        Return a 4-tuple with enough information to recreate the field.
        """
        # note: this override is necessary because we have a custom constructor.

        name, path, args, kwargs = super().deconstruct()

        if self.validate_dv != self.validate_dv_by_default:
            kwargs['validate_dv'] = self.validate_dv

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

    def get_prep_value(self, value: Optional[object]) -> Optional[str]:
        """
        Convert the model's attribute value to a format suitable for the DB.

        i.e. prepared for use as a parameter in a query.
        It is the reverse of :meth:`from_db_value`.

        However, these are preliminary non-DB specific value checks and
        conversions (otherwise customize :meth:`get_db_prep_value`).

        Note: Before returning, ``value`` will be passed to :meth:`to_python` so that, if needed, it
        will be converted to an instance of :class:`Rut`, which is very convenient in cases such
        as when the type of ``value`` is :class:`str`.
        """
        value = super().get_prep_value(value)
        value_rut: Optional[Rut] = self.to_python(value)
        return value_rut if value_rut is None else value_rut.canonical

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
        if value is None:
            converted_value = value
            return converted_value
        elif isinstance(value, Rut):
            if not self.validate_dv:
                converted_value = value
                return converted_value
            elif self.validate_dv and value.validate_dv(raise_exception=False):
                converted_value = value
                return converted_value

        try:
            converted_value = Rut(value, validate_dv=self.validate_dv)  # type: ignore
        except (AttributeError, TypeError, ValueError) as exc:
            if (
                isinstance(exc, ValueError)
                and exc.args
                and exc.args[0] == Rut.INVALID_DV_ERROR_MESSAGE
            ):
                raise django.core.exceptions.ValidationError(
                    self.error_messages['invalid_dv'],
                    code='invalid_dv',
                    params={'value': value},
                )

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


TipoDocumentoChoices = django.db.models.IntegerChoices(
    'TipoDocumentoChoices',
    names={
        tipo_doc.name: (  # Enum member name
            tipo_doc.value,  # Enum member value
            tipo_doc.name.replace('_', ' ').title(),  # Enum member display name
        )
        for tipo_doc in TipoDocumento
    },
)


class TipoDocumentoField(django.db.models.SmallIntegerField):
    """
    Django model field for "Tipo de Documento".

    * Python data type: :class:`cl_sii.base.constants.TipoDocumento`

    .. note::
        If the field's default `choices` is overridden, those custom `choices` will be
        used instead. In that case, it is the user's responsibility to ensure the
        validity of the choices.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if 'choices' not in kwargs:
            kwargs['choices'] = TipoDocumentoChoices.choices
        super().__init__(*args, **kwargs)


_TIPO_DTE_LABEL_LOWERCASE_WORDS = frozenset({'o', 'y', 'de', 'del', 'la', 'el', 'en'})


def _get_tipo_dte_label(tipo_dte: TipoDte) -> str:
    """
    Build the display name of a "Tipo de DTE" from its name and its code.

    Example: ``'Factura No Afecta o Exenta Electronica (34)'``
    """
    words = tipo_dte.name.replace('_', ' ').title().split(' ')
    words = [
        words[0],
        *(
            word.lower() if word.lower() in _TIPO_DTE_LABEL_LOWERCASE_WORDS else word
            for word in words[1:]
        ),
    ]
    return f"{' '.join(words)} ({tipo_dte.value})"


TipoDteChoices = django.db.models.IntegerChoices(
    'TipoDteChoices',
    names={
        tipo_dte.name: (  # Enum member name
            tipo_dte.value,  # Enum member value
            _get_tipo_dte_label(tipo_dte),  # Enum member display name
        )
        for tipo_dte in TipoDte
    },
)


class TipoDteField(django.db.models.SmallIntegerField):
    """
    Django model field for "Tipo de DTE".

    * Python data type: :class:`cl_sii.dte.constants.TipoDte`, or :class:`int` for a
      code that is not a member of :class:`cl_sii.dte.constants.TipoDte` (e.g. one that
      the SII adds after this version of the library), so that reading it does not fail.

    .. note::
        If the field's default `choices` is overridden, those custom `choices` will be
        used instead. In that case, it is the user's responsibility to ensure the
        validity of the choices.

    .. seealso::
        :class:`.dj_form_fields.TipoDteField`
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if 'choices' not in kwargs:
            kwargs['choices'] = TipoDteChoices.choices
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs: Any) -> django.forms.Field:
        # note: imported here because module `dj_form_fields` imports this module.
        import cl_sii.extras.dj_form_fields

        return super().formfield(
            **{
                'choices_form_class': cl_sii.extras.dj_form_fields.TipoDteField,
                **kwargs,
            }
        )

    def from_db_value(
        self,
        value: Optional[int],
        expression: object,
        connection: object,
    ) -> TipoDte | int | None:
        """
        Convert a value as returned by the database to a Python object.

        .. seealso::
            :meth:`to_python`
        """
        return self.to_python(value)

    def to_python(self, value: Optional[object]) -> TipoDte | int | None:
        """
        Convert the input value to a :class:`TipoDte`.

        A code that is not a member of :class:`TipoDte` is returned as an :class:`int`.

        :raises django.core.exceptions.ValidationError:
            if the value can't be converted to an integer
        """
        converted_value: Optional[int] = super().to_python(value)

        if converted_value is None:
            return None

        try:
            return TipoDte(converted_value)
        except ValueError:
            return converted_value

    def value_from_object(self, obj: django.db.models.Model) -> Optional[int]:
        """
        Return the value of this field in model instance ``obj``, as a plain :class:`int`.

        It is the value that Django's serializers (e.g. ``dumpdata``) and model forms use.
        A :class:`TipoDte` would be written as its name by the XML serializer before
        Python 3.11, and could not be written at all by the YAML serializer.
        """
        value: Optional[int] = super().value_from_object(obj)
        return value if value is None else int(value)


RcvTipoDoctoChoices = django.db.models.IntegerChoices(
    'RcvTipoDoctoChoices',
    names={
        tipo_doc.name: (  # Enum member name
            tipo_doc.value,  # Enum member value
            tipo_doc.name.replace('_', ' ').title(),  # Enum member display name
        )
        for tipo_doc in RcvTipoDocto
    },
)


class RcvTipoDoctoField(django.db.models.SmallIntegerField):
    """
    Django model field for "Tipo de Documento" for the RCV domain.

    * Python data type: :class:`cl_sii.rcv.constants.RcvTipoDocto`

    .. note::
        If the field's default `choices` is overridden, those custom `choices` will be
        used instead. In that case, it is the user's responsibility to ensure the
        validity of the choices.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if 'choices' not in kwargs:
            kwargs['choices'] = RcvTipoDoctoChoices.choices
        super().__init__(*args, **kwargs)


class DteFolioField(django.db.models.BigIntegerField):
    """
    Django model field for a DTE's "folio".

    * Python data type: :class:`int`
    * DB type: ``bigint``, the same one as the one for model field
      :class:`django.db.models.BigIntegerField`

    The value must be within the range of valid values for a DTE's "folio",
    i.e. between :data:`cl_sii.dte.constants.DTE_FOLIO_FIELD_MIN_VALUE` and
    :data:`cl_sii.dte.constants.DTE_FOLIO_FIELD_MAX_VALUE`. The range is
    enforced by validators (e.g. in :meth:`django.db.models.Model.full_clean`,
    forms and serializers), not by a database constraint.

    .. seealso::
        :class:`.drf_fields.DteFolioField`, :class:`.mm_fields.DteFolioField`
        and :data:`.pydantic_types.DteFolio`
    """

    description = 'DTE folio for SII (Chile)'
    default_validators = [
        django.core.validators.MinValueValidator(DTE_FOLIO_FIELD_MIN_VALUE),
        django.core.validators.MaxValueValidator(DTE_FOLIO_FIELD_MAX_VALUE),
    ]

    def formfield(self, **kwargs: Any) -> django.forms.Field:
        return super().formfield(
            **{
                'min_value': DTE_FOLIO_FIELD_MIN_VALUE,
                'max_value': DTE_FOLIO_FIELD_MAX_VALUE,
                **kwargs,
            }
        )
