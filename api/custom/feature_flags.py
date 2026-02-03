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


# Log Timezone Unification Feature
# When set, all frontend log displays use this unified timezone
# instead of each user's individual timezone setting.
# If empty, falls back to user's individual timezone setting.
# Example values: "Asia/Shanghai", "America/New_York", "UTC", "Europe/London"
DIFY_CUSTOM_LOG_TIMEZONE = os.getenv("DIFY_CUSTOM_LOG_TIMEZONE", "")
