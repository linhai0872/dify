# 变更日志

## 基于 Dify 1.14.1

### 修复 (fix)

- 修复 1.14.0 graphon 迁移兼容性：WorkflowExecutionExt 子类保留 external_trace_id [30d70ae]
- 修复前端 TypeScript 类型错误 - 1.14.0 组件迁移兼容性 [7d66cead]
- 修复 lint 错误 - ReactNode 条件渲染防泄漏 [e324b22]
- 修复 make test-custom 在 Mac asdf 环境下失败的问题 [4fc2f79]

### 重构 (refactor)

- 修复二开规范违规：WorkflowExecution 类重命名为 WorkflowExecutionExt，补全标记平衡 [608028f]

### 基础设施 (chore)

- 同步 Dify 1.14.0（dify_graph → graphon 包迁移）
- 同步 Dify 1.14.1（graphon 0.2.2→0.3.1，docker YAML anchors）
- 升级后更新 uv.lock - 添加自定义依赖 [a0503543]
- 升级前清理：移除未完成的 dify_graph 改动 [7407b93]
- .tool-versions 加入 .gitignore（与 .nvmrc 功能重叠）[7d66cead]

### 文档 (docs)

- 更新费用显示文档 - 新增 WorkflowExecutionExt 扩展方案 [c94b982]

---

## 基于 Dify 1.13.2

### 修复 (fix)

- 修复 code_node.py 中错误的 core.file 导入路径（迁移至 dify_graph.file）[fe764ca]
- 修复 core.workflow/core.file 残留 import 路径（测试文件 + custom_remote_file）[7268dce]

### 重构 (refactor)

- 重命名 external_trace_id → custom_external_trace_id（遵循 custom_ 前缀规范）[8d33998]
  - 涉及 workflow_runs / messages 两张表，新增可逆 migration
- 修复 dify_graph 导入顺序并同步 uv.lock（ebooklib 依赖）[9637504]
- 完善二开文档结构与配置说明 [56cfc37]

### 基础设施 (chore)

- 同步 Dify 1.13.1 [5d3945]
- 同步 Dify 1.13.2（8 个 upstream commits，bugfix/refactor）[f16a739]
  - 引入 RAGPipelineVariable 类型、移除 declared_attr、修复 Redis max_retries 硬编码
- 镜像版本管理改造 + 开发规范完善 [e8ad349]

---

## 基于 Dify 1.13.0

### 新功能 (feat)

- Workflow 费用显示 + 日期时间范围选择器 [21bc2ba]
- 完善多工作空间权限管理系统 [62f70d1]
- 添加原生文档提取器支持 DOC/PPT/PPTX/EPUB 格式 [fd85d80]
- 添加应用日志时区统一功能 [77db6e4]
- 添加指数退避重试机制 [74816a8]
- 添加追踪搜索功能和 keyword_scope 参数 [26589d9]
- 添加 Service API 远程文件操作接口 [bbc3d9b]
- 添加 Sandbox 依赖管理和代码节点文件输出功能 [fb11c68]
- 添加二开环境变量性能优化模板 [8dc9f0e]

### 修复 (fix)

- 修复 datasets API 参数验证失败问题 [4044b30]

### 重构 (refactor)

- 重构 Makefile.custom 命令规范 [1143173]

### 基础设施 (chore)

- 同步 Dify 1.13.0 [7aaffaa]
- 补全环境配置模板和 CLI 登录工具 [5d56560]
- 合并 upstream 1.13.0 和二开数据库迁移 [a76abc4]
- 完善开发环境幂等性和文档 [e4fc9dc]
- 同步 v1.12.1 前暂存工作进度 [6e7f51c]
- 合并 upstream 1.12.0 和二开数据库迁移 [7ccf708]
- 代码风格修复和 Sandbox 配置完善 [6c148f1]
- 补充环境变量性能优化配置 [67ebc2b]

### 文档 (docs)

- 添加原生文档提取器功能文档 [d231068]
- 更新 CHANGES.md - 同步 1.12.0 后 [4600a10]

---

## 更新方法

```bash
# 生成原始日志
git log main..development --pretty=format:"- [%h] %s"

# 手动按类型分类整理到本文件
```

前提：commit message 遵循 [Commit 规范](../development/README.md#commit-规范)
