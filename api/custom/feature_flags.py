"""
[CUSTOM] Feature flags for custom extensions.

This module provides feature flags to control custom functionality.
All flags default to True (enabled) for seamless operation.
Set to "false" in environment to disable specific features.
"""

import os


def _get_bool_env(key: str, default: bool = True) -> bool:
    """Get boolean value from environment variable."""
    value = os.getenv(key, str(default).lower())
    return value.lower() in ("true", "1", "yes", "on")


# Trace Search Feature
# Enables external trace ID persistence and trace-based lookup APIs
# - Persists external_trace_id to workflow_runs and messages tables
# - Enables /custom/apps/<app_id>/trace/<trace_id> API endpoints
# - Adds keyword_scope parameter to log search APIs
DIFY_CUSTOM_TRACE_SEARCH_ENABLED = _get_bool_env("DIFY_CUSTOM_TRACE_SEARCH_ENABLED", default=True)
