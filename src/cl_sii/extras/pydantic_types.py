"""
cl_sii "extras" / Pydantic types.
"""

from __future__ import annotations

import sys
from typing import Any


if sys.version_info[:2] >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

try:
    import pydantic
    import pydantic.json_schema
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'pydantic' is required to use this module.") from exc

try:
    import pydantic_core
except ImportError as exc:  # pragma: no cover
    raise ImportError("Package 'pydantic-core' is required to use this module.") from exc

import cl_sii.rut
import cl_sii.rut.constants


class _RutPydanticAnnotation:
    """
    `Annotated` wrapper that can be used as the annotation for `cl_sii.rut.Rut`
    fields on `pydantic.BaseModels`, `@pydantic.dataclasses`, etc.

    .. seealso::
        - Handling third-party types:
            https://docs.pydantic.dev/2.9/concepts/types/#handling-third-party-types
            (https://github.com/pydantic/pydantic/blob/v2.9.2/docs/concepts/types.md#handling-third-party-types)
        - Customizing the core schema and JSON schema:
            https://docs.pydantic.dev/2.9/architecture/#customizing-the-core-schema-and-json-schema
            (https://github.com/pydantic/pydantic/blob/v2.9.2/docs/architecture.md#customizing-the-core-schema-and-json-schema)

    Examples:

    >>> from typing import Annotated
    >>> import pydantic
    >>> import cl_sii.rut

    >>> Rut = Annotated[cl_sii.rut.Rut, _RutPydanticAnnotation]

    >>> class ExampleModel(pydantic.BaseModel):
    ...     rut: Rut
    >>>
    >>> example_model_instance = ExampleModel.model_validate({'rut': '78773510-K'})

    >>> import pydantic.dataclasses
    >>>
    >>> @pydantic.dataclasses.dataclass
    ... class ExampleDataclass:
    ...     rut: Rut
    >>>
    >>> example_dataclass_instance = ExampleDataclass(rut='78773510-K')

    >>> example_type_adapter = pydantic.TypeAdapter(Rut)
    >>>
    >>> example_type_adapter.validate_python('78773510-K')
    Rut('78773510-K')
    >>> example_type_adapter.validate_json('"78773510-K"')
    Rut('78773510-K')
    >>> example_type_adapter.dump_python(cl_sii.rut.Rut('78773510-K'))
    '78773510-K'
    >>> example_type_adapter.dump_json(cl_sii.rut.Rut('78773510-K'))
    b'"78773510-K"'
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.core_schema.CoreSchema:
        def validate_from_str(value: str) -> cl_sii.rut.Rut:
            return cl_sii.rut.Rut(value, validate_dv=False)

        from_str_schema = pydantic_core.core_schema.chain_schema(
            [
                pydantic_core.core_schema.str_schema(
                    pattern=cl_sii.rut.constants.RUT_CANONICAL_STRICT_REGEX.pattern
                ),
                pydantic_core.core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return pydantic_core.core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=pydantic_core.core_schema.union_schema(
                [
                    pydantic_core.core_schema.is_instance_schema(cl_sii.rut.Rut),
                    from_str_schema,
                ]
            ),
            serialization=pydantic_core.core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.canonical
            ),
        )


Rut = Annotated[cl_sii.rut.Rut, _RutPydanticAnnotation]
"""
Convenience type alias for Pydantic fields that represent Chilean RUTs.
"""
