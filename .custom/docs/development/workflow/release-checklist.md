# 发布检查清单

> 二开功能发布到生产环境前的检查项。
>
> 详细的部署流程和回滚策略见 [development/README.md](../README.md)。

---

## 一、代码检查

- [ ] 代码审查通过（使用 [code-review-checklist.md](code-review-checklist.md)）
- [ ] 所有修改已提交到 development 分支
- [ ] 所有 commit 使用 `<类型>(<范围>): [CUSTOM] <标题>` 格式

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
- [ ] 构建成功后，更新 `.custom/env/.env.custom.prod` 中的 `API_IMAGE` 和 `WEB_IMAGE` 为新版本标签（格式：`<registry>/<name>:<VERSION>-<GIT_SHA>`）
- [ ] 镜像已推送到镜像仓库：`make -f Makefile.custom prod-push`
- [ ] 数据库已备份：`make -f Makefile.custom db-backup`
- [ ] 功能开关默认值为 `false`（如需灰度）

**同步上游版本时额外检查：**
- [ ] 检查 migration heads 是否有分叉：在仓库根目录执行 `cd api && uv run flask db heads`（须能解析 Flask 应用；仅一个 `head`）。若有多个 head，先 `uv run flask db merge heads -m "..."` 生成合并迁移，放入 `api/migrations/versions/` 且文件名/`revision` 使用 `custom_` 前缀
- [ ] **合并迁移 revision 与生产库一致**：若生产库曾执行过手工 `stamp` 或带特定名的 merge，仓库里该迁移文件的 `revision = '...'` 必须与 `SELECT version_num FROM alembic_version;` 一致，否则 API 启动迁移阶段会报 *Can't locate revision*
- [ ] 扫描上游对已使用组件的 breaking change：重点关注 named/default export 变化、Props 签名变化（`rg "export default" web/app/components/base/` 与自定义导入对比）
- [ ] MDX 模板（`web/app/components/develop/template/*.mdx`）修改后必须执行 `cd web && pnpm build`：Turbopack 对 `<i>`、未闭合的 `CodeGroup`/`targetCode` 模板字符串、以及合并冲突把 `Heading`/`CodeGroup` 粘进 JSON 示例等情况会直接导致构建失败
- [ ] **插件守护进程镜像**：`dify-plugin-daemon` 为独立仓库/镜像，官方主仓库 `docker-compose.yaml` 中的 tag 可能滞后于修复版本。二开在 `docker/docker-compose.yaml` 使用 `PLUGIN_DAEMON_IMAGE`（默认 `langgenius/dify-plugin-daemon:0.5.6-local`）。同步上游后若官方仍 pin 旧 tag，保留二开默认值或按 [dify-plugin-daemon Releases](https://github.com/langgenius/dify-plugin-daemon/releases) 上调；生产覆盖时写入 `docker/.env`，与 `prod-deploy` 拉取列表一致
- [ ] **自定义 Sandbox 镜像**：`SANDBOX_IMAGE` 若为仅本地构建的标签（如 `dify-sandbox-custom:latest`），`docker-compose` 中已使用 `pull_policy: never`；`prod-deploy` 仅拉取 `api` / `web` / `worker` / `worker_beat` / `plugin_daemon`（不包含 `sandbox`），避免对仅本地存在的 Sandbox 标签执行 `pull` 导致失败
- [ ] **镜像标签与回滚**：更新 `.custom/env/.env.custom.prod` 的 `API_IMAGE`、`WEB_IMAGE`（及按需的 `PLUGIN_DAEMON_IMAGE`）后，同步修改服务器上 `docker/.env` 中对应行（`env-merge` 不会覆盖已有块内旧值）。若 `prod-deploy` 触发回滚脚本，历史上可能只改写 `API_IMAGE`，需人工核对 `WEB_IMAGE` / `PLUGIN_DAEMON_IMAGE` 是否仍指向预期版本

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

> **运维注意**：nginx 启动时静态缓存各服务的 DNS（`api`、`web` 等）。若手动重启 API 容器（非通过 `prod-deploy`），必须同步重启 nginx，否则 nginx 会连接旧 IP 导致所有 API 请求挂死：
> ```bash
> docker compose -f docker/docker-compose.yaml --env-file docker/.env -p dify-custom-prod restart api nginx
> ```

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
