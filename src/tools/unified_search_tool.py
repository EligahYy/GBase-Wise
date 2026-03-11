"""
统一联网搜索工具
整合竞品搜索、市场趋势搜索、最佳实践搜索等功能
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Optional, Literal


@tool
def web_search(
    query: str,
    search_type: Literal["general", "competitor", "market", "best_practice"] = "general",
    time_range: Optional[str] = None,
    count: int = 5,
    need_summary: bool = True,
    runtime: ToolRuntime = None
) -> str:
    """
    统一的联网搜索工具，支持多种搜索场景

    Args:
        query: 搜索关键词，例如 "Oracle 数据库特性", "数据库市场趋势"
        search_type: 搜索类型
            - "general": 通用搜索
            - "competitor": 竞品搜索（产品特性、市场表现、技术架构）
            - "market": 市场趋势搜索（行业趋势、发展方向）
            - "best_practice": 最佳实践搜索（技术方案、实践指南）
        time_range: 时间范围，支持 "1d"(1天), "1w"(1周), "1m"(1月)，仅市场趋势搜索使用
        count: 返回结果数量，默认 5
        need_summary: 是否包含 AI 总结，默认 True
        runtime: 工具运行时上下文

    Returns:
        返回搜索结果，包含标题、来源、URL、AI 总结等信息
    """
    ctx = runtime.context if runtime else new_context(method="search.web")
    client = SearchClient(ctx=ctx)

    try:
        # 根据搜索类型设置默认参数
        search_params = {
            "query": query,
            "count": count,
            "need_summary": need_summary
        }

        # 市场趋势搜索特殊处理
        if search_type == "market":
            search_params["search_type"] = "web"
            search_params["time_range"] = time_range or "1m"
            search_params["count"] = min(count, 8)  # 市场趋势返回更多结果
            response = client.search(**search_params)
        else:
            # web_search 方法只支持 query, count, need_summary 参数
            response = client.web_search(**search_params)

        if not response.web_items:
            return f"未找到关于 '{query}' 的相关信息"

        # 构建结果
        result_parts = []
        search_type_name = {
            "general": "通用",
            "competitor": "竞品",
            "market": "市场趋势",
            "best_practice": "最佳实践"
        }.get(search_type, "通用")

        result_parts.append(f"## {search_type_name}搜索: {query}\n")
        if search_type == "market" and time_range:
            result_parts.append(f"### 时间范围: 最近 {time_range}\n")
        result_parts.append(f"### 找到 {len(response.web_items)} 条相关信息\n")

        # AI 总结
        if response.summary and need_summary:
            summary_title = "AI 分析总结" if search_type == "market" else "AI 总结"
            result_parts.append(f"**{summary_title}**:\n{response.summary}\n")

        # 详细信息
        result_parts.append("**详细信息**:\n")

        for idx, item in enumerate(response.web_items, 1):
            result_parts.append(f"\n{idx}. **{item.title}**")
            result_parts.append(f"   - 来源: {item.site_name}")
            result_parts.append(f"   - URL: {item.url}")
            if item.publish_time:
                result_parts.append(f"   - 发布时间: {item.publish_time}")
            if item.snippet:
                snippet_length = 200 if search_type == "general" else (250 if search_type == "market" else 200)
                result_parts.append(f"   - 摘要: {item.snippet[:snippet_length]}...")
            if item.auth_info_des:
                result_parts.append(f"   - 权威性: {item.auth_info_des}")
            if item.auth_info_level:
                result_parts.append(f"   - 权威级别: {item.auth_info_level}")

        return "\n".join(result_parts)

    except Exception as e:
        return f"搜索失败: {str(e)}"


@tool
def search_competitor_info(query: str, runtime: ToolRuntime = None) -> str:
    """
    搜索竞品数据库的相关信息，包括产品特性、市场表现、技术架构等
    （保留此工具以向后兼容，内部调用 web_search）

    Args:
        query: 搜索关键词
        runtime: 工具运行时上下文

    Returns:
        返回竞品信息搜索结果
    """
    return web_search(
        query=query,
        search_type="competitor",
        count=5,
        need_summary=True,
        runtime=runtime
    )


@tool
def search_market_trends(query: str, time_range: str = "1m", runtime: ToolRuntime = None) -> str:
    """
    搜索数据库市场的最新趋势和技术发展
    （保留此工具以向后兼容，内部调用 web_search）

    Args:
        query: 搜索关键词
        time_range: 时间范围
        runtime: 工具运行时上下文

    Returns:
        返回市场趋势搜索结果
    """
    return web_search(
        query=query,
        search_type="market",
        time_range=time_range,
        count=8,
        need_summary=True,
        runtime=runtime
    )


@tool
def search_database_best_practices(query: str, runtime: ToolRuntime = None) -> str:
    """
    搜索数据库开发的最佳实践和技术方案
    （保留此工具以向后兼容，内部调用 web_search）

    Args:
        query: 搜索关键词
        runtime: 工具运行时上下文

    Returns:
        返回最佳实践搜索结果
    """
    return web_search(
        query=query,
        search_type="best_practice",
        count=5,
        need_summary=True,
        runtime=runtime
    )
