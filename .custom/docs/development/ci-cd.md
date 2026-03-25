# CI/CD 流程

> 当前状态：手动部署

## 现有流程

```
开发者本地 → git push → 手动构建镜像 → 手动部署
```

```bash
make -f Makefile.custom prod-build    # 构建镜像
make -f Makefile.custom prod-push     # 推送镜像
make -f Makefile.custom prod-deploy   # 滚动更新 (含自动回滚)
```

## 预期自动化流程

```
PR → 自动测试 → 合并到 development → 构建镜像 → 部署测试环境
                                          ↓
                合并到 production → 构建镜像 → 部署生产环境
```

### 阶段规划

1. **Lint + 类型检查** — PR 时自动运行
2. **二开功能测试** — PR 时自动运行 `pytest tests/custom/`
3. **镜像构建** — 合并后自动构建 API/Web/Sandbox 镜像
4. **自动部署** — 推送镜像后自动触发目标环境更新

### 候选方案

- GitHub Actions (与 GitHub 仓库集成最紧密)
- 自建 Runner (敏感代码不出内网)
