"""
[CUSTOM] Custom API Controllers

This module provides custom API extensions for Dify.
- Console API: /console/api/custom/
- Service API: /v1/custom/
"""

from flask import Blueprint
from flask_restx import Namespace

from libs.external_api import ExternalApi

# Console API Blueprint
console_custom_bp = Blueprint("console_custom", __name__, url_prefix="/console/api/custom")
console_custom_api = ExternalApi(
    console_custom_bp,
    version="1.0",
    title="Console Custom API",
    description="Custom console management APIs",
)
console_custom_ns = Namespace("console_custom", description="Custom console API operations", path="/")

# Service API Blueprint
service_custom_bp = Blueprint("service_custom", __name__, url_prefix="/v1/custom")
service_custom_api = ExternalApi(
    service_custom_bp,
    version="1.0",
    title="Service Custom API",
    description="Custom service APIs",
)
service_custom_ns = Namespace("service_custom", description="Custom service API operations", path="/")

# Import controllers to register routes
from . import trace

console_custom_api.add_namespace(console_custom_ns)
service_custom_api.add_namespace(service_custom_ns)

__all__ = [
    "console_custom_api",
    "console_custom_bp",
    "console_custom_ns",
    "service_custom_api",
    "service_custom_bp",
    "service_custom_ns",
    "trace",
]
