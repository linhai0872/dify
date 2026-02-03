# 工作流日志搜索增强

> **状态**: 已实现
> **创建时间**: 2026-02-03
> **功能开关**: `DIFY_CUSTOM_TRACE_SEARCH_ENABLED`

---

## 1. 需求背景

### 1.1 业务场景

外部系统调用 Dify 应用 API 后，需要溯源执行情况进行 debug。

### 1.2 当前痛点

1. **两步查询**：先通过 inputs 内容搜索找到 `run_id`，再用 `run_id` 查询详情
2. **搜索不精准**：keyword 搜索混合了所有字段（inputs/outputs/session_id/run_id），无法指定范围
3. **WebApp 场景受限**：嵌入式应用无法通过 Header 传递追踪 ID

### 1.3 预期效果

- **API 调用场景**：传入 `trace_id`，一步查询完整执行详情
- **WebApp 场景**：通过 inputs 传入追踪字段，精准搜索
- **通用场景**：支持 `keyword_scope` 参数，按字段范围搜索

---

## 2. 方案设计

### 2.1 三个方案组合

| 方案 | 功能 | 适用场景 |
|------|------|---------|
| **A: trace_id 持久化** | 持久化 external_trace_id 并支持精准查询 | API 调用 |
| **B: keyword_scope** | 日志搜索支持指定字段范围 | 所有场景 |
| **C: inputs 约定字段** | 从 inputs 中提取 `dify_trace_id` | WebApp 嵌入 |

### 2.2 追踪 ID 来源（优先级）

```
1. HTTP Header: X-Trace-Id
2. Query 参数: trace_id
3. 请求体: trace_id
4. inputs 字段: dify_trace_id  ← 新增，WebApp 场景
```

### 2.3 应用类型覆盖

| 应用类型 | 日志模型 | trace_id 字段 |
|---------|---------|--------------|
| Workflow | WorkflowRun | external_trace_id |
| Chatflow | WorkflowRun + Message | 两者都添加 |
| Chat/Agent | Message | external_trace_id |

---

## 3. API 设计

### 3.1 新增：追踪查询接口

**Console API**:
```
GET /console/api/custom/apps/{app_id}/trace/{trace_id}
```

**Service API**:
```
GET /v1/custom/apps/{app_id}/trace/{trace_id}
```

**返回结构（Workflow 应用）**:
```json
{
    "type": "workflow",
    "workflow_run": {
        "id": "run_xxx",
        "status": "succeeded",
        "inputs": {},
        "outputs": {},
        "elapsed_time": 3.5,
        "total_tokens": 1234,
        "error": null,
        "created_at": "2026-02-03T10:00:00Z",
        "finished_at": "2026-02-03T10:00:03Z"
    },
    "node_executions": [
        {
            "node_id": "start",
            "node_type": "start",
            "title": "开始",
            "status": "succeeded",
            "inputs": {},
            "outputs": {},
            "elapsed_time": 0.1,
            "error": null
        }
    ]
}
```

**返回结构（Chat/Agent 应用）**:
```json
{
    "type": "chat",
    "message": {
        "id": "msg_xxx",
        "conversation_id": "conv_xxx",
        "query": "用户问题",
        "answer": "AI 回答",
        "inputs": {},
        "status": "normal",
        "created_at": "2026-02-03T10:00:00Z"
    },
    "agent_thoughts": [
        {
            "position": 1,
            "thought": "思考内容",
            "tool": "tool_name",
            "tool_input": {},
            "observation": "工具返回"
        }
    ],
    "workflow_run": null,
    "node_executions": []
}
```

**返回结构（Chatflow 应用）**:
```json
{
    "type": "chatflow",
    "message": {
        "id": "msg_xxx",
        "conversation_id": "conv_xxx",
        "query": "用户问题",
        "answer": "AI 回答",
        "workflow_run_id": "run_xxx"
    },
    "agent_thoughts": [],
    "workflow_run": {
        "id": "run_xxx",
        "status": "succeeded"
    },
    "node_executions": [...]
}
```

### 3.2 增强：日志查询接口

