"""
Request parsing utilities for Flask + Pydantic integration.

[CUSTOM] 修复上游 bug: flat=False 导致 Pydantic 验证失败
详见: https://github.com/langgenius/dify/commit/f6be9cd90
"""

from typing import TypeVar, get_origin

from flask import Request
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def parse_and_validate(request: Request, model_class: type[T]) -> T:
    """
    Parse Flask request.args and validate with Pydantic model.

    Handles the case where flat=False returns list values for all parameters,
    but scalar fields (int, str, bool) expect single values.

    Args:
        request: Flask request object
        model_class: Pydantic BaseModel class to validate against

    Returns:
        Validated Pydantic model instance

    Example:
        >>> class MyQuery(BaseModel):
        ...     page: int = 1
        ...     ids: list[str] = []
        >>> query = parse_and_validate(request, MyQuery)
    """
    raw_args = request.args.to_dict(flat=False)
    parsed = {}

    for field_name, field_info in model_class.model_fields.items():
        if field_name not in raw_args:
            continue

        values = raw_args[field_name]
        origin = get_origin(field_info.annotation)

        # If field expects a list, keep as list; otherwise take first value
        if origin is list:
            parsed[field_name] = values
        else:
            parsed[field_name] = values[0] if values else None

    return model_class.model_validate(parsed)
