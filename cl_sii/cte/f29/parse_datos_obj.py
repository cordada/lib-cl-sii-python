from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Mapping, MutableMapping

import jsonschema

from cl_sii.libs.json_utils import JsonSchemaValidationError, read_json_schema
from cl_sii.rut import Rut
from cl_sii.rcv.data_models import PeriodoTributario

from .data_models import CteForm29


SiiCteF29DatosObjType = Mapping[str, Mapping[str, object]]
_CTE_F29_DATOS_OBJ_SCHEMA_PATH = (
    Path(__file__).parent.parent.parent
    / 'data' / 'cte' / 'schemas-json' / 'f29_datos_obj.schema.json'
)
CTE_F29_DATOS_OBJ_SCHEMA = read_json_schema(_CTE_F29_DATOS_OBJ_SCHEMA_PATH)


def parse_sii_cte_f29_datos_obj(datos_obj: SiiCteF29DatosObjType) -> CteForm29:
    """
    Parse the ``datos`` JavaScript object embedded in the IFrames of the
    HTML version of the CTE's 'Declaraciones de IVA (F29)'.

    :raises JsonSchemaValidationError: If schema validation fails.
    """
    obj_params = _parse_sii_cte_f29_datos_obj_to_dict(datos_obj=datos_obj)
    obj = CteForm29(**obj_params)
    return obj


def _parse_sii_cte_f29_datos_obj_to_dict(datos_obj: SiiCteF29DatosObjType) -> Mapping[str, object]:
    """
    Parse the ``datos`` JavaScript object embedded in the IFrames of the
    HTML version of the CTE's 'Declaraciones de IVA (F29)' and return a
    dictionary.

    :raises JsonSchemaValidationError: If schema validation fails.
    """
    _validate_cte_f29_datos_schema(datos_obj=datos_obj)

    datos_obj_campos: Mapping[int, str] = {
        int(code): str(value) for code, value in datos_obj['campos'].items()
    }
    datos_obj_extras: Mapping[str, object] = datos_obj['extras']
    datos_obj_glosa: Mapping[int, str] = {  # noqa: F841
        int(code): str(value) for code, value in datos_obj['glosa'].items()
    }
    datos_obj_tipos: Mapping[int, str] = {
        int(code): str(value) for code, value in datos_obj['tipos'].items()
    }

    deserialized_datos_obj_campos = {
        code: _deserialize_cte_f29_datos_obj_campo(campo_value=value, tipo=datos_obj_tipos[code])
        for code, value in datos_obj_campos.items()
    }

    obj_extra: MutableMapping[int, object] = {}
    for code, value in deserialized_datos_obj_campos.items():
        obj_extra[code] = value

    periodo_tributario = PeriodoTributario.from_date(
        datetime.strptime(str(datos_obj_extras['PERIODO']), '%Y%m').date(),
    )

    obj_dict = dict(
        folio=obj_extra[7],
        contribuyente_rut=obj_extra[3],
        periodo_tributario=periodo_tributario,

        tipo_declaracion=datos_obj_extras.get('CLASE'),
        banco=datos_obj_extras.get('BANCO'),
        medio_pago=datos_obj_extras.get('MEDIO_PAGO'),

        extra=obj_extra,
    )
    return obj_dict


def _deserialize_cte_f29_datos_obj_campo(campo_value: object, tipo: str) -> object:
    """
    Convert raw values from the ``datos`` object to the corresponding Python
    data type.

    :param campo_value: Raw value from 'campos'.
    :param tipo: Data type code from 'tipos'.
    """
    if not isinstance(campo_value, str):
        return campo_value

    deserialized_value: object

    if tipo == 'R':
        deserialized_value = Rut(campo_value)
    elif tipo == 'F':
        deserialized_value = datetime.strptime(campo_value, '%d/%m/%Y').date()
    elif tipo == 'C':
        deserialized_value = campo_value
    elif tipo in ('N', 'M'):
        deserialized_value = int(campo_value)
    elif tipo == 'D':
        deserialized_value = Decimal(campo_value)
    else:
        raise ValueError(f"Invalid or unknown tipo of campo: '{tipo}'")

    return deserialized_value


def _validate_cte_f29_datos_schema(datos_obj: SiiCteF29DatosObjType) -> None:
    """
    Validate the ``datos`` object against the schema.

    :raises JsonSchemaValidationError: If schema validation fails.
    :returns: ``None`` if schema validation passed.
    """
    try:
        jsonschema.validate(datos_obj, schema=CTE_F29_DATOS_OBJ_SCHEMA)
    except jsonschema.exceptions.ValidationError as exc:
        raise JsonSchemaValidationError('Validation against JSON Schema failed') from exc

    if datos_obj['campos'].keys() != datos_obj['tipos'].keys():
        raise JsonSchemaValidationError("The keys of 'campos' and 'tipos' are not exactly the same")
    if datos_obj['campos'].keys() != datos_obj['glosa'].keys():
        raise JsonSchemaValidationError("The keys of 'campos' and 'tipos' are not exactly the same")
