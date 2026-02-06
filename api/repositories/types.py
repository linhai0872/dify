from typing import NotRequired, TypedDict


class DailyRunsStats(TypedDict):
    date: str
    runs: int


class DailyTerminalsStats(TypedDict):
    date: str
    terminal_count: int


class DailyTokenCostStats(TypedDict):
    date: str
    token_count: int
    # [CUSTOM] 二开: Workflow 费用统计 (API 响应字段名保持 total_price 以兼容前端)
    total_price: NotRequired[float]
    currency: NotRequired[str]
    # [/CUSTOM]


class AverageInteractionStats(TypedDict):
    date: str
    interactions: float
