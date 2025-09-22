from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from decimal import Decimal
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


@pydantic.dataclasses.dataclass(
    frozen=True,
    config=pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        extra='forbid',
    ),
)
class TaxpayerProperties:
    """
    Propiedades y Bienes Raíces (3)
    """

    properties: Sequence[Property]


@pydantic.dataclasses.dataclass(
    frozen=True,
)
class Property:
    commune: Optional[str]
    """
    Comuna
    """
    role: Optional[str]
    """
    Rol
    """
    address: Optional[str]
    """
    Dirección
    """
    purpose: Optional[str]
    """
    Destino
    """
    fiscal_valuation: Optional[Decimal]
    """
    Avalúo Fiscal
    """
    overdue_installments: Optional[bool]
    """
    Cuotas vencidas por pagar
    """
    current_installments: Optional[bool]
    """
    Cuotas vigentes por pagar
    """
    condition: Optional[str]
    """
    Condición
    """

    ###########################################################################
    # Validators
    ###########################################################################

    @pydantic.field_validator('fiscal_valuation', mode='before')
    @classmethod
    def parse_fiscal_valuation(cls, v: Optional[str]) -> Optional[Decimal]:
        if isinstance(v, str):
            v = v.replace('.', '').replace(',', '.')
            return Decimal(v)
        return v

    @pydantic.field_validator('commune', 'role', 'address', 'purpose', 'condition')
    @classmethod
    def parse_str_fields(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @pydantic.field_validator('current_installments', 'overdue_installments', mode='before')
    @classmethod
    def parse_boolean_fields(cls, v: Optional[str | bool]) -> Optional[bool]:
        if isinstance(v, str):
            if v == 'NO':
                return False
            elif v == 'SI':
                return True
            else:
                return None
        if isinstance(v, bool):
            return v
        return None
