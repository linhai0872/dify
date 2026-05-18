# [CUSTOM] Extended graphon entities with custom fields
from __future__ import annotations

from datetime import datetime
from typing import Any
from collections.abc import Mapping

from graphon.entities.workflow_execution import WorkflowExecution as _BaseWorkflowExecution
from graphon.enums import WorkflowExecutionStatus, WorkflowType
from pydantic import Field


class WorkflowExecution(_BaseWorkflowExecution):
    """WorkflowExecution extended with custom_external_trace_id support."""

    external_trace_id: str | None = Field(default=None)

    @classmethod
    def new(
        cls,
        *,
        id_: str,
        workflow_id: str,
        workflow_type: WorkflowType,
        workflow_version: str,
        graph: Mapping[str, Any],
        inputs: Mapping[str, Any],
        started_at: datetime,
        external_trace_id: str | None = None,
    ) -> WorkflowExecution:
        return cls(
            id_=id_,
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            workflow_version=workflow_version,
            graph=graph,
            inputs=inputs,
            status=WorkflowExecutionStatus.RUNNING,
            started_at=started_at,
            external_trace_id=external_trace_id,
        )
