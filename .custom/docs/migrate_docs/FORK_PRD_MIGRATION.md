# Dify 二次开发需求文档

> **目标版本**: Dify 最新版本  
> **基线参考**: 基于 Dify 1.8.1 的二开实践总结  
> **整理日期**: 2026-01-30  
> **总功能数**: 12 个核心功能

---

## 📋 功能清单

| 优先级 | 功能名称 | 复杂度 | 涉及模块 |
| :----- | :------- | :----- | :------- |
| **P0** | 环境配置优化 | 低 | Docker/Nginx |
| **P0** | Sandbox 依赖管理 | 中 | Docker/Sandbox |
| **P1** | DOC 格式文档解析 | 中 | API/RAG |
| **P1** | 远程文件操作接口 | 低 | API/Service |
| **P1** | 工作流日志搜索增强 | 低 | API/Service |
| **P2** | 代码节点文件输出 | 中 | API/Workflow/前端 |
| **P2** | 异步工作流执行接口 | 中 | API/Service |
| **P2** | 工作流重试机制增强 | 中 | API/Workflow/前端 |
| **P2** | 应用日志时区统一 | 低 | API/前端 |
| **P3** | 多工作空间权限控制 | 高 | API/前端 |
| **P3** | 应用分析功能 | 中 | API/前端 |
| **P3** | 应用级模型凭证管理 | 高 | API/前端 |

---

## P0 - 基础设施 🔧

### 1. 环境配置优化

**业务价值**: 提升生产环境稳定性和性能

**功能描述**:
- 优化 Nginx 连接池、超时、缓冲区配置
- 调整 LLM 超时参数 (`TEXT_GENERATION_TIMEOUT_MS` 等)
- 开放 PostgreSQL 和 Redis 端口便于调试
- 更新环境变量示例文件

**实现思路**:
- 修改 `docker/nginx/nginx.conf.template`: 增加 worker_connections、keepalive_timeout
- 修改 `docker/nginx/default.conf.template`: 优化 proxy_buffer、proxy_timeout
- 修改 `docker/.env.example`: 添加性能相关变量及注释
- 修改 `docker/docker-compose.yaml`: 暴露 PG 和 Redis 端口

**验收标准**: 高并发场景下无超时断连，调试工具可直连数据库

---

### 2. Sandbox 依赖管理

**业务价值**: 支持代码节点使用系统依赖库（如 pyzbar、opencv 等）

**功能描述**:
- 支持声明式系统依赖管理 (`apt-requirements.txt`)
- 支持声明式 Python 包管理 (`requirements-custom.txt`)
- 自动修复 ctypes 动态库查找问题
- 容器重启后自动安装依赖

**实现思路**:
- 创建 `docker/volumes/sandbox/dependencies/apt-requirements.txt`: 声明系统库
- 创建 `docker/volumes/sandbox/dependencies/requirements-custom.txt`: 声明 Python 包
- 创建 `docker/volumes/sandbox/init-dependencies.sh`: 启动脚本，自动安装依赖
- 修改 `api/core/helper/code_executor/python3/python3_transformer.py`: 注入 ctypes 修复补丁
- 修改 `docker/docker-compose.yaml`: 挂载依赖配置和安装脚本

**验收标准**: 代码节点中可直接 `import pyzbar`，无需手动安装

---

## P1 - 核心API扩展 🚀

### 3. DOC 格式文档解析

**业务价值**: 支持老旧 `.doc` 格式文档入库

**功能描述**:
- 知识库支持上传 `.doc` 文件
- 工作流文档提取节点支持 `.doc`
- 集成 antiword 解析引擎

**实现思路**:
- 修改 `api/Dockerfile`: 安装 antiword 系统工具
- 创建 `api/core/rag/extractor/antiword_doc_extractor.py`: 实现 AntiwordDocExtractor 类
- 修改 `api/constants/__init__.py`: 添加 `.doc` 到支持扩展名列表
- 修改 `api/core/rag/extractor/extract_processor.py`: 注册新提取器
- 修改 `api/core/workflow/nodes/document_extractor/node.py`: 支持 `.doc` 节点

**验收标准**: 上传 `.doc` 文件可正常解析并分段入库

---

### 4. 远程文件操作接口

**业务价值**: 业务系统通过 URL 直接导入文件到 Dify

**功能描述**:
- 获取远程文件元信息接口
- 下载并上传远程文件到 Dify 接口
- 支持 SSRF 防护代理

**实现思路**:
- 创建 `api/controllers/service_api/app/remote_file.py`: 实现两个接口
  - `GET /v1/remote-files/<url>`: 返回文件名、大小、MIME 类型
  - `POST /v1/remote-files/upload`: 下载远程文件并转为 Dify 文件对象
- 修改 `api/controllers/service_api/__init__.py`: 注册路由
- 修改 `docker/ssrf_proxy/squid.conf.template`: 配置代理白名单

**验收标准**: 通过 API 可将远程 URL 文件导入知识库

---

### 5. 工作流日志搜索增强

**业务价值**: 精准检索工作流执行日志

