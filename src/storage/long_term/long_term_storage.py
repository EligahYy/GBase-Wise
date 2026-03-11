"""
长期记忆存储
将压缩后的对话存储到数据库和知识库
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

from coze_coding_dev_sdk import KnowledgeClient, Config, KnowledgeDocument, DataSourceType
from coze_coding_utils.runtime_ctx.context import new_context

from storage.database.db import get_session
from .models import CompressedConversation, ConversationKeyInfo, KeyInfoType

logger = logging.getLogger(__name__)


class LongTermMemoryStorage:
    """长期记忆存储"""
    
    def __init__(self, kb_table_name: str = "long_term_conversations"):
        """
        初始化长期记忆存储
        
        Args:
            kb_table_name: 知识库数据集名称
        """
        self.kb_table_name = kb_table_name
        
        # 初始化知识库客户端
        config = Config()
        ctx = new_context(method="LongTermMemoryStorage")
        self.kb_client = KnowledgeClient(config=config, ctx=ctx)
    
    async def store(
        self,
        compressed: CompressedConversation,
        store_to_kb: bool = True
    ) -> int:
        """
        存储压缩的对话
        
        Args:
            compressed: 压缩后的对话对象
            store_to_kb: 是否存储到知识库
        
        Returns:
            数据库中的记录 ID
        """
        try:
            logger.info(f"开始存储长期记忆，thread_id={compressed.metadata.get('thread_id')}")
            
            # 1. 存储到数据库
            db_id = await self._store_to_db(compressed)
            
            # 2. 存储到知识库（可选）
            if store_to_kb:
                kb_doc_id = await self._store_to_knowledge_base(compressed)
                logger.info(f"已存储到知识库，doc_id={kb_doc_id}")
            
            logger.info(f"长期记忆存储完成，db_id={db_id}")
            return db_id
            
        except Exception as e:
            logger.error(f"存储长期记忆失败，error: {e}", exc_info=True)
            raise
    
    async def _store_to_db(
        self,
        compressed: CompressedConversation
    ) -> int:
        """
        存储到数据库
        
        Returns:
            数据库中的记录 ID
        """
        session = get_session()
        
        try:
            # 插入长期记忆记录
            query = text("""
                INSERT INTO memory.long_term_conversations
                (thread_id, summary, key_info, metadata, created_at, compressed_at, retention_days)
                VALUES (:thread_id, :summary, :key_info, :metadata, :created_at, :compressed_at, :retention_days)
                RETURNING id
            """)
            
            result = session.execute(query, {
                "thread_id": compressed.metadata.get("thread_id"),
                "summary": compressed.summary,
                "key_info": compressed.key_info,
                "metadata": compressed.metadata,
                "created_at": datetime.fromisoformat(compressed.metadata.get("created_at", datetime.now().isoformat())),
                "compressed_at": datetime.fromisoformat(compressed.metadata.get("compressed_at", datetime.now().isoformat())),
                "retention_days": 90
            })
            
            session.commit()
            conversation_id = result.scalar()
            
            # 插入关键信息
            await self._store_key_info(session, conversation_id, compressed.key_info)
            
            return conversation_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"存储到数据库失败，error: {e}", exc_info=True)
            raise
        finally:
            session.close()
    
    async def _store_key_info(
        self,
        session: Session,
        conversation_id: int,
        key_info: Dict[str, Any]
    ):
        """
        存储关键信息
        
        Args:
            session: 数据库会话
            conversation_id: 对话 ID
            key_info: 关键信息字典
        """
        # 映射字段到 KeyInfoType
        type_mapping = {
            "topics": KeyInfoType.TOPIC,
            "intents": KeyInfoType.INTENT,
            "decisions": KeyInfoType.DECISION,
            "conclusions": KeyInfoType.CONCLUSION,
            "technical_details": KeyInfoType.TECHNICAL_DETAIL
        }
        
        # 插入关键信息
        for field_name, key_type in type_mapping.items():
            values = key_info.get(field_name, [])
            if not values:
                continue
            
            for i, value in enumerate(values):
                query = text("""
                    INSERT INTO memory.conversation_key_info
                    (conversation_id, key_type, key_value, importance_score, created_at)
                    VALUES (:conversation_id, :key_type, :key_value, :importance_score, :created_at)
                """)
                
                session.execute(query, {
                    "conversation_id": conversation_id,
                    "key_type": key_type.value,
                    "key_value": str(value),
                    "importance_score": 1.0,  # 默认重要性
                    "created_at": datetime.now()
                })
        
        session.commit()
    
    async def _store_to_knowledge_base(
        self,
        compressed: CompressedConversation
    ) -> str:
        """
        存储到知识库
        
        Returns:
            文档 ID
        """
        # 构建知识库文档内容
        content = self._build_knowledge_content(compressed)
        
        # 创建知识库文档
        doc = KnowledgeDocument(
            source=DataSourceType.TEXT,
            raw_data=content,
            metadata={
                "thread_id": compressed.metadata.get("thread_id"),
                "compressed_at": compressed.metadata.get("compressed_at"),
                "original_message_count": compressed.metadata.get("original_message_count"),
                "type": "long_term_conversation"
            }
        )
        
        # 添加到知识库
        response = self.kb_client.add_documents(
            documents=[doc],
            table_name=self.kb_table_name
        )
        
        if response.code != 0:
            logger.error(f"添加到知识库失败，error: {response.msg}")
            raise Exception(f"添加到知识库失败: {response.msg}")
        
        return response.doc_ids[0]
    
    def _build_knowledge_content(
        self,
        compressed: CompressedConversation
    ) -> str:
        """
        构建知识库文档内容
        
        Args:
            compressed: 压缩后的对话对象
        
        Returns:
            文档内容
        """
        content = f"# 对话摘要\n\n{compressed.summary}\n\n"
        
        # 添加关键信息
        content += "## 关键信息\n\n"
        
        if compressed.key_info.get("topics"):
            content += f"### 主题\n\n{', '.join(compressed.key_info['topics'])}\n\n"
        
        if compressed.key_info.get("intents"):
            content += f"### 用户意图\n\n{', '.join(compressed.key_info['intents'])}\n\n"
        
        if compressed.key_info.get("decisions"):
            content += f"### 重要决策\n\n{', '.join(compressed.key_info['decisions'])}\n\n"
        
        if compressed.key_info.get("conclusions"):
            content += f"### 关键结论\n\n{', '.join(compressed.key_info['conclusions'])}\n\n"
        
        if compressed.key_info.get("technical_details"):
            content += f"### 技术细节\n\n{', '.join(compressed.key_info['technical_details'])}\n\n"
        
        # 添加元数据
        content += "## 元数据\n\n"
        content += f"- 会话 ID: {compressed.metadata.get('thread_id')}\n"
        content += f"- 创建时间: {compressed.metadata.get('created_at')}\n"
        content += f"- 压缩时间: {compressed.metadata.get('compressed_at')}\n"
        content += f"- 原始消息数: {compressed.metadata.get('original_message_count')}\n"
        
        return content
    
    async def get_by_thread_id(
        self,
        thread_id: str,
        limit: int = 5
    ) -> List[CompressedConversation]:
        """
        根据 thread_id 获取长期记忆
        
        Args:
            thread_id: 会话 ID
            limit: 返回数量
        
        Returns:
            压缩对话列表
        """
        session = get_session()
        
        try:
            query = text("""
                SELECT id, thread_id, summary, key_info, metadata, created_at, compressed_at
                FROM memory.long_term_conversations
                WHERE thread_id = :thread_id
                ORDER BY compressed_at DESC
                LIMIT :limit
            """)
            
            result = session.execute(query, {
                "thread_id": thread_id,
                "limit": limit
            })
            
            rows = result.fetchall()
            
            conversations = []
            for row in rows:
                conversations.append(CompressedConversation(
                    id=row[0],
                    summary=row[2],
                    key_info=row[3],
                    metadata=row[4]
                ))
            
            return conversations
            
        except Exception as e:
            logger.error(f"获取长期记忆失败，thread_id={thread_id}, error: {e}", exc_info=True)
            return []
        finally:
            session.close()
    
    async def cleanup_old_records(self, days: int = 90):
        """
        清理过期的长期记忆
        
        Args:
            days: 保留天数
        """
        session = get_session()
        
        try:
            query = text("""
                DELETE FROM memory.long_term_conversations
                WHERE compressed_at < NOW() - INTERVAL ':days days'
            """)
            
            result = session.execute(query, {"days": days})
            session.commit()
            
            logger.info(f"清理了 {result.rowcount} 条过期的长期记忆记录")
            
        except Exception as e:
            session.rollback()
            logger.error(f"清理过期记录失败，error: {e}", exc_info=True)
        finally:
            session.close()
