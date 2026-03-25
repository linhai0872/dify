# Dify 二次开发

> 所有二开相关文件集中在此目录

## 快速开始

```bash
make -f Makefile.custom dev-setup   # 初始化开发环境
make -f Makefile.custom dev-start   # 一键启动
make -f Makefile.custom help        # 查看所有命令
```

-> [开发规范](docs/development/README.md)

## 文档索引

| 目录 | 说明 |
|------|------|
| [docs/development/](docs/development/README.md) | 开发规范、环境配置、工作流 |
| [docs/api/](docs/api/README.md) | API 接口规范 |
| [docs/features/](docs/features/README.md) | 功能文档和变更日志 |
| [docs/archive/](docs/archive/) | 已归档的历史文档 |
| [docker/](docker/) | 自定义 Docker 配置 (API、Sandbox) |
| [env/](env/) | 分环境变量配置 (dev/test/prod) |

## 目录结构

```
.custom/
├── docker/           # Docker 自定义配置
│   ├── api/          #   API 镜像扩展 (LibreOffice)
│   ├── sandbox/      #   Sandbox 镜像扩展 (系统依赖)
│   └── docker-compose.override.yaml
├── docs/             # 文档
│   ├── development/  #   开发规范
│   ├── api/          #   API 文档
│   ├── features/     #   功能文档
│   └── archive/      #   归档文档
├── env/              # 环境变量
│   ├── .env.custom.example  # 模板
│   └── .env.custom.*        # 各环境配置
└── logs/             # 开发日志输出
```