**功能描述**:
- 支持按字段范围搜索: `all`, `inputs`, `outputs`, `session_id`, `run_id`
- Console API 和 Service API 同时支持
- 新增查询参数 `keyword_scope`

**实现思路**:
- 修改 `api/services/workflow_app_service.py`: 
  - 在 `get_paginate_workflow_app_logs` 方法中解析 `keyword_scope` 参数
  - 根据 scope 构建不同的 SQL 查询条件
- 修改 `api/controllers/console/app/workflow_app_log.py`: 添加参数接收
- 修改 `api/controllers/service_api/app/workflow.py`: 添加参数接收
- 编写单元测试验证各个 scope 的查询准确性

**验收标准**: 可按 `session_id` 精准过滤，不返回无关日志

---

## P2 - 工作流增强 ⚡

### 6. 代码节点文件输出

**业务价值**: 代码节点生成文件供用户下载（如 Excel、PDF）

**功能描述**:
- 代码节点返回 File 类型变量
- 支持自定义文件名和 MIME 类型
- 前端变量选择器识别 File 类型

**实现思路**:
- 修改 `api/core/workflow/nodes/code/entities.py`: 添加 File 类型定义
- 修改 `api/core/workflow/nodes/code/code_node.py`:
  - 检测代码返回值中的 File 对象
  - 上传到文件存储服务获取 URL
  - 转换为标准 File 变量输出
- 修改 `api/core/helper/code_executor/code_executor.py`: 传递 tenant_id 等上下文
- 修改前端 `web/app/components/workflow/_base/components/variable/var-type-picker.tsx`: 添加 File 类型图标
- 在 Sandbox 安装 openpyxl 等文件生成库

**验收标准**: 代码节点生成 Excel 文件，工作流结果可下载

---

### 7. 异步工作流执行接口

**业务价值**: 支持不使用长连接的客户端触发工作流

**功能描述**:
- 立即返回 `workflow_run_id`，不等待执行完成
- 后台完整消费流式响应
- 客户端断开不影响任务执行

**实现思路**:
- 修改 `api/controllers/service_api/app/workflow.py`:
  - 新增 `POST /workflows/run-async` 路由
  - 调用原 run 接口获取 Generator
  - 预读取前 5 个 chunk 提取 workflow_run_id
  - 使用 Flask 应用上下文复制技术创建后台线程
  - 后台线程消费完整 Generator 直到结束
  - 立即返回 workflow_run_id 给客户端

**验收标准**: 接口立即返回，工作流后台完整执行并记录日志

---

### 8. 工作流重试机制增强

**业务价值**: 解决高并发下 LLM 提供商 502/503 错误导致工作流失败

**功能描述**:
- Plugin Stream 层自动捕获 502/503/504 错误并重试
- Graph Engine 支持指数退避策略 (1s → 2s → 4s)
- 前端节点配置支持指数退避开关

**实现思路**:
- 修改 `api/core/plugin/impl/base.py`:
  - 在 `_request_stream` 方法中捕获 HTTP 5xx 错误
  - 实现重试逻辑（最多 3 次）
- 修改 `api/core/workflow/graph_engine/graph_engine.py`:
  - 捕获节点执行异常
  - 根据配置实现指数退避重试
- 修改 `api/core/workflow/nodes/base/entities.py`: 添加指数退避配置字段
- 修改前端 `web/app/components/workflow/nodes/_base/components/retry/retry-on-panel.tsx`: 添加指数退避开关 UI
- 修改 `web/i18n/`: 添加重试相关国际化文案

**验收标准**: OpenRouter 返回 502 时自动重试，工作流最终成功

---

### 9. 应用日志时区统一

**业务价值**: 跨时区团队查看日志时间一致

**功能描述**:
- 新增 `LOG_TZ` 环境变量控制日志时区
- API 返回 `log_timezone` 字段
- 前端所有时间显示遵循统一时区

**实现思路**:
- 修改 `api/services/workspace_service.py`:
  - 读取 `LOG_TZ` 环境变量
  - 在 tenant 信息中添加 `log_timezone` 字段
- 修改 `api/controllers/console/workspace/workspace.py`: 添加字段到返回结构
- 修改前端 `web/context/app-context.tsx`: 添加 `logTimezone` 上下文
- 修改 `web/hooks/use-timestamp.ts`: 优先使用 `logTimezone` 格式化时间
- 修改 `web/app/components/app/log/list.tsx`: 使用统一时区
- 修改 `web/models/common.ts`: 添加类型定义

**验收标准**: 所有用户看到的日志时间统一为 `LOG_TZ` 指定时区

---

## P3 - 高级功能 🎯

### 10. 多工作空间权限控制

**业务价值**: 企业级多租户隔离

**功能描述**:
- 启用 Dify 的多工作空间功能
- 基于角色的权限控制服务
- 前端工作空间选择器增强

**实现思路**:
- 修改 `api/configs/feature/__init__.py`: 开启多工作空间开关
- 修改 `api/controllers/console/feature.py`: 暴露功能开关 API
- 创建 `api/services/workspace_permission_service.py`:
  - 实现 `WorkspacePermissionService` 类
  - 基于角色判断工作空间访问权限
