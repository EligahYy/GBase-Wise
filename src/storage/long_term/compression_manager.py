"""
对话压缩管理器
管理对话压缩的生命周期
"""
import logging
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
from langchain_core.messages import AnyMessage
from langchain_openai import ChatOpenAI

from storage.long_term import ConversationCompressor, LongTermMemoryStorage

logger = logging.getLogger(__name__)


class ConversationCompressionManager:
    """对话压缩管理器"""
    
    def __init__(
        self,
        llm: ChatOpenAI,
        compression_threshold: int = 100,
        compression_interval_hours: int = 24,
        enable_compression: bool = True
    ):
        """
        初始化对话压缩管理器
        
        Args:
            llm: ChatOpenAI 实例
            compression_threshold: 压缩阈值（消息数）
            compression_interval_hours: 压缩间隔（小时）
            enable_compression: 是否启用压缩
        """
        self.llm = llm
        self.compression_threshold = compression_threshold
        self.compression_interval = timedelta(hours=compression_interval_hours)
        self.enable_compression = enable_compression
        
        # 初始化组件
        self.compressor = ConversationCompressor(llm=llm)
        self.storage = LongTermMemoryStorage()
        
        # 记录上次压缩时间
        self.last_compression_times: dict = {}
    
    def should_compress(
        self,
        thread_id: str,
        message_count: int
    ) -> bool:
        """
        判断是否需要压缩
        
        Args:
            thread_id: 会话 ID
            message_count: 消息数量
        
        Returns:
            是否需要压缩
        """
        if not self.enable_compression:
            return False
        
        # 检查消息数量
        if message_count < self.compression_threshold:
            return False
        
        # 检查压缩间隔
        last_time = self.last_compression_times.get(thread_id)
        if last_time:
            time_since_last = datetime.now() - last_time
            if time_since_last < self.compression_interval:
                return False
        
        return True
    
    async def compress(
        self,
        thread_id: str,
        messages: List[AnyMessage],
        keep_recent: int = 20
    ) -> List[AnyMessage]:
        """
        压缩对话
        
        Args:
            thread_id: 会话 ID
            messages: 消息列表
            keep_recent: 保留最近的消息数量
        
        Returns:
            压缩后的消息列表
        """
        try:
            logger.info(f"开始压缩对话，thread_id={thread_id}, 总消息数={len(messages)}")
            
            # 1. 提取要压缩的消息（保留最近 keep_recent 条）
            messages_to_compress = messages[:-keep_recent] if len(messages) > keep_recent else []
            
            if not messages_to_compress:
                logger.warning(f"没有需要压缩的消息，thread_id={thread_id}")
                return messages
            
            # 2. 压缩对话
            compressed = await self.compressor.compress_conversation(
                thread_id=thread_id,
                messages=messages_to_compress
            )
            
            # 3. 存储到长期记忆
            await self.storage.store(compressed, store_to_kb=True)
            
            # 4. 更新上次压缩时间
            self.last_compression_times[thread_id] = datetime.now()
            
            # 5. 返回保留的消息
            retained_messages = messages[-keep_recent:]
            
            logger.info(
                f"对话压缩完成，thread_id={thread_id}, "
                f"压缩了 {len(messages_to_compress)} 条消息，保留了 {len(retained_messages)} 条"
            )
            
            return retained_messages
            
        except Exception as e:
            logger.error(f"对话压缩失败，thread_id={thread_id}, error: {e}", exc_info=True)
            # 压缩失败时返回原消息
            return messages
    
    async def try_compress_async(
        self,
        thread_id: str,
        messages: List[AnyMessage]
    ):
        """
        异步尝试压缩（不阻塞主流程）
        
        Args:
            thread_id: 会话 ID
            messages: 消息列表
        """
        if not self.should_compress(thread_id, len(messages)):
            return
        
        try:
            # 在后台执行压缩
            asyncio.create_task(self._compress_async(thread_id, messages))
        except Exception as e:
            logger.error(f"异步压缩任务创建失败，thread_id={thread_id}, error: {e}", exc_info=True)
    
    async def _compress_async(
        self,
        thread_id: str,
        messages: List[AnyMessage]
    ):
        """
        后台异步压缩
        
        Args:
            thread_id: 会话 ID
            messages: 消息列表
        """
        try:
            await self.compress(thread_id, messages)
        except Exception as e:
            logger.error(f"后台异步压缩失败，thread_id={thread_id}, error: {e}", exc_info=True)
