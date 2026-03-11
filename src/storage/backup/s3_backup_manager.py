"""
S3 备份管理器
将数据备份到 S3 对象存储
"""
import json
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

from coze_coding_dev_sdk.s3 import S3SyncStorage

from storage.database.db import get_session

logger = logging.getLogger(__name__)


class S3BackupManager:
    """S3 备份管理器"""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        初始化 S3 备份管理器
        
        Args:
            bucket_name: S3 桶名称，默认从环境变量读取
        """
        # 初始化 S3 客户端
        self.storage = S3SyncStorage(
            endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
            access_key="",
            secret_key="",
            bucket_name=bucket_name or os.getenv("COZE_BUCKET_NAME"),
            region="cn-beijing",
        )
        self.backup_prefix = "backups/"
    
    async def backup_sql_examples(
        self,
        limit: int = 1000
    ) -> Optional[str]:
        """
        备份 SQL 示例到 S3
        
        Args:
            limit: 备份的最大记录数
        
        Returns:
            S3 对象 key
        """
        try:
            logger.info("开始备份 SQL 示例到 S3")
            
            # 1. 从 PostgreSQL 导出数据
            session = get_session()
            
            try:
                query = text("""
                    SELECT 
                        id, thread_id, business_requirement, generated_sql, 
                        feedback_type, feedback_comment, created_at
                    FROM memory.sql_examples
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)
                
                result = session.execute(query, {"limit": limit})
                rows = result.fetchall()
                
                if not rows:
                    logger.warning("没有 SQL 示例需要备份")
                    return None
                
                # 2. 转换为 JSONL 格式
                examples = []
                for row in rows:
                    examples.append({
                        "id": row[0],
                        "thread_id": row[1],
                        "business_requirement": row[2],
                        "generated_sql": row[3],
                        "feedback_type": row[4],
                        "feedback_comment": row[5],
                        "created_at": row[6].isoformat() if row[6] else None
                    })
                
                # 3. 上传到 S3
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{self.backup_prefix}sql_examples/backup_{timestamp}.jsonl"
                content = "\n".join([json.dumps(e, ensure_ascii=False) for e in examples])
                
                key = self.storage.upload_file(
                    file_content=content.encode('utf-8'),
                    file_name=file_name,
                    content_type="application/x-jsonlines"
                )
                
                logger.info(f"SQL 示例备份完成，记录数={len(examples)}, key={key}")
                return key
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"备份 SQL 示例失败，error: {e}", exc_info=True)
            return None
    
    async def backup_language_styles(self) -> Optional[str]:
        """
        备份语言风格配置到 S3
        
        Returns:
            S3 对象 key
        """
        try:
            logger.info("开始备份语言风格配置到 S3")
            
            # 1. 从 PostgreSQL 导出数据
            session = get_session()
            
            try:
                query = text("""
                    SELECT 
                        id, style_id, style_name, description, 称呼, 
                        tone, greeting, closing, is_default, created_at, updated_at
                    FROM memory.language_styles
                    ORDER BY created_at DESC
                """)
                
                result = session.execute(query)
                rows = result.fetchall()
                
                if not rows:
                    logger.warning("没有语言风格配置需要备份")
                    return None
                
                # 2. 转换为字典格式
                styles = {}
                for row in rows:
                    styles[row[1]] = {
                        "id": row[0],
                        "style_id": row[1],
                        "style_name": row[2],
                        "description": row[3],
                        "称呼": row[4],
                        "tone": row[5],
                        "greeting": row[6],
                        "closing": row[7],
                        "is_default": row[8],
                        "created_at": row[9].isoformat() if row[9] else None,
                        "updated_at": row[10].isoformat() if row[10] else None
                    }
                
                # 3. 上传到 S3
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{self.backup_prefix}language_styles/backup_{timestamp}.json"
                content = json.dumps(styles, ensure_ascii=False, indent=2)
                
                key = self.storage.upload_file(
                    file_content=content.encode('utf-8'),
                    file_name=file_name,
                    content_type="application/json"
                )
                
                logger.info(f"语言风格配置备份完成，记录数={len(styles)}, key={key}")
                return key
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"备份语言风格配置失败，error: {e}", exc_info=True)
            return None
    
    async def backup_long_term_conversations(
        self,
        limit: int = 1000
    ) -> Optional[str]:
        """
        备份长期记忆到 S3
        
        Args:
            limit: 备份的最大记录数
        
        Returns:
            S3 对象 key
        """
        try:
            logger.info("开始备份长期记忆到 S3")
            
            # 1. 从 PostgreSQL 导出数据
            session = get_session()
            
            try:
                query = text("""
                    SELECT 
                        id, thread_id, summary, key_info, metadata, 
                        created_at, compressed_at
                    FROM memory.long_term_conversations
                    ORDER BY compressed_at DESC
                    LIMIT :limit
                """)
                
                result = session.execute(query, {"limit": limit})
                rows = result.fetchall()
                
                if not rows:
                    logger.warning("没有长期记忆需要备份")
                    return None
                
                # 2. 转换为列表格式
                conversations = []
                for row in rows:
                    conversations.append({
                        "id": row[0],
                        "thread_id": row[1],
                        "summary": row[2],
                        "key_info": row[3],
                        "metadata": row[4],
                        "created_at": row[5].isoformat() if row[5] else None,
                        "compressed_at": row[6].isoformat() if row[6] else None
                    })
                
                # 3. 上传到 S3
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{self.backup_prefix}long_term_conversations/backup_{timestamp}.json"
                content = json.dumps(conversations, ensure_ascii=False, indent=2)
                
                key = self.storage.upload_file(
                    file_content=content.encode('utf-8'),
                    file_name=file_name,
                    content_type="application/json"
                )
                
                logger.info(f"长期记忆备份完成，记录数={len(conversations)}, key={key}")
                return key
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"备份长期记忆失败，error: {e}", exc_info=True)
            return None
    
    async def backup_all(self) -> Dict[str, Any]:
        """
        备份所有数据到 S3
        
        Returns:
            备份结果
        """
        logger.info("开始全量备份到 S3")
        
        results = {
            "sql_examples_key": None,
            "language_styles_key": None,
            "long_term_conversations_key": None,
            "success": False,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 备份 SQL 示例
            results["sql_examples_key"] = await self.backup_sql_examples()
            
            # 备份语言风格配置
            results["language_styles_key"] = await self.backup_language_styles()
            
            # 备份长期记忆
            results["long_term_conversations_key"] = await self.backup_long_term_conversations()
            
            results["success"] = True
            logger.info("全量备份完成")
            
        except Exception as e:
            logger.error(f"全量备份失败，error: {e}", exc_info=True)
            results["success"] = False
        
        return results
    
    def list_backups(
        self,
        backup_type: str = "all",
        limit: int = 10
    ) -> List[str]:
        """
        列出备份文件
        
        Args:
            backup_type: 备份类型（sql_examples, language_styles, long_term_conversations, all）
            limit: 返回数量
        
        Returns:
            备份文件 key 列表
        """
        try:
            if backup_type == "all":
                prefix = self.backup_prefix
            else:
                prefix = f"{self.backup_prefix}{backup_type}/"
            
            result = self.storage.list_files(
                prefix=prefix,
                max_keys=limit
            )
            
            return result.get("keys", [])
            
        except Exception as e:
            logger.error(f"列出备份文件失败，error: {e}", exc_info=True)
            return []
    
    def download_backup(
        self,
        key: str
    ) -> Optional[bytes]:
        """
        下载备份文件
        
        Args:
            key: S3 对象 key
        
        Returns:
            文件内容
        """
        try:
            logger.info(f"开始下载备份文件，key={key}")
            
            content = self.storage.read_file(file_key=key)
            
            logger.info(f"备份文件下载完成，大小={len(content)} bytes")
            return content
            
        except Exception as e:
            logger.error(f"下载备份文件失败，key={key}, error: {e}", exc_info=True)
            return None
    
    def generate_backup_url(
        self,
        key: str,
        expire_time: int = 3600
    ) -> Optional[str]:
        """
        生成备份文件的访问 URL
        
        Args:
            key: S3 对象 key
            expire_time: 有效期（秒）
        
        Returns:
            签名 URL
        """
        try:
            url = self.storage.generate_presigned_url(
                key=key,
                expire_time=expire_time
            )
            return url
        except Exception as e:
            logger.error(f"生成备份 URL 失败，key={key}, error: {e}", exc_info=True)
            return None


if __name__ == "__main__":
    import asyncio
    
    async def main():
        manager = S3BackupManager()
        results = await manager.backup_all()
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    asyncio.run(main())
