from __future__ import annotations

from collections.abc import Sequence

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
