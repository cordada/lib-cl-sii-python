from __future__ import annotations

import random
from typing import Any

from cl_sii.cte.f29 import data_models
from cl_sii.rcv.data_models import PeriodoTributario
from cl_sii.rut import Rut


def create_CteForm29(**kwargs: Any) -> data_models.CteForm29:
    defaults = dict(
        contribuyente_rut=Rut.random(),
        periodo_tributario=PeriodoTributario(year=2018, month=random.randint(1, 12)),
        folio=random.randint(1, 9999999999),
    )
    defaults.update(kwargs)

    obj = data_models.CteForm29(**defaults)
    return obj