**Workflow 日志**:
```
GET /console/api/apps/{app_id}/workflow-app-logs?keyword=xxx&keyword_scope=inputs
GET /v1/workflows/logs?keyword=xxx&keyword_scope=inputs
```

**Chat 日志**:
```
GET /console/api/apps/{app_id}/chat-conversations?keyword=xxx&keyword_scope=inputs
```

**keyword_scope 参数值**:

| scope 值 | Workflow 日志 | Chat 日志 |
|---------|--------------|-----------|
| `all` (默认) | inputs + outputs + session_id + run_id | query + answer + inputs + session_id |
| `inputs` | WorkflowRun.inputs | Message.inputs |
| `outputs` | WorkflowRun.outputs | Message.answer |
| `query` | _(不适用)_ | Message.query |
| `session_id` | EndUser.session_id | EndUser.session_id |
| `trace_id` | WorkflowRun.external_trace_id | Message.external_trace_id |

---

## 4. 数据库变更

### 4.1 WorkflowRun 表

```sql
ALTER TABLE workflow_runs
ADD COLUMN external_trace_id VARCHAR(128) NULL;

CREATE INDEX workflow_run_external_trace_id_idx
ON workflow_runs(tenant_id, app_id, external_trace_id);
```

### 4.2 Message 表

```sql
ALTER TABLE messages
ADD COLUMN external_trace_id VARCHAR(128) NULL;

CREATE INDEX message_external_trace_id_idx
ON messages(app_id, external_trace_id);
```

---

## 5. 实现计划

### 5.1 文件清单

#### 后端文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `api/migrations/versions/2026_02_03_custom_trace_id.py` | 新建 | 数据库迁移 |
| `api/models/workflow.py` | 修改 | WorkflowRun 添加字段 |
| `api/models/model.py` | 修改 | Message 添加字段 |
| `api/core/helper/trace_id_helper.py` | 修改 | 添加 inputs 提取逻辑 |
| `api/core/workflow/graph_engine/layers/persistence.py` | 修改 | 持久化 trace_id |
| `api/core/app/apps/base_app_runner.py` | 修改 | Message 持久化 trace_id |
| `api/custom/services/custom_trace_service.py` | 新建 | 追踪查询服务 |
| `api/controllers/custom/__init__.py` | 新建 | 二开路由注册 |
| `api/controllers/custom/trace.py` | 新建 | 追踪查询 API |
| `api/services/workflow_app_service.py` | 修改 | 添加 keyword_scope |
| `api/controllers/console/app/workflow_app_log.py` | 修改 | 添加参数 |
| `api/controllers/service_api/app/workflow.py` | 修改 | 添加参数 |
| `api/controllers/console/app/conversation.py` | 修改 | 添加 keyword_scope |
| `api/tests/custom/test_trace_search.py` | 新建 | 集成测试 |

#### 前端文档文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `web/app/components/develop/template/template.en.mdx` | 修改 | 英文 API 文档（添加追踪查询接口） |
| `web/app/components/develop/template/template.zh.mdx` | 修改 | 中文 API 文档（添加追踪查询接口） |
| `web/app/components/develop/template/template_workflow.en.mdx` | 修改 | Workflow 英文文档（添加追踪查询） |
| `web/app/components/develop/template/template_workflow.zh.mdx` | 修改 | Workflow 中文文档（添加追踪查询） |
| `web/app/components/develop/template/template_chat.en.mdx` | 修改 | Chat 英文文档（添加追踪查询） |
| `web/app/components/develop/template/template_chat.zh.mdx` | 修改 | Chat 中文文档（添加追踪查询） |
| `web/app/components/develop/template/template_advanced_chat.en.mdx` | 修改 | Chatflow 英文文档（添加追踪查询） |
| `web/app/components/develop/template/template_advanced_chat.zh.mdx` | 修改 | Chatflow 中文文档（添加追踪查询） |

#### 文档文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `.custom/docs/api/README.md` | 已更新 | 二开 API 文档 |
| `.custom/docs/features/workflow-log-search-enhancement.md` | 已创建 | 功能设计文档 |

### 5.2 实现步骤

**Phase 1: 数据库迁移**
- 创建迁移脚本，添加 external_trace_id 字段和索引

