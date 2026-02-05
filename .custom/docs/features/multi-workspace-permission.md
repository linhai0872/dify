# 多工作空间权限控制

## 功能概述

多工作空间权限控制功能在 Dify 现有的多工作空间（Tenant）基础上，新增**系统级角色**概念，支持跨工作空间的用户管理和成员分配。

## 系统角色

| 角色 | 说明 | 能力 |
|------|------|------|
| `super_admin` | 超级管理员 | 查看所有工作空间、管理所有用户、分配成员到任意工作空间 |
| `workspace_admin` | 工作空间管理员 | 管理被分配的工作空间（预留，当前与 normal 相同） |
| `normal` | 普通用户 | 默认角色，只能访问已加入的工作空间 |

## 与工作空间角色的关系

系统角色和工作空间角色是**独立且叠加**的：

```
系统级权限 (system_role)
├── super_admin → 管理所有用户、查看所有工作空间
├── workspace_admin → 预留
└── normal → 默认
        ↓
工作空间级权限 (TenantAccountRole)
├── owner → 工作空间所有者
├── admin → 管理员
├── editor → 编辑者
├── normal → 普通成员
└── dataset_operator → 数据集操作员
```

**重要规则**：
- 超管可以**看到**所有工作空间（包括未加入的）
- 超管进入未加入的工作空间时是**只读模式**
- 超管想操作某个工作空间，需通过管理界面将自己加入

## 启用功能

### 1. 设置环境变量

```bash
# 在 docker/.env 或 .custom/env/.env.custom.* 中添加
DIFY_CUSTOM_MULTI_WORKSPACE_PERMISSION_ENABLED=true
```

### 2. 执行数据库迁移

```bash
cd api
flask db upgrade
```

### 3. 设置首个超级管理员

```bash
# 方式一：CLI 命令（推荐）
flask custom-set-super-admin --email admin@example.com

# 方式二：环境变量（启动时自动设置）
DIFY_CUSTOM_INITIAL_SUPER_ADMIN_EMAIL=admin@example.com
```

## CLI 命令

```bash
# 设置用户为超管
flask custom-set-super-admin --email <email>

# 列出所有超管
flask custom-list-super-admins

# 移除超管权限（需要确认）
flask custom-remove-super-admin --email <email> --confirm
```

## API 端点

### 用户管理 API（仅超管可访问）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/console/api/custom/admin/users` | 获取用户列表（支持分页、搜索、筛选） |
| GET | `/console/api/custom/admin/users/<id>` | 获取用户详情 |
| PUT | `/console/api/custom/admin/users/<id>/role` | 修改用户系统角色 |
| PUT | `/console/api/custom/admin/users/<id>/status` | 修改用户状态（启用/禁用） |
| GET | `/console/api/custom/admin/system-roles` | 获取可用系统角色列表 |

### 公共 API（已登录用户可访问）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/console/api/custom/me/system-role` | 获取当前用户系统角色及功能开关状态 |
| GET | `/console/api/custom/feature-flags` | 获取功能开关状态 |

### 成员分配 API（仅超管可访问）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/console/api/custom/admin/workspaces` | 获取所有工作空间列表（支持分页、搜索） |
| GET | `/console/api/custom/admin/workspaces/<id>/members` | 获取工作空间成员列表 |
| POST | `/console/api/custom/admin/workspaces/<id>/members` | 添加成员到工作空间 |
| PUT | `/console/api/custom/admin/workspaces/<id>/members/<uid>` | 修改成员角色 |
| DELETE | `/console/api/custom/admin/workspaces/<id>/members/<uid>` | 移除成员 |
| GET | `/console/api/custom/admin/workspaces/<id>/available-users` | 获取可添加的用户列表 |
| GET | `/console/api/custom/admin/workspace-roles` | 获取可用工作空间角色列表 |

### 工作空间列表 API（增强）

`GET /console/api/workspaces` 响应增加 `role` 字段：

```json
{
  "workspaces": [
    {
      "id": "workspace-1",
      "name": "My Workspace",
      "plan": "sandbox",
      "status": "normal",
      "created_at": 1234567890,
      "current": true,
      "role": "owner"  // 新增：用户在该工作空间的角色，null 表示未加入
    }
  ]
}
```

