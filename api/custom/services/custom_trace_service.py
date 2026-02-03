"""
[CUSTOM] Custom Trace Service

This service provides trace ID lookup functionality for workflow runs and messages.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from extensions.ext_database import db
from models.model import App, AppMode, EndUser, Message, MessageAgentThought
from models.workflow import WorkflowNodeExecutionModel, WorkflowRun


class CustomTraceService:
    """Service for trace ID based lookups."""

    @staticmethod
    def get_execution_by_trace_id(
        app_model: App,
        trace_id: str,
    ) -> dict[str, Any] | None:
        """
        Get execution details by external trace ID.

        Args:
            app_model: The application model
            trace_id: The external trace ID to look up

        Returns:
            A dictionary containing execution details, or None if not found.
            The structure varies based on application type.
        """
        app_mode = AppMode(app_model.mode)

        if app_mode == AppMode.WORKFLOW:
            return CustomTraceService._get_workflow_execution(app_model, trace_id)
        elif app_mode == AppMode.ADVANCED_CHAT:
            return CustomTraceService._get_chatflow_execution(app_model, trace_id)
        elif app_mode in (AppMode.CHAT, AppMode.AGENT_CHAT):
            return CustomTraceService._get_chat_execution(app_model, trace_id)
        elif app_mode == AppMode.COMPLETION:
            return CustomTraceService._get_completion_execution(app_model, trace_id)
        else:
            return None

    @staticmethod
    def _get_workflow_execution(app_model: App, trace_id: str) -> dict[str, Any] | None:
        """Get workflow execution by trace ID."""
        # Query WorkflowRun by external_trace_id
        workflow_run = (
            db.session.query(WorkflowRun)
            .filter(
                WorkflowRun.app_id == app_model.id,
                WorkflowRun.tenant_id == app_model.tenant_id,
                WorkflowRun.external_trace_id == trace_id,
            )
            .order_by(WorkflowRun.created_at.desc())
            .first()
        )

        if not workflow_run:
            return None

        # Get node executions
        node_executions = CustomTraceService._get_node_executions(workflow_run.id)

        return {
            "type": "workflow",
            "workflow_run": CustomTraceService._format_workflow_run(workflow_run),
            "node_executions": node_executions,
        }

    @staticmethod
    def _get_chatflow_execution(app_model: App, trace_id: str) -> dict[str, Any] | None:
        """Get chatflow (advanced chat) execution by trace ID."""
        # First try to find message by trace_id
        message = (
            db.session.query(Message)
            .filter(
                Message.app_id == app_model.id,
                Message.external_trace_id == trace_id,
            )
            .order_by(Message.created_at.desc())
            .first()
        )

        if not message:
            # Also try to find by workflow_run's trace_id
            workflow_run = (
                db.session.query(WorkflowRun)
                .filter(
                    WorkflowRun.app_id == app_model.id,
                    WorkflowRun.tenant_id == app_model.tenant_id,
                    WorkflowRun.external_trace_id == trace_id,
                )
                .order_by(WorkflowRun.created_at.desc())
                .first()
            )

            if workflow_run:
                # Find associated message
                message = (
                    db.session.query(Message)
                    .filter(
                        Message.app_id == app_model.id,
                        Message.workflow_run_id == workflow_run.id,
                    )
                    .first()
                )

            if not message:
                return None

        # Get workflow run if available
        workflow_run_data = None
        node_executions = []
        if message.workflow_run_id:
            workflow_run = db.session.query(WorkflowRun).filter(WorkflowRun.id == message.workflow_run_id).first()
            if workflow_run:
                workflow_run_data = CustomTraceService._format_workflow_run(workflow_run)
                node_executions = CustomTraceService._get_node_executions(workflow_run.id)

        return {
            "type": "chatflow",
            "message": CustomTraceService._format_message(message),
            "agent_thoughts": [],
            "workflow_run": workflow_run_data,
            "node_executions": node_executions,
        }

    @staticmethod
    def _get_chat_execution(app_model: App, trace_id: str) -> dict[str, Any] | None:
        """Get chat/agent execution by trace ID."""
        message = (
            db.session.query(Message)
            .filter(
                Message.app_id == app_model.id,
                Message.external_trace_id == trace_id,
            )
            .order_by(Message.created_at.desc())
            .first()
        )

        if not message:
            return None

        # Get agent thoughts if any
        agent_thoughts = CustomTraceService._get_agent_thoughts(message.id)

        app_type = "agent" if app_model.mode == AppMode.AGENT_CHAT else "chat"

        return {
            "type": app_type,
            "message": CustomTraceService._format_message(message),
            "agent_thoughts": agent_thoughts,
            "workflow_run": None,
            "node_executions": [],
        }

    @staticmethod
    def _get_completion_execution(app_model: App, trace_id: str) -> dict[str, Any] | None:
        """Get completion execution by trace ID."""
        message = (
            db.session.query(Message)
            .filter(
                Message.app_id == app_model.id,
                Message.external_trace_id == trace_id,
            )
            .order_by(Message.created_at.desc())
            .first()
        )

        if not message:
            return None

        return {
            "type": "completion",
            "message": CustomTraceService._format_message(message),
            "agent_thoughts": [],
            "workflow_run": None,
            "node_executions": [],
        }

    @staticmethod
    def _format_workflow_run(workflow_run: WorkflowRun) -> dict[str, Any]:
        """Format WorkflowRun for response."""
        return {
            "id": workflow_run.id,
            "status": workflow_run.status,
            "inputs": workflow_run.inputs_dict,
            "outputs": workflow_run.outputs_dict,
            "elapsed_time": workflow_run.elapsed_time,
            "total_tokens": workflow_run.total_tokens,
            "total_steps": workflow_run.total_steps,
            "error": workflow_run.error,
            "created_at": workflow_run.created_at.isoformat() if workflow_run.created_at else None,
            "finished_at": workflow_run.finished_at.isoformat() if workflow_run.finished_at else None,
            "external_trace_id": workflow_run.external_trace_id,
        }

    @staticmethod
    def _format_message(message: Message) -> dict[str, Any]:
        """Format Message for response."""
        return {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "query": message.query,
            "answer": message.answer,
            "inputs": message.inputs,
            "status": message.status,
            "error": message.error,
            "created_at": message.created_at.isoformat() if message.created_at else None,
            "external_trace_id": message.external_trace_id,
        }

    @staticmethod
    def _get_node_executions(workflow_run_id: str) -> list[dict[str, Any]]:
        """Get node executions for a workflow run."""
        node_executions = (
            db.session.query(WorkflowNodeExecutionModel)
            .filter(WorkflowNodeExecutionModel.workflow_run_id == workflow_run_id)
            .order_by(WorkflowNodeExecutionModel.index.asc())
            .all()
        )

        return [
            {
                "id": ne.id,
                "node_id": ne.node_id,
                "node_type": ne.node_type,
                "title": ne.title,
                "index": ne.index,
                "status": ne.status,
                "inputs": ne.inputs_dict,
                "outputs": ne.outputs_dict,
                "process_data": ne.process_data_dict,
                "elapsed_time": ne.elapsed_time,
                "error": ne.error,
                "created_at": ne.created_at.isoformat() if ne.created_at else None,
                "finished_at": ne.finished_at.isoformat() if ne.finished_at else None,
            }
            for ne in node_executions
        ]

    @staticmethod
    def _get_agent_thoughts(message_id: str) -> list[dict[str, Any]]:
        """Get agent thoughts for a message."""
        thoughts = (
            db.session.query(MessageAgentThought)
            .filter(MessageAgentThought.message_id == message_id)
            .order_by(MessageAgentThought.position.asc())
            .all()
        )

        return [
            {
                "id": t.id,
                "position": t.position,
                "thought": t.thought,
                "tool": t.tool,
                "tool_labels": t.tool_labels,
                "tool_input": t.tool_input,
                "observation": t.observation,
                "message": t.message,
                "answer": t.answer,
                "tokens": t.tokens,
                "latency": t.latency,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in thoughts
        ]
