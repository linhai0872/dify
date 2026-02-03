from __future__ import annotations

from collections.abc import Generator, Mapping, Sequence
from typing import TYPE_CHECKING, Any

from dify_graph.entities.graph_config import NodeConfigDict
from dify_graph.enums import BuiltinNodeTypes, SystemVariableKey, WorkflowNodeExecutionStatus
from dify_graph.node_events import NodeEventBase, NodeRunResult, StreamCompletedEvent
from dify_graph.nodes.base.node import Node
from dify_graph.nodes.base.variable_template_parser import VariableTemplateParser

from .entities import AgentNodeData
from .exceptions import (
    AgentInvocationError,
    AgentMessageTransformError,
)
from .message_transformer import AgentMessageTransformer
from .runtime_support import AgentRuntimeSupport
from .strategy_protocols import AgentStrategyPresentationProvider, AgentStrategyResolver

if TYPE_CHECKING:
    from dify_graph.entities import GraphInitParams
    from dify_graph.runtime import GraphRuntimeState


class AgentNode(Node[AgentNodeData]):
    node_type = BuiltinNodeTypes.AGENT

    _strategy_resolver: AgentStrategyResolver
    _presentation_provider: AgentStrategyPresentationProvider
    _runtime_support: AgentRuntimeSupport
    _message_transformer: AgentMessageTransformer

    def __init__(
        self,
        id: str,
        config: NodeConfigDict,
        graph_init_params: GraphInitParams,
        graph_runtime_state: GraphRuntimeState,
        *,
        strategy_resolver: AgentStrategyResolver,
        presentation_provider: AgentStrategyPresentationProvider,
        runtime_support: AgentRuntimeSupport,
        message_transformer: AgentMessageTransformer,
    ) -> None:
        super().__init__(
            id=id,
            config=config,
            graph_init_params=graph_init_params,
            graph_runtime_state=graph_runtime_state,
        )
        self._strategy_resolver = strategy_resolver
        self._presentation_provider = presentation_provider
        self._runtime_support = runtime_support
        self._message_transformer = message_transformer

    @classmethod
    def version(cls) -> str:
        return "1"

    def populate_start_event(self, event) -> None:
        dify_ctx = self.require_dify_context()
        event.extras["agent_strategy"] = {
            "name": self.node_data.agent_strategy_name,
            "icon": self._presentation_provider.get_icon(
                tenant_id=dify_ctx.tenant_id,
                agent_strategy_provider_name=self.node_data.agent_strategy_provider_name,
            ),
        }

    def _run(self) -> Generator[NodeEventBase, None, None]:
        from core.plugin.impl.exc import PluginDaemonClientSideError

        dify_ctx = self.require_dify_context()

        try:
            strategy = self._strategy_resolver.resolve(
                tenant_id=dify_ctx.tenant_id,
                agent_strategy_provider_name=self.node_data.agent_strategy_provider_name,
                agent_strategy_name=self.node_data.agent_strategy_name,
            )
        except Exception as e:
            yield StreamCompletedEvent(
                node_run_result=NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    inputs={},
                    error=f"Failed to get agent strategy: {str(e)}",
                ),
            )
            return

        agent_parameters = strategy.get_parameters()

        parameters = self._runtime_support.build_parameters(
            agent_parameters=agent_parameters,
            variable_pool=self.graph_runtime_state.variable_pool,
            node_data=self.node_data,
            strategy=strategy,
            tenant_id=dify_ctx.tenant_id,
            app_id=dify_ctx.app_id,
            invoke_from=dify_ctx.invoke_from,
        )
        parameters_for_log = self._runtime_support.build_parameters(
            agent_parameters=agent_parameters,
            variable_pool=self.graph_runtime_state.variable_pool,
            node_data=self.node_data,
            strategy=strategy,
            tenant_id=dify_ctx.tenant_id,
            app_id=dify_ctx.app_id,
            invoke_from=dify_ctx.invoke_from,
            for_log=True,
        )
        credentials = self._runtime_support.build_credentials(parameters=parameters)

        conversation_id = self.graph_runtime_state.variable_pool.get(["sys", SystemVariableKey.CONVERSATION_ID])

        try:
            message_stream = strategy.invoke(
                params=parameters,
                user_id=dify_ctx.user_id,
                app_id=dify_ctx.app_id,
                conversation_id=conversation_id.text if conversation_id else None,
                credentials=credentials,
            )
        except Exception as e:
            error = AgentInvocationError(f"Failed to invoke agent: {str(e)}", original_error=e)
            yield StreamCompletedEvent(
                node_run_result=NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    inputs=parameters_for_log,
                    error=str(error),
                )
            )
            return

        try:
            yield from self._message_transformer.transform(
                messages=message_stream,
                tool_info={
                    "icon": self._presentation_provider.get_icon(
                        tenant_id=dify_ctx.tenant_id,
                        agent_strategy_provider_name=self.node_data.agent_strategy_provider_name,
                    ),
                    "agent_strategy": self.node_data.agent_strategy_name,
                },
                parameters_for_log=parameters_for_log,
                user_id=dify_ctx.user_id,
                tenant_id=dify_ctx.tenant_id,
                node_type=self.node_type,
                node_id=self._node_id,
                node_execution_id=self.id,
            )
        except PluginDaemonClientSideError as e:
            transform_error = AgentMessageTransformError(
                f"Failed to transform agent message: {str(e)}", original_error=e
            )
            yield StreamCompletedEvent(
                node_run_result=NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    inputs=parameters_for_log,
                    error=str(transform_error),
                )
            )

    @classmethod
    def _extract_variable_selector_to_variable_mapping(
        cls,
        *,
        graph_config: Mapping[str, Any],
        node_id: str,
        node_data: AgentNodeData,
    ) -> Mapping[str, Sequence[str]]:
        _ = graph_config  # Explicitly mark as unused
        result: dict[str, Any] = {}
        typed_node_data = node_data
        for parameter_name in typed_node_data.agent_parameters:
            input = typed_node_data.agent_parameters[parameter_name]
            match input.type:
                case "mixed" | "constant":
                    selectors = VariableTemplateParser(str(input.value)).extract_variable_selectors()
                    for selector in selectors:
                        result[selector.variable] = selector.value_selector
                case "variable":
                    result[parameter_name] = input.value

        result = {node_id + "." + key: value for key, value in result.items()}

        return result

    # [CUSTOM] 二开: Agent 节点支持重试
    @property
    def retry(self) -> bool:
        return self.node_data.retry_config.retry_enabled

    # [/CUSTOM]

    @property
    def agent_strategy_icon(self) -> str | None:
        """
        Get agent strategy icon
        :return:
        """
        from core.plugin.impl.plugin import PluginInstaller

        manager = PluginInstaller()
        plugins = manager.list_plugins(self.tenant_id)
        try:
            current_plugin = next(
                plugin
                for plugin in plugins
                if f"{plugin.plugin_id}/{plugin.name}" == self.node_data.agent_strategy_provider_name
            )
            icon = current_plugin.declaration.icon
        except StopIteration:
            icon = None
        return icon

    def _fetch_memory(self, model_instance: ModelInstance) -> TokenBufferMemory | None:
        # get conversation id
        conversation_id_variable = self.graph_runtime_state.variable_pool.get(
            ["sys", SystemVariableKey.CONVERSATION_ID]
        )
        if not isinstance(conversation_id_variable, StringSegment):
            return None
        conversation_id = conversation_id_variable.value

        with Session(db.engine, expire_on_commit=False) as session:
            stmt = select(Conversation).where(Conversation.app_id == self.app_id, Conversation.id == conversation_id)
            conversation = session.scalar(stmt)

            if not conversation:
                return None

        memory = TokenBufferMemory(conversation=conversation, model_instance=model_instance)

        return memory

    def _fetch_model(self, value: dict[str, Any]) -> tuple[ModelInstance, AIModelEntity | None]:
        provider_manager = ProviderManager()
        provider_model_bundle = provider_manager.get_provider_model_bundle(
            tenant_id=self.tenant_id, provider=value.get("provider", ""), model_type=ModelType.LLM
        )
        model_name = value.get("model", "")
        model_credentials = provider_model_bundle.configuration.get_current_credentials(
            model_type=ModelType.LLM, model=model_name
        )
        provider_name = provider_model_bundle.configuration.provider.provider
        model_type_instance = provider_model_bundle.model_type_instance
        model_instance = ModelManager().get_model_instance(
            tenant_id=self.tenant_id,
            provider=provider_name,
            model_type=ModelType(value.get("model_type", "")),
            model=model_name,
        )
        model_schema = model_type_instance.get_model_schema(model_name, model_credentials)
        return model_instance, model_schema

    def _remove_unsupported_model_features_for_old_version(self, model_schema: AIModelEntity) -> AIModelEntity:
        if model_schema.features:
            for feature in model_schema.features[:]:  # Create a copy to safely modify during iteration
                try:
                    AgentOldVersionModelFeatures(feature.value)  # Try to create enum member from value
                except ValueError:
                    model_schema.features.remove(feature)
        return model_schema

    def _filter_mcp_type_tool(self, strategy: PluginAgentStrategy, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Filter MCP type tool
        :param strategy: plugin agent strategy
        :param tool: tool
        :return: filtered tool dict
        """
        meta_version = strategy.meta_version
        if meta_version and Version(meta_version) > Version("0.0.1"):
            return tools
        else:
            return [tool for tool in tools if tool.get("type") != ToolProviderType.MCP]

    def _transform_message(
        self,
        messages: Generator[ToolInvokeMessage, None, None],
        tool_info: Mapping[str, Any],
        parameters_for_log: dict[str, Any],
        user_id: str,
        tenant_id: str,
        node_type: NodeType,
        node_id: str,
        node_execution_id: str,
    ) -> Generator[NodeEventBase, None, None]:
        """
        Convert ToolInvokeMessages into tuple[plain_text, files]
        """
        # transform message and handle file storage
        from core.plugin.impl.plugin import PluginInstaller

        message_stream = ToolFileMessageTransformer.transform_tool_invoke_messages(
            messages=messages,
            user_id=user_id,
            tenant_id=tenant_id,
            conversation_id=None,
        )

        text = ""
        files: list[File] = []
        json_list: list[dict | list] = []

        agent_logs: list[AgentLogEvent] = []
        agent_execution_metadata: Mapping[WorkflowNodeExecutionMetadataKey, Any] = {}
        llm_usage = LLMUsage.empty_usage()
        variables: dict[str, Any] = {}

        for message in message_stream:
            if message.type in {
                ToolInvokeMessage.MessageType.IMAGE_LINK,
                ToolInvokeMessage.MessageType.BINARY_LINK,
                ToolInvokeMessage.MessageType.IMAGE,
            }:
                assert isinstance(message.message, ToolInvokeMessage.TextMessage)

                url = message.message.text
                if message.meta:
                    transfer_method = message.meta.get("transfer_method", FileTransferMethod.TOOL_FILE)
                else:
                    transfer_method = FileTransferMethod.TOOL_FILE

                tool_file_id = str(url).split("/")[-1].split(".")[0]

                with Session(db.engine) as session:
                    stmt = select(ToolFile).where(ToolFile.id == tool_file_id)
                    tool_file = session.scalar(stmt)
                    if tool_file is None:
                        raise ToolFileNotFoundError(tool_file_id)

                mapping = {
                    "tool_file_id": tool_file_id,
                    "type": file_factory.get_file_type_by_mime_type(tool_file.mimetype),
                    "transfer_method": transfer_method,
                    "url": url,
                }
                file = file_factory.build_from_mapping(
                    mapping=mapping,
                    tenant_id=tenant_id,
                )
                files.append(file)
            elif message.type == ToolInvokeMessage.MessageType.BLOB:
                # get tool file id
                assert isinstance(message.message, ToolInvokeMessage.TextMessage)
                assert message.meta

                tool_file_id = message.message.text.split("/")[-1].split(".")[0]
                with Session(db.engine) as session:
                    stmt = select(ToolFile).where(ToolFile.id == tool_file_id)
                    tool_file = session.scalar(stmt)
                    if tool_file is None:
                        raise ToolFileNotFoundError(tool_file_id)

                mapping = {
                    "tool_file_id": tool_file_id,
                    "transfer_method": FileTransferMethod.TOOL_FILE,
                }

                files.append(
                    file_factory.build_from_mapping(
                        mapping=mapping,
                        tenant_id=tenant_id,
                    )
                )
            elif message.type == ToolInvokeMessage.MessageType.TEXT:
                assert isinstance(message.message, ToolInvokeMessage.TextMessage)
                text += message.message.text
                yield StreamChunkEvent(
                    selector=[node_id, "text"],
                    chunk=message.message.text,
                    is_final=False,
                )
            elif message.type == ToolInvokeMessage.MessageType.JSON:
                assert isinstance(message.message, ToolInvokeMessage.JsonMessage)
                if node_type == NodeType.AGENT:
                    if isinstance(message.message.json_object, dict):
                        msg_metadata: dict[str, Any] = message.message.json_object.pop("execution_metadata", {})
                        llm_usage = LLMUsage.from_metadata(cast(LLMUsageMetadata, msg_metadata))
                        agent_execution_metadata = {
                            WorkflowNodeExecutionMetadataKey(key): value
                            for key, value in msg_metadata.items()
                            if key in WorkflowNodeExecutionMetadataKey.__members__.values()
                        }
                    else:
                        msg_metadata = {}
                        llm_usage = LLMUsage.empty_usage()
                        agent_execution_metadata = {}
                if message.message.json_object:
                    json_list.append(message.message.json_object)
            elif message.type == ToolInvokeMessage.MessageType.LINK:
                assert isinstance(message.message, ToolInvokeMessage.TextMessage)
                stream_text = f"Link: {message.message.text}\n"
                text += stream_text
                yield StreamChunkEvent(
                    selector=[node_id, "text"],
                    chunk=stream_text,
                    is_final=False,
                )
            elif message.type == ToolInvokeMessage.MessageType.VARIABLE:
                assert isinstance(message.message, ToolInvokeMessage.VariableMessage)
                variable_name = message.message.variable_name
                variable_value = message.message.variable_value
                if message.message.stream:
                    if not isinstance(variable_value, str):
                        raise AgentVariableTypeError(
                            "When 'stream' is True, 'variable_value' must be a string.",
                            variable_name=variable_name,
                            expected_type="str",
                            actual_type=type(variable_value).__name__,
                        )
                    if variable_name not in variables:
                        variables[variable_name] = ""
                    variables[variable_name] += variable_value

                    yield StreamChunkEvent(
                        selector=[node_id, variable_name],
                        chunk=variable_value,
                        is_final=False,
                    )
                else:
                    variables[variable_name] = variable_value
            elif message.type == ToolInvokeMessage.MessageType.FILE:
                assert message.meta is not None
                assert isinstance(message.meta, dict)
                # Validate that meta contains a 'file' key
                if "file" not in message.meta:
                    raise AgentNodeError("File message is missing 'file' key in meta")

                # Validate that the file is an instance of File
                if not isinstance(message.meta["file"], File):
                    raise AgentNodeError(f"Expected File object but got {type(message.meta['file']).__name__}")
                files.append(message.meta["file"])
            elif message.type == ToolInvokeMessage.MessageType.LOG:
                assert isinstance(message.message, ToolInvokeMessage.LogMessage)
                if message.message.metadata:
                    icon = tool_info.get("icon", "")
                    dict_metadata = dict(message.message.metadata)
                    if dict_metadata.get("provider"):
                        manager = PluginInstaller()
                        plugins = manager.list_plugins(tenant_id)
                        try:
                            current_plugin = next(
                                plugin
                                for plugin in plugins
                                if f"{plugin.plugin_id}/{plugin.name}" == dict_metadata["provider"]
                            )
                            icon = current_plugin.declaration.icon
                        except StopIteration:
                            pass
                        icon_dark = None
                        try:
                            builtin_tool = next(
                                provider
                                for provider in BuiltinToolManageService.list_builtin_tools(
                                    user_id,
                                    tenant_id,
                                )
                                if provider.name == dict_metadata["provider"]
                            )
                            icon = builtin_tool.icon
                            icon_dark = builtin_tool.icon_dark
                        except StopIteration:
                            pass

                        dict_metadata["icon"] = icon
                        dict_metadata["icon_dark"] = icon_dark
                        message.message.metadata = dict_metadata
                agent_log = AgentLogEvent(
                    message_id=message.message.id,
                    node_execution_id=node_execution_id,
                    parent_id=message.message.parent_id,
                    error=message.message.error,
                    status=message.message.status.value,
                    data=message.message.data,
                    label=message.message.label,
                    metadata=message.message.metadata,
                    node_id=node_id,
                )

                # check if the agent log is already in the list
                for log in agent_logs:
                    if log.message_id == agent_log.message_id:
                        # update the log
                        log.data = agent_log.data
                        log.status = agent_log.status
                        log.error = agent_log.error
                        log.label = agent_log.label
                        log.metadata = agent_log.metadata
                        break
                else:
                    agent_logs.append(agent_log)

                yield agent_log

        # Add agent_logs to outputs['json'] to ensure frontend can access thinking process
        json_output: list[dict[str, Any] | list[Any]] = []

        # Step 1: append each agent log as its own dict.
        if agent_logs:
            for log in agent_logs:
                json_output.append(
                    {
                        "id": log.message_id,
                        "parent_id": log.parent_id,
                        "error": log.error,
                        "status": log.status,
                        "data": log.data,
                        "label": log.label,
                        "metadata": log.metadata,
                        "node_id": log.node_id,
                    }
                )
        # Step 2: normalize JSON into {"data": [...]}.change json to list[dict]
        if json_list:
            json_output.extend(json_list)
        else:
            json_output.append({"data": []})

        # Send final chunk events for all streamed outputs
        # Final chunk for text stream
        yield StreamChunkEvent(
            selector=[node_id, "text"],
            chunk="",
            is_final=True,
        )

        # Final chunks for any streamed variables
        for var_name in variables:
            yield StreamChunkEvent(
                selector=[node_id, var_name],
                chunk="",
                is_final=True,
            )

        yield StreamCompletedEvent(
            node_run_result=NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                outputs={
                    "text": text,
                    "usage": jsonable_encoder(llm_usage),
                    "files": ArrayFileSegment(value=files),
                    "json": json_output,
                    **variables,
                },
                metadata={
                    **agent_execution_metadata,
                    WorkflowNodeExecutionMetadataKey.TOOL_INFO: tool_info,
                    WorkflowNodeExecutionMetadataKey.AGENT_LOG: agent_logs,
                },
                inputs=parameters_for_log,
                llm_usage=llm_usage,
            )
        )
>>>>>>> 74816a8a7a (feat(workflow): [CUSTOM] 添加指数退避重试机制)
