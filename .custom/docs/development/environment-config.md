# 环境配置管理指南

> **本文档说明**: Dify 二次开发项目的环境配置管理机制和最佳实践
> **最后更新**: 2026-02-09
> **适用范围**: 开发/测试/生产环境

---

## 📋 目录

1. [配置文件结构](#配置文件结构)
2. [配置管理机制](#配置管理机制)
3. [幂等性设计](#幂等性设计)
4. [正确修改配置](#正确修改配置)
5. [常见问题](#常见问题)
6. [故障排查](#故障排查)

---

## 配置文件结构

### 文件布局

```
.custom/env/
├── .env.custom.example       # 模板 (check-in 到 Git)
├── .env.custom.dev           # 开发环境 (gitignore)
├── .env.custom.test          # 测试环境 (gitignore)
└── .env.custom.prod          # 生产环境 (gitignore)

api/
├── .env.example              # 官方模板 (只读)
├── .env                      # 运行时生成 (gitignore)
└── .env.custom               # [已废弃] 不再使用

web/
├── .env.example              # 官方模板 (只读)
└── .env                      # 运行时生成 (gitignore)

docker/
├── .env.example              # 官方模板 (只读)
├── .env                      # 测试/生产环境 (gitignore)
└── middleware.env            # 中间件配置 (gitignore)
```

### 配置优先级

```
二开配置 > 官方默认值
.env.custom.* → 覆盖 → .env.example → 生成 → .env
```

**示例流程**：

```bash
# 1. 官方模板 (api/.env.example)
SECRET_KEY=

# 2. 二开配置 (.custom/env/.env.custom.dev)
SECRET_KEY=sk-dev-random-key

# 3. 最终生成 (api/.env)
SECRET_KEY=              # 从官方模板
...
# ====== Custom Environment Variables (dev) ======
SECRET_KEY=sk-dev-random-key  # 二开配置覆盖
```

---

## 配置管理机制

### 开发环境 (dev-*)

**自动合并机制**：

```bash
make -f Makefile.custom dev-start
```

执行流程：

1. **检查 api/.env 是否存在**
   - 不存在 → 从 `api/.env.example` 复制
   - 已存在 → **跳过重置**（保护手动修改）

2. **检查是否已追加二开配置**
   - 未追加 → 追加 `.custom/env/.env.custom.dev`
   - 已追加 → **跳过追加**（避免重复）

3. **启动服务**

**涉及命令**：
- `dev-api` - 启动后端 (前台)
- `dev-api-background` - 启动后端 (后台)
- `dev-web` - 启动前端
- `dev-start` - 一键启动
- `db-migrate-dev` - 数据库迁移

### 测试/生产环境 (test-*/prod-*)

**手动合并机制**：

```bash
make -f Makefile.custom test-start
```

执行流程：

1. **调用 env-merge**
   - 合并 `.env.example` + `.env.custom.*` → `docker/.env`

2. **Docker Compose 读取**
   - `docker compose --env-file docker/.env up -d`

**涉及命令**：
- `test-start` / `prod-start` - 一键启动/部署
- `test-up` / `prod-up` - 启动容器
- `env-merge` - 手动合并配置

---

## 幂等性设计

### 什么是幂等性？

**幂等性**: 多次执行相同操作，结果保持一致

**示例**：

```bash
# 第一次执行
make -f Makefile.custom dev-api
# ✅ 初始化 api/.env

# 第二次执行
make -f Makefile.custom dev-api
# ✅ 跳过重置，保留手动修改

# 第三次执行
make -f Makefile.custom dev-api
# ✅ 仍然跳过，不会覆盖配置
```

### 为什么要幂等性？

**场景 1: 开发过程中频繁重启**
```bash
# 修改了 api/.env 中的某个配置
vim api/.env

# 重启后端服务
make -f Makefile.custom dev-api
# ❌ 旧逻辑: 配置被重置，修改丢失
# ✅ 新逻辑: 配置保留，修改生效
```

**场景 2: SECRET_KEY 导致的登录问题**
```bash
# api/.env.example 中 SECRET_KEY= 为空

# 首次启动
make -f Makefile.custom dev-start
# → api/.env 中 SECRET_KEY= 为空
# → 登录成功，但 token 无法验证
# → 刷新页面无限重定向

# 重启服务
make -f Makefile.custom dev-start
# ❌ 旧逻辑: SECRET_KEY 重新变空，问题依旧
# ✅ 新逻辑: 在 .env.custom.dev 中设置，永久生效
```

### 实现机制

**关键代码**（Makefile.custom）：

```makefile
# ❌ 旧逻辑（非幂等）
@cp api/.env.example api/.env

# ✅ 新逻辑（幂等）
@if [ ! -f "api/.env" ]; then \
    echo "$(GREEN)✓ 初始化 api/.env (从模板)$(NC)"; \
    cp api/.env.example api/.env; \
else \
    echo "$(YELLOW)⚠️  api/.env 已存在，跳过重置$(NC)"; \
fi
```

---

## 正确修改配置

### 方法 1: 修改二开配置（推荐）

**适用场景**: 需要持久化的配置

```bash
# 1. 编辑二开配置
vim .custom/env/.env.custom.dev

# 2. 添加配置
SECRET_KEY=sk-dev-your-random-key
INNER_API_KEY_FOR_PLUGIN=your-key

# 3. 重启服务
make -f Makefile.custom dev-restart
```

**优点**：
- ✅ 持久化，不会被覆盖
- ✅ 符合二开规范
- ✅ 可以提交到 Git（如果不含敏感信息）

**缺点**：
- ⚠️ 需要重启服务才能生效

---

### 方法 2: 直接修改运行时配置

**适用场景**: 临时调试

```bash
# 1. 编辑运行时配置
vim api/.env

# 2. 修改配置
SECRET_KEY=sk-temp-key

# 3. 重启服务
make -f Makefile.custom dev-restart
```

**优点**：
- ✅ 立即生效（重启后）
- ✅ 适合临时测试

**缺点**：
- ❌ 下次 `env-init` 会被覆盖（除非先删除 api/.env）
- ❌ 无法提交到 Git

---

### 方法 3: 环境变量覆盖

**适用场景**: CI/CD 或 Docker

```bash
# 方式 1: 命令行
SECRET_KEY=sk-production-key make -f Makefile.custom prod-start

# 方式 2: Docker Compose
# docker/.env
SECRET_KEY=sk-production-key
```

---

## 常见问题

### Q1: 为什么我的 SECRET_KEY 每次都变空？

**原因**: 未在二开配置中设置，`api/.env.example` 中默认为空

**解决方案**：

```bash
# 在 .custom/env/.env.custom.dev 中添加
SECRET_KEY=sk-dev-your-random-key
```

---

### Q2: 修改了 api/.env，重启后配置丢失

**原因**: 旧版 Makefile 每次启动都会重置 `.env`

**解决方案**：

1. **确认 Makefile 版本**：检查是否已更新为幂等版本
2. **手动删除 `.env`**：确保使用最新配置
   ```bash
   rm api/.env web/.env docker/.env
   make -f Makefile.custom dev-start
   ```

---

### Q3: env-merge 会覆盖我的手动修改吗？

**是的**，env-merge 设计为重新生成 `docker/.env`

**解决方案**：

1. **修改 `.env.example`**（推荐）
   - 将通用配置提交到官方模板
2. **修改 `.env.custom.*`**
   - 将环境特定配置放到二开文件
3. **手动编辑 `docker/.env` 后，避免再次调用 env-merge**

---

### Q4: 如何生成 SECRET_KEY？

**开发环境**（快速生成）：
```bash
openssl rand -base64 42
```

**生产环境**（建议使用密钥管理服务）：
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault

---

### Q5: 不同环境可以使用相同的 SECRET_KEY 吗？

**❌ 不建议**，存在以下风险：

1. **安全风险**: 开发环境密钥泄露影响生产
2. **Session 混乱**: 相同密钥导致跨环境 session 认证问题

**最佳实践**：

| 环境 | SECRET_KEY 策略 |
|------|----------------|
| 开发 | 本地生成，不提交 Git |
| 测试 | CI/CD 自动生成或密钥管理服务 |
| 生产 | 强密钥，定期轮换 |

---

## 故障排查

### 问题 1: 登录后立即 401，无限重定向

**症状**：
- 登录接口返回 200
- 随后所有请求返回 401
- 刷新页面重定向到登录页

**原因**：`SECRET_KEY` 为空或不一致

**排查步骤**：

```bash
# 1. 检查 api/.env 中的 SECRET_KEY
grep SECRET_KEY api/.env

# 2. 检查后端日志
tail -50 .custom/logs/api.log | grep -E "401|refresh-token"

# 3. 检查是否为空
grep "^SECRET_KEY=$" api/.env
```

**解决方案**：

```bash
# 在 .custom/env/.env.custom.dev 中设置
SECRET_KEY=sk-dev-your-random-key

# 删除旧的 api/.env 并重启
rm api/.env
make -f Makefile.custom dev-restart
```

---

### 问题 2: 插件功能无法使用

**症状**：
- 插件列表为空
- 安装插件失败

**原因**：`INNER_API_KEY_FOR_PLUGIN` 或 `PLUGIN_DAEMON_KEY` 不匹配

**排查步骤**：

```bash
# 1. 检查配置是否一致
grep INNER_API_KEY api/.env .custom/env/.env.custom.dev
grep PLUGIN_DAEMON_KEY api/.env .custom/env/.env.custom.dev

# 2. 检查插件服务日志
docker logs dify-custom-dev-plugin_daemon-1
```

---

### 问题 3: 配置修改不生效

**可能原因**：

1. **未追加二开配置**
   ```bash
   # 检查 api/.env 中是否包含以下标记
   grep "# ====== Custom Environment Variables (dev) ======" api/.env
   ```

2. **配置被重复追加**
   ```bash
   # 检查是否有重复的标记
   grep -c "# ====== Custom Environment Variables" api/.env
   ```

3. **Pydantic 缓存**
   ```bash
   # 重启 Python 进程
   make -f Makefile.custom dev-restart
   ```

**解决方案**：

```bash
# 1. 清理旧配置
rm api/.env web/.env docker/.env

# 2. 重新初始化
make -f Makefile.custom dev-setup

# 3. 重启服务
make -f Makefile.custom dev-start
```

---

## 最佳实践

### 开发环境

1. **✅ 在 `.env.custom.dev` 中配置所有需要覆盖的变量**
2. **✅ 首次设置后不要轻易修改 `SECRET_KEY`**
3. **✅ 使用版本控制管理 `.env.custom.example`**
4. **❌ 不要手动修改 `api/.env` 或 `web/.env`**（除非临时调试）

### 测试/生产环境

1. **✅ 使用密钥管理服务存储敏感配置**
2. **✅ 通过 CI/CD 注入环境变量**
3. **✅ 定期轮换密钥**
4. **❌ 不要将生产配置提交到 Git**

### 配置检查清单

- [ ] SECRET_KEY 已设置（非空）
- [ ] INNER_API_KEY_FOR_PLUGIN 与插件服务一致
- [ ] PLUGIN_DAEMON_KEY 与插件服务一致
- [ ] 数据库连接配置正确
- [ ] Redis 连接配置正确
- [ ] 向量数据库配置正确
- [ ] 文件存储配置正确

---

## 相关文档

- [开发规范 README](README.md)
- [配置参数说明 (已归档)](../archive/CUSTOM_CONFIG_PARAMS.md)
- [Sandbox 依赖管理](README.md#sandbox-依赖管理)
