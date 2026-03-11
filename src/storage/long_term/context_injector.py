"""
上下文注入器
将检索到的上下文注入到消息中
"""
import logging
from typing import List, Optional
from langchain_core.messages import AnyMessage, SystemMessage

from storage.long_term.models import ContextItem

logger = logging.getLogger(__name__)


class ContextInjector:
    """上下文注入器"""
    
    def __init__(
        self,
        max_contexts: int = 5,
        min_score: float = 0.5,
        enable_injection: bool = True
    ):
        """
        初始化上下文注入器
        
        Args:
            max_contexts: 最大上下文数量
            min_score: 最小相似度阈值
            enable_injection: 是否启用注入
        """
        self.max_contexts = max_contexts
        self.min_score = min_score
        self.enable_injection = enable_injection
    
    async def inject(
        self,
        messages: List[AnyMessage],
        contexts: List[ContextItem],
        thread_id: Optional[str] = None
    ) -> List[AnyMessage]:
        """
        将检索到的上下文注入到消息中
        
        Args:
            messages: 原始消息列表
            contexts: 检索到的上下文
            thread_id: 会话 ID（可选，用于日志）
        
        Returns:
            注入上下文后的消息列表
        """
        if not self.enable_injection:
            return messages
        
        if not contexts:
            logger.debug(f"没有可注入的上下文，thread_id={thread_id}")
            return messages
        
        # 过滤低分上下文
        valid_contexts = [c for c in contexts if c.final_score >= self.min_score]
        
        if not valid_contexts:
            logger.debug(f"没有达到阈值的上下文，thread_id={thread_id}")
            return messages
        
        # 限制上下文数量
        valid_contexts = valid_contexts[:self.max_contexts]
        
        try:
            # 构建上下文消息
            context_message = self._build_context_message(valid_contexts)
            
            # 在最后一条用户消息之前插入上下文消息
            messages_copy = messages.copy()
            for i in range(len(messages_copy) - 1, -1, -1):
                if messages_copy[i].type == "human":
                    messages_copy.insert(i, context_message)
                    break
            
            logger.info(
                f"上下文注入完成，thread_id={thread_id}, "
                f"注入了 {len(valid_contexts)} 条上下文"
            )
            
            return messages_copy
            
        except Exception as e:
            logger.error(f"上下文注入失败，thread_id={thread_id}, error: {e}", exc_info=True)
            return messages
    
    def _build_context_message(
        self,
        contexts: List[ContextItem]
    ) -> SystemMessage:
        """
        构建上下文消息
        
        Args:
            contexts: 上下文列表
        
        Returns:
            系统消息
        """
        context_text = "## 相关历史上下文\n\n"
        
        for i, context in enumerate(contexts, 1):
            source = "长期记忆" if context.source == "long_term" else "短期记忆"
            context_text += f"### {source} (相关度: {context.score:.2%})\n\n"
            context_text += f"{context.content}\n\n"
        
        context_text += "请结合上述历史上下文回答当前问题。"
        
        return SystemMessage(content=context_text)
    
    async def inject_to_last_user_message(
        self,
        messages: List[AnyMessage],
        contexts: List[ContextItem],
        thread_id: Optional[str] = None
    ) -> List[AnyMessage]:
        """
        将上下文注入到最后一条用户消息中（而不是作为独立消息）
        
        Args:
            messages: 原始消息列表
            contexts: 检索到的上下文
            thread_id: 会话 ID（可选，用于日志）
        
        Returns:
            注入上下文后的消息列表
        """
        if not self.enable_injection or not contexts:
            return messages
        
        # 过滤低分上下文
        valid_contexts = [c for c in contexts if c.final_score >= self.min_score]
        
        if not valid_contexts:
            return messages
        
        # 限制上下文数量
        valid_contexts = valid_contexts[:self.max_contexts]
        
        try:
            # 构建上下文文本
            context_text = "\n\n相关历史上下文：\n"
            for i, context in enumerate(valid_contexts, 1):
                context_text += f"{i}. {context.content[:100]}...\n"
            
            # 修改最后一条用户消息
            messages_copy = messages.copy()
            for i in range(len(messages_copy) - 1, -1, -1):
                if messages_copy[i].type == "human":
                    original_content = messages_copy[i].content
                    messages_copy[i] = HumanMessage(
                        content=f"{original_content}{context_text}"
                    )
                    break
            
            logger.info(
                f"上下文注入到用户消息完成，thread_id={thread_id}, "
                f"注入了 {len(valid_contexts)} 条上下文"
            )
            
            return messages_copy
            
        except Exception as e:
            logger.error(f"上下文注入失败，thread_id={thread_id}, error: {e}", exc_info=True)
            return messages
