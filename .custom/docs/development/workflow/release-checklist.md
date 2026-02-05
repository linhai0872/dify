# 发布检查清单

> 二开功能发布到生产环境前的检查项。
>
> 详细的部署流程和回滚策略见 [development/README.md](../README.md)。

---

## 一、代码检查

- [ ] 代码审查通过（使用 [code-review-checklist.md](code-review-checklist.md)）
- [ ] 所有修改已提交到 development 分支
- [ ] 修改官方文件的 commit 包含 `[CUSTOM]` 标记

---

## 二、测试检查

- [ ] 本地开发环境测试通过
- [ ] Docker 测试环境构建成功：`make -f Makefile.custom test-build`
- [ ] 测试环境功能验证通过
- [ ] 数据库迁移脚本可逆（有 downgrade）
- [ ] 二开测试通过：`make -f Makefile.custom test-custom`

---

## 三、文档检查

- [ ] 新增 API 已记录到 `api/README.md`
- [ ] 需要的功能文档已创建（`features/`）
- [ ] 环境变量已添加到 `env/.env.custom.example`
- [ ] `features/CHANGES.md` 已更新

---

## 四、部署准备

- [ ] Docker 镜像构建成功：`make -f Makefile.custom prod-build`
- [ ] 镜像已推送到镜像仓库：`make -f Makefile.custom prod-push`
- [ ] 数据库已备份：`make -f Makefile.custom db-backup`
- [ ] 功能开关默认值为 `false`（如需灰度）

---

## 五、上线执行

```bash
# 1. 合并到 production 分支
git checkout production
git merge development

# 2. 服务器执行部署
ssh prod-server
cd /path/to/dify
make -f Makefile.custom prod-deploy
```

---

## 六、上线验证

- [ ] API 健康检查正常
- [ ] 核心功能验证通过
- [ ] 日志无异常错误：`docker compose logs -f`
- [ ] 功能开关可正常控制

---

## 七、回滚准备

回滚命令详见 [development/README.md#回滚策略](../README.md#回滚策略)。

- [ ] 上一个稳定版本已记录
- [ ] 回滚方案已确认（代码回滚 / 功能开关回滚 / 数据库回滚）
- [ ] 数据库回滚脚本可用

**快速回滚（功能开关）**：
```bash
# 关闭有问题的二开功能，无需重启
DIFY_CUSTOM_PROBLEMATIC_FEATURE_ENABLED=false
```

---

## 发布记录模板

```markdown
## YYYY-MM-DD 发布

**版本**：基于官方 vX.X.X
**分支**：development → production

**变更内容**：
- feat(api): xxx 功能
- fix(web): xxx 问题

**验证结果**：✅ 通过 / ❌ 回滚
**回滚方案**：功能开关 DIFY_CUSTOM_XXX_ENABLED=false
```
