"""
[CUSTOM] Tests for log timezone unification feature.

This module tests the DIFY_CUSTOM_LOG_TIMEZONE environment variable
and its integration with SystemFeatureModel.
"""

import os
from unittest.mock import patch


class TestLogTimezoneFeatureFlag:
    """Test DIFY_CUSTOM_LOG_TIMEZONE feature flag."""

    def test_log_timezone_default_empty(self):
        """Default value should be empty string."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove the env var if it exists
            os.environ.pop("DIFY_CUSTOM_LOG_TIMEZONE", None)

            # Re-import to get fresh value
            import importlib

            import custom.feature_flags as ff

            importlib.reload(ff)

            assert ff.DIFY_CUSTOM_LOG_TIMEZONE == ""

    def test_log_timezone_from_env(self):
        """Should read timezone from environment variable."""
        with patch.dict(os.environ, {"DIFY_CUSTOM_LOG_TIMEZONE": "Asia/Shanghai"}):
            import importlib

            import custom.feature_flags as ff

            importlib.reload(ff)

            assert ff.DIFY_CUSTOM_LOG_TIMEZONE == "Asia/Shanghai"

    def test_log_timezone_various_values(self):
        """Should accept various timezone values."""
        test_cases = [
            "UTC",
            "America/New_York",
            "Europe/London",
            "Asia/Tokyo",
        ]

        for tz in test_cases:
            with patch.dict(os.environ, {"DIFY_CUSTOM_LOG_TIMEZONE": tz}):
                import importlib

                import custom.feature_flags as ff

                importlib.reload(ff)

                assert tz == ff.DIFY_CUSTOM_LOG_TIMEZONE


class TestSystemFeatureModelLogTimezone:
    """Test log_timezone field in SystemFeatureModel."""

    def test_system_feature_model_has_log_timezone_field(self):
        """SystemFeatureModel should have log_timezone field."""
        from services.feature_service import SystemFeatureModel

        model = SystemFeatureModel()
        assert hasattr(model, "log_timezone")
        assert model.log_timezone == ""

    def test_system_feature_model_log_timezone_accepts_string(self):
        """log_timezone field should accept string values."""
        from services.feature_service import SystemFeatureModel

        model = SystemFeatureModel(log_timezone="Asia/Shanghai")
        assert model.log_timezone == "Asia/Shanghai"

    def test_get_system_features_includes_log_timezone(self):
        """get_system_features should include log_timezone from env."""
        with patch.dict(os.environ, {"DIFY_CUSTOM_LOG_TIMEZONE": "Asia/Shanghai"}):
            # Reload feature_flags to pick up env change
            import importlib

            import custom.feature_flags as ff

            importlib.reload(ff)

            from services.feature_service import FeatureService

            features = FeatureService.get_system_features()
            assert features.log_timezone == "Asia/Shanghai"

    def test_get_system_features_empty_when_not_set(self):
        """get_system_features should return empty string when env not set."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DIFY_CUSTOM_LOG_TIMEZONE", None)

            import importlib

            import custom.feature_flags as ff

            importlib.reload(ff)

            from services.feature_service import FeatureService

            features = FeatureService.get_system_features()
            assert features.log_timezone == ""
