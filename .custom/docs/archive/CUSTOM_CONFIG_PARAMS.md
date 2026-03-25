> **[ARCHIVED]** 本文档已归档 (2026-02-26)
> 当前配置以 `.custom/env/.env.custom.example` 为准
> 本文档保留作为历史参考

---

# Dify 二次开发环境变量及配置清单

> **说明**: 此文档列出所有非官方默认的二次开发配置参数
> **基线版本**: Dify 1.8.1
> **整理日期**: 2026-01-30

---

## 环境变量 (.env)

### 性能优化参数

#### Redis 优化
```bash
REDIS_ENABLE_CLIENT_SIDE_CACHE=false
REDIS_SERIALIZATION_PROTOCOL=3
```

#### API 优化
```bash
API_COMPRESSION_ENABLED=true
```

#### Gunicorn Worker 优化
```bash
SERVER_WORKER_AMOUNT=3        # 官方默认: 1
SERVER_WORKER_CONNECTIONS=100  # 官方默认: 10
```

#### PostgreSQL 优化
```bash
SQLALCHEMY_POOL_SIZE=30           # 官方默认: 30
SQLALCHEMY_MAX_OVERFLOW=20        # 官方默认: 10
SQLALCHEMY_POOL_PRE_PING=true     # 官方默认: false
SQLALCHEMY_POOL_USE_LIFO=true     # 官方默认: false
POSTGRES_MAX_CONNECTIONS=180      # 官方默认: 100
POSTGRES_SHARED_BUFFERS=4096MB    # 官方默认: 128MB
POSTGRES_WORK_MEM=16MB            # 官方默认: 4MB
POSTGRES_EFFECTIVE_CACHE_SIZE=10240MB  # 官方默认: 4096MB
```

---

### 端口配置

```bash
EXPOSE_POSTGRES_PORT=20081   # 官方默认: 5432
EXPOSE_REDIS_PORT=20082      # 官方默认: 6379
EXPOSE_NGINX_PORT=20080      # 官方默认: 80
EXPOSE_NGINX_SSL_PORT=20443  # 官方默认: 443
```

---

### 功能配置

#### 文件相关
```bash
FILES_ACCESS_TIMEOUT=604800          # 官方默认: 300 (7天)
UPLOAD_FILE_SIZE_LIMIT=256           # 官方默认: 15
UPLOAD_FILE_BATCH_LIMIT=30           # 官方默认: 5
UPLOAD_IMAGE_FILE_SIZE_LIMIT=100     # 官方默认: 10
UPLOAD_VIDEO_FILE_SIZE_LIMIT=1024    # 官方默认: 100
UPLOAD_AUDIO_FILE_SIZE_LIMIT=200     # 官方默认: 50
```

#### 工作流相关
```bash
TEXT_GENERATION_TIMEOUT_MS=120000    # 官方默认: 60000
CODE_EXECUTION_CONNECT_TIMEOUT=300   # 官方默认: 10
CODE_EXECUTION_READ_TIMEOUT=300      # 官方默认: 60
CODE_EXECUTION_WRITE_TIMEOUT=300     # 官方默认: 10
SANDBOX_WORKER_TIMEOUT=300           # 官方默认: 15
MAX_VARIABLE_SIZE=409600             # 官方默认: 204800
WORKFLOW_FILE_UPLOAD_LIMIT=100       # 官方默认: 10
```

#### RAG 相关
```bash
INDEXING_MAX_SEGMENTATION_TOKENS_LENGTH=8000  # 官方默认: 4000
TOP_K_MAX_VALUE=100                           # 官方默认: 10
```

#### 日志相关
```bash
LOG_TZ=Asia/Shanghai  # 官方默认: UTC
```

---

### 关键配置说明

#### 性能调优参数计算公式

```
总并发连接数 = SERVER_WORKER_AMOUNT × SERVER_WORKER_CONNECTIONS
当前配置: 3 × 100 = 300 并发

总数据库连接需求 = SERVER_WORKER_AMOUNT × (SQLALCHEMY_POOL_SIZE + SQLALCHEMY_MAX_OVERFLOW)
当前配置: 3 × (30 + 20) = 150 连接

PostgreSQL最大连接数应大于总需求:
POSTGRES_MAX_CONNECTIONS (180) > 150 ✓
```

#### 超时时间层级

```
前端超时:      TEXT_GENERATION_TIMEOUT_MS = 120000ms (120秒)
API超时:       GUNICORN_TIMEOUT = 360秒
代码执行超时:   CODE_EXECUTION_READ_TIMEOUT = 300秒
沙盒超时:      SANDBOX_WORKER_TIMEOUT = 300秒

层级关系: 前端 < 代码执行 < API
```

---

**文档版本**: v1.0
**最后更新**: 2026-01-30
