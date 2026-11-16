from typing import Callable

from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, ModelRequest, dynamic_prompt
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompts, load_system_prompts


@wrap_tool_call
def monitor_tool(
    # 请求的数据封装
    request: ToolCallRequest,
    # 执行的函数本身
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    # 工具执行的监控
    logger.info(f"[tool monitor]执行工具: {request.tool_call['name']}")
    logger.info(f"[tool monitor]传入参数: {request.tool_call['args']}")
    try:
        result = handler(request)
        logger.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")

        if request.tool_call['name']=="fill_context_for_report":
            request.runtime.context["report"]=True
        return result
    except Exception as e:
        logger.error(f"工具{request.tool_call['name']}调用失败，原因: {str(e)}")
        raise e

@before_model
def log_before_model(
    state: AgentState,        # 整个Agent智能体中的状态记录
    runtime: Runtime,         # 记录了整个执行过程中的上下文信息
):
    # 在模型执行前输出日志
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")
    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content}")
    return None


@dynamic_prompt  # 每一次在生成提示词之前，调用此函数
def report_prompt_switch(request: ModelRequest):  # 动态切换提示词
    # 第一优先级：本次调用内 middleware 写入的运行时标记
    if request.runtime.context.get("report", False):
        return load_report_prompts()

    # 第二优先级：从历史消息里回溯本轮是否已触发过报告信号
    # 这样在「多轮对话 + checkpointer」场景下，报告角色仍能在本轮内延续
    if _report_triggered_in_current_turn(request):
        return load_report_prompts()

    return load_system_prompts()


def _report_triggered_in_current_turn(request: ModelRequest) -> bool:
    """判断「本轮对话」中是否已经调用过 fill_context_for_report。

    关键点是作用范围：只看最后一条 HumanMessage 之后的消息。
    这样上一轮生成过报告，不会污染这一轮的普通咨询——角色切换的生命周期
    被限定在一轮问答之内，天然避免了状态残留。
    """
    state = getattr(request, "state", None) or {}
    messages = state.get("messages", []) if isinstance(state, dict) else []

    # 找到本轮起点：最后一条用户消息的位置
    last_human_index = -1
    for index, message in enumerate(messages):
        if isinstance(message, HumanMessage):
            last_human_index = index

    # 只看本轮产生的消息，历史轮次里的报告信号不生效
    for message in messages[last_human_index + 1:]:
        if isinstance(message, ToolMessage) and message.name == "fill_context_for_report":
            return True
    return False
