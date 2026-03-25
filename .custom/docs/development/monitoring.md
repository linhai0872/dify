# 监控与告警

> 当前状态：待规划

## 建议方向

### 健康检查

- API: `GET /health` (已有)
- Worker: Celery worker 进程存活检测
- Sandbox: 容器状态检查

### 日志聚合

- 后端日志: `.custom/logs/api.log` / `.custom/logs/worker.log`
- Docker 容器日志: `make -f Makefile.custom {env}-logs`
- 候选方案: Loki + Grafana / ELK

### 告警

- API 健康检查失败
- Worker 进程异常退出
- 数据库连接池耗尽
- 磁盘空间不足

### 指标监控

- API 请求延迟和错误率
- Celery 任务队列深度和执行时间
- PostgreSQL 连接数和查询性能
- 候选方案: Prometheus + Grafana
