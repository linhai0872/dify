# 指数退避重试机制

## 概述

工作流节点支持指数退避重试策略，在 LLM 提供商返回 5xx 错误时自动重试，等待时间随重试次数指数增长，配合 Full Jitter 抖动机制避免多个工作流同时重试造成雪崩。

## 退避策略

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| 固定间隔 (FIXED) | 每次重试等待相同时间 | 低并发、确定性场景 |
| 指数退避 (EXPONENTIAL) | 等待时间按倍数增长 | 高并发、5xx 错误 |

### 指数退避示例

基础间隔 1000ms，multiplier 2.0：

| 重试次数 | 计算值 | 实际等待 (含抖动) |
|---------|--------|------------------|
| 第 1 次 | 1000ms | 0~1000ms |
| 第 2 次 | 2000ms | 0~2000ms |
| 第 3 次 | 4000ms | 0~4000ms |

抖动下限保护：实际等待时间至少 100ms。

## 配置字段

`RetryConfig` 模型扩展字段：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `backoff_strategy` | BackoffStrategy | FIXED | 退避策略 (fixed/exponential) |
| `backoff_multiplier` | float | 2.0 | 指数底数 |
| `max_backoff_interval` | int | 60000 | 最大退避时间 (ms) |

向后兼容：旧版节点配置无新字段时使用默认值，行为与固定间隔一致。

## 支持的节点

LLM、HTTP Request、Code、Tool、Agent

## 前端配置

启用节点重试后，面板显示策略选择器：
- 固定间隔：仅显示重试间隔
- 指数退避：显示基础间隔 (100-5000ms) 和最大退避时间 (1000-60000ms)

## 相关文件

- `api/core/workflow/nodes/base/entities.py` — `RetryConfig` 模型 (backoff_strategy 等字段)
- `api/core/workflow/graph_engine/graph_engine.py` — 指数退避执行逻辑
- `web/app/components/workflow/nodes/_base/components/retry/retry-on-panel.tsx` — 前端配置面板
- `openspec/specs/exponential-backoff-retry/spec.md` — 完整规范
