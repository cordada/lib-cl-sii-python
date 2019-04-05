from datetime import date, datetime
from typing import Any, Union

import marshmallow
import marshmallow.fields
import marshmallow.utils


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

    def __init__(self, format: str = None, **kwargs: Any) -> None:
        """Constructor.

        :param format: Either ``"iso"`` (for ISO-8601) or a date format str.
            If `None`, defaults to "iso".
        :param kwargs: the same ones that :class:`Field` receives.

        """
        super().__init__(**kwargs)
        # Allow this to be None. It may be set later in the ``_serialize``
        # or ``_desrialize`` methods This allows a Schema to dynamically set the
        # dateformat, e.g. from a Meta option
        self.dateformat = format

    def _add_to_schema(self, field_name: str, schema: marshmallow.Schema) -> None:
        super()._add_to_schema(field_name, schema)
        self.dateformat = self.dateformat or schema.opts.dateformat

    def _serialize(self, value: date, attr: str, obj: object) -> Union[str, None]:
        if value is None:
            return None
        self.dateformat = self.dateformat or self.DEFAULT_FORMAT
        format_func = self.DATEFORMAT_SERIALIZATION_FUNCS.get(self.dateformat, None)
        if format_func:
            try:
                date_str = format_func(value)
            except (AttributeError, ValueError):
                self.fail('format', input=value)
        else:
            date_str = value.strftime(self.dateformat)

        return date_str

    def _deserialize(self, value: str, attr: str, data: dict) -> date:
        if not value:  # Falsy values, e.g. '', None, [] are not valid
            self.fail('invalid')
        self.dateformat = self.dateformat or self.DEFAULT_FORMAT
        func = self.DATEFORMAT_DESERIALIZATION_FUNCS.get(self.dateformat)
        if func:
            try:
                date_value = func(value)  # type: date
            except (TypeError, AttributeError, ValueError):
                self.fail('invalid')
        elif self.dateformat:
            try:
                date_value = datetime.strptime(value, self.dateformat).date()
            except (TypeError, AttributeError, ValueError):
                self.fail('invalid')
        else:
            self.fail('invalid')

        return date_value
