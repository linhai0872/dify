# Dify Fork 二次开发规范

> 本文档定义了 Dify Fork 项目的分支策略、编码规范和工作流程。

---

## 目录

1. [分支策略](#分支策略)
2. [开发流程](#开发流程)
3. [环境与部署](#环境与部署)
4. [环境配置管理](#环境配置管理)
5. [Sandbox 依赖管理](#sandbox-依赖管理)
6. [编码规范](#编码规范)
7. [命名规范](#命名规范)
8. [Commit 规范](#commit-规范)
9. [功能开关](#功能开关)
10. [测试策略](#测试策略)
11. [API 规范](#api-规范)
12. [数据库迁移管理](#数据库迁移管理)
13. [变更追踪](#变更追踪)
14. [回滚策略](#回滚策略)
15. [同步与升级](#同步与升级)

---

## 分支策略

```
upstream/main      ──→ 官方上游（只读）
origin/main        ──→ 与上游同步（不修改）
origin/development ──→ 二开主分支（测试环境）
origin/production  ──→ 稳定版本（生产环境）
```

| 分支          | 用途     | 可直接提交              |
| ------------- | -------- | ----------------------- |
| `main`        | 上游镜像 | ❌ 只同步                |
| `development` | 开发测试 | ✅                       |
| `production`  | 生产部署 | ❌ 只从 development 合并 |

---

## 开发流程

### 功能开发

```bash
# 1. 创建功能分支
git checkout development
git checkout -b feature/xxx

# 2. 开发完成后合并
git checkout development
git merge feature/xxx
git branch -d feature/xxx  # 删除临时分支

# 3. 测试通过后发布
git checkout production
git merge development
```

### 同步上游

按官方版本发布频率适当执行，同步前先查看 [Release Notes](https://github.com/langgenius/dify/releases)。

```bash
git fetch upstream
git checkout main
git rebase upstream/main
git push origin main

git checkout development
git rebase main  # 解决冲突
git push origin development --force-with-lease
```

---

## 快速开始

### 三环境对应关系

| 环境 | 分支 | 启动方式 | 一键命令 |
|------|------|----------|---------|
| **开发** | feature/* | 源码热重载 | `dev-setup` → `dev-start` |
| **测试** | development | Docker镜像 | `test-setup` → `test-start` |
| **生产** | production | Docker镜像 | `prod-setup` → `prod-start` |

### 命令命名规范

所有命令遵循 `{env}-{action}` 格式，类似 docker compose：

| 操作 | 开发环境 | 测试环境 | 生产环境 |
|------|---------|---------|---------|
| **初始化** | `dev-setup` | `test-setup` | `prod-setup` |
| **一键启动** | `dev-start` | `test-start` | `prod-start` |
| **启动容器** | `dev-up` | `test-up` | `prod-up` |
| **停止容器** | `dev-down` | `test-down` | `prod-down` |
| **重启容器** | `dev-restart` | `test-restart` | `prod-restart` |
| **查看日志** | `dev-logs` | `test-logs` | `prod-logs` |

**区别说明**：
- `*-start`: 一键启动，包含构建/迁移等完整流程
- `*-up`: 仅启动容器，不构建/不拉取镜像
- `*-restart`: 快速重启，调用 down + up

### 常用命令

```bash
# 查看所有命令
make -f Makefile.custom help

# 开发环境
make -f Makefile.custom dev-setup        # 1. 初始化
make -f Makefile.custom dev-start        # 2. 一键启动
make -f Makefile.custom dev-down         # 停止
make -f Makefile.custom dev-restart      # 重启

# 测试环境
make -f Makefile.custom test-setup       # 1. 初始化
make -f Makefile.custom test-start       # 2. 一键启动 (含构建)
make -f Makefile.custom test-restart     # 快速重启 (不重新构建)

# 生产环境
make -f Makefile.custom prod-setup       # 1. 初始化
make -f Makefile.custom prod-start       # 2. 一键部署 (构建+推送+滚动更新)
make -f Makefile.custom prod-deploy      # 滚动更新 (零停机)
make -f Makefile.custom prod-restart     # 快速重启 (不拉取新镜像)

# 同步上游
make -f Makefile.custom sync-upstream
```

更多命令见 `make -f Makefile.custom help`

---

## 环境变量管理

### 核心原则

1. **官方配置不动**: `api/.env`、`web/.env`、`docker/.env` 从 `.env.example` 复制后保持不变
2. **二开配置分环境**: 三套独立文件 `.custom/env/.env.custom.{dev,test,prod}`
3. **自动加载合并**: Makefile 启动时自动处理环境变量

### 快速开始

**开发环境**:
```bash
make -f Makefile.custom dev-setup         # 1. 初始化配置
# 编辑 .custom/env/.env.custom.dev
make -f Makefile.custom dev-start         # 2. 一键启动
```

**测试环境**:
```bash
make -f Makefile.custom test-setup        # 1. 初始化配置
# 编辑 .custom/env/.env.custom.test
make -f Makefile.custom test-start        # 2. 一键启动
```

**生产环境**:
```bash
make -f Makefile.custom prod-setup        # 1. 初始化配置
# 编辑 .custom/env/.env.custom.prod
make -f Makefile.custom prod-start        # 2. 一键部署
```

### 文件结构

```bash
.custom/env/
├── .env.custom.example    # 模板 (check-in)
├── .env.custom.dev        # 开发环境 (git ignore)
├── .env.custom.test       # 测试环境 (git ignore)
└── .env.custom.prod       # 生产环境 (git ignore)
```

### 二开变量规范

所有二开功能开关统一前缀 `DIFY_CUSTOM_<FEATURE>_ENABLED`：

```bash
# .custom/env/.env.custom.dev
DIFY_CUSTOM_MULTITENANCY_ENABLED=true
DIFY_CUSTOM_EXTERNAL_API_URL=http://localhost:8000
DIFY_CUSTOM_DEBUG=true
```

不同环境只需修改具体值（如 URL、Bucket 名称），功能开关保持一致。

### 常用命令

```bash
# 查看帮助
make -f Makefile.custom help

# 手动合并环境变量（调试用）
make -f Makefile.custom env-merge ENV=test

# 查看合并结果
tail -20 docker/.env
```

---

## 环境配置管理

### 核心原则

1. **幂等性优先**: 多次执行相同操作，结果保持一致
2. **配置分层**: 官方配置 → 二开配置 → 运行时配置
3. **最小重置**: 只在必要时重置配置文件

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 登录后 401 重定向 | `SECRET_KEY` 为空 | 在 `.env.custom.dev` 中设置 |
| 配置修改不生效 | 旧版 Makefile 非幂等 | 更新 Makefile 或删除 `.env` |
| 插件功能无法使用 | 密钥不匹配 | 检查 `INNER_API_KEY_FOR_PLUGIN` |

### 详细文档

完整的环境配置管理指南，包括：
- 配置文件结构
- 幂等性设计原理
- 正确修改配置的方法
- 故障排查步骤

📖 **[环境配置管理指南](environment-config.md)**

---

## Sandbox 依赖管理

Dify 代码节点运行在隔离的 Sandbox 环境中。如需使用第三方 Python 库或系统级依赖（如 `pyzbar`、`opencv` 等），需通过自定义 Sandbox 镜像实现。

### 文件结构

```
.custom/docker/sandbox/
├── Dockerfile.sandbox-custom     # 自定义镜像（安装系统依赖）
└── system-requirements.txt       # 系统依赖声明（apt 包名）

docker/volumes/sandbox/dependencies/
└── python-requirements.txt       # Python 包声明（原生机制）
```

### 添加依赖

**Python 包**（无需重建镜像）：

```bash
# 1. 编辑依赖文件
vim docker/volumes/sandbox/dependencies/python-requirements.txt

# 2. 刷新依赖（或等待 30 分钟自动刷新）
make -f Makefile.custom sandbox-refresh-deps
```

**系统依赖**（需重建镜像）：

```bash
# 1. 编辑系统依赖
vim .custom/docker/sandbox/system-requirements.txt

# 2. 重建镜像
make -f Makefile.custom sandbox-rebuild

# 3. 重启服务
make -f Makefile.custom dev-down && make -f Makefile.custom dev-up
```

### 常用命令

```bash
make -f Makefile.custom sandbox-build         # 构建镜像（当前架构）
make -f Makefile.custom sandbox-rebuild       # 强制重建（不使用缓存）
make -f Makefile.custom sandbox-build-multiarch  # 构建多架构镜像
make -f Makefile.custom sandbox-test-deps     # 测试依赖是否正常
make -f Makefile.custom sandbox-info          # 查看容器信息
```

### 环境变量

在 `.custom/env/.env.custom.*` 中配置：

```bash
# 使用自定义镜像（留空则使用官方镜像）
SANDBOX_IMAGE=dify-sandbox-custom:latest

# PIP 镜像加速
PIP_MIRROR_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

### 技术原理

部分 Python 库（如 `pyzbar`）依赖系统动态库（如 `libzbar.so`）。Sandbox 使用 chroot 隔离，`ctypes.util.find_library()` 无法正常查找库文件。

**解决方案**：在自定义 Dockerfile 中安装系统依赖并创建符号链接：

```dockerfile
# 安装系统依赖
RUN apt-get install -y libzbar0

# 创建符号链接（解决 ctypes 查找问题）
RUN ln -sf libzbar.so.0 /usr/lib/$ARCH_DIR/libzbar.so && ldconfig
```

---

## 编码规范

### 核心原则

| 原则             | 说明                                |
| ---------------- | ----------------------------------- |
| **隔离优于修改** | 新增文件 > 继承扩展 > 直接修改      |
| **配置外置**     | 用环境变量/配置文件控制二开功能开关 |
| **最小侵入**     | 修改官方文件时，改动行数越少越好    |

### 后端 (api/)

**1. Flask 扩展**
```
api/extensions/
├── ext_xxx.py          # 官方
└── ext_custom_xxx.py   # ✅ 二开（新增文件）
```

**2. 服务层继承**
```python
# ✅ api/custom/services/app_service_ext.py
from services.app_service import AppService

class AppServiceExt(AppService):
    def custom_method(self):
        ...
```

**3. API 路由**
```
api/controllers/
├── console/           # 官方路由
└── custom/            # ✅ 二开路由（新增目录）
```

**4. 数据库迁移**
```
api/migrations/versions/
└── 2026_01_27_custom_xxx.py  # 表名: custom_xxx
```

### 前端 (web/)

**1. 组件**
```
web/app/components/
├── base/              # 官方
└── custom/            # ✅ 二开
```

**2. 页面**
```
web/app/(commonLayout)/
├── apps/              # 官方
└── custom-feature/    # ✅ 二开
```

**3. Hook**
```
web/hooks/
├── use-xxx.ts         # 官方
└── use-custom-xxx.ts  # ✅ 二开
```

### 修改官方文件时

1. **最小化改动**：只改必要的行
2. **添加注释标记**：
```python
# [CUSTOM] 二开: 功能描述
custom_code_here()
# [/CUSTOM]
```

---

## 命名规范

### 后端 (Python)

| 类型     | 规范                        | 示例                       |
| -------- | --------------------------- | -------------------------- |
| 文件名   | snake_case + `custom_` 前缀 | `custom_tenant_service.py` |
| 类名     | PascalCase                  | `CustomTenantService`      |
| 函数     | snake_case                  | `get_tenant_by_id()`       |
| 常量     | UPPER_SNAKE_CASE            | `CUSTOM_MAX_TENANTS`       |
| 数据库表 | snake_case + `custom_` 前缀 | `custom_tenants`           |

### 前端 (TypeScript/React)

| 类型      | 规范           | 示例                      |
| --------- | -------------- | ------------------------- |
| 目录      | kebab-case     | `custom-tenant-selector/` |
| 组件文件  | kebab-case.tsx | `tenant-selector.tsx`     |
| 组件名    | PascalCase     | `TenantSelector`          |
| Hook 文件 | use-xxx.ts     | `use-custom-tenant.ts`    |
| Hook 函数 | useXxx         | `useCustomTenant()`       |
| 工具函数  | camelCase      | `formatTenantName()`      |
| 类型/接口 | PascalCase     | `CustomTenantConfig`      |

### 通用

- 二开新增使用 `custom`/`Custom` 前缀
- 继承官方类使用 `Ext` 后缀：`AppServiceExt`
- 避免缩写，保持可读性

---

## Commit 规范

### 格式

```
<类型>(<范围>): <标题>

<正文>
```

- **标题**：50 字内，中文
- **范围**：可选，如 `api`、`web`、`workflow`
- **正文**：可选，分点描述

### 类型

包括但不限于以下提交类型：

| 类型       | 说明      |
| ---------- | --------- |
| `feat`     | 新功能    |
| `fix`      | Bug 修复  |
| `refactor` | 重构      |
| `perf`     | 性能优化  |
| `style`    | 代码格式  |
| `test`     | 测试      |
| `docs`     | 文档      |
| `build`    | 构建/依赖 |
| `ci`       | CI/CD     |
| `chore`    | 杂项      |
| `sync`     | 同步上游  |

### 示例

```bash
# 简单
feat(api): 添加自定义用户权限模块

# 详细
feat(api): 添加多租户支持

- 新增 TenantService 处理租户隔离
- 扩展 User 模型增加 tenant_id 字段
- 添加租户切换 API /api/v1/tenant/switch

# 修改官方文件
refactor(api): [CUSTOM] 重构 app_service 支持多租户

- 修改 api/services/app_service.py (+15 行)
- 原因：官方不支持多租户，必须修改核心文件
```

修改官方文件的 commit 用 `[CUSTOM]` 标记，便于 `git log --grep="\[CUSTOM\]"` 追溯。

---

## 功能开关

二开功能使用独立环境变量控制，便于灰度发布和故障隔离。

```bash
# .env 格式
DIFY_CUSTOM_<FEATURE>_ENABLED=true|false

# 示例
DIFY_CUSTOM_MULTITENANCY_ENABLED=true
DIFY_CUSTOM_AUDIT_LOG_ENABLED=false
```

工具函数放置于 `api/custom/feature_flags.py`。

---

## 测试策略

| 类型     | 官方覆盖 | 二开需要 | 说明                   |
| -------- | -------- | -------- | ---------------------- |
| 单元测试 | ✅        | ❌        | 官方已覆盖核心逻辑     |
| 集成测试 | ✅        | ✅        | 验证二开功能端到端可用 |
| E2E 测试 | ❌        | ❌        | ROI 低，跳过           |

### 测试目录

```
api/tests/custom/
├── test_multitenancy.py     # 多租户功能
└── test_custom_auth.py      # 自定义认证
```

### 测试原则

- 每个功能 1-2 个测试文件，覆盖核心路径
- 使用 AAA 模式：Arrange → Act → Assert
- 不追求覆盖率

### 执行测试

```bash
make -f Makefile.custom test-custom            # 二开测试
cd api && uv run pytest tests/custom/ -v       # 手动执行
```

---

## API 规范

二开 API 使用 `/custom/` 前缀隔离，分为两类：

| API 类型 | 前缀 | 用途 | 认证 |
|---------|------|------|------|
| Console API | `/console/api/custom/` | 管理后台功能 | Session |
| Service API | `/v1/custom/` | 应用调用能力 | API Key |

详细规范（命名、响应格式、错误码、文档模板）见 [api/README.md](../api/README.md)

---

## 数据库迁移管理

**核心原则**：所有数据库操作通过 Alembic 迁移，禁止手动修改。

### 迁移文件规范

- **命名**: `YYYY_MM_DD_custom_<feature>_<description>.py`
- **表名**: 使用 `custom_` 前缀隔离
- **可逆**: 必须实现 `downgrade()` 函数

```bash
# 执行迁移
cd api && uv run flask db upgrade
```

详细模板和最佳实践见代码审查清单。

---

## 变更追踪

```bash
# 生成变更日志
git log main..development --pretty=format:"- [%h] %s" > .custom/docs/features/CHANGES.md

# 查看修改官方文件的提交
git log main..development --grep="\[CUSTOM\]" --oneline
```

---

## 回滚策略

### 回滚优先级

```
代码回滚 > 配置回滚 > 数据回滚
```

### 快速回滚（代码）

```bash
# 1. 回滚到上一个稳定版本
git checkout production
git revert HEAD

# 2. 重新构建部署
make -f Makefile.custom prod-build
make -f Makefile.custom prod-deploy
```

### 功能开关回滚（配置）

```bash
# 关闭有问题的二开功能，无需重启
# .env
DIFY_CUSTOM_PROBLEMATIC_FEATURE_ENABLED=false
```

### 数据库回滚

```bash
# 下游一个版本
cd api && uv run flask db downgrade -1

# 回滚到指定版本
cd api && uv run flask db downgrade <revision_id>
```

回滚检查清单见 [workflow/release-checklist.md](workflow/release-checklist.md#回滚准备)。

### 数据备份策略

```bash
# 部署前自动备份
make -f Makefile.custom db-backup

# 恢复
docker exec -i dify-db psql -U postgres dify < backup_20260127.sql
```

---

## 同步与升级

### 升级前备份

```bash
# 数据库
make -f Makefile.custom db-backup

# 文件存储
tar -czvf storage_$(date +%Y%m%d).tar.gz ./volumes/
```

### 同步流程

1. 同步上游代码
2. 合并到 development 并解决冲突
3. 运行数据库迁移：`make -f Makefile.custom db-migrate`
4. 运行测试：`make -f Makefile.custom test-custom`
5. 重新构建镜像

### 减少冲突

1. **新增而非修改**：代码放 `api/custom/`、`web/custom/`
2. **表隔离**：二开表使用 `custom_` 前缀
3. **适时同步**：每月至少同步一次上游

