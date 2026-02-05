#!/usr/bin/env python
"""
[CUSTOM] 演示指数退避重试效果

运行: uv run --project api python api/tests/custom/demo_exponential_backoff.py
"""

from core.workflow.enums import BackoffStrategy
from core.workflow.graph_engine.error_handler import calculate_wait_time
from core.workflow.nodes.base.entities import RetryConfig


def demo_fixed_vs_exponential():
    print("=" * 60)
    print("指数退避重试机制演示")
    print("=" * 60)

    # 固定间隔配置
    fixed_config = RetryConfig(
        retry_enabled=True,
        max_retries=5,
        retry_interval=1000,  # 1秒
        backoff_strategy=BackoffStrategy.FIXED,
    )

    # 指数退避配置
    exp_config = RetryConfig(
        retry_enabled=True,
        max_retries=5,
        retry_interval=1000,  # 1秒基础间隔
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        backoff_multiplier=2.0,
        max_backoff_interval=30000,  # 30秒上限
    )

    print("\n📊 固定间隔策略 (FIXED)")
    print("-" * 40)
    print(f"配置: interval={fixed_config.retry_interval}ms")
    for i in range(5):
        wait = calculate_wait_time(i, fixed_config)
        print(f"  重试 #{i + 1}: 等待 {wait:.2f}s")

    print("\n📊 指数退避策略 (EXPONENTIAL)")
    print("-" * 40)
    print(
        f"配置: base={exp_config.retry_interval}ms, "
        f"multiplier={exp_config.backoff_multiplier}, max={exp_config.max_backoff_interval}ms"
    )
    print("公式: wait = random(0, min(base * 2^retry, max))")
    print()

    for i in range(5):
        # 计算理论最大值
        theoretical_max = min(
            exp_config.retry_interval * (exp_config.backoff_multiplier ** i),
            exp_config.max_backoff_interval
        ) / 1000

        # 实际等待时间（含抖动）
        wait = calculate_wait_time(i, exp_config)
        print(f"  重试 #{i + 1}: 等待 {wait:.2f}s (理论最大: {theoretical_max:.2f}s)")

    print("\n" + "=" * 60)
    print("✅ 指数退避可以有效分散重试请求，避免重试风暴")
    print("=" * 60)


if __name__ == "__main__":
    demo_fixed_vs_exponential()
