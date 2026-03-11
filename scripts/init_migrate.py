"""
初始化和迁移脚本
执行数据库迁移和数据迁移
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
src_path = os.path.join(workspace_path, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from storage.database.db import get_session
from storage.migration.migrator import DataMigrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_migrations():
    """运行数据库迁移"""
    logger.info("=" * 60)
    logger.info("开始执行数据库迁移")
    logger.info("=" * 60)
    
    migrations_dir = os.path.join(workspace_path, "migrations")
    
    if not os.path.exists(migrations_dir):
        logger.error(f"迁移目录不存在: {migrations_dir}")
        return False
    
    # 按顺序执行迁移文件
    migration_files = [
        "001_long_term_memory.sql",
        "002_data_storage.sql"
    ]
    
    session = get_session()
    
    try:
        for migration_file in migration_files:
            file_path = os.path.join(migrations_dir, migration_file)
            
            if not os.path.exists(file_path):
                logger.warning(f"迁移文件不存在: {file_path}")
                continue
            
            logger.info(f"执行迁移: {migration_file}")
            
            # 读取 SQL 文件
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 执行 SQL
            from sqlalchemy import text
            for statement in sql_content.split(';'):
                statement = statement.strip()
                if not statement:
                    continue
                
                try:
                    session.execute(text(statement))
                except Exception as e:
                    logger.warning(f"执行语句失败（可能已存在）: {e}")
            
            session.commit()
            logger.info(f"迁移完成: {migration_file}")
        
        logger.info("=" * 60)
        logger.info("数据库迁移完成")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"数据库迁移失败: {e}", exc_info=True)
        return False
    finally:
        session.close()


def run_data_migration():
    """运行数据迁移"""
    logger.info("=" * 60)
    logger.info("开始执行数据迁移")
    logger.info("=" * 60)
    
    try:
        migrator = DataMigrator(workspace_path=workspace_path)
        results = migrator.migrate_all()
        
        logger.info("迁移结果:")
        logger.info(f"  SQL 示例: {results['sql_examples']}")
        logger.info(f"  语言风格: {results['language_styles']}")
        logger.info(f"  成功: {results['success']}")
        
        if results["success"]:
            logger.info("=" * 60)
            logger.info("数据迁移完成")
            logger.info("=" * 60)
        else:
            logger.warning("数据迁移部分失败")
        
        return results["success"]
        
    except Exception as e:
        logger.error(f"数据迁移失败: {e}", exc_info=True)
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="初始化和迁移脚本")
    parser.add_argument(
        "--skip-db-migration",
        action="store_true",
        help="跳过数据库迁移"
    )
    parser.add_argument(
        "--skip-data-migration",
        action="store_true",
        help="跳过数据迁移"
    )
    
    args = parser.parse_args()
    
    success = True
    
    # 执行数据库迁移
    if not args.skip_db_migration:
        if not run_migrations():
            success = False
    
    # 执行数据迁移
    if not args.skip_data_migration:
        if not run_data_migration():
            success = False
    
    if success:
        logger.info("✅ 所有迁移完成")
        sys.exit(0)
    else:
        logger.error("❌ 迁移失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
