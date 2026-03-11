"""
GBase8a 数据库产品经理助手 Agent
"""
import os
import json
import logging
from typing import Annotated
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, ToolMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver
from storage.long_term.compression_manager import ConversationCompressionManager
from storage.long_term.context_retriever import ContextRetriever
from storage.long_term.context_injector import ContextInjector
from storage.long_term.agent_managers import AgentManagers

logger = logging.getLogger(__name__)

# 导入工具
from tools.unified_search_tool import (
    web_search,
    search_competitor_info,
    search_market_trends,
    search_database_best_practices
)
from tools.knowledge_tool import (
    import_document_to_knowledge,
    search_knowledge_base,
    query_technical_detail
)
from tools.hybrid_search_tool import hybrid_search
from tools.document_generation_tool import (
    generate_requirement_doc,
    generate_competitor_report,
    generate_market_analysis_doc,
    generate_optimization_proposal
)
from tools.unified_fetch_tool import (
    fetch_url,
    fetch_webpage_content,
    fetch_article_summary,
    fetch_document_content
)
from tools.language_style_tool import (
    list_available_styles,
    switch_language_style,
    get_current_style_info
)
# SQL 生成工具
from tools.sql_generation_tool import generate_sql
from tools.sql_validation_tool import validate_sql
from tools.sql_feedback_tool import record_sql_feedback, manage_sql_examples

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore

class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        logger.error(f"Tool execution error: {e}", exc_info=True)
        return ToolMessage(
            content=f"Tool execute error: ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )


def build_agent(ctx=None):
    """
    构建 GBase8a 数据库产品经理助手 Agent

    Returns:
        Agent 实例
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)

    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    # 初始化 LLM
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )

    # 定义工具列表（按优先级排序）
    tools = [
        # 混合检索工具（最高优先级 - 强制执行）
        hybrid_search,
        # 知识库管理工具
        import_document_to_knowledge,
        search_knowledge_base,
        query_technical_detail,
        # 统一搜索工具
        web_search,
        # 兼容性搜索工具（调用统一搜索工具）
        search_competitor_info,
        search_market_trends,
        search_database_best_practices,
        # 文档生成工具
        generate_requirement_doc,
        generate_competitor_report,
        generate_market_analysis_doc,
        generate_optimization_proposal,
        # 统一网页获取工具（新增）
        fetch_url,
        # 兼容性网页获取工具（调用统一获取工具）
        fetch_webpage_content,
        fetch_article_summary,
        fetch_document_content,
        # 语言风格管理工具
        list_available_styles,
        switch_language_style,
        get_current_style_info,
        # SQL 生成工具
        generate_sql,
        validate_sql,
        record_sql_feedback,
        manage_sql_examples
    ]

    # 创建 Agent
    agent = create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
        middleware=[handle_tool_errors]
    )
    
    # 初始化管理器（单例模式）
    if not AgentManagers.is_initialized():
        AgentManagers.initialize(
            llm=llm,
            compression_threshold=100,  # 消息数达到 100 时触发压缩
            compression_interval_hours=24,  # 每 24 小时最多压缩一次
            enable_compression=True,  # 启用压缩
            kb_table_name="long_term_conversations",
            min_score=0.6,
            max_contexts=5,
            enable_injection=True
        )
    
    return agent
