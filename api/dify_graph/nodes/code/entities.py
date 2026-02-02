from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel

from dify_graph.entities.base_node_data import BaseNodeData
from dify_graph.enums import BuiltinNodeTypes, NodeType
from dify_graph.nodes.base.entities import VariableSelector
from dify_graph.variables.types import SegmentType


class CodeLanguage(StrEnum):
    PYTHON3 = "python3"
    JINJA2 = "jinja2"
    JAVASCRIPT = "javascript"


# [CUSTOM] 扩展代码节点允许的输出类型
# 添加 FILE 和 ARRAY_FILE 支持文件生成功能
_ALLOWED_OUTPUT_FROM_CODE = frozenset(
    [
        SegmentType.STRING,
        SegmentType.NUMBER,
        SegmentType.OBJECT,
        SegmentType.BOOLEAN,
        SegmentType.ARRAY_STRING,
        SegmentType.ARRAY_NUMBER,
        SegmentType.ARRAY_OBJECT,
        SegmentType.ARRAY_BOOLEAN,
        SegmentType.FILE,        # [CUSTOM] 单文件输出
        SegmentType.ARRAY_FILE,  # [CUSTOM] 文件数组输出
    ]
)
# [/CUSTOM]


def _validate_type(segment_type: SegmentType) -> SegmentType:
    if segment_type not in _ALLOWED_OUTPUT_FROM_CODE:
        raise ValueError(f"invalid type for code output, expected {_ALLOWED_OUTPUT_FROM_CODE}, actual {segment_type}")
    return segment_type


class CodeNodeData(BaseNodeData):
    """
    Code Node Data.
    """

    type: NodeType = BuiltinNodeTypes.CODE

    class Output(BaseModel):
        type: Annotated[SegmentType, AfterValidator(_validate_type)]
        children: dict[str, "CodeNodeData.Output"] | None = None

    class Dependency(BaseModel):
        name: str
        version: str

    variables: list[VariableSelector]
    code_language: Literal[CodeLanguage.PYTHON3, CodeLanguage.JAVASCRIPT]
    code: str
    outputs: dict[str, Output]
    dependencies: list[Dependency] | None = None
