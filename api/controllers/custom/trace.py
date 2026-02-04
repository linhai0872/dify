"""
[CUSTOM] Trace API Controllers

Provides API endpoints for trace ID based lookups.
"""

from flask_login import current_user
from flask_restx import Resource, fields

from controllers.console.wraps import account_initialization_required, setup_required
from controllers.custom import console_custom_api, console_custom_ns, service_custom_api, service_custom_ns
from controllers.service_api.wraps import validate_app_token
from custom.feature_flags import DIFY_CUSTOM_TRACE_SEARCH_ENABLED
from custom.services.custom_trace_service import CustomTraceService
from extensions.ext_database import db
from libs.login import login_required
from models.model import App

# Response models for swagger documentation
workflow_run_model = console_custom_api.model(
    "TraceWorkflowRun",
    {
        "id": fields.String(description="Workflow run ID"),
        "status": fields.String(description="Execution status"),
        "inputs": fields.Raw(description="Input parameters"),
        "outputs": fields.Raw(description="Output results"),
        "elapsed_time": fields.Float(description="Elapsed time in seconds"),
        "total_tokens": fields.Integer(description="Total tokens used"),
        "total_steps": fields.Integer(description="Total steps"),
        "error": fields.String(description="Error message"),
        "created_at": fields.String(description="Created timestamp"),
        "finished_at": fields.String(description="Finished timestamp"),
        "external_trace_id": fields.String(description="External trace ID"),
    },
)

node_execution_model = console_custom_api.model(
    "TraceNodeExecution",
    {
        "id": fields.String(description="Node execution ID"),
        "node_id": fields.String(description="Node ID"),
        "node_type": fields.String(description="Node type"),
        "title": fields.String(description="Node title"),
        "index": fields.Integer(description="Execution order index"),
        "status": fields.String(description="Execution status"),
        "inputs": fields.Raw(description="Node inputs"),
        "outputs": fields.Raw(description="Node outputs"),
        "process_data": fields.Raw(description="Process data"),
        "elapsed_time": fields.Float(description="Elapsed time"),
        "error": fields.String(description="Error message"),
        "created_at": fields.String(description="Created timestamp"),
        "finished_at": fields.String(description="Finished timestamp"),
    },
)

message_model = console_custom_api.model(
    "TraceMessage",
    {
        "id": fields.String(description="Message ID"),
        "conversation_id": fields.String(description="Conversation ID"),
        "query": fields.String(description="User query"),
        "answer": fields.String(description="AI answer"),
        "inputs": fields.Raw(description="Input parameters"),
        "status": fields.String(description="Message status"),
        "error": fields.String(description="Error message"),
        "created_at": fields.String(description="Created timestamp"),
        "external_trace_id": fields.String(description="External trace ID"),
    },
)

agent_thought_model = console_custom_api.model(
    "TraceAgentThought",
    {
        "id": fields.String(description="Thought ID"),
        "position": fields.Integer(description="Position in chain"),
        "thought": fields.String(description="Thought content"),
        "tool": fields.String(description="Tool used"),
        "tool_labels": fields.Raw(description="Tool labels"),
        "tool_input": fields.Raw(description="Tool input"),
        "observation": fields.String(description="Tool observation"),
        "message": fields.String(description="Intermediate message"),
        "answer": fields.String(description="Answer from this thought"),
        "tokens": fields.Integer(description="Tokens used"),
        "latency": fields.Float(description="Latency"),
        "created_at": fields.String(description="Created timestamp"),
    },
)

trace_response_model = console_custom_api.model(
    "TraceResponse",
    {
        "type": fields.String(description="Application type: workflow/chatflow/chat/agent/completion"),
        "workflow_run": fields.Nested(workflow_run_model, allow_null=True, description="Workflow run details"),
        "node_executions": fields.List(
            fields.Nested(node_execution_model), description="Node execution details"
        ),
        "message": fields.Nested(message_model, allow_null=True, description="Message details"),
        "agent_thoughts": fields.List(fields.Nested(agent_thought_model), description="Agent thoughts"),
    },
)


@console_custom_ns.route("/apps/<uuid:app_id>/trace/<string:trace_id>")
class ConsoleTraceApi(Resource):
    """Console API for trace ID lookup."""

    @setup_required
    @login_required
    @account_initialization_required
    @console_custom_api.response(200, "Success", trace_response_model)
    @console_custom_api.response(403, "Forbidden")
    @console_custom_api.response(404, "Not found")
    def get(self, app_id: str, trace_id: str):
        """
        Get execution details by external trace ID.

        Returns complete execution details including workflow run, node executions,
        or message and agent thoughts based on application type.
        """
        # [CUSTOM] Check feature flag
        if not DIFY_CUSTOM_TRACE_SEARCH_ENABLED:
            return {"message": "Trace search feature is disabled"}, 404

        # Get app model and verify access
        app_model = db.session.query(App).filter(App.id == str(app_id)).first()

        if not app_model:
            return {"message": "App not found"}, 404

        # Verify user has access to this app
        if app_model.tenant_id != current_user.current_tenant_id:
            return {"message": "Forbidden"}, 403

        # Get execution details
        result = CustomTraceService.get_execution_by_trace_id(app_model, trace_id)

        if not result:
            return {"message": "No execution found for trace ID"}, 404

        return result, 200


@service_custom_ns.route("/apps/<uuid:app_id>/trace/<string:trace_id>")
class ServiceTraceApi(Resource):
    """Service API for trace ID lookup."""

    @validate_app_token
    @service_custom_api.response(200, "Success", trace_response_model)
    @service_custom_api.response(404, "Not found")
    def get(self, app_model: App, app_id: str, trace_id: str):
        """
        Get execution details by external trace ID.

        Returns complete execution details including workflow run, node executions,
        or message and agent thoughts based on application type.
        """
        # [CUSTOM] Check feature flag
        if not DIFY_CUSTOM_TRACE_SEARCH_ENABLED:
            return {"message": "Trace search feature is disabled"}, 404

        # Get execution details
        result = CustomTraceService.get_execution_by_trace_id(app_model, trace_id)

        if not result:
            return {"message": "No execution found for trace ID"}, 404

        return result, 200