**Phase 2: 模型层**
- WorkflowRun 添加 external_trace_id 字段
- Message 添加 external_trace_id 字段

**Phase 3: trace_id 提取增强**
- 修改 trace_id_helper.py，支持从 inputs 中提取 `dify_trace_id`

**Phase 4: 持久化层**
- 工作流执行时持久化 trace_id 到 WorkflowRun
- 消息创建时持久化 trace_id 到 Message

**Phase 5: 追踪查询服务**
- 创建 CustomTraceService，支持按 trace_id 查询
- 根据应用类型返回不同结构

**Phase 6: API 层**
- 创建二开路由 /custom/
- 实现 Console API 和 Service API

**Phase 7: keyword_scope 支持**
- 修改 workflow_app_service.py
- 修改 conversation.py
- 更新 API 参数

**Phase 8: 测试**
- 编写集成测试验证各场景

---

## 6. 使用示例

### 6.1 API 调用场景

```bash
# 1. 调用工作流时传入 trace_id
curl -X POST /v1/workflows/run \
  -H "Authorization: Bearer {api_key}" \
  -H "X-Trace-Id: order-12345" \
  -d '{"inputs": {"customer_id": "C001"}}'

# 2. 需要 debug 时，一步查询完整详情
curl GET /v1/custom/apps/{app_id}/trace/order-12345 \
  -H "Authorization: Bearer {api_key}"
```

### 6.2 WebApp 嵌入场景

```javascript
// 1. 前端在 inputs 中传入追踪 ID
const response = await fetch('/v1/chat-messages', {
  method: 'POST',
  body: JSON.stringify({
    inputs: {
      dify_trace_id: 'session-abc-123',  // 约定字段
      user_question: '...'
    },
    query: '用户问题'
  })
});

// 2. 后台通过 keyword_scope 精准搜索
// GET /console/api/apps/{app_id}/workflow-app-logs?keyword=session-abc-123&keyword_scope=inputs
```

### 6.3 keyword_scope 搜索

```bash
# 只搜索 inputs 字段
GET /v1/workflows/logs?keyword=customer_id&keyword_scope=inputs

# 只搜索 outputs 字段
GET /v1/workflows/logs?keyword=success&keyword_scope=outputs

# 只搜索 session_id
GET /v1/workflows/logs?keyword=user-001&keyword_scope=session_id

# 搜索 trace_id
GET /v1/workflows/logs?keyword=order-12345&keyword_scope=trace_id
```

---

## 7. 验收标准

1. **trace_id 持久化**：工作流/消息执行时正确保存 external_trace_id
2. **追踪查询**：按 trace_id 查询返回完整执行详情（包括节点执行）
3. **inputs 提取**：从 inputs.dify_trace_id 正确提取并持久化
4. **keyword_scope**：各 scope 值返回精准的搜索结果
5. **向后兼容**：不传 keyword_scope 时，行为与原来一致（scope=all）
6. **应用类型覆盖**：Workflow、Chatflow、Chat、Agent 都支持

---

## 8. 前端 API 文档模板

### 8.1 MDX 模板内容（中文）

以下内容需要添加到各应用类型的 MDX 模板中：

