"""Helpers for registering Pydantic models with Flask-RESTX namespaces."""

from enum import StrEnum

from flask_restx import Namespace
from pydantic import BaseModel, TypeAdapter

# [CUSTOM] 移除模块级别的 console_ns 导入以避免循环依赖
# 原因: upstream 1.12.0 在此导入 console_ns 导致循环导入
# 解决: 延迟导入移至 get_or_create_model 函数内部
# [/CUSTOM]

DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"


def register_schema_model(namespace: Namespace, model: type[BaseModel]) -> None:
    """Register a single BaseModel with a namespace for Swagger documentation."""

    namespace.schema_model(model.__name__, model.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0))


def register_schema_models(namespace: Namespace, *models: type[BaseModel]) -> None:
    """Register multiple BaseModels with a namespace."""

    for model in models:
        register_schema_model(namespace, model)


def get_or_create_model(model_name: str, field_def):
    # [CUSTOM] 延迟导入以避免循环依赖
    from controllers.console import console_ns

    # [/CUSTOM]
    existing = console_ns.models.get(model_name)
    if existing is None:
        existing = console_ns.model(model_name, field_def)
    return existing


def register_enum_models(namespace: Namespace, *models: type[StrEnum]) -> None:
    """Register multiple StrEnum with a namespace."""
    for model in models:
        namespace.schema_model(
            model.__name__, TypeAdapter(model).json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0)
        )


__all__ = [
    "DEFAULT_REF_TEMPLATE_SWAGGER_2_0",
    "get_or_create_model",
    "register_enum_models",
    "register_schema_model",
    "register_schema_models",
]
