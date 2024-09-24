from __future__ import annotations

import copy
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Mapping, MutableMapping, Optional

import jsonschema

from cl_sii.libs.json_utils import JsonSchemaValidationError, read_json_schema
from cl_sii.rcv.data_models import PeriodoTributario
from cl_sii.rut import Rut
from .data_models import CteForm29


SiiCteF29DatosObjType = Mapping[str, Mapping[str, object]]
_CTE_F29_DATOS_OBJ_SCHEMA_PATH = (
    Path(__file__).parent.parent.parent
    / 'data'
    / 'cte'
    / 'schemas-json'
    / 'f29_datos_obj.schema.json'
)
CTE_F29_DATOS_OBJ_SCHEMA = read_json_schema(_CTE_F29_DATOS_OBJ_SCHEMA_PATH)

_CTE_F29_DATOS_OBJ_MISSING_KEY_FIXES_PATH = (
    Path(__file__).parent.parent.parent / 'data' / 'cte' / 'f29_datos_obj_missing_key_fixes.json'
)
with open(_CTE_F29_DATOS_OBJ_MISSING_KEY_FIXES_PATH) as f:
    CTE_F29_DATOS_OBJ_MISSING_KEY_FIXES: SiiCteF29DatosObjType = json.load(f)


def parse_sii_cte_f29_datos_obj(
    datos_obj: SiiCteF29DatosObjType,
    schema_validator: Optional[Callable[[SiiCteF29DatosObjType], SiiCteF29DatosObjType]] = None,
    campo_deserializer: Optional[Callable[[object, str], object]] = None,
) -> CteForm29:
    """
    Parse the ``datos`` JavaScript object embedded in the IFrames of the
    HTML version of the CTE's 'Declaraciones de IVA (F29)'.

    :param schema_validator: Schema validator. For the signature of the callable, see the docstring
        of ``cte_f29_datos_schema_default_validator``.
    :param campo_deserializer: 'Campo' deserializer. For the signature of the callable, see the
        docstring of ``cte_f29_datos_obj_campo_default_deserializer``.
    :raises JsonSchemaValidationError: If schema validation fails.
    """
    if schema_validator is None:
        schema_validator = cte_f29_datos_schema_default_validator
    if campo_deserializer is None:
        campo_deserializer = cte_f29_datos_obj_campo_default_deserializer

    obj_params: Mapping[str, Any] = _parse_sii_cte_f29_datos_obj_to_dict(
        datos_obj=datos_obj,
        schema_validator=schema_validator,
        campo_deserializer=campo_deserializer,
    )
    obj = CteForm29(**obj_params)
    return obj


def _parse_sii_cte_f29_datos_obj_to_dict(
    datos_obj: SiiCteF29DatosObjType,
    schema_validator: Callable[[SiiCteF29DatosObjType], SiiCteF29DatosObjType],
    campo_deserializer: Callable[[object, str], object],
) -> Mapping[str, object]:
    """
    Parse the ``datos`` JavaScript object embedded in the IFrames of the
    HTML version of the CTE's 'Declaraciones de IVA (F29)' and return a
    dictionary.

    :param schema_validator:
    :param campo_deserializer:
    :raises JsonSchemaValidationError: If schema validation fails.
    """
    validated_datos_obj = schema_validator(datos_obj)

    datos_obj_campos: Mapping[int, str] = {
        int(code): str(value) for code, value in validated_datos_obj['campos'].items()
    }
    datos_obj_extras: Mapping[str, object] = validated_datos_obj['extras']
    datos_obj_glosa: Mapping[int, str] = {  # noqa: F841
        int(code): str(value) for code, value in validated_datos_obj['glosa'].items()
    }
    datos_obj_tipos: Mapping[int, str] = {
        int(code): str(value) for code, value in validated_datos_obj['tipos'].items()
    }

    deserialized_datos_obj_campos = {
        code: campo_deserializer(value, datos_obj_tipos[code])
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
        #
        tipo_declaracion=datos_obj_extras.get('CLASE'),
        banco=datos_obj_extras.get('BANCO'),
        medio_pago=datos_obj_extras.get('MEDIO_PAGO'),
        #
        extra=obj_extra,
    )
    return obj_dict


