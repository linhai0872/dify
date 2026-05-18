# 二开功能文档

本目录用于存放二开功能的说明文档和变更记录。

---

## 功能总览

### 已上线

| 功能 | 文档 | 功能开关 |
|------|------|---------|
| 追踪搜索 | [workflow-log-search-enhancement.md](workflow-log-search-enhancement.md) | `DIFY_CUSTOM_TRACE_SEARCH_ENABLED` |
| 原生文档提取 | [native-document-extractors.md](native-document-extractors.md) | `DIFY_CUSTOM_NATIVE_EXTRACTORS_ENABLED` |
| 多工作空间权限 | [multi-workspace-permission.md](multi-workspace-permission.md) | `DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED` |
| 代码节点文件输出 | [code-node-file-output.md](code-node-file-output.md) | — |
| 远程文件操作 | [API 文档](../api/README.md#远程文件操作) | — |
| 应用日志时区统一 | — | `LOG_TZ` / `DIFY_CUSTOM_LOG_TIMEZONE` |

### 待完成

| 功能 | 文档 | 当前状态 | 待办 |
|------|------|---------|------|
| 指数退避重试 | [exponential-backoff-retry.md](exponential-backoff-retry.md) | 后端逻辑已设计，升级至 1.14.x 后重新实现 | 升级后在 graphon 实现后端 + 补全前端配置面板 |
| Workflow 费用显示 | [workflow-cost-display.md](workflow-cost-display.md) | 字段设计完成，未持久化/未展示 | 接入持久化层 + 前端费用展示组件 |

---

## 目录说明

| 文档 | 说明 |
|------|------|
| [CHANGES.md](CHANGES.md) | 变更日志，记录所有二开功能的变更历史 |
| `<feature>.md` | 具体功能文档，每个重大二开功能一个文件 |

---

## 变更日志 (CHANGES.md)

### 更新规则

`CHANGES.md` 通过 `git log` 生成原始数据，手动按类型分类整理：

```bash
# 生成原始日志
git log main..development --pretty=format:"- [%h] %s"

# 手动按 feat/fix/chore 等类型分类整理到 CHANGES.md
```

**前提**：commit message 需遵循 [development/README.md#Commit规范](../development/README.md#commit-规范)

---

## 功能文档

### 创建时机

**需要创建独立文档**：
- 新增完整的业务功能模块（如多租户、审计日志）
- 功能配置复杂，需要详细说明
- 面向最终用户的功能（需要用户了解如何使用）

**无需创建文档**：
- 内部技术优化
- 简单的 bug 修复
- 配置项少于 3 个的简单功能

### 文档规范

- 文件名使用 `kebab-case`，如 `multitenancy.md`
- 内容包括：概述、配置、使用方法、注意事项

### 文档模板

```markdown
# 功能名称

## 概述
简要描述功能目的和价值。

## 配置

| 环境变量                | 默认值 | 说明     |
| ----------------------- | ------ | -------- |
| DIFY_CUSTOM_XXX_ENABLED | false  | 是否启用 |

## 使用方法
1. 步骤一
2. 步骤二

## 相关文件
- `api/path/to/file.py`
```
