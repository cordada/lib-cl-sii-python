import json
from pathlib import Path
from typing import Mapping


###############################################################################
# exceptions
###############################################################################


class JsonSchemaValidationError(Exception):
    """
    JSON data failed validation against a schema.

    Note: For the purpose of using this exception, anything that performs
        schema-like validations against JSON data is considered a 'schema', even
        if it is not a standard 'JSON Schema'.
    """


###############################################################################
# functions
###############################################################################


def read_json_schema(file_path: Path) -> Mapping[str, object]:
    """
    Instantiate an JSON schema object from a file.

    .. warning:: It is assumed that the schema is valid, and providing an
        invalid schema can lead to undefined behavior.

    :raises FileNotFoundError: If there is no file at ``file_path``.
    """
    with file_path.open(mode='rb') as file:
        content = json.load(file)

    if isinstance(content, Mapping):
        return content
    else:
        raise TypeError(
            f"Expected JSON file content to be a 'Mapping', not a '{content.__class__.__name__}'.",
        )
