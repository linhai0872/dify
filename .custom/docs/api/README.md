# 二开 API 文档

> 本文档记录所有二次开发 API 接口，格式参考 Dify 官方 API 文档规范。
>
> **API 设计原则** 见主文档 [development/README.md](../development/README.md#api-规范)

---

## 目录

- [一、编写规范](#一编写规范)
  - [Base URL](#base-url)
  - [命名规范](#命名规范)
  - [认证方式](#认证方式)
  - [通用错误码](#通用错误码)
  - [响应格式](#响应格式)
- [二、接口文档模板](#二接口文档模板)
  - [标准接口模板](#标准接口模板)
  - [应用 API 模板（MDX）](#应用-api-模板mdx)
- [三、开发指南](#三开发指南)
  - [添加新 API 步骤](#添加新-api-步骤)
  - [文档更新位置](#文档更新位置)
- [四、Console API](#四console-api)
- [五、Service API](#五service-api)

---

## 一、编写规范

### Base URL

```bash
# Console API (管理后台)
{DIFY_URL}/console/api/custom/

# Service API (应用调用)
{DIFY_URL}/v1/custom/
```

### 命名规范

```bash
# Console API：管理后台功能
/console/api/custom/<feature>/
示例: /console/api/custom/tenants
      /console/api/custom/audit-logs

# Service API：应用调用能力
/v1/custom/<feature>/
示例: /v1/custom/remote-files
      /v1/custom/webhooks/callback
```

**命名规则**：
- 使用 `/custom/` 前缀与官方接口隔离
- `<feature>` 使用 kebab-case（如 `remote-files`）
- 资源操作遵循 REST 风格：GET 查询、POST 创建、PUT 更新、DELETE 删除

### 认证方式

| API 类型 | 认证方式 |
|---------|---------|
| Console API | 用户 Session (Cookie) |
| Service API | API Key (`Authorization: Bearer {api_key}`) |

### 通用错误码

| Code | Status | 说明 |
|------|--------|------|
| `invalid_param` | 400 | 参数错误 |
| `unauthorized` | 401 | 未授权 |
| `forbidden` | 403 | 权限不足 |
| `not_found` | 404 | 资源不存在 |
| `internal_error` | 500 | 服务器内部错误 |

### 响应格式

**成功响应**

```json
{
  "result": "success",
  "data": {
    // 响应数据
  }
}
```

**错误响应**

```json
{
  "result": "error",
  "code": "error_code",
  "message": "错误描述",
  "status": 400
}
```

---

## 二、接口文档模板

### 标准接口模板

添加新 API 时，复制以下模板并填写信息：

```markdown
### <API_NAME>

**功能描述**：简要描述接口功能（1-2 句话）

**端点**：`<METHOD> <PATH>`

**认证**：`Session` / `API Key`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `param_name` | `string` | 是 | 参数说明 |

#### 响应

**成功响应** (Status: 200)

```json
{
  "result": "success",
  "data": {
    // 响应数据
  }
}
```

**错误响应**

| Status | Code | 说明 |
|--------|------|------|
| 400 | `invalid_param` | 参数错误 |
| 403 | `forbidden` | 权限不足 |

#### 代码示例

```bash
# Request
curl -X POST '{DIFY_URL}/console/api/custom/xxx' \
  -H 'Authorization: Bearer {api_key}' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "param": "value"
  }'
```
```

### 应用 API 模板（MDX）

如果二开接口涉及 **Dify 应用 API**（用户通过 App API Key 调用，前端需要展示）：

**同步更新要求**：必须同时更新以下三个文档

| 文档 | 格式 | 用途 |
|------|------|------|
| `docs/api/README.md` | Markdown | 开发参考（本文档）|
| `web/app/components/develop/template/template.en.mdx` | MDX | 前端展示（英文）|
| `web/app/components/develop/template/template.zh.mdx` | MDX | 前端展示（中文）|

**MDX 文档格式**：使用与 Dify 官方相同的组件（`Heading`、`Row`、`Col`、`Properties`、`CodeGroup`）

```markdown
<Heading url='/custom/xxx' method='POST' title='Feature Name' />
<Row>
  <Col>功能描述、参数说明...</Col>
  <Col sticky><CodeGroup title="Request" ... /></Col>
</Row>
```

详细组件说明见 [development/README.md#API规范](../development/README.md#api-规范)。

---

## 三、开发指南

### 添加新 API 步骤

1. **创建路由**：在 `api/controllers/custom/` 创建路由文件
2. **实现逻辑**：遵循响应格式规范
3. **更新文档**：
   - 按模板在本文档记录接口
   - 更新对应功能模块的快速索引表
4. **测试验证**：运行 `make -f Makefile.custom test-custom`

### 文档更新位置

| API 类型 | 文档位置 | 功能模块示例 |
|---------|---------|-------------|
| Console API | [Console API](#四console-api) | 用户管理、系统配置、审计日志 |
| Service API | [Service API](#五service-api) | 消息处理、数据同步、Webhook |
| 应用 API | `web/app/components/develop/template/` | 与官方应用 API 一同展示 |

### 安全检查

API 开发完成后的安全检查见 [workflow/code-review-checklist.md](../development/workflow/code-review-checklist.md#五安全检查)。

---

## 四、Console API

管理后台功能的二开接口。

### 追踪搜索

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/console/api/custom/apps/<app_id>/trace/<trace_id>` | GET | 按追踪 ID 查询执行详情 | ✅ 已实现 |

#### 按追踪 ID 查询执行详情

**功能描述**：通过外部追踪 ID 查询应用执行的完整详情，包括工作流节点执行或 Agent 思考链。

**端点**：`GET /console/api/custom/apps/<app_id>/trace/<trace_id>`

**认证**：`Session`

##### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `app_id` | `string` (path) | 是 | 应用 ID |
| `trace_id` | `string` (path) | 是 | 外部追踪 ID（来自 X-Trace-Id 或 inputs.dify_trace_id） |

##### 响应

**成功响应 - Workflow 应用** (Status: 200)

```json
{
  "type": "workflow",
  "workflow_run": {
    "id": "run_xxx",
    "status": "succeeded",
    "inputs": {"key": "value"},
    "outputs": {"result": "..."},
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

**成功响应 - Chat/Agent 应用** (Status: 200)

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

**成功响应 - Chatflow 应用** (Status: 200)

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
    "status": "succeeded",
    "inputs": {},
    "outputs": {},
    "elapsed_time": 2.1
  },
  "node_executions": [...]
}
```

**错误响应**

| Status | Code | 说明 |
|--------|------|------|
| 401 | `unauthorized` | 未登录 |
| 403 | `forbidden` | 无权限访问该应用 |
| 404 | `not_found` | 未找到匹配的执行记录 |

##### 代码示例

```bash
curl -X GET '{DIFY_URL}/console/api/custom/apps/{app_id}/trace/order-12345' \
  -H 'Cookie: session=...'
```

---

### 用户管理

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| *暂无二开接口* | | | |

### 系统配置

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| *暂无二开接口* | | | |

### 审计日志

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| *暂无二开接口* | | | |

---

## 五、Service API

应用调用能力的二开接口。

### 远程文件操作

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/v1/custom/remote-files/<url>` | GET | 获取远程文件元信息 | ✅ 已实现 |
| `/v1/custom/remote-files/upload` | POST | 下载并上传远程文件 | ✅ 已实现 |

#### 获取远程文件信息

**功能描述**：获取远程文件的元信息，包括文件类型和大小。通过 SSRF 防护代理访问远程 URL。

**端点**：`GET /v1/custom/remote-files/<url>`

**认证**：`API Key`

##### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | `string` (path) | 是 | 远程文件的 URL（需要 URL 编码） |

##### 响应

**成功响应** (Status: 200)

```json
{
  "file_type": "application/pdf",
  "file_length": 1024000
}
```

**错误响应**

| Status | Code | 说明 |
|--------|------|------|
| 400 | `remote_file_upload_error` | 无法获取远程文件 |
| 401 | `unauthorized` | API Token 无效 |

##### 代码示例

```bash
curl -X GET '{DIFY_URL}/v1/custom/remote-files/https%3A%2F%2Fexample.com%2Ffile.pdf' \
  -H 'Authorization: Bearer {api_key}'
```

---

#### 上传远程文件

**功能描述**：从远程 URL 下载文件并上传到 Dify 存储。通过 SSRF 防护代理下载文件。

**端点**：`POST /v1/custom/remote-files/upload`

**认证**：`API Key`

##### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | `string` | 是 | 远程文件的 URL |
| `user` | `string` | 是 | 用户标识，需与发送消息接口的 user 一致 |

##### 响应

**成功响应** (Status: 201)

```json
{
  "id": "72fa9618-8f89-4a37-9b33-7e1178a24a67",
  "name": "file.pdf",
  "size": 1024000,
  "extension": ".pdf",
  "url": "https://dify.example.com/files/xxx/file-preview?sign=...",
  "mime_type": "application/pdf",
  "created_by": "user-123",
  "created_at": 1706500000
}
```

**错误响应**

| Status | Code | 说明 |
|--------|------|------|
| 400 | `remote_file_upload_error` | 无法获取远程文件 |
| 400 | `invalid_param` | URL 格式无效 |
| 401 | `unauthorized` | API Token 无效 |
| 413 | `file_too_large` | 文件太大 |
| 415 | `unsupported_file_type` | 不支持的文件类型 |

##### 代码示例

```bash
curl -X POST '{DIFY_URL}/v1/custom/remote-files/upload' \
  -H 'Authorization: Bearer {api_key}' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "url": "https://example.com/file.pdf",
    "user": "abc-123"
  }'
```

---

### 追踪搜索

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/v1/custom/apps/<app_id>/trace/<trace_id>` | GET | 按追踪 ID 查询执行详情 | ✅ 已实现 |

#### 按追踪 ID 查询执行详情 (Service API)

**功能描述**：通过外部追踪 ID 查询应用执行的完整详情。支持通过 `X-Trace-Id` Header、`trace_id` 参数或 `inputs.dify_trace_id` 传入的追踪 ID。

**端点**：`GET /v1/custom/apps/<app_id>/trace/<trace_id>`

**认证**：`API Key`

##### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `app_id` | `string` (path) | 是 | 应用 ID |
| `trace_id` | `string` (path) | 是 | 外部追踪 ID |

##### 响应

响应结构与 Console API 一致，参见上方 [按追踪 ID 查询执行详情](#按追踪-id-查询执行详情)。

##### 代码示例

```bash
# 1. 调用工作流时传入 trace_id
curl -X POST '{DIFY_URL}/v1/workflows/run' \
  -H 'Authorization: Bearer {api_key}' \
  -H 'X-Trace-Id: order-12345' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "inputs": {"customer_id": "C001"},
    "response_mode": "blocking",
    "user": "user-123"
  }'

# 2. 按 trace_id 查询完整执行详情
curl -X GET '{DIFY_URL}/v1/custom/apps/{app_id}/trace/order-12345' \
  -H 'Authorization: Bearer {api_key}'
```

---

### 消息处理

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| *暂无二开接口* | | | |

### 数据同步

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| *暂无二开接口* | | | |

### Webhook

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| *暂无二开接口* | | | |
