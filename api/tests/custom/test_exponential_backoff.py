"""
[CUSTOM] 二开: 指数退避重试机制单元测试

测试 calculate_wait_time() 函数的固定间隔和指数退避计算。
"""

import pytest

from core.workflow.enums import BackoffStrategy
from core.workflow.graph_engine.error_handler import MIN_JITTER_FLOOR_SECONDS, calculate_wait_time
from core.workflow.nodes.base.entities import RetryConfig


class TestCalculateWaitTime:
    """Test calculate_wait_time function."""

    def test_fixed_strategy_returns_constant_interval(self):
        """Fixed strategy should always return the same interval."""
        config = RetryConfig(
            retry_enabled=True,
            max_retries=3,
            retry_interval=1000,  # 1 second
            backoff_strategy=BackoffStrategy.FIXED,
        )

        # All retries should have the same wait time
        assert calculate_wait_time(0, config) == 1.0
        assert calculate_wait_time(1, config) == 1.0
        assert calculate_wait_time(2, config) == 1.0
        assert calculate_wait_time(5, config) == 1.0

    def test_exponential_strategy_increases_wait_time(self):
        """Exponential strategy should increase wait time with each retry."""
        config = RetryConfig(
            retry_enabled=True,
            max_retries=5,
            retry_interval=1000,  # 1 second base
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            backoff_multiplier=2.0,
            max_backoff_interval=60000,  # 60 seconds max
        )

        # Run multiple times to account for jitter randomness
        samples = 100
        for retry_count in range(4):
            wait_times = [calculate_wait_time(retry_count, config) for _ in range(samples)]

            # Expected max wait: base * multiplier^retry_count
            expected_max = (1000 * (2.0**retry_count)) / 1000  # in seconds

            # All values should be between floor and expected max
            for wait in wait_times:
                assert wait >= MIN_JITTER_FLOOR_SECONDS
                assert wait <= expected_max + 0.001  # small tolerance for float comparison

    def test_exponential_strategy_respects_max_backoff(self):
        """Exponential backoff should be capped at max_backoff_interval."""
        config = RetryConfig(
            retry_enabled=True,
            max_retries=10,
            retry_interval=1000,  # 1 second base
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            backoff_multiplier=2.0,
            max_backoff_interval=5000,  # 5 seconds max
        )

        # At retry 10, exponential would be 1000 * 2^10 = 1024000ms = 1024s
        # But it should be capped at 5000ms = 5s
        samples = 100
        wait_times = [calculate_wait_time(10, config) for _ in range(samples)]

        for wait in wait_times:
            assert wait >= MIN_JITTER_FLOOR_SECONDS
            assert wait <= 5.0 + 0.001  # Should be capped at 5 seconds

    def test_jitter_floor_protection(self):
        """Wait time should never be less than the minimum floor."""
        config = RetryConfig(
            retry_enabled=True,
            max_retries=3,
            retry_interval=100,  # Very small interval
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            backoff_multiplier=2.0,
            max_backoff_interval=60000,
        )

        # Even with jitter potentially producing small values,
        # the floor should protect against near-zero waits
        samples = 100
        for _ in range(samples):
            wait = calculate_wait_time(0, config)
            assert wait >= MIN_JITTER_FLOOR_SECONDS

    def test_default_config_uses_fixed_strategy(self):
        """Default RetryConfig should use FIXED strategy."""
        config = RetryConfig(
            retry_enabled=True,
            max_retries=3,
            retry_interval=1000,
        )

        # Default should be FIXED
        assert config.backoff_strategy == BackoffStrategy.FIXED

        # Should return constant interval
        assert calculate_wait_time(0, config) == 1.0
        assert calculate_wait_time(1, config) == 1.0

    def test_backward_compatibility_with_minimal_config(self):
        """Minimal config (without new fields) should work with defaults."""
        # Simulate loading old config without new backoff fields
        config = RetryConfig(
            retry_enabled=True,
            max_retries=3,
            retry_interval=2000,
        )

        # Should use FIXED by default and work correctly
        assert config.backoff_strategy == BackoffStrategy.FIXED
        assert config.backoff_multiplier == 2.0
        assert config.max_backoff_interval == 60000

        # Wait time should be fixed at 2 seconds
        assert calculate_wait_time(0, config) == 2.0
        assert calculate_wait_time(5, config) == 2.0

    def test_exponential_with_different_multiplier(self):
        """Exponential strategy should respect custom multiplier."""
        config = RetryConfig(
            retry_enabled=True,
            max_retries=5,
            retry_interval=1000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            backoff_multiplier=3.0,  # Triple each time
            max_backoff_interval=100000,
        )

        # Expected maximums: 1s, 3s, 9s, 27s
        expected_maxes = [1.0, 3.0, 9.0, 27.0]

        samples = 50
        for retry_count, expected_max in enumerate(expected_maxes):
            wait_times = [calculate_wait_time(retry_count, config) for _ in range(samples)]
            for wait in wait_times:
                assert wait <= expected_max + 0.001


class TestRetryConfigProperties:
    """Test RetryConfig model properties."""

    def test_retry_interval_seconds(self):
        """retry_interval_seconds should convert ms to seconds."""
        config = RetryConfig(retry_interval=2500)
        assert config.retry_interval_seconds == 2.5

    def test_max_backoff_interval_seconds(self):
        """max_backoff_interval_seconds should convert ms to seconds."""
        config = RetryConfig(max_backoff_interval=30000)
        assert config.max_backoff_interval_seconds == 30.0
