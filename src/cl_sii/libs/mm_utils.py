from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping, Optional, Union

import marshmallow
import marshmallow.fields
import marshmallow.utils


###############################################################################
# validators
###############################################################################


def validate_no_unexpected_input_fields(
    schema: marshmallow.Schema,
    data: dict,
    original_data: dict,
) -> None:
    """
    Fail validation if there was an unexpected input field.

    Usage::

        class MySchema(marshmallow.Schema):
            folio = marshmallow.fields.Integer()

            @marshmallow.validates_schema(pass_original=True)
            def validate_schema(self, data: dict, original_data: dict) -> None:
                validate_no_unexpected_input_fields(self, data, original_data)

    """
    # Original inspiration from
    #   https://marshmallow.readthedocs.io/en/2.x-line/extending.html#validating-original-input-data
    fields_name_or_load_from = {
        field.name if field.data_key is None else field.data_key
        for field_key, field in schema.fields.items()
    }
    unexpected_input_fields = set(original_data) - fields_name_or_load_from
    if unexpected_input_fields:
        raise marshmallow.ValidationError(
            "Unexpected input field.", field_names=list(unexpected_input_fields)
        )


###############################################################################
# fields
###############################################################################


class CustomMarshmallowDateField(marshmallow.fields.Field):
    """
    A formatted date string.

    Customizated alternative to :class:`marshmallow.fields.Date` that allows
    setting a date format string (like :class:`marshmallow.fields.DateTime`
    does).

    Implementation largely based on ``marshmallow`` version 2.16.3, classes
    :class:`marshmallow.fields.Date` and :class:`marshmallow.fields.DateTime`.

    """

    # note: function's return type must be 'str'.
    DATEFORMAT_SERIALIZATION_FUNCS = {
        'iso': date.isoformat,
        'iso8601': date.isoformat,
    }

    # note: function's return type must be 'datetime.date'.
    DATEFORMAT_DESERIALIZATION_FUNCS = {
        'iso': marshmallow.utils.from_iso_date,
        'iso8601': marshmallow.utils.from_iso_date,
    }

    DEFAULT_FORMAT = 'iso'

    default_error_messages = {
        'invalid': 'Not a valid date.',
        'format': '"{input}" cannot be formatted as a date.',
    }

    def __init__(self, format: Optional[str] = None, **kwargs: Any) -> None:
        """Constructor.

        :param format: Either ``"iso"`` (for ISO-8601) or a date format str.
            If `None`, defaults to "iso".
        :param kwargs: the same ones that :class:`Field` receives.

        """
        super().__init__(**kwargs)
        # Allow this to be None. It may be set later in the ``_serialize``
        # or ``_deserialize`` methods This allows a Schema to dynamically set the
        # dateformat, e.g. from a Meta option
        # TODO: for 'marshmallow 3', rename 'dateformat' to 'datetimeformat'.
        self.dateformat = format

    def _bind_to_schema(
        self, field_name: str, schema: marshmallow.Schema | marshmallow.Field
    ) -> None:
        super()._bind_to_schema(field_name, schema)
        self.dateformat = self.dateformat or schema.opts.dateformat

    def _serialize(
        self, value: date, attr: str | None, obj: object, **kwargs: Any
    ) -> Union[str, None]:
        if value is None:
            return None
        self.dateformat = self.dateformat or self.DEFAULT_FORMAT
        format_func = self.DATEFORMAT_SERIALIZATION_FUNCS.get(self.dateformat, None)
        if format_func:
            try:
                date_str = format_func(value)
            except (AttributeError, ValueError) as exc:
                raise self.make_error('format', input=value) from exc
        else:
            date_str = value.strftime(self.dateformat)

        return date_str

    def _deserialize(
        self, value: str, attr: str | None, data: Mapping[str, Any] | None, **kwargs: Any
    ) -> date:
        if not value:  # Falsy values, e.g. '', None, [] are not valid
            raise self.make_error('invalid')
        self.dateformat = self.dateformat or self.DEFAULT_FORMAT
        func = self.DATEFORMAT_DESERIALIZATION_FUNCS.get(self.dateformat)
        if func:
            try:
                date_value = func(value)  # type: date
            except (TypeError, AttributeError, ValueError) as exc:
                raise self.make_error('invalid') from exc
        elif self.dateformat:
            try:
                date_value = datetime.strptime(value, self.dateformat).date()
            except (TypeError, AttributeError, ValueError) as exc:
                raise self.make_error('invalid') from exc
        else:
            raise self.make_error('invalid')

        return date_value