- 修改 `api/controllers/console/workspace/workspace.py`:
  - 查询工作空间列表时调用权限服务过滤
- 修改前端 `web/app/components/header/account-dropdown/workplace-selector/index.tsx`: 
  - 根据权限显示工作空间列表
  - 优化切换逻辑
- 修改 `docker/.env.example`: 添加多工作空间功能开关

**验收标准**: 不同角色用户看到不同的工作空间列表

**注意事项**: 需先调研目标版本是否已原生支持此功能

---

### 11. 应用分析功能

**业务价值**: 查看应用使用情况和趋势分析

**功能描述**:
- 统计概览: 消息数、会话数、用户数、应用数
- 应用排行榜（列表视图 + 饼图视图）
- 趋势分析（支持多选最多 20 个应用）
- 按标签筛选、"今天"时间范围
- 管理员可查看所有工作空间数据

**实现思路**:
- 修改 `api/controllers/console/app/statistic.py`:
  - 新增 `/console/api/apps/statistics/overview` 接口: 聚合统计
  - 新增 `/console/api/apps/statistics/trend` 接口: 趋势数据
  - 实现基于角色的权限过滤
  - 统计工作流运行次数计入消息数
- 创建前端页面 `web/app/(commonLayout)/apps-analytics/page.tsx`: 主页面
- 创建前端组件:
  - `overview-cards.tsx`: 概览卡片
  - `apps-ranking.tsx`: 排行榜（列表+饼图）
  - `trend-chart.tsx`: 趋势图表（ECharts）
- 修改 `web/app/components/header/index.tsx`: 添加"应用分析"导航入口
- 创建 `web/service/apps-analytics.ts`: API 调用服务
- 添加国际化文案 `web/i18n/en-US/apps-analytics.ts` 和 `zh-Hans/apps-analytics.ts`

**验收标准**: 主界面可查看应用统计、排行榜和趋势图

---

### 12. 应用级模型凭证管理

**业务价值**: 不同应用使用不同的模型凭证（如不同预算账号）

**功能描述**:
- 应用独立配置模型凭证
- 覆盖工作空间默认凭证
- 支持 LLM 节点、Agent 节点、Agent 应用
- 完整的 CRUD API 和管理界面
- 插件反向调用支持凭证覆盖

**实现思路**:
- 创建数据库模型 `api/models/app_provider_credential.py`: 
  - AppProviderCredential 模型（app_id、provider、model_type、credentials）
- 创建数据库迁移脚本: 添加 `app_provider_credentials` 表
- 创建 `api/services/app_credential_service.py`:
  - `AppCredentialService` 类
  - 实现凭证的 CRUD 和查询方法
  - 实现凭证覆盖逻辑
- 创建 `api/controllers/console/app/credentials.py`: CRUD API 路由
- 修改 `api/core/workflow/nodes/llm/llm_utils.py`:
  - 在模型实例创建后检查应用级凭证
  - 覆盖工作空间凭证
- 修改 `api/core/workflow/nodes/agent/agent_node.py`: 支持凭证覆盖
- 修改 `api/core/app/apps/agent_chat/app_runner.py`: Agent 应用支持凭证覆盖
- 修改 `api/core/plugin/backwards_invocation/model.py`: 插件反向调用传递 app_id
- 修改 `api/core/plugin/entities/request.py`: 请求结构添加 app_id 字段
- 创建前端页面 `web/app/(appDetailLayout)/[appId]/credentials/page.tsx`: 凭证管理页
- 创建前端组件 `web/app/components/app/credentials/index.tsx`:
  - 凭证列表（按凭证分组）
  - 添加/编辑/删除凭证对话框
  - 模型多选、全选功能
- 修改 `web/app/(appDetailLayout)/[appId]/layout-main.tsx`: 添加"模型凭证"标签页
- 创建 `web/service/apps.ts`: 凭证管理 API 调用
- 添加国际化文案

**验收标准**: 应用 A 使用凭证 X，应用 B 使用凭证 Y，互不影响

---

## 🎯 实施建议

### 分阶段执行顺序

**第一阶段** (1-2 天)
- P0 功能: 环境配置优化、Sandbox 依赖管理
- 为后续开发提供稳定基础

**第二阶段** (2-3 天)
- P1 功能: DOC 格式、远程文件接口、日志搜索
- 快速交付核心业务价值

**第三阶段** (3-4 天)
- P2 功能: 代码节点文件输出、异步工作流、重试机制、时区统一
- 显著提升用户体验

**第四阶段** (4-5 天)
- P3 功能: 多工作空间、应用分析、凭证管理
- 企业级高级能力

### 依赖关系

- **应用分析** 依赖 **多工作空间** 的权限服务
- **应用凭证管理** 无强依赖，但建议在 P3 阶段统一实施
- **代码节点文件输出** 依赖 **Sandbox 依赖管理**

### 风险提示

1. **多工作空间功能**: 目标版本可能已原生支持，需先调研避免重复开发
2. **工作流重试机制**: 注意不要与目标版本的重试逻辑冲突
3. **应用级凭证管理**: 数据库 schema 变更，需提前规划迁移策略

