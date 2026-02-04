# 原生文档提取器

为 Dify 默认模式（ETL_TYPE=dify）添加对 DOC、PPT、PPTX、EPUB 文件格式的原生支持。

## 概述

**业务价值**：
- 降低部署复杂度：用户无需配置 Unstructured API 即可使用常见办公文档格式
- 支持更多文件类型：知识库和工作流文档提取节点均可处理这些格式
- 保持灵活性：通过功能开关控制，可随时切换回 Unstructured 模式

**支持格式**：

| 格式 | 解析库 | 依赖 |
|------|--------|------|
| PPTX | python-pptx | 纯 Python |
| EPUB | ebooklib + BeautifulSoup | 纯 Python |
| DOC | unstructured.partition.doc | LibreOffice |
| PPT | unstructured.partition.ppt | LibreOffice |

## 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `DIFY_CUSTOM_NATIVE_EXTRACTORS_ENABLED` | `true` | 启用原生提取器 |
| `API_IMAGE` | 官方镜像 | 自定义 API 镜像（含 LibreOffice） |

## 使用方法

### 1. PPTX/EPUB（无需额外配置）

PPTX 和 EPUB 使用纯 Python 库，启动即可使用：
- 知识库：上传 PPTX/EPUB 文件到知识库
- 工作流：在文档提取节点中处理 PPTX/EPUB 文件

### 2. DOC/PPT（需要 LibreOffice）

DOC 和 PPT 格式需要 LibreOffice 支持。

**Docker 环境**（推荐）：

使用 Makefile.custom 启动会自动构建包含 LibreOffice 的镜像：

```bash
# 测试环境
make -f Makefile.custom start-test

# 生产环境
make -f Makefile.custom deploy-prod
```

**本地开发环境**：

手动安装 LibreOffice：

```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt-get install libreoffice-writer-nogui libreoffice-impress-nogui
```

## 功能范围

本功能影响两个入口点：

| 入口 | 位置 | 影响 |
|------|------|------|
| 知识库上传 | `api/core/rag/extractor/extract_processor.py` | 支持 DOC/PPT/PPTX/EPUB 文件上传 |
| 工作流节点 | `api/core/workflow/nodes/document_extractor/node.py` | 文档提取节点支持这些格式 |

## 文件结构

```
api/custom/extractors/
├── __init__.py              # 模块导出
├── pptx_extractor.py        # PPTX 原生提取器
├── epub_extractor.py        # EPUB 原生提取器
├── doc_extractor.py         # DOC 提取器（需 LibreOffice）
└── ppt_extractor.py         # PPT 提取器（需 LibreOffice）

.custom/docker/api/
├── Dockerfile.api-custom    # 扩展镜像（含 LibreOffice）
└── system-requirements.txt  # 系统依赖声明
```

## 注意事项

1. **LibreOffice 冷启动**：首次处理 DOC/PPT 文件时，LibreOffice 启动需要约 10 秒，后续调用会快很多

2. **禁用功能**：设置 `DIFY_CUSTOM_NATIVE_EXTRACTORS_ENABLED=false` 可回退到原有行为

3. **本地开发**：如果只处理 PPTX/EPUB，无需安装 LibreOffice；只有 DOC/PPT 需要

4. **镜像体积**：自定义 API 镜像增加约 150MB（LibreOffice 最小化安装 + CJK 字体）

## 测试

```bash
# 运行提取器单元测试
cd api && uv run pytest tests/custom/extractors/ -v

# 测试特定提取器
cd api && uv run pytest tests/custom/extractors/test_pptx_extractor.py -v
```

## 相关提交

- [c5fbf37ca] feat(rag): [CUSTOM] 添加原生文档提取器支持 DOC/PPT/PPTX/EPUB 格式
