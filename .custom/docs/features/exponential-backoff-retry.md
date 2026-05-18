# 指数退避重试机制

## 概述

工作流节点支持指数退避重试策略，在 LLM 提供商返回 5xx 错误时自动重试，等待时间随重试次数指数增长，配合 Full Jitter 抖动机制避免多个工作流同时重试造成雪崩。

## 当前状态

**后端待升级重建** — 前端 UI 已完整实现，后端因升级至 1.14.x（graphon 包）需在 fork 中重新实现。

### 已完成

- ✅ 退避策略设计（固定间隔 / 指数退避）
- ✅ `calculate_wait_time()` 核心算法设计（Full Jitter）
- ✅ 前端策略选择器面板（`retry-on-panel.tsx`）
- ✅ 前端配置项：基础间隔、最大退避时间
- ✅ 前端 i18n key（`backoffStrategy`、`baseInterval`、`maxBackoffInterval` 等）
- ✅ 配置数据已存入 workflow 节点 JSON（可随升级保留）

### 待实现（基于 Dify 1.14.x + graphon）

- [ ] Fork `langgenius/graphon`，在 `RetryConfig` 中添加 `backoff_strategy`、`backoff_multiplier`、`max_backoff_interval` 字段
- [ ] 在 graphon `error_handler.py` 中实现 `calculate_wait_time()` 并替换 `time.sleep` 调用
- [ ] 重写测试 `api/tests/custom/test_exponential_backoff.py`（针对新 graphon 路径）

> 当前过渡状态：前端可保存退避配置，后端忽略 backoff 字段（Pydantic 丢弃未知字段），实际以固定间隔重试。升级后补完后端即可恢复完整功能。

## 退避策略

| 策略 | 行为 | 适用场景 |
|------|------|---------|
| 固定间隔 (FIXED) | 每次重试等待相同时间 | 低并发、确定性场景 |
| 指数退避 (EXPONENTIAL) | 等待时间按倍数增长 + Full Jitter | 高并发、5xx 错误 |

### 指数退避示例

基础间隔 1000ms，multiplier 2.0：

| 重试次数 | 计算值 | 实际等待 (含抖动) |
|---------|--------|------------------|
| 第 1 次 | 1000ms | 0~1000ms |
| 第 2 次 | 2000ms | 0~2000ms |
| 第 3 次 | 4000ms | 0~4000ms |

抖动下限保护：实际等待时间至少 100ms。

## 配置字段（设计稿）

`RetryConfig` 扩展字段（待在 graphon fork 中实现）：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `backoff_strategy` | BackoffStrategy | FIXED | 退避策略 (fixed/exponential) |
| `backoff_multiplier` | float | 2.0 | 指数底数 |
| `max_backoff_interval` | int | 60000 | 最大退避时间 (ms) |

向后兼容：旧版节点配置无新字段时使用默认值，行为与固定间隔一致。

## 支持的节点

LLM、HTTP Request、Code、Tool、Agent

## 前端配置（待实现）

启用节点重试后，面板显示策略选择器：
- 固定间隔：仅显示重试间隔
- 指数退避：显示基础间隔（100–5000ms）和最大退避时间（1000–60000ms）

## 实现路径（升级后）

```
1. fork langgenius/graphon (tag 0.3.1)
2. 在 graphon/entities/base_node_data.py 添加 BackoffStrategy enum 和 RetryConfig 字段
3. 在 graphon/graph_engine/error_handler.py 实现 calculate_wait_time() 并替换 time.sleep
4. api/pyproject.toml 改用 git 依赖指向 fork
5. 前端：web/app/components/workflow/nodes/_base/components/retry/retry-on-panel.tsx 新增策略选择器
```

## 相关文件（实现后）

- graphon fork `entities/base_node_data.py` — `RetryConfig` 扩展字段
- graphon fork `graph_engine/error_handler.py` — 指数退避执行逻辑
- `web/app/components/workflow/nodes/_base/components/retry/retry-on-panel.tsx` — 前端配置面板
