# 代码节点文件输出

## 概述

代码节点支持返回 `File` 和 `Array[File]` 类型变量，允许在工作流中通过 Python 代码生成文件（如 Excel、PDF），供后续节点使用或用户下载。

## 支持的输出类型

| 类型 | 说明 |
|------|------|
| `File` | 单个文件 |
| `Array[File]` | 文件数组 |

## 使用方法

在代码节点中返回包含文件信息的字典，支持两种方式：

### 方式一：Base64 编码

```python
import base64
import json

def main():
    content = json.dumps({"hello": "world"}, ensure_ascii=False)
    return {
        "result": {
            "content_base64": base64.b64encode(content.encode()).decode(),
            "mime_type": "application/json",
            "filename": "data.json"
        }
    }
```

### 方式二：文件路径

```python
def main():
    with open("/tmp/output.csv", "w") as f:
        f.write("name,age\nAlice,30\nBob,25")
    return {
        "result": {
            "file_path": "/tmp/output.csv",
            "mime_type": "text/csv",
            "filename": "report.csv"
        }
    }
```

### 返回文件数组

```python
import base64

def main():
    files = []
    for i in range(3):
        content = f"File {i} content"
        files.append({
            "content_base64": base64.b64encode(content.encode()).decode(),
            "mime_type": "text/plain",
            "filename": f"file_{i}.txt"
        })
    return {"files": files}
```

## 配置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `CODE_MAX_FILE_SIZE` | 256 | 代码节点生成文件的大小限制 (MB) |

## 相关文件

- `api/core/workflow/nodes/code/code_node.py` — 文件处理逻辑 (`_create_file_from_info`, `_transform_result`)
- `api/core/workflow/nodes/code/entities.py` — File/ArrayFile 类型注册
- `api/core/variables/segments.py` — `FileSegment` / `ArrayFileSegment`
- `api/core/variables/types.py` — `SegmentType.FILE` / `SegmentType.ARRAY_FILE`
