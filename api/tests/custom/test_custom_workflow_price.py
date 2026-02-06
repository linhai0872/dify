"""
[CUSTOM] Tests for workflow total_price feature.

Verifies the write path from GraphRuntimeState.llm_usage → WorkflowExecution
→ WorkflowRun, and the statistics query response shape.
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock, PropertyMock, patch

from core.workflow.entities.workflow_execution import WorkflowExecution
from core.workflow.enums import WorkflowExecutionStatus, WorkflowType


def _make_execution(**overrides) -> WorkflowExecution:
    """Create a WorkflowExecution with sensible defaults."""
    defaults = {
        "id_": "run-test",
        "workflow_id": "wf-test",
        "workflow_type": WorkflowType.WORKFLOW,
        "workflow_version": "v1",
        "graph": {"nodes": [], "edges": []},
        "inputs": {"key": "value"},
        "started_at": datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return WorkflowExecution.new(**defaults)


class TestWorkflowExecutionPriceFields:
    """Tests that WorkflowExecution carries custom_total_price/custom_currency."""

    def test_default_values(self):
        """New WorkflowExecution has zero price and USD currency."""
        execution = _make_execution()
        assert execution.custom_total_price == Decimal(0)
        assert execution.custom_currency == "USD"

    def test_price_assignment(self):
        """custom_total_price and custom_currency can be set."""
        execution = _make_execution()
        execution.custom_total_price = Decimal("0.0012345")
        execution.custom_currency = "CNY"
        assert execution.custom_total_price == Decimal("0.0012345")
        assert execution.custom_currency == "CNY"


class TestWorkflowRunMapping:
    """Tests that _create/_update_workflow_run_from_execution maps price fields."""

    @patch("tasks.workflow_execution_tasks.WorkflowRuntimeTypeConverter")
    @patch("tasks.workflow_execution_tasks.WorkflowRun")
    def test_create_maps_price_fields(self, mock_workflow_run_cls, mock_converter_cls):
        """_create_workflow_run_from_execution copies custom_total_price to WorkflowRun."""
        from tasks.workflow_execution_tasks import _create_workflow_run_from_execution

        mock_run = MagicMock()
        mock_workflow_run_cls.return_value = mock_run
        mock_converter_cls.return_value.to_json_encodable.return_value = {}

        execution = _make_execution(id_="run-3")
        execution.status = WorkflowExecutionStatus.SUCCEEDED
        execution.finished_at = datetime(2026, 1, 1, 0, 0, 5, tzinfo=UTC)
        execution.custom_total_price = Decimal("0.0024")
        execution.custom_currency = "USD"

        result = _create_workflow_run_from_execution(
            execution=execution,
            tenant_id="t1",
            app_id="a1",
            triggered_from=MagicMock(value="app"),
            creator_user_id="u1",
            creator_user_role=MagicMock(value="account"),
        )

        assert result.custom_total_price == Decimal("0.0024")
        assert result.custom_currency == "USD"

    @patch("tasks.workflow_execution_tasks.WorkflowRuntimeTypeConverter")
    def test_update_maps_price_fields(self, mock_converter_cls):
        """_update_workflow_run_from_execution copies custom_total_price to WorkflowRun."""
        from tasks.workflow_execution_tasks import _update_workflow_run_from_execution

        mock_converter_cls.return_value.to_json_encodable.return_value = {}

        mock_run = MagicMock()
        execution = _make_execution(id_="run-4")
        execution.status = WorkflowExecutionStatus.SUCCEEDED
        execution.finished_at = datetime(2026, 1, 1, 0, 0, 10, tzinfo=UTC)
        execution.custom_total_price = Decimal("1.5")
        execution.custom_currency = "EUR"

        _update_workflow_run_from_execution(mock_run, execution)

        assert mock_run.custom_total_price == Decimal("1.5")
        assert mock_run.custom_currency == "EUR"


class TestPersistencePopulatePrice:
    """Tests that _populate_completion_statistics writes price from llm_usage."""

    def test_populate_writes_price_from_llm_usage(self):
        """Verify persistence layer copies llm_usage.total_price → execution.custom_total_price."""
        from core.app.workflow.layers.persistence import WorkflowPersistenceLayer

        mock_runtime_state = MagicMock()
        mock_runtime_state.total_tokens = 500
        mock_runtime_state.node_run_steps = 3
        mock_runtime_state.outputs = {"result": "ok"}
        mock_runtime_state.exceptions_count = 0
        mock_runtime_state.llm_usage.total_price = Decimal("0.0042")
        mock_runtime_state.llm_usage.currency = "USD"

        execution = _make_execution(id_="run-5")

        layer = WorkflowPersistenceLayer.__new__(WorkflowPersistenceLayer)
        type(layer).graph_runtime_state = PropertyMock(return_value=mock_runtime_state)

        layer._populate_completion_statistics(execution, update_finished=False)

        assert execution.custom_total_price == Decimal("0.0042")
        assert execution.custom_currency == "USD"
        assert execution.total_tokens == 500
