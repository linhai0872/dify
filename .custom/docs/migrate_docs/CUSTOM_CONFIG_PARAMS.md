# Dify 二次开发环境变量及配置清单

> **说明**: 此文档列出所有非官方默认的二次开发配置参数  
> **基线版本**: Dify 1.8.1  
> **整理日期**: 2026-01-30

---

## 📋 目录

1. [环境变量 (.env)](#环境变量-env)
2. [Docker Compose 配置](#docker-compose-配置)
3. [Docker Compose Override](#docker-compose-override)

---

## 环境变量 (.env)

### 🔧 性能优化参数

#### Redis 优化
```bash
# Redis 客户端缓存优化
REDIS_ENABLE_CLIENT_SIDE_CACHE=false
# 说明: 启用客户端缓存，允许应用在本地缓存常用的Redis键值
# 效果: 大幅减少应用和Redis之间的网络往返次数和延迟，提高应用响应速度

REDIS_SERIALIZATION_PROTOCOL=3
# 说明: Redis序列化协议版本（添加到docker-compose.yaml）
```

#### API 优化
```bash
# API 响应压缩优化
API_COMPRESSION_ENABLED=true
# 说明: 对API响应启用压缩（如Gzip/Brotli）
# 效果: 显著减少数据传输量，尤其在网络较慢时能有效缩短数据传输时间
```

#### Gunicorn Worker 优化
```bash
# Worker 进程数量
SERVER_WORKER_AMOUNT=3
# 官方默认: 1
# 说明: worker进程数量,建议为CPU核心数-1(留1核给DB),解决CPU过载问题

# Worker 并发连接数
SERVER_WORKER_CONNECTIONS=100
# 官方默认: 10
# 说明: 每个worker的并发连接数,总并发=worker数×此值(当前3×100=300)
```

#### PostgreSQL 优化
```bash
# 数据库连接池大小
SQLALCHEMY_POOL_SIZE=30
# 官方默认: 30（未修改，但添加了说明）
# 说明: 每个worker进程的基础连接池大小(Gunicorn多进程独立连接池)

# 连接池溢出
SQLALCHEMY_MAX_OVERFLOW=20
# 官方默认: 10
# 说明: 连接池耗尽后可临时创建的额外连接数,总需求=worker数×(pool_size+max_overflow)

# 连接预检查
SQLALCHEMY_POOL_PRE_PING=true
# 官方默认: false
# 说明: 启用连接预检查，避免使用无效连接，提高应用稳定性

# 连接池策略
SQLALCHEMY_POOL_USE_LIFO=true
# 官方默认: false
# 说明: 启用后进先出策略。让最新使用的数据库连接被优先复用

# PostgreSQL 最大连接数
POSTGRES_MAX_CONNECTIONS=180
# 官方默认: 100
# 说明: PostgreSQL 数据库服务器能同时接受的总连接数上限

# PostgreSQL 共享缓冲区
POSTGRES_SHARED_BUFFERS=4096MB
# 官方默认: 128MB
# 说明: PostgreSQL共享缓冲区,建议为总内存25%(当前4GB合理)

# PostgreSQL 工作内存
POSTGRES_WORK_MEM=16MB
# 官方默认: 4MB
# 说明: 提高每个Worker用于排序/Join操作的内存，避免溢出到磁盘

# PostgreSQL 查询缓存
POSTGRES_EFFECTIVE_CACHE_SIZE=10240MB
# 官方默认: 4096MB
# 说明: 提示PostgreSQL查询优化器系统大约有10GB内存可用于缓存
```

---

### 🔌 端口配置

```bash
# PostgreSQL 暴露端口
EXPOSE_POSTGRES_PORT=20081
# 官方默认: 5432（不暴露）
# 说明: pg数据库的暴露端口,建议改为非常规端口便于调试

# Redis 暴露端口
EXPOSE_REDIS_PORT=20082
# 官方默认: 6379（不暴露）
# 说明: Redis的暴露端口,便于开发调试

# Nginx HTTP 端口
EXPOSE_NGINX_PORT=20080
# 官方默认: 80
# 说明: Nginx HTTP暴露端口

# Nginx HTTPS 端口
EXPOSE_NGINX_SSL_PORT=20443
# 官方默认: 443
# 说明: Nginx HTTPS暴露端口
```

---

### ⚙️ 功能配置

#### 文件相关
```bash
# 文件访问超时时间
FILES_ACCESS_TIMEOUT=604800
# 官方默认: 300
# 说明: 文件访问超时时间（秒），604800 = 7天

# 单文件上传大小限制
UPLOAD_FILE_SIZE_LIMIT=256
# 官方默认: 15
# 说明: 单文件上传大小限制(MB)

# 批量上传文件数量限制
UPLOAD_FILE_BATCH_LIMIT=30
# 官方默认: 5
# 说明: 批量上传文件数量限制

# 图片文件大小限制
UPLOAD_IMAGE_FILE_SIZE_LIMIT=100
# 官方默认: 10
# 说明: 图片文件大小限制(MB)

# 视频文件大小限制
UPLOAD_VIDEO_FILE_SIZE_LIMIT=1024
# 官方默认: 100
# 说明: 视频文件大小限制(MB)

# 音频文件大小限制
UPLOAD_AUDIO_FILE_SIZE_LIMIT=200
# 官方默认: 50
# 说明: 音频文件大小限制(MB)
```

#### 工作流相关
```bash
# 前端文本生成超时
TEXT_GENERATION_TIMEOUT_MS=120000
# 官方默认: 60000
# 说明: 前端等待工作流完成的超时时间,120秒为宜

# 代码执行超时
CODE_EXECUTION_CONNECT_TIMEOUT=300
# 官方默认: 10
# 说明: 沙盒连接超时时间限制(秒)

CODE_EXECUTION_READ_TIMEOUT=300
# 官方默认: 60
# 说明: 沙盒读取超时时间限制(秒)

CODE_EXECUTION_WRITE_TIMEOUT=300
# 官方默认: 10
# 说明: 沙盒写入超时时间限制(秒)

# 沙盒Worker超时
SANDBOX_WORKER_TIMEOUT=300
# 官方默认: 15
# 说明: 沙盒运行时间限制(秒)

# 变量大小限制
MAX_VARIABLE_SIZE=409600
# 官方默认: 204800
# 说明: 变量的大小限制(字节)

# 工作流文件上传限制
WORKFLOW_FILE_UPLOAD_LIMIT=100
# 官方默认: 10
# 说明: 工作流文件上传数量限制
```

#### RAG 相关
```bash
# 索引分段最大Token长度
INDEXING_MAX_SEGMENTATION_TOKENS_LENGTH=8000
# 官方默认: 4000
# 说明: 索引分段最大Token长度

# RAG检索Top-K最大值
TOP_K_MAX_VALUE=100
# 官方默认: 10
# 说明: RAG检索Top-K最大值
```

#### 日志相关
```bash
# 日志时区
LOG_TZ=Asia/Shanghai
# 官方默认: UTC
# 说明: 日志的时区,统一所有日志时间显示
```

---

### 🏢 多工作空间功能

```bash
# 是否允许创建新工作空间（全局开关）
ALLOW_CREATE_WORKSPACE=true
# 官方默认: false
# 说明: 启用多工作空间功能

# 工作空间创建权限控制
WORKSPACE_CREATE_PERMISSION=owner_only
# 官方默认: owner_only
# 可选值: 
#   - "all": 所有登录用户都可以创建
#   - "admin_only": 只有当前工作空间的管理员/所有者可以创建
#   - "owner_only": 只有系统管理员（第一个注册的用户）可以创建
```

---

### 🗑️ 其他配置

```bash
# 代码节点文件大小限制
CODE_MAX_FILE_SIZE=256
# 说明: 代码节点生成文件的大小限制(MB)
```

---

## Docker Compose 配置

### docker-compose.yaml 新增配置

#### 1. 数据库端口暴露
```yaml
db:
  ports:
    - "${EXPOSE_POSTGRES_PORT:-5432}:5432"
```

#### 2. Redis 端口暴露
```yaml
redis:
  ports:
    - "${EXPOSE_REDIS_PORT:-6379}:6379"
```

#### 3. Sandbox Python 依赖持久化
```yaml
sandbox:
  environment:
    PYTHONPATH: /dependencies/python_packages
  volumes:
    - ./volumes/sandbox/dependencies:/dependencies
    - ./volumes/sandbox/conf:/conf
    - ./volumes/sandbox/init-dependencies.sh:/init-dependencies.sh
```

#### 4. 共享环境变量新增项
```yaml
x-shared-env:
  API_COMPRESSION_ENABLED: ${API_COMPRESSION_ENABLED:-false}
  REDIS_SERIALIZATION_PROTOCOL: ${REDIS_SERIALIZATION_PROTOCOL:-3}
  REDIS_ENABLE_CLIENT_SIDE_CACHE: ${REDIS_ENABLE_CLIENT_SIDE_CACHE:-false}
  ALLOW_CREATE_WORKSPACE: ${ALLOW_CREATE_WORKSPACE:-false}
  WORKSPACE_CREATE_PERMISSION: ${WORKSPACE_CREATE_PERMISSION:-owner_only}
```

---

## Docker Compose Override

### docker-compose.override.yaml 完整配置

> **用途**: 开发环境下挂载本地代码实现热更新

#### 1. Sandbox 服务增强

```yaml
sandbox:
  security_opt:
    - seccomp:unconfined  # 允许pandas/openpyxl系统调用
  environment:
    PYTHONPATH: "/dependencies/python_packages"
    PIP_INDEX_URL: "https://mirrors.aliyun.com/pypi/simple"
    PIP_EXTRA_INDEX_URL: "https://pypi.tuna.tsinghua.edu.cn/simple"
    HTTP_PROXY: "http://ssrf_proxy:3128"
    HTTPS_PROXY: "http://ssrf_proxy:3128"
  volumes:
    - ./volumes/sandbox/dependencies:/dependencies
    - ./volumes/sandbox/conf:/conf
    - ./volumes/sandbox/files:/sandbox_files  # 代码节点文件输出
    - ./volumes/sandbox/init-dependencies.sh:/init-dependencies.sh
  entrypoint: /bin/sh -c "bash /init-dependencies.sh && mkdir -p /var/sandbox/sandbox-python/tmp /tmp && chmod 777 /var/sandbox/sandbox-python/tmp /tmp && exec /main"
```

**关键说明**:
- `seccomp:unconfined`: 允许 pandas、openpyxl 等库的系统调用
- `init-dependencies.sh`: 自动安装系统依赖和 Python 包
- `/sandbox_files`: 代码节点生成文件的共享目录

#### 2. Web 服务代码挂载

**挂载的功能模块**:
- 代码节点文件输出
- 多工作空间选择器
- 应用分析功能
- 工作流重试机制增强
- 应用级模型凭证管理

```yaml
web:
  build:
    context: ../web
    dockerfile: Dockerfile
  volumes:
    # 变量类型选择器 (File类型支持)
    - ../web/app/components/workflow/nodes/_base/components/variable/var-type-picker.tsx:/app/web/...
    
    # 多工作空间功能
    - ../web/app/components/header/account-dropdown/workplace-selector/index.tsx:/app/web/...
    - ../web/service/common.ts:/app/web/...
    
    # 应用分析功能
    - ../web/app/(commonLayout)/apps-analytics:/app/web/app/(commonLayout)/apps-analytics
    - ../web/app/components/header/analytics-nav:/app/web/app/components/header/analytics-nav
    - ../web/service/apps-analytics.ts:/app/web/...
    
    # 工作流重试机制
    - ../web/app/components/workflow/nodes/_base/components/retry/retry-on-panel.tsx:/app/web/...
    
    # 应用凭证管理
    - ../web/app/components/app/credentials:/app/web/app/components/app/credentials
    - ../web/app/(commonLayout)/app/(appDetailLayout)/[appId]/credentials:/app/web/...
```

#### 3. API/Worker 服务代码挂载

**挂载的功能模块**:
- 远程文件操作接口
- DOC 格式文档解析
- 工作流日志搜索增强
- 代码节点文件输出
- Sandbox 依赖管理优化
- 多工作空间权限控制
- 应用分析功能
- 工作流重试机制
- 应用级模型凭证管理

```yaml
api:
  build:
    context: ../api
    dockerfile: Dockerfile
  volumes:
    # 远程文件接口
    - ../api/controllers/service_api/app/remote_file.py:/app/api/...
    
    # DOC 格式支持
    - ../api/core/rag/extractor/antiword_doc_extractor.py:/app/api/...
    
    # 工作流日志搜索
    - ../api/services/workflow_app_service.py:/app/api/...
    
    # 代码节点文件输出
    - ../api/core/workflow/nodes/code/code_node.py:/app/api/...
    - ../api/core/helper/code_executor/code_executor.py:/app/api/...
    
    # Python依赖动态库修复
    - ../api/core/helper/code_executor/python3/python3_transformer.py:/app/api/...
    
    # 多工作空间功能
    - ../api/services/workspace_service.py:/app/api/...
    - ../api/services/workspace_permission_service.py:/app/api/...
    
    # 应用分析
    - ../api/controllers/console/app/statistic.py:/app/api/...
    
    # 工作流重试机制
    - ../api/core/plugin/impl/base.py:/app/api/...
    - ../api/core/workflow/graph_engine/graph_engine.py:/app/api/...
    
    # 应用凭证管理
    - ../api/models/app_provider_credential.py:/app/api/...
    - ../api/services/app_credential_service.py:/app/api/...
    - ../api/controllers/console/app/credentials.py:/app/api/...
    - ../api/core/workflow/nodes/llm/llm_utils.py:/app/api/...
    
    # 共享文件目录
    - ./volumes/sandbox/files:/sandbox_files
    - ./volumes/app/storage:/app/api/storage
  environment:
    - FLASK_DEBUG=true
    - DEBUG=true
```

---

## 📌 关键配置说明

### 1. 性能调优参数计算公式

```
总并发连接数 = SERVER_WORKER_AMOUNT × SERVER_WORKER_CONNECTIONS
当前配置: 3 × 100 = 300 并发

总数据库连接需求 = SERVER_WORKER_AMOUNT × (SQLALCHEMY_POOL_SIZE + SQLALCHEMY_MAX_OVERFLOW)
当前配置: 3 × (30 + 20) = 150 连接

PostgreSQL最大连接数应大于总需求:
POSTGRES_MAX_CONNECTIONS (180) > 150 ✓
```

### 2. 超时时间层级

```
前端超时:      TEXT_GENERATION_TIMEOUT_MS = 120000ms (120秒)
API超时:       GUNICORN_TIMEOUT = 360秒
代码执行超时:   CODE_EXECUTION_READ_TIMEOUT = 300秒
沙盒超时:      SANDBOX_WORKER_TIMEOUT = 300秒

层级关系: 前端 < 代码执行 < API
```

### 3. 文件大小限制层级

```
单文件上传:         UPLOAD_FILE_SIZE_LIMIT = 256MB
批量上传数量:       UPLOAD_FILE_BATCH_LIMIT = 30个
代码节点文件:       CODE_MAX_FILE_SIZE = 256MB
图片:              UPLOAD_IMAGE_FILE_SIZE_LIMIT = 100MB
视频:              UPLOAD_VIDEO_FILE_SIZE_LIMIT = 1024MB
音频:              UPLOAD_AUDIO_FILE_SIZE_LIMIT = 200MB
```

---

## ⚠️ 注意事项

### 1. 端口配置建议
- 生产环境使用非常规端口（如 20081、20082）
- 开发环境可以保持默认端口

### 2. 性能参数调优
- `SERVER_WORKER_AMOUNT` 应根据 CPU 核心数调整
- `POSTGRES_SHARED_BUFFERS` 建议为系统内存的 25%
- `POSTGRES_MAX_CONNECTIONS` 应大于所有 worker 的连接需求

### 3. 超时参数配置
- 前端超时应小于 API 超时
- 长时间运行的工作流需要调大超时参数

### 4. Docker Override 使用
- Override 文件仅用于开发环境
- 生产环境应通过正式构建镜像部署
- 挂载路径必须与实际项目结构匹配

---

**文档版本**: v1.0  
**最后更新**: 2026-01-30
