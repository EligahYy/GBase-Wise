"""
知识库管理工具
用于导入公司文档、进行语义搜索和专业问题解答
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import KnowledgeClient, Config, KnowledgeDocument, DataSourceType
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Optional


@tool
def import_document_to_knowledge(content: str, doc_type: str = "text", url: Optional[str] = None, runtime: ToolRuntime = None) -> str:
    """
    将文档导入到知识库中，用于构建本地专业知识库

    Args:
        content: 文档内容，当 doc_type 为 "text" 时直接传入文本内容
        doc_type: 文档类型，支持 "text"(纯文本) 或 "url"(网页链接)
        url: 当 doc_type 为 "url" 时，传入网页 URL 地址
        runtime: 工具运行时上下文

    Returns:
        返回导入结果，包括成功状态和文档 ID
    """
    ctx = runtime.context if runtime else new_context(method="knowledge.import")
    config = Config()
    client = KnowledgeClient(config=config, ctx=ctx)

    try:
        if doc_type == "url" and url:
            doc = KnowledgeDocument(
                source=DataSourceType.URL,
                url=url
            )
        else:
            doc = KnowledgeDocument(
                source=DataSourceType.TEXT,
                raw_data=content
            )

        response = client.add_documents(
            documents=[doc],
            table_name="coze_doc_knowledge"
        )

        if response.code == 0:
            return f"✅ 文档导入成功！文档 ID: {response.doc_ids}"
        else:
            return f"❌ 文档导入失败: {response.msg}"

    except Exception as e:
        return f"文档导入异常: {str(e)}"


@tool
def search_knowledge_base(query: str, top_k: int = 5, dataset: str = "gbase8a", runtime: ToolRuntime = None) -> str:
    """
    在知识库中进行语义搜索，回答专业的技术问题

    Args:
        query: 搜索问题或关键词
        top_k: 返回结果数量，默认 5
        dataset: 知识库数据集名称，默认 "gbase8a"（GBase8a 官方文档）
        runtime: 工具运行时上下文

    Returns:
        返回相关的知识库内容和相似度评分
    """
    ctx = runtime.context if runtime else new_context(method="knowledge.search")
    config = Config()
    client = KnowledgeClient(config=config, ctx=ctx)

    try:
        # 构造搜索参数
        search_params = {
            "query": query,
            "top_k": top_k,
            "min_score": 0.5  # 设置最低相似度阈值，过滤低质量结果
        }

        # 如果指定了数据集，添加 table_names 参数
        if dataset:
            search_params["table_names"] = [dataset]

        response = client.search(**search_params)

        if response.code != 0:
            return f"知识库搜索失败: {response.msg}"

        if not response.chunks:
            return f"在知识库（数据集: {dataset}）中未找到与 '{query}' 相关的信息。请尝试使用联网搜索工具查找相关信息。"

        result_parts = []
        result_parts.append(f"## 知识库搜索结果: {query}\n")
        result_parts.append(f"### 找到 {len(response.chunks)} 条相关信息（数据集: {dataset}）\n")

        for idx, chunk in enumerate(response.chunks, 1):
            result_parts.append(f"\n{idx}. **相关度**: {chunk.score:.2%}")
            result_parts.append(f"   **内容**:\n   {chunk.content}")

        return "\n".join(result_parts)

    except Exception as e:
        return f"知识库搜索异常: {str(e)}"


@tool
def query_technical_detail(question: str, runtime: ToolRuntime = None) -> str:
    """
    查询 GBase8a 数据库的技术细节问题，基于知识库回答

    Args:
        question: 技术问题，例如 "GBase8a 如何实现分布式存储？", "GBase8a 支持哪些数据类型？"
        runtime: 工具运行时上下文

    Returns:
        返回基于知识库的专业技术回答
    """
    ctx = runtime.context if runtime else new_context(method="knowledge.query")
    config = Config()
    client = KnowledgeClient(config=config, ctx=ctx)

    try:
        response = client.search(
            query=question,
            top_k=3,
            min_score=0.6  # 技术问题需要更高的相似度要求
        )

        if response.code != 0:
            return f"技术细节查询失败: {response.msg}"

        if not response.chunks:
            return f"⚠️ 知识库中未找到关于 '{question}' 的技术细节。\n\n根据边界限制，无法给出建议。建议：\n1. 检查问题是否准确\n2. 确认该技术是否已在知识库中\n3. 如果确实需要，请提供更多上下文"

        result_parts = []
        result_parts.append(f"## 技术问题: {question}\n")

        # 如果找到了高质量匹配，直接回答
        if response.chunks[0].score >= 0.8:
            result_parts.append("**答案**:\n")
            result_parts.append(response.chunks[0].content)
            result_parts.append(f"\n*(相关度: {response.chunks[0].score:.2%})*")

            # 如果有补充信息，也提供
            if len(response.chunks) > 1:
                result_parts.append("\n\n**补充信息**:\n")
                for chunk in response.chunks[1:]:
                    result_parts.append(f"- {chunk.content}")
        else:
            # 如果匹配度不够高，提供多个候选
            result_parts.append("找到以下相关技术信息，请确认是否符合您的需求：\n")
            for idx, chunk in enumerate(response.chunks, 1):
                result_parts.append(f"{idx}. (相关度: {chunk.score:.2%})")
                result_parts.append(f"   {chunk.content}\n")

        return "\n".join(result_parts)

    except Exception as e:
        return f"技术细节查询异常: {str(e)}"
