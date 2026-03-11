"""
对话压缩引擎
使用 LLM 将对话压缩为摘要和关键信息
"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .models import CompressedConversation, ConversationKeyInfo, KeyInfoType

logger = logging.getLogger(__name__)


class ConversationCompressor:
    """对话压缩引擎"""
    
    def __init__(self, llm: ChatOpenAI):
        """
        初始化对话压缩引擎
        
        Args:
            llm: ChatOpenAI 实例
        """
        self.llm = llm
    
    async def compress_conversation(
        self,
        thread_id: str,
        messages: List[AnyMessage]
    ) -> CompressedConversation:
        """
        压缩对话为长期记忆
        
        Args:
            thread_id: 会话 ID
            messages: 消息列表
        
        Returns:
            压缩后的对话对象
        """
        try:
            logger.info(f"开始压缩对话，thread_id={thread_id}, 消息数={len(messages)}")
            
            # 1. 提取关键信息
            key_info = await self._extract_key_info(messages)
            
            # 2. 生成摘要
            summary = await self._generate_summary(messages, key_info)
            
            # 3. 保留元数据
            metadata = {
                "thread_id": thread_id,
                "created_at": datetime.now().isoformat(),
                "compressed_at": datetime.now().isoformat(),
                "original_message_count": len(messages),
                "key_topics": key_info.get("topics", []),
                "user_intents": key_info.get("intents", [])
            }
            
            # 4. 创建压缩对象
            compressed = CompressedConversation(
                summary=summary,
                key_info=key_info,
                metadata=metadata
            )
            
            logger.info(f"对话压缩完成，thread_id={thread_id}")
            return compressed
            
        except Exception as e:
            logger.error(f"对话压缩失败，thread_id={thread_id}, error={e}", exc_info=True)
            raise
    
    async def _extract_key_info(
        self,
        messages: List[AnyMessage]
    ) -> Dict[str, Any]:
        """
        提取关键信息
        
        Returns:
            {
                "topics": List[str],  # 主题列表
                "intents": List[str],  # 用户意图列表
                "decisions": List[str],  # 重要决策
                "conclusions": List[str],  # 关键结论
                "technical_details": List[str]  # 技术细节
            }
        """
        # 格式化消息
        formatted_messages = self._format_messages(messages)
        
        prompt = f"""
你是一个专业的对话分析助手。请分析以下对话，提取关键信息。

对话内容：
{formatted_messages}

请提取以下信息，并以 JSON 格式返回：
1. topics: 对话主题（3-5 个关键词）
2. intents: 用户意图（1-3 个）
3. decisions: 重要决策（如有）
4. conclusions: 关键结论（如有）
5. technical_details: 技术细节（如有）

要求：
- 如果某类信息不存在，返回空列表
- 确保返回的是有效的 JSON 格式
- 使用中文

返回格式示例：
{{
    "topics": ["GBase8a", "性能优化", "索引"],
    "intents": ["查询性能问题", "优化建议"],
    "decisions": ["使用列式存储"],
    "conclusions": ["索引可以提升查询性能"],
    "technical_details": ["使用 CREATE INDEX 语句"]
}}
"""
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="你是专业的对话分析助手，擅长提取关键信息。"),
                HumanMessage(content=prompt)
            ])
            
            # 解析响应
            content = response.content.strip()
            
            # 移除可能存在的 markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # 解析 JSON
            key_info = json.loads(content)
            
            # 验证字段
            required_fields = ["topics", "intents", "decisions", "conclusions", "technical_details"]
            for field in required_fields:
                if field not in key_info:
                    key_info[field] = []
            
            return key_info
            
        except json.JSONDecodeError as e:
            logger.error(f"解析关键信息失败，响应内容: {response.content}, error: {e}")
            # 返回默认值
            return {
                "topics": [],
                "intents": [],
                "decisions": [],
                "conclusions": [],
                "technical_details": []
            }
        except Exception as e:
            logger.error(f"提取关键信息失败，error: {e}", exc_info=True)
            return {
                "topics": [],
                "intents": [],
                "decisions": [],
                "conclusions": [],
                "technical_details": []
            }
    
    async def _generate_summary(
        self,
        messages: List[AnyMessage],
        key_info: Dict[str, Any]
    ) -> str:
        """
        生成对话摘要
        
        Args:
            messages: 消息列表
            key_info: 关键信息
        
        Returns:
            摘要文本
        """
        # 格式化消息（限制长度以避免 token 溢出）
        formatted_messages = self._format_messages(messages, max_length=3000)
        
        # 构建关键信息描述
        key_info_desc = ""
        if key_info.get("topics"):
            key_info_desc += f"主题：{', '.join(key_info['topics'])}\n"
        if key_info.get("intents"):
            key_info_desc += f"用户意图：{', '.join(key_info['intents'])}\n"
        if key_info.get("decisions"):
            key_info_desc += f"重要决策：{', '.join(key_info['decisions'])}\n"
        if key_info.get("conclusions"):
            key_info_desc += f"关键结论：{', '.join(key_info['conclusions'])}\n"
        
        prompt = f"""
你是一个专业的对话摘要助手。请为以下对话生成简洁的摘要。

关键信息：
{key_info_desc if key_info_desc else '无'}

对话内容：
{formatted_messages}

要求：
1. 摘要长度控制在 200-300 字
2. 包含对话主题、主要讨论内容
3. 如果有重要结论或决策，请包含
4. 如果有未解决的问题，请提及
5. 使用中文
"""
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="你是专业的对话摘要助手，擅长生成简洁准确的摘要。"),
                HumanMessage(content=prompt)
            ])
            
            summary = response.content.strip()
            
            # 移除可能存在的 markdown 代码块标记
            if summary.startswith("```"):
                summary = "\n".join(summary.split("\n")[1:-1])
            
            return summary
            
        except Exception as e:
            logger.error(f"生成摘要失败，error: {e}", exc_info=True)
            # 返回简单的摘要
            return f"包含 {len(messages)} 条消息的对话，涉及 {', '.join(key_info.get('topics', ['未知主题']))}"
    
    def _format_messages(
        self,
        messages: List[AnyMessage],
        max_length: Optional[int] = None
    ) -> str:
        """
        格式化消息为文本
        
        Args:
            messages: 消息列表
            max_length: 最大长度（字符数）
        
        Returns:
            格式化后的文本
        """
        formatted = []
        
        for msg in messages:
            role = "用户"
            if isinstance(msg, AIMessage):
                role = "助手"
            elif isinstance(msg, SystemMessage):
                role = "系统"
            
            content = str(msg.content)
            formatted.append(f"{role}：{content}")
        
        result = "\n\n".join(formatted)
        
        # 限制长度
        if max_length and len(result) > max_length:
            result = result[:max_length] + "\n...（内容已截断）"
        
        return result
