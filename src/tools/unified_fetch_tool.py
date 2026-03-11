"""
统一网页内容获取工具
整合网页内容、文章摘要、文档内容获取等功能
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_dev_sdk.fetch import FetchClient
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Literal


@tool
def fetch_url(
    url: str,
    detail_level: Literal["full", "summary", "brief"] = "summary",
    max_length: int = 3000,
    runtime: ToolRuntime = None
) -> str:
    """
    统一的网页内容获取工具，支持多种详细程度

    Args:
        url: 网页链接地址
        detail_level: 详细程度
            - "full": 获取完整内容（文本、图片、链接等全部信息）
            - "summary": 获取摘要内容（标题、摘要、关键信息）
            - "brief": 获取简要内容（仅标题和核心摘要）
        max_length: 文本内容最大长度，超过将截断，默认 3000
        runtime: 工具运行时上下文

    Returns:
        返回网页内容，根据 detail_level 返回不同详细程度的信息
    """
    ctx = runtime.context if runtime else new_context(method="fetch.url")
    client = FetchClient(ctx=ctx)

    try:
        response = client.fetch(url=url)

        if response.status_code != 0:
            return f"❌ 获取网页内容失败: {response.status_message}"

        result_parts = []

        # 根据详细程度构建结果
        if detail_level == "brief":
            # 简要内容：仅标题和核心摘要
            result_parts.append(f"## 网页摘要\n")
            result_parts.append(f"**标题**: {response.title or '无标题'}")
            result_parts.append(f"**来源**: {response.url}")

            if response.publish_time:
                result_parts.append(f"**发布时间**: {response.publish_time}")

            if response.filetype:
                result_parts.append(f"**文件类型**: {response.filetype}")

            # 提取主要文本
            text_content = [item.text for item in response.content if item.type == "text"]
            if text_content:
                full_text = "\n".join(text_content)
                summary_text = full_text[:800] if len(full_text) > 800 else full_text
                result_parts.append(f"\n### 核心内容\n{summary_text}...")

        elif detail_level == "summary":
            # 摘要内容：标题、摘要、关键信息
            result_parts.append(f"## 文章摘要\n")
            result_parts.append(f"**标题**: {response.title or '无标题'}")
            result_parts.append(f"**来源**: {response.url}")

            if response.publish_time:
                result_parts.append(f"**发布时间**: {response.publish_time}")

            if response.filetype:
                result_parts.append(f"**文件类型**: {response.filetype}")

            # 提取主要文本
            text_content = [item.text for item in response.content if item.type == "text"]
            if text_content:
                full_text = "\n".join(text_content)

                if len(full_text) > max_length:
                    summary_text = full_text[:max_length].rsplit('\n', 1)[0]
                    result_parts.append(f"\n### 摘要内容\n{summary_text}\n\n...（点击链接查看完整内容）")
                else:
                    result_parts.append(f"\n### 文章内容\n{full_text}")

            # 提取图片信息（简要）
            images = [item for item in response.content if item.type == "image"]
            if images:
                result_parts.append(f"\n### 包含 {len(images)} 张图片")

            # 检查显示信息
            if response.display_info and response.display_info.no_display:
                result_parts.append(f"\n⚠️ 注意: 此页面可能无法正常显示 - {response.display_info.no_display_reason}")

        else:  # full
            # 完整内容：文本、图片、链接等全部信息
            result_parts.append(f"## 网页内容获取成功\n")
            result_parts.append(f"**标题**: {response.title or '无标题'}")
            result_parts.append(f"**来源链接**: {response.url}")

            if response.publish_time:
                result_parts.append(f"**发布时间**: {response.publish_time}")

            if response.filetype:
                result_parts.append(f"**文件类型**: {response.filetype}")

            # 提取文本内容
            text_content = [item.text for item in response.content if item.type == "text"]
            if text_content:
                result_parts.append(f"\n### 文本内容\n")
                full_text = "\n".join(text_content)

                if len(full_text) > max_length:
                    result_parts.append(full_text[:max_length] + "\n...（内容过长，已截断）")
                else:
                    result_parts.append(full_text)

            # 提取图片信息
            images = [item for item in response.content if item.type == "image"]
            if images:
                result_parts.append(f"\n### 图片信息 (共 {len(images)} 张)\n")
                for idx, img in enumerate(images[:10], 1):
                    result_parts.append(f"{idx}. 图片 URL: {img.image.display_url}")
                    result_parts.append(f"   尺寸: {img.image.width}x{img.image.height}")
                    if img.image.thumbnail_display_url:
                        result_parts.append(f"   缩略图: {img.image.thumbnail_display_url}")
                if len(images) > 10:
                    result_parts.append(f"\n...还有 {len(images) - 10} 张图片未显示")

            # 提取链接信息
            links = [item.url for item in response.content if item.type == "link"]
            if links:
                result_parts.append(f"\n### 页面链接 (共 {len(links)} 个)\n")
                for idx, link in enumerate(links[:15], 1):
                    result_parts.append(f"{idx}. {link}")
                if len(links) > 15:
                    result_parts.append(f"\n...还有 {len(links) - 15} 个链接未显示")

            # 检查显示信息
            if response.display_info and response.display_info.no_display:
                result_parts.append(f"\n⚠️ 注意: 此页面可能无法正常显示 - {response.display_info.no_display_reason}")

        return "\n".join(result_parts)

    except Exception as e:
        return f"❌ 获取网页内容异常: {str(e)}"


@tool
def fetch_webpage_content(url: str, runtime: ToolRuntime = None) -> str:
    """
    获取指定网页链接的详细内容，包括文本、图片和链接等信息
    （保留此工具以向后兼容，内部调用 fetch_url）

    Args:
        url: 网页链接地址
        runtime: 工具运行时上下文

    Returns:
        返回网页的完整内容
    """
    return fetch_url(
        url=url,
        detail_level="full",
        max_length=3000,
        runtime=runtime
    )


@tool
def fetch_article_summary(url: str, runtime: ToolRuntime = None) -> str:
    """
    获取文章类网页的摘要内容，提取关键信息
    （保留此工具以向后兼容，内部调用 fetch_url）

    Args:
        url: 文章链接地址
        runtime: 工具运行时上下文

    Returns:
        返回文章的摘要内容
    """
    return fetch_url(
        url=url,
        detail_level="summary",
        max_length=1500,
        runtime=runtime
    )


@tool
def fetch_document_content(url: str, runtime: ToolRuntime = None) -> str:
    """
    获取文档链接的内容，支持 PDF、Word、Excel 等多种文档格式
    （保留此工具以向后兼容，内部调用 fetch_url）

    Args:
        url: 文档链接地址
        runtime: 工具运行时上下文

    Returns:
        返回文档的内容
    """
    return fetch_url(
        url=url,
        detail_level="full",
        max_length=5000,
        runtime=runtime
    )
