# 二开功能文档

本目录用于存放二开功能的说明文档和变更记录。

---

## 目录说明

| 文档 | 说明 |
|------|------|
| [CHANGES.md](CHANGES.md) | 变更日志，记录所有二开功能的变更历史 |
| `<feature>.md` | 具体功能文档，每个重大二开功能一个文件 |

---

## 变更日志 (CHANGES.md)

### 更新规则

`CHANGES.md` 通过 `git log` 自动生成，每次发布二开功能时更新：

```bash
# 生成变更日志
git log main..development --pretty=format:"- [%h] %s" > .custom/docs/features/CHANGES.md
```

**前提**：commit message 需遵循 [development/README.md#Commit规范](../development/README.md#commit-规范)

```
<类型>(<范围>): <标题>

示例：feat(api): 添加多租户支持
```

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

## 注意事项
- 注意点 1
- 注意点 2
```
