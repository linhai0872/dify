# 变更日志

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
