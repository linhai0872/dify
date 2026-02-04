# Dify 二次开发变更日志

> 本文档记录所有二次开发功能的变更历史，通过 `git log` 自动生成。

## 生成方式

```bash
# 生成变更日志
git log main..development --pretty=format:"- [%h] %s" > .custom/docs/features/CHANGES.md
```

---

## 变更记录

- [c5fbf37ca] feat(rag): [CUSTOM] 添加原生文档提取器支持 DOC/PPT/PPTX/EPUB 格式
- [e8d009cd7] feat(log): [CUSTOM] 添加应用日志时区统一功能
- [44268e72f] feat(workflow): [CUSTOM] 添加指数退避重试机制
- [9f64cec28] feat(api): [CUSTOM] 添加追踪搜索功能和 keyword_scope 参数
- [77c9bb086] feat(api): [CUSTOM] 添加 Service API 远程文件操作接口
- [16a2006dc] feat(workflow): [CUSTOM] 添加 Sandbox 依赖管理和代码节点文件输出功能
- [fb63a893d] perf(docker): [CUSTOM] 补充环境变量性能优化配置
- [278bca6b4] feat(docker): [CUSTOM] 添加二开环境变量性能优化模板
- [167ae600f] fix(api): [CUSTOM] 修复 datasets API 参数验证失败问题
