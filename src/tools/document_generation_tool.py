"""
文档生成工具
用于生成需求文档、调研报告等
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk import DocumentGenerationClient
from typing import Literal


@tool
def generate_requirement_doc(markdown_content: str, title: str, format_type: Literal["pdf", "docx"] = "pdf", runtime: ToolRuntime = None) -> str:
    """
    生成需求文档，支持 PDF 和 DOCX 格式

    Args:
        markdown_content: Markdown 格式的文档内容
        title: 文档标题（必须使用英文，用于生成文件名，避免空格和特殊字符）
        format_type: 输出格式，支持 "pdf" 或 "docx"，默认为 "pdf"
        runtime: 工具运行时上下文

    Returns:
        返回文档下载链接（24小时内有效）
    """
    client = DocumentGenerationClient()

    try:
        if format_type == "pdf":
            url = client.create_pdf_from_markdown(markdown_content, title)
        elif format_type == "docx":
            url = client.create_docx_from_markdown(markdown_content, title)
        else:
            return "❌ 不支持的文档格式，请选择 'pdf' 或 'docx'"

        return f"✅ 需求文档生成成功！\n\n文档格式: {format_type.upper()}\n下载链接: {url}\n\n⏰ 链接有效期: 24小时"

    except Exception as e:
        return f"❌ 文档生成失败: {str(e)}"


@tool
def generate_competitor_report(markdown_content: str, title: str, format_type: Literal["pdf", "docx"] = "pdf", runtime: ToolRuntime = None) -> str:
    """
    生成竞品调研报告

    Args:
        markdown_content: Markdown 格式的调研报告内容
        title: 报告标题（必须使用英文，用于生成文件名）
        format_type: 输出格式，支持 "pdf" 或 "docx"，默认为 "pdf"
        runtime: 工具运行时上下文

    Returns:
        返回报告下载链接（24小时内有效）
    """
    client = DocumentGenerationClient()

    try:
        if format_type == "pdf":
            url = client.create_pdf_from_markdown(markdown_content, title)
        elif format_type == "docx":
            url = client.create_docx_from_markdown(markdown_content, title)
        else:
            return "❌ 不支持的文档格式，请选择 'pdf' 或 'docx'"

        return f"✅ 竞品调研报告生成成功！\n\n文档格式: {format_type.upper()}\n下载链接: {url}\n\n⏰ 链接有效期: 24小时"

    except Exception as e:
        return f"❌ 报告生成失败: {str(e)}"


@tool
def generate_market_analysis_doc(markdown_content: str, title: str, format_type: Literal["pdf", "docx"] = "pdf", runtime: ToolRuntime = None) -> str:
    """
    生成市场分析文档

    Args:
        markdown_content: Markdown 格式的市场分析内容
        title: 文档标题（必须使用英文，用于生成文件名）
        format_type: 输出格式，支持 "pdf" 或 "docx"，默认为 "pdf"
        runtime: 工具运行时上下文

    Returns:
        返回市场分析文档下载链接（24小时内有效）
    """
    client = DocumentGenerationClient()

    try:
        if format_type == "pdf":
            url = client.create_pdf_from_markdown(markdown_content, title)
        elif format_type == "docx":
            url = client.create_docx_from_markdown(markdown_content, title)
        else:
            return "❌ 不支持的文档格式，请选择 'pdf' 或 'docx'"

        return f"✅ 市场分析文档生成成功！\n\n文档格式: {format_type.upper()}\n下载链接: {url}\n\n⏰ 链接有效期: 24小时"

    except Exception as e:
        return f"❌ 文档生成失败: {str(e)}"


@tool
def generate_optimization_proposal(markdown_content: str, title: str, format_type: Literal["pdf", "docx"] = "pdf", runtime: ToolRuntime = None) -> str:
    """
    生成产品优化需求文档

    Args:
        markdown_content: Markdown 格式的优化提案内容
        title: 提案标题（必须使用英文，用于生成文件名）
        format_type: 输出格式，支持 "pdf" 或 "docx"，默认为 "pdf"
        runtime: 工具运行时上下文

    Returns:
        返回优化提案文档下载链接（24小时内有效）
    """
    client = DocumentGenerationClient()

    try:
        if format_type == "pdf":
            url = client.create_pdf_from_markdown(markdown_content, title)
        elif format_type == "docx":
            url = client.create_docx_from_markdown(markdown_content, title)
        else:
            return "❌ 不支持的文档格式，请选择 'pdf' 或 'docx'"

        return f"✅ 产品优化提案生成成功！\n\n文档格式: {format_type.upper()}\n下载链接: {url}\n\n⏰ 链接有效期: 24小时"

    except Exception as e:
        return f"❌ 提案生成失败: {str(e)}"