def cte_f29_datos_obj_campo_default_deserializer(campo_value: object, tipo: str) -> object:
    """
    Convert raw values from the ``datos`` object to the corresponding Python
    data type.

    :param campo_value: Raw value from 'campos'.
    :param tipo: Data type code from 'tipos'.
    :raises ValueError: If value conversion fails.
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


def cte_f29_datos_obj_campo_best_effort_deserializer(campo_value: object, tipo: str) -> object:
    """
    Convert raw values from the ``datos`` object to the corresponding Python
    data type. Values that cannot be converted will be returned without modification.

    :param campo_value: Raw value from 'campos'.
    :param tipo: Data type code from 'tipos'.
    """
    try:
        deserialized_value = cte_f29_datos_obj_campo_default_deserializer(
            campo_value=campo_value,
            tipo=tipo,
        )
    except Exception:
        deserialized_value = campo_value

    return deserialized_value


def cte_f29_datos_schema_default_validator(
    datos_obj: SiiCteF29DatosObjType,
) -> SiiCteF29DatosObjType:
    """
    Validate the ``datos`` object against the schema.

    :raises JsonSchemaValidationError: If schema validation fails.
    :returns: Validated ``datos`` object if schema validation passed.
    """
    try:
        jsonschema.validate(datos_obj, schema=CTE_F29_DATOS_OBJ_SCHEMA)
    except jsonschema.exceptions.ValidationError as exc:
        raise JsonSchemaValidationError('Validation against JSON Schema failed') from exc

    if datos_obj['campos'].keys() != datos_obj['tipos'].keys():
        raise JsonSchemaValidationError("The keys of 'campos' and 'tipos' are not exactly the same")
    if datos_obj['campos'].keys() != datos_obj['glosa'].keys():
        raise JsonSchemaValidationError("The keys of 'campos' and 'glosa' are not exactly the same")

    return datos_obj


def cte_f29_datos_schema_best_effort_validator(
    datos_obj: SiiCteF29DatosObjType,
) -> SiiCteF29DatosObjType:
    """
    Validate the ``datos`` object against the schema.

    If there are missing keys in the `tipos` or `glosa` dicts, it will try to get them
    from a list of default values.

    :raises JsonSchemaValidationError: If schema validation fails.
    :returns: Validated ``datos`` object if schema validation passed.
    """
    try:
        validated_datos_obj = cte_f29_datos_schema_default_validator(datos_obj)
    except JsonSchemaValidationError as exc:
        if exc.__cause__ is jsonschema.exceptions.ValidationError:
            # We will not try to fix this kind of error.
            raise
        elif exc.__cause__ is None:
            # Let's try to fix this.
            new_datos_obj = try_fix_cte_f29_datos(datos_obj)

            # Let's try again.
            cte_f29_datos_schema_default_validator(new_datos_obj)
            return new_datos_obj
        else:
            raise
    else:
        return validated_datos_obj


def try_fix_cte_f29_datos(datos_obj: SiiCteF29DatosObjType) -> SiiCteF29DatosObjType:
    """
    Try to fix the ``datos`` object.

    If there are missing keys in the `tipos` or `glosa` dicts, it will try to get them
    from a list of default values.

    :raises JsonSchemaValidationError: If an unfixable issue is found.
    :returns: A possibly fixed ``datos`` object.
    """
    new_datos_obj: Mapping[str, MutableMapping[str, object]]
    new_datos_obj = copy.deepcopy(datos_obj)  # type: ignore[arg-type]

    campos_tipos_keys_diff = datos_obj['campos'].keys() - datos_obj['tipos'].keys()
    remaining_campos_tipos_diff = (
        campos_tipos_keys_diff - CTE_F29_DATOS_OBJ_MISSING_KEY_FIXES['tipos'].keys()
    )
    if remaining_campos_tipos_diff:
        raise JsonSchemaValidationError(
            "The keys of 'campos' and 'tipos' differ for the following codes: "
            f"{remaining_campos_tipos_diff}"
        )
    else:
        for missing_key in campos_tipos_keys_diff:
            new_datos_obj['tipos'][missing_key] = CTE_F29_DATOS_OBJ_MISSING_KEY_FIXES['tipos'][
                missing_key
            ]

    campos_glosa_keys_diff = datos_obj['campos'].keys() - datos_obj['glosa'].keys()
    remaining_campos_glosa_diff = (
        campos_glosa_keys_diff - CTE_F29_DATOS_OBJ_MISSING_KEY_FIXES['glosa'].keys()
    )
    if remaining_campos_glosa_diff:
        raise JsonSchemaValidationError(
            "The keys of 'campos' and 'glosa' differ for the following codes: "
            f"{remaining_campos_glosa_diff}"
        )
    else:
        for missing_key in campos_glosa_keys_diff:
            new_datos_obj['glosa'][missing_key] = CTE_F29_DATOS_OBJ_MISSING_KEY_FIXES['glosa'][
                missing_key
            ]

    return new_datos_obj
