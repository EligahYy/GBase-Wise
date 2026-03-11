"""
数据迁移工具
将本地文件数据迁移到 PostgreSQL
"""
import json
import logging
import os
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

from storage.database.db import get_session

logger = logging.getLogger(__name__)


class DataMigrator:
    """数据迁移工具"""
    
    def __init__(self, workspace_path: str = "/workspace/projects"):
        """
        初始化数据迁移工具
        
        Args:
            workspace_path: 工作空间路径
        """
        self.workspace_path = workspace_path
        self.assets_path = os.path.join(workspace_path, "assets")
    
    def migrate_sql_examples(
        self,
        positive_file: str = "sql_examples/positive_examples.jsonl",
        negative_file: str = "sql_examples/negative_examples.jsonl"
    ) -> Dict[str, int]:
        """
        迁移 SQL 示例到 PostgreSQL
        
        Args:
            positive_file: 正面示例文件路径
            negative_file: 负面示例文件路径
        
        Returns:
            迁移统计信息
        """
        logger.info("开始迁移 SQL 示例到 PostgreSQL")
        
        stats = {
            "positive_count": 0,
            "negative_count": 0,
            "total_count": 0,
            "failed_count": 0
        }
        
        session = get_session()
        
        try:
            # 迁移正面示例
            positive_path = os.path.join(self.assets_path, positive_file)
            if os.path.exists(positive_path):
                positive_count = self._migrate_sql_file(
                    session,
                    positive_path,
                    "positive"
                )
                stats["positive_count"] = positive_count
                logger.info(f"迁移了 {positive_count} 条正面 SQL 示例")
            else:
                logger.warning(f"正面示例文件不存在: {positive_path}")
            
            # 迁移负面示例
            negative_path = os.path.join(self.assets_path, negative_file)
            if os.path.exists(negative_path):
                negative_count = self._migrate_sql_file(
                    session,
                    negative_path,
                    "negative"
                )
                stats["negative_count"] = negative_count
                logger.info(f"迁移了 {negative_count} 条负面 SQL 示例")
            else:
                logger.warning(f"负面示例文件不存在: {negative_path}")
            
            session.commit()
            
            stats["total_count"] = stats["positive_count"] + stats["negative_count"]
            logger.info(f"SQL 示例迁移完成，总计 {stats['total_count']} 条")
            
            return stats
            
        except Exception as e:
            session.rollback()
            logger.error(f"SQL 示例迁移失败，error: {e}", exc_info=True)
            stats["failed_count"] = 1
            return stats
        finally:
            session.close()
    
    def _migrate_sql_file(
        self,
        session: Session,
        file_path: str,
        feedback_type: str
    ) -> int:
        """
        迁移单个 SQL 文件
        
        Args:
            session: 数据库会话
            file_path: 文件路径
            feedback_type: 反馈类型（positive/negative）
        
        Returns:
            迁移的记录数
        """
        count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # 检查是否已存在
                        check_query = text("""
                            SELECT id FROM memory.sql_examples
                            WHERE business_requirement = :req AND generated_sql = :sql
                            LIMIT 1
                        """)
                        result = session.execute(check_query, {
                            "req": data.get("business_requirement", ""),
                            "sql": data.get("generated_sql", "")
                        })
                        
                        if result.scalar():
                            logger.debug(f"SQL 示例已存在，跳过")
                            continue
                        
                        # 插入数据
                        insert_query = text("""
                            INSERT INTO memory.sql_examples
                            (thread_id, business_requirement, generated_sql, feedback_type, feedback_comment, created_at)
                            VALUES (:thread_id, :business_requirement, :generated_sql, :feedback_type, :feedback_comment, :created_at)
                        """)
                        
                        session.execute(insert_query, {
                            "thread_id": data.get("thread_id", "migration"),
                            "business_requirement": data.get("business_requirement", ""),
                            "generated_sql": data.get("generated_sql", ""),
                            "feedback_type": feedback_type,
                            "feedback_comment": data.get("feedback_comment", ""),
                            "created_at": data.get("created_at", datetime.now())
                        })
                        
                        count += 1
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"解析 JSON 行失败，line={line[:50]}..., error={e}")
                        continue
                    except Exception as e:
                        logger.warning(f"插入 SQL 示例失败，error={e}")
                        continue
        
        except FileNotFoundError:
            logger.warning(f"文件不存在: {file_path}")
        except Exception as e:
            logger.error(f"读取文件失败，file_path={file_path}, error={e}", exc_info=True)
        
        return count
    
    def migrate_language_styles(
        self,
        style_file: str = "language_styles.json"
    ) -> Dict[str, int]:
        """
        迁移语言风格配置到 PostgreSQL
        
        Args:
            style_file: 语言风格配置文件路径
        
        Returns:
            迁移统计信息
        """
        logger.info("开始迁移语言风格配置到 PostgreSQL")
        
        stats = {
            "total_count": 0,
            "failed_count": 0
        }
        
        session = get_session()
        
        try:
            style_path = os.path.join(self.assets_path, style_file)
            
            if not os.path.exists(style_path):
                logger.warning(f"语言风格文件不存在: {style_path}")
                return stats
            
            with open(style_path, 'r', encoding='utf-8') as f:
                styles_config = json.load(f)
            
            # 检查格式
            available_styles = styles_config.get("available_styles", [])
            if not isinstance(available_styles, list):
                logger.error(f"语言风格文件格式错误，available_styles 应为列表")
                return stats
            
            # 迁移每个语言风格
            for style_data in available_styles:
                try:
                    style_id = style_data.get("id")
                    if not style_id:
                        logger.warning("跳过没有 id 的语言风格")
                        continue
                    
                    # 检查是否已存在
                    check_query = text("""
                        SELECT id FROM memory.language_styles
                        WHERE style_id = :style_id
                        LIMIT 1
                    """)
                    result = session.execute(check_query, {"style_id": style_id})
                    
                    if result.scalar():
                        logger.debug(f"语言风格已存在，跳过: {style_id}")
                        continue
                    
                    # 插入数据
                    insert_query = text("""
                        INSERT INTO memory.language_styles
                        (style_id, style_name, description, 称呼, tone, greeting, closing, is_default, created_at, updated_at)
                        VALUES (:style_id, :style_name, :description, :称呼, :tone, :greeting, :closing, :is_default, :created_at, :updated_at)
                    """)
                    
                    session.execute(insert_query, {
                        "style_id": style_id,
                        "style_name": style_data.get("name", style_id),
                        "description": style_data.get("description", ""),
                        "称呼": style_data.get("user_address", ""),
                        "tone": style_data.get("tone", ""),
                        "greeting": style_data.get("greeting", ""),
                        "closing": style_data.get("closing", ""),
                        "is_default": (styles_config.get("default_style") == style_id),
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    })
                    
                    stats["total_count"] += 1
                    
                except Exception as e:
                    logger.warning(f"插入语言风格失败，style_id={style_data.get('id', 'unknown')}, error={e}")
                    continue
            
            session.commit()
            logger.info(f"语言风格迁移完成，总计 {stats['total_count']} 条")
            
            return stats
            
        except json.JSONDecodeError as e:
            session.rollback()
            logger.error(f"解析语言风格文件失败，error={e}")
            stats["failed_count"] = 1
            return stats
        except Exception as e:
            session.rollback()
            logger.error(f"语言风格迁移失败，error={e}", exc_info=True)
            stats["failed_count"] = 1
            return stats
        finally:
            session.close()
    
    def migrate_all(self) -> Dict[str, Any]:
        """
        迁移所有本地数据到 PostgreSQL
        
        Returns:
            迁移统计信息
        """
        logger.info("开始迁移所有本地数据到 PostgreSQL")
        
        results = {
            "sql_examples": {},
            "language_styles": {},
            "success": False
        }
        
        try:
            # 迁移 SQL 示例
            sql_stats = self.migrate_sql_examples()
            results["sql_examples"] = sql_stats
            
            # 迁移语言风格配置
            style_stats = self.migrate_language_styles()
            results["language_styles"] = style_stats
            
            results["success"] = True
            logger.info("所有本地数据迁移完成")
            
        except Exception as e:
            logger.error(f"数据迁移失败，error: {e}", exc_info=True)
            results["success"] = False
        
        return results


if __name__ == "__main__":
    # 运行迁移
    migrator = DataMigrator()
    results = migrator.migrate_all()
    print(json.dumps(results, ensure_ascii=False, indent=2))
