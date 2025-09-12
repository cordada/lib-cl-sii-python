from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Optional

import pydantic


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        extra='forbid',
    ),
)
class TaxpayerProvidedInfo:
    """
    Información proporcionada por el contribuyente para fines tributarios (1)
    """

    legal_representatives: Sequence[LegalRepresentative]
    company_formation: Sequence[LegalRepresentative]
    participation_in_existing_companies: Sequence[LegalRepresentative]


@pydantic.dataclasses.dataclass(
    frozen=True,
)
class LegalRepresentative:
    name: str
    """
    Nombre o Razón social.
    """
    rut: str
    """
    RUT.
    """
    incorporation_date: str
    """
    Fecha de incorporación.
    """


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        extra='forbid',
    ),
)
class TaxpayerData:
    start_of_activities_date: Optional[date]
    """
    Fecha de inicio de actividades.
    """
    economic_activities: str
    """
    Actividades Económicas
    """
    tax_category: str
    """
    Categoría Tributaria
    """
    address: str
    """
    Domicilio
    """
    branches: Sequence[str]
    """
    Sucursales
    """
    last_filed_documents: Sequence[LastFiledDocument]
    """
    Últimos documentos timbrados
    """
    tax_observations: Optional[str] = None
    """
    Observaciones tributarias
    """


@pydantic.dataclasses.dataclass(
    frozen=True,
)
class LastFiledDocument:
    name: str
    date: date
