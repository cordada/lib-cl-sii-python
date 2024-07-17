"""
cl_sii "extras" / Django URL converters.
"""

from __future__ import annotations

from typing import ClassVar

import cl_sii.dte.constants
import cl_sii.rut


class RutConverter:
    """
    Django URL path converter for Chilean RUT.

    Thousands separators are not supported.

    Example:

    >>> from django.urls import path, register_converter
    >>> register_converter(RutConverter, 'cl_sii_rut')
    >>> urlpatterns = [path('example/<cl_sii_rut:emisor_rut>/', ...)]

    .. seealso::
        https://docs.djangoproject.com/en/4.2/topics/http/urls/#registering-custom-path-converters
    """

    regex: ClassVar[str] = r'\d{1,8}-[\dKk]'

    def to_python(self, value: str) -> cl_sii.rut.Rut:
        return cl_sii.rut.Rut(value)

    def to_url(self, value: cl_sii.rut.Rut) -> str:
        return str(value)


class TipoDteConverter:
    """
    Django URL path converter for `Tipo DTE` object.

    Example:

    >>> from django.urls import path, register_converter
    >>> register_converter(TipoDteConverter, 'cl_sii_tipo_dte')
    >>> urlpatterns = [path('example/<cl_sii_tipo_dte:tipo_dte>/', ...)]

    .. seealso::
        https://docs.djangoproject.com/en/4.2/topics/http/urls/#registering-custom-path-converters
    """

    regex: ClassVar[str] = r'\d{2,3}'

    def to_python(self, value: str) -> cl_sii.dte.constants.TipoDte:
        return cl_sii.dte.constants.TipoDte(int(value))

    def to_url(self, value: cl_sii.dte.constants.TipoDte) -> str:
        return str(value.value)
