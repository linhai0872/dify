# Workflow 费用显示

## 概述

在工作流执行日志和概览页面展示每次执行的 LLM 调用费用（金额 + 货币），帮助用户掌握应用成本。

## 当前状态

**待完成** — 字段设计完成，未接入持久化，前端未实现。

### 待实现

- [ ] 在 graphon `WorkflowExecution` 域模型中添加 `total_price` 和 `currency` 字段（或通过扩展表方案）
- [ ] 在持久化层（`persistence.py`）从 LLM 调用结果中汇总费用并写入
- [ ] 在 `sqlalchemy_workflow_execution_repository.py` 映射到 DB 列
- [ ] 数据库迁移：`WorkflowRun` 表新增 `custom_total_price`（Numeric）和 `custom_currency`（String）列
- [ ] 后端 API：在工作流日志接口中返回费用字段
- [ ] 前端：工作流执行日志列表显示费用
- [ ] 前端：概览页面费用趋势图（可选，对应 PRD P3「应用分析功能」）

## 方案设计

### 方案 A：graphon fork（推荐，与指数退避共用 fork）

在 graphon `WorkflowExecution` 中添加：
```python
total_price: Decimal = Field(default=Decimal(0))
currency: str = Field(default="USD")
```

持久化层从 `app_generate_entity` 的 LLM usage 数据中聚合费用。

### 方案 B：扩展表（不依赖 graphon fork）

新建 `custom_workflow_execution_price` 表：
```
workflow_run_id  → FK to workflow_run.id
total_price      Numeric(10,7)
currency         VARCHAR(10)
```

在 `persistence.py` 执行完毕后单独写入此表。查询时 JOIN。

## 数据来源

费用数据从工作流各节点（主要是 LLM 节点）的执行元数据中汇总：
- `WorkflowNodeExecution.metadata` 中包含 `total_price` 和 `currency`
- 在 `persistence.py` 的 `_on_workflow_finished()` 中汇总各节点费用

## 相关文件（实现后）

- `api/core/app/workflow/layers/persistence.py` — 费用汇总逻辑
- `api/core/repositories/sqlalchemy_workflow_execution_repository.py` — DB 映射
- `api/migrations/versions/YYYY_MM_DD_custom_workflow_price.py` — DB 迁移
- `api/controllers/console/app/workflow_app_log.py` — API 返回费用字段
- `web/app/(commonLayout)/app/(appDetailLayout)/[appId]/overview/` — 概览页费用展示