## 安全机制

### 保护逻辑

1. **防止自我降级**：超管不能将自己从 super_admin 降级
2. **防止自我禁用**：用户不能禁用自己的账户
3. **最后 owner 保护**：不能移除工作空间的最后一个 owner
4. **功能开关**：关闭时所有自定义逻辑不生效，保持原有行为

### 权限检查

- 所有管理 API 都使用 `@super_admin_required` 装饰器
- 功能关闭时，管理 API 返回 404

## 与现有功能的区分

| 维度 | 现有成员管理 | 新增管理功能 |
|------|-------------|-------------|
| 入口 | 设置 Modal (`?tab=members`) | Admin 管理界面（前端待实现） |
| 管理范围 | 当前工作空间成员 | 跨工作空间所有用户 |
| 权限基础 | 工作空间角色 (owner/admin) | 系统角色 (super_admin) |
| 用途 | 团队自管理（邀请加入） | 系统管理员统一分配 |

## 数据模型

### accounts 表新增字段

```sql
ALTER TABLE accounts ADD COLUMN system_role VARCHAR(20) DEFAULT 'normal';
```

### SystemRole 枚举

```python
class SystemRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    WORKSPACE_ADMIN = "workspace_admin"
    NORMAL = "normal"
```

## 文件清单

### 后端

| 文件 | 说明 |
|------|------|
| `api/custom/feature_flags.py` | 功能开关 |
| `api/custom/models/custom_account_ext.py` | SystemRole 枚举 |
| `api/custom/services/custom_system_permission_service.py` | 权限服务 |
| `api/custom/services/custom_admin_user_service.py` | 用户管理服务 |
| `api/custom/services/custom_admin_member_service.py` | 成员管理服务 |
| `api/custom/wraps/custom_permission_wraps.py` | 权限装饰器 |
| `api/custom/commands.py` | CLI 命令 |
| `api/controllers/console/custom/admin_user.py` | 用户管理 API |
| `api/controllers/console/custom/admin_workspace.py` | 成员管理 API |
| `api/migrations/versions/2026_02_04_custom_add_system_role_to_accounts.py` | 数据库迁移 |

### 后端（修改的官方文件）

| 文件 | 修改内容 |
|------|----------|
| `api/models/account.py` | 添加 `system_role` 字段到 Account 模型 |
| `api/controllers/console/workspace/workspace.py` | 增强工作空间列表 API，添加 role 字段 |
| `api/controllers/console/__init__.py` | 注册 custom 控制器 |
| `api/extensions/ext_commands.py` | 注册 custom CLI 命令 |

### 前端

| 路径 | 说明 |
|------|------|
| `web/app/(commonLayout)/custom-admin/layout.tsx` | 管理页面布局（含左侧导航） |
| `web/app/(commonLayout)/custom-admin/users/page.tsx` | 用户管理页面 |
| `web/app/(commonLayout)/custom-admin/workspaces/page.tsx` | 工作空间列表页面 |
| `web/app/(commonLayout)/custom-admin/workspaces/[workspaceId]/members/page.tsx` | 成员管理页面 |
| `web/models/custom/admin.ts` | 类型定义 |
| `web/service/custom/admin-user.ts` | 用户管理 API 服务 |
| `web/service/custom/admin-member.ts` | 成员管理 API 服务 |
| `web/hooks/custom/use-system-role.ts` | 系统角色 Hook |
| `web/i18n/zh-Hans/custom.json` | 中文翻译 |
| `web/i18n/en-US/custom.json` | 英文翻译 |

### 前端（修改的官方文件）

| 文件 | 修改内容 |
|------|----------|
| `web/models/common.ts` | IWorkspace 类型添加 `role` 字段 |
| `web/app/components/header/account-dropdown/index.tsx` | 添加「系统管理」入口 |
| `web/app/components/header/account-dropdown/workplace-selector/index.tsx` | 显示工作空间角色标签 |

## 测试

```bash
# 运行所有自定义测试
uv run --project api pytest api/tests/custom/ -v

# 运行权限相关测试
uv run --project api pytest api/tests/custom/services/test_custom_system_permission_service.py -v
uv run --project api pytest api/tests/custom/models/test_system_role.py -v
```