```mdx
---

<Heading
  url='/custom/apps/{app_id}/trace/{trace_id}'
  method='GET'
  title='按追踪 ID 查询执行详情'
  name='#trace-query'
/>
<Row>
  <Col>
    通过外部追踪 ID 查询应用执行的完整详情，包括工作流节点执行或 Agent 思考链。

    **追踪 ID 来源**（按优先级）：
    1. HTTP Header: `X-Trace-Id`
    2. Query 参数: `trace_id`
    3. 请求体: `trace_id`
    4. inputs 字段: `dify_trace_id`

    ### Path
    <Properties>
      <Property name='app_id' type='string' key='app_id'>
        应用 ID
      </Property>
      <Property name='trace_id' type='string' key='trace_id'>
        外部追踪 ID
      </Property>
    </Properties>

    ### Response
    <Properties>
    返回执行详情，结构根据应用类型不同：

    - `type` (string) 应用类型：workflow / chat / chatflow
    - `workflow_run` (object) 工作流运行信息（Workflow/Chatflow 应用）
      - `id` (string) 运行 ID
      - `status` (string) 执行状态：running / succeeded / failed / stopped
      - `inputs` (object) 输入参数
      - `outputs` (object) 输出结果
      - `elapsed_time` (float) 执行耗时（秒）
      - `total_tokens` (int) 总 token 数
      - `error` (string) 错误信息
      - `created_at` (string) 创建时间
      - `finished_at` (string) 完成时间
    - `node_executions` (array) 节点执行列表（Workflow/Chatflow 应用）
      - `node_id` (string) 节点 ID
      - `node_type` (string) 节点类型
      - `title` (string) 节点标题
      - `status` (string) 执行状态
      - `inputs` (object) 节点输入
      - `outputs` (object) 节点输出
      - `elapsed_time` (float) 执行耗时
      - `error` (string) 错误信息
    - `message` (object) 消息信息（Chat/Agent/Chatflow 应用）
      - `id` (string) 消息 ID
      - `conversation_id` (string) 对话 ID
      - `query` (string) 用户问题
      - `answer` (string) AI 回答
      - `inputs` (object) 输入参数
      - `status` (string) 消息状态
    - `agent_thoughts` (array) Agent 思考链（Agent 应用）
      - `position` (int) 顺序
      - `thought` (string) 思考内容
      - `tool` (string) 使用的工具
      - `tool_input` (object) 工具输入
      - `observation` (string) 工具返回

    ### Errors
    - 401，未授权
    - 403，无权限访问该应用
    - 404，未找到匹配的执行记录
    </Properties>
  </Col>
  <Col sticky>
    <CodeGroup
      title="Request"
      tag="GET"
      label="/custom/apps/{app_id}/trace/{trace_id}"
      targetCode={`curl -X GET '${props.appDetail.api_base_url}/custom/apps/{app_id}/trace/order-12345' \\
--header 'Authorization: Bearer {api_key}'`}
    />
    <CodeGroup title="Response">
    ```json {{ title: 'Workflow Response' }}
    {
      "type": "workflow",
      "workflow_run": {
        "id": "run_xxx",
        "status": "succeeded",
        "inputs": {"customer_id": "C001"},
        "outputs": {"result": "处理完成"},
        "elapsed_time": 3.5,
        "total_tokens": 1234,
        "error": null,
        "created_at": "2026-02-03T10:00:00Z",
        "finished_at": "2026-02-03T10:00:03Z"
      },
      "node_executions": [
        {
          "node_id": "start",
          "node_type": "start",
          "title": "开始",
          "status": "succeeded",
          "inputs": {},
          "outputs": {},
          "elapsed_time": 0.1
        },
        {
          "node_id": "llm_1",
          "node_type": "llm",
          "title": "LLM 处理",
          "status": "succeeded",
          "inputs": {"prompt": "..."},
          "outputs": {"text": "..."},
          "elapsed_time": 2.8
        }
      ]
    }
    ```
    </CodeGroup>
  </Col>
</Row>
```

### 8.2 更新位置

| 应用类型 | 文件路径 |
|---------|---------|
| 文本生成 | `web/app/components/develop/template/template.{en,zh}.mdx` |
| Workflow | `web/app/components/develop/template/template_workflow.{en,zh}.mdx` |
| Chat | `web/app/components/develop/template/template_chat.{en,zh}.mdx` |
| Chatflow | `web/app/components/develop/template/template_advanced_chat.{en,zh}.mdx` |
| Agent | `web/app/components/develop/template/template_agent.{en,zh}.mdx` |

---

## 9. 相关文件

- [二开规范](../development/README.md)
- [二开 API 文档](../api/README.md)
- [trace_id_helper.py](../../../api/core/helper/trace_id_helper.py) - 现有 trace_id 提取逻辑
- [workflow_app_service.py](../../../api/services/workflow_app_service.py) - 现有日志查询服务
- [workflow_run_fields.py](../../../api/fields/workflow_run_fields.py) - 现有返回字段定义
- [template.zh.mdx](../../../web/app/components/develop/template/template.zh.mdx) - 前端 API 文档模板
