"""
混合检索工具
结合知识库检索和联网搜索，提供更全面、准确的信息
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import KnowledgeClient, Config, KnowledgeDocument, DataSourceType, SearchClient
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Dict, List, Tuple
import json


@tool
def hybrid_search(query: str, top_k: int = 10, dataset: str = "gbase8a", runtime: ToolRuntime = None) -> str:
    """
    混合检索：结合知识库检索和联网搜索，提供更全面的信息

    Args:
        query: 搜索问题或关键词
        top_k: 返回结果数量，默认 10
        dataset: 知识库数据集名称，默认 "gbase8a"
        runtime: 工具运行时上下文

    Returns:
        返回融合后的搜索结果，标注信息来源
    """
    ctx = runtime.context if runtime else new_context(method="hybrid_search")

    # 1. 知识库检索
    knowledge_results = _search_knowledge_base(query, dataset, top_k // 2, ctx)

    # 2. 联网搜索
    web_results = _search_web(query, top_k // 2, ctx)

    # 3. 结果融合
    fused_results = _fuse_results(knowledge_results, web_results)

    # 4. 格式化输出
    return _format_results(query, fused_results)


def _search_knowledge_base(query: str, dataset: str, top_k: int, ctx) -> List[Dict]:
    """搜索知识库"""
    config = Config()
    client = KnowledgeClient(config=config, ctx=ctx)

    try:
        search_params = {
            "query": query,
            "top_k": top_k,
            "min_score": 0.5
        }

        if dataset:
            search_params["table_names"] = [dataset]

        response = client.search(**search_params)

        if response.code != 0 or not response.chunks:
            return []

        results = []
        for chunk in response.chunks:
            results.append({
                "content": chunk.content,
                "score": chunk.score,
                "source": "knowledge_base",
                "weight": 0.7  # 知识库权重 70%
            })

        return results

    except Exception as e:
        return []


def _search_web(query: str, top_k: int, ctx) -> List[Dict]:
    """联网搜索"""
    client = SearchClient(ctx=ctx)

    try:
        response = client.search(
            query=query,
            count=top_k,
            need_summary=True
        )

        # 检查是否有结果
        if not response.web_items:
            return []

        results = []
        for item in response.web_items:
            # 使用 snippet 作为内容摘要
            content = item.snippet if item.snippet else ""
            # 截取前 500 个字符
            if len(content) > 500:
                content = content[:500] + "..."

            results.append({
                "content": content,
                "url": item.url if hasattr(item, 'url') else "",
                "title": item.title if hasattr(item, 'title') else "",
                "source": "web_search",
                "weight": 0.3  # 联网搜索权重 30%
            })

        return results

    except Exception as e:
        return []


def _fuse_results(knowledge_results: List[Dict], web_results: List[Dict]) -> List[Dict]:
    """融合知识库和联网搜索结果"""
    fused = []

    # 1. 添加知识库结果
    for result in knowledge_results:
        fused.append({
            **result,
            "final_score": result["score"] * result["weight"]
        })

    # 2. 添加联网搜索结果
    for result in web_results:
        # 计算简单评分（基于内容长度，越详细分数越高）
        content_score = min(1.0, len(result["content"]) / 500)
        fused.append({
            **result,
            "score": content_score,
            "final_score": content_score * result["weight"]
        })

    # 3. 排序
    fused.sort(key=lambda x: x["final_score"], reverse=True)

    # 4. 去重（基于内容相似度）
    deduplicated = []
    seen_contents = set()

    for result in fused:
        # 简单去重：检查内容是否相似
        content = result["content"][:100]  # 取前100个字符
        is_duplicate = False

        for seen in seen_contents:
            # 如果前100个字符有80%相似，认为是重复
            if _calculate_similarity(content, seen) > 0.8:
                is_duplicate = True
                break

        if not is_duplicate:
            deduplicated.append(result)
            seen_contents.add(content)

    return deduplicated


def _calculate_similarity(str1: str, str2: str) -> float:
    """计算两个字符串的相似度（简单实现）"""
    # 使用集合交集计算相似度
    set1 = set(str1)
    set2 = set(str2)

    intersection = set1 & set2
    union = set1 | set2

    if not union:
        return 0.0

    return len(intersection) / len(union)


def _format_results(query: str, results: List[Dict]) -> str:
    """格式化搜索结果"""
    output = f"## 混合检索结果: {query}\n\n"

    if not results:
        output += "❌ 未找到相关信息。请尝试调整搜索关键词。"
        return output

    output += f"### 找到 {len(results)} 条相关信息\n\n"

    knowledge_count = sum(1 for r in results if r["source"] == "knowledge_base")
    web_count = sum(1 for r in results if r["source"] == "web_search")

    output += f"- 知识库结果: {knowledge_count} 条\n"
    output += f"- 联网搜索结果: {web_count} 条\n\n"
    output += "---\n\n"

    for idx, result in enumerate(results, 1):
        source_label = "📚 知识库" if result["source"] == "knowledge_base" else "🌐 联网搜索"
        output += f"{idx}. **{source_label}** (相关度: {result['score']:.2%})\n\n"
        output += f"   {result['content']}\n"

        if result["source"] == "web_search" and result.get("url"):
            output += f"   \n   🔗 来源: {result['url']}\n"

        output += "\n"

    return output
