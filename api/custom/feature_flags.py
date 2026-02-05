"""
[CUSTOM] Feature flags for custom extensions.

This module provides feature flags to control custom functionality.
All flags default to True (enabled) for seamless operation.
Set to "false" in environment to disable specific features.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file before reading environment variables
# This ensures feature flags work correctly even when imported before DifyConfig
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


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


# Native Document Extractors Feature
# Enables native (non-Unstructured-API-dependent) extraction for DOC/PPT/PPTX/EPUB formats
# in default ETL mode without requiring external Unstructured API.
# - PPTX: Uses python-pptx (pure Python, no external dependencies)
# - EPUB: Uses ebooklib + BeautifulSoup (pure Python, no pypandoc needed)
# - DOC/PPT: Uses unstructured local partition (requires LibreOffice)
DIFY_CUSTOM_NATIVE_EXTRACTORS_ENABLED = _get_bool_env(
    "DIFY_CUSTOM_NATIVE_EXTRACTORS_ENABLED", default=True
)


# Multi-Workspace Permission Control Feature
# Enables system-level roles (super_admin/workspace_admin/normal) for cross-workspace management.
# - super_admin: Can view all workspaces, manage all users, assign members to any workspace
# - workspace_admin: Can manage workspaces they are assigned to (same as normal for now)
# - normal: Default role, can only access joined workspaces
# When disabled, all system role checks are skipped and original behavior is preserved.
DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED = _get_bool_env(
    "DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED", default=False
)

# Initial Super Admin Email
# If set and no super_admin exists, the user with this email will be promoted to super_admin on startup.
# Only effective when DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED is True.
DIFY_CUSTOM_INITIAL_SUPER_ADMIN_EMAIL = os.getenv("DIFY_CUSTOM_INITIAL_SUPER_ADMIN_EMAIL", "")
