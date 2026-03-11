"""
上下文检索引擎
从短期和长期记忆中检索相关上下文
"""
import logging
from typing import List, Optional
from datetime import datetime
from langchain_core.messages import AnyMessage, HumanMessage

from coze_coding_dev_sdk import KnowledgeClient, Config
from coze_coding_utils.runtime_ctx.context import new_context

from storage.long_term.models import ContextItem
from storage.long_term.long_term_storage import LongTermMemoryStorage

logger = logging.getLogger(__name__)


class ContextRetriever:
    """上下文检索引擎"""
    
    def __init__(
        self,
        kb_table_name: str = "long_term_conversations",
        min_score: float = 0.6
    ):
        """
        初始化上下文检索引擎
        
        Args:
            kb_table_name: 知识库数据集名称
            min_score: 最小相似度阈值
        """
        self.min_score = min_score
        
        # 初始化组件
        self.long_term_storage = LongTermMemoryStorage(kb_table_name=kb_table_name)
        
        # 初始化知识库客户端
        config = Config()
        ctx = new_context(method="ContextRetriever")
        self.kb_client = KnowledgeClient(config=config, ctx=ctx)
    
    async def retrieve(
        self,
        thread_id: str,
        current_query: str,
        short_term_limit: int = 3,
        long_term_limit: int = 2
    ) -> List[ContextItem]:
        """
        检索相关上下文
        
        Args:
            thread_id: 会话 ID
            current_query: 当前查询
            short_term_limit: 短期记忆返回数量
            long_term_limit: 长期记忆返回数量
        
        Returns:
            相关上下文列表
        """
        try:
            logger.info(
                f"开始检索上下文，thread_id={thread_id}, query={current_query[:50]}..."
            )
            
            # 1. 从短期记忆检索（最近 N 条消息）
            short_term_contexts = await self._retrieve_short_term(
                thread_id,
                current_query,
                limit=short_term_limit
            )
            
            # 2. 从长期记忆检索（知识库）
            long_term_contexts = await self._retrieve_long_term(
                thread_id,
                current_query,
                limit=long_term_limit
            )
            
            # 3. 合并和排序
            all_contexts = short_term_contexts + long_term_contexts
            all_contexts = self._rank_contexts(all_contexts, current_query)
            
            logger.info(
                f"上下文检索完成，thread_id={thread_id}, "
                f"短期记忆={len(short_term_contexts)}, 长期记忆={len(long_term_contexts)}, "
                f"总计={len(all_contexts)}"
            )
            
            return all_contexts
            
        except Exception as e:
            logger.error(f"上下文检索失败，thread_id={thread_id}, error: {e}", exc_info=True)
            return []
    
    async def _retrieve_short_term(
        self,
        thread_id: str,
        query: str,
        limit: int
    ) -> List[ContextItem]:
        """
        从短期记忆检索
        
        Args:
            thread_id: 会话 ID
            query: 查询文本
            limit: 返回数量
        
        Returns:
            相关上下文列表
        """
        # 短期记忆从 checkpointer 获取
        # 这里我们返回空列表，因为短期记忆已经在消息中了
        # 未来可以从 memory.checkpoints 表中检索
        return []
    
    async def _retrieve_long_term(
        self,
        thread_id: str,
        query: str,
        limit: int
    ) -> List[ContextItem]:
        """
        从长期记忆检索
        
        Args:
            thread_id: 会话 ID
            query: 查询文本
            limit: 返回数量
        
        Returns:
            相关上下文列表
        """
        try:
            # 从知识库检索
            search_query = f"""
            会话 ID: {thread_id}
            查询: {query}
            
            请检索相关的历史对话摘要和关键信息。
            """
            
            response = self.kb_client.search(
                query=search_query,
                top_k=limit * 2,  # 检索更多结果，然后过滤
                min_score=self.min_score
            )
            
            if response.code != 0:
                logger.error(f"知识库搜索失败，error: {response.msg}")
                return []
            
            contexts = []
            for chunk in response.chunks:
                # 过滤掉分数过低的结果
                if chunk.score < self.min_score:
                    continue
                
                contexts.append(ContextItem(
                    content=chunk.content,
                    score=chunk.score,
                    source="long_term",
                    metadata={
                        "doc_id": chunk.doc_id,
                        "created_at": chunk.metadata.get("compressed_at") or chunk.metadata.get("created_at")
                    }
                ))
            
            return contexts[:limit]
            
        except Exception as e:
            logger.error(f"长期记忆检索失败，thread_id={thread_id}, error: {e}", exc_info=True)
            return []
    
    def _rank_contexts(
        self,
        contexts: List[ContextItem],
        query: str
    ) -> List[ContextItem]:
        """
        对上下文进行排序
        
        排序规则：
        1. 语义相似度（70% 权重）
        2. 时间权重（越新越重要，20% 权重）
        3. 重要性权重（10% 权重）
        
        Args:
            contexts: 上下文列表
            query: 查询文本
        
        Returns:
            排序后的上下文列表
        """
        now = datetime.now()
        
        for context in contexts:
            # 计算时间权重（7 天内权重 1.0，之后线性递减）
            if context.metadata.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(context.metadata["created_at"])
                    days_ago = (now - created_at).days
                    time_weight = max(0.1, 1.0 - days_ago / 90)
                except:
                    time_weight = 0.5
            else:
                time_weight = 0.5
            
            # 计算重要性权重（从元数据中获取）
            importance = context.metadata.get("importance", 1.0)
            
            # 综合评分
            context.final_score = (
                context.score * 0.7 +
                time_weight * 0.2 +
                importance * 0.1
            )
        
        # 按综合评分降序排序
        contexts.sort(key=lambda x: x.final_score, reverse=True)
        
        return contexts
