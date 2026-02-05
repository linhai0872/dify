# Dify 二次开发代码审查清单

> 本文档供 Agent 自检代码时使用，完成开发任务后按此清单逐项检查。
>
> 完整的编码规范见 [development/README.md](../README.md)。

---

## 一、编码规范检查

完整的命名规范见 [development/README.md#命名规范](../README.md#命名规范)。

- [ ] 二开文件使用 `custom_` 前缀
- [ ] 二开类名使用 `Custom` 前缀或继承类使用 `Ext` 后缀
- [ ] 数据库表使用 `custom_` 前缀
- [ ] 前端组件目录使用 `custom-` 前缀或放置于 `custom/` 目录
- [ ] Hook 文件使用 `use-custom-` 前缀
- [ ] 二开后端代码位于 `api/custom/` 目录
- [ ] 二开前端组件位于 `web/app/components/custom/` 目录
- [ ] 二开 API 路由位于 `api/controllers/custom/` 目录
- [ ] 二开测试位于 `api/tests/custom/` 目录
- [ ] 修改的官方文件已添加 `[CUSTOM]` 标记
- [ ] 修改范围最小化（只改必要行）
- [ ] Commit message 包含 `[CUSTOM]` 标记和修改原因
- [ ] 二开功能使用环境变量控制（`DIFY_CUSTOM_*_ENABLED`）
- [ ] 功能开关检查代码位于 `api/custom/feature_flags.py`
- [ ] 默认值为 `false`，避免影响现有功能

---

## 二、数据库检查

完整的数据库迁移管理见 [development/README.md#数据库迁移管理](../README.md#数据库迁移管理)。

- [ ] 所有数据库操作通过 Alembic 迁移管理
- [ ] 迁移文件命名：`YYYY_MM_DD_custom_<feature>_<description>.py`
- [ ] 二开表使用 `custom_` 前缀
- [ ] 扩展上游表时，新增字段使用 `custom_` 前缀
- [ ] `downgrade()` 函数已实现（可逆迁移）
- [ ] 不修改官方表结构（只新增字段或创建新表）
- [ ] 不删除官方字段或表
- [ ] 外键关系正确处理（二开表指向上游表）

---

## 三、API 规范检查

完整的 API 规范见 [api/README.md](../../api/README.md)。

- [ ] 管理后台 API 使用 `/console/api/custom/<feature>/` 前缀
- [ ] 服务 API 使用 `/v1/custom/<feature>/` 前缀
- [ ] 路由函数位于 `api/controllers/custom/` 目录
- [ ] Console API 响应格式与官方一致
- [ ] Service API 响应格式与官方一致
- [ ] 分页参数与官方统一（`limit`, `has_more` 等）
- [ ] Console API 使用用户 Session 认证
- [ ] Service API 使用 App API Key 认证
- [ ] 权限检查已实现（基于官方权限系统）
- [ ] 新增 API 已记录到 `.custom/docs/api/README.md`

---

## 四、前端规范检查

- [ ] 组件位于 `web/app/components/custom/` 或使用 `custom-` 前缀目录
- [ ] 用户文本使用 i18n（`web/i18n/en-US/`）
- [ ] 不硬编码文本
- [ ] 自定义 Hook 使用 `useCustom` 前缀
- [ ] Hook 文件使用 `use-custom-*.ts` 命名

---

## 五、安全检查

### 输入验证

- [ ] API 参数已验证（使用 Pydantic 或类似）
- [ ] 用户输入已过滤和清理
- [ ] 文件上传类型和大小已限制

### SQL 注入防护

- [ ] 使用参数化查询（ORM 或参数绑定）
- [ ] 不拼接 SQL 字符串

### XSS 防护

- [ ] 前端用户输入内容已转义
- [ ] 使用 React 的默认转义机制

### 权限检查

- [ ] 每个 API endpoint 有权限检查
- [ ] 租户隔离（如适用）已实现
- [ ] 敏感操作有审计日志

### 敏感信息

- [ ] 不在代码中硬编码密钥、密码
- [ ] 不在日志中输出敏感信息
- [ ] API Key、Token 使用环境变量

---

## 六、测试检查

### 测试覆盖

- [ ] 新增功能有对应测试（`api/tests/custom/`）
- [ ] 测试覆盖核心路径（1-2 个测试文件）
- [ ] 使用 AAA 模式（Arrange → Act → Assert）

### 测试执行

- [ ] 测试可执行：`make -f Makefile.custom test-custom`
- [ ] 测试通过

---

## 七、文档检查

- [ ] 新增 API 已记录到 `.custom/docs/api/README.md`（包含请求示例、响应示例、错误码）
- [ ] Commit 格式：`<类型>(<范围>): <标题>`
- [ ] 类型选择正确（feat/fix/refactor 等）
- [ ] 修改官方文件时包含 `[CUSTOM]` 标记

---

## 八、性能检查

### 查询优化

- [ ] 避免 N+1 查询
- [ ] 大数据量操作使用分页
- [ ] 数据库查询有索引（必要时）

### 前端性能

- [ ] 避免不必要的重渲染
- [ ] 大列表使用虚拟滚动（如适用）
- [ ] 图片/资源已优化

---

## 九、部署检查

### 配置

- [ ] 新增环境变量已添加到 `.custom/env/.env.custom.example`
- [ ] Docker 镜像构建正常
- [ ] 迁移脚本可正常执行

### 回滚准备

- [ ] 数据库迁移可逆（有 downgrade）
- [ ] 功能开关可用（出问题可快速关闭）
- [ ] 部署前备份流程已确认

---

## 十、与上游兼容性

### 冲突预防

- [ ] 二开表与上游表隔离（`custom_` 前缀）
- [ ] 不修改官方核心逻辑
- [ ] 便于合并上游更新

### 可维护性

- [ ] 代码可读性良好
- [ ] 注释清晰（如有复杂逻辑）
- [ ] 便于后续同步上游

---

## 十一、经验检查（常见陷阱）

> 静态类型检查无法发现，只会在运行时报错。

### Flask 装饰器参数注入

- [ ] API 方法签名与装饰器注入参数匹配（如 `@validate_app_token` 只注入 `app_model`）
- [ ] 需要 `end_user` 时使用 `@validate_app_token(fetch_user_arg='end_user')`

---

## 审查结论

**必须项**：命名规范、安全检查、数据库规范
**推荐项**：测试覆盖、文档完善

未通过项需修复后重新审查。

---

## 快速检查命令

```bash
# 命名规范检查
grep -r "custom_" api/custom/ web/app/components/custom/ > /dev/null && echo "✅ 命名规范检查通过" || echo "❌ 未检测到 custom 前缀使用"

# 修改官方文件检查
git diff --name-only main | grep -v "custom/" && echo "⚠️ 检测到官方文件修改"

# 功能开关检查
grep -r "DIFY_CUSTOM_" api/custom/ > /dev/null && echo "✅ 功能开关检查通过" || echo "⚠️ 未检测到功能开关使用"

# 测试检查
make -f Makefile.custom test-custom
```
