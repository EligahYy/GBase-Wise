"""
Agent 管理器
存储对话压缩管理器和上下文感知引擎
"""
import logging

from storage.long_term.compression_manager import ConversationCompressionManager
from storage.long_term.context_retriever import ContextRetriever
from storage.long_term.context_injector import ContextInjector

logger = logging.getLogger(__name__)


class AgentManagers:
    """Agent 管理器单例"""
    
    _compression_manager = None
    _context_retriever = None
    _context_injector = None
    _initialized = False
    
    @classmethod
    def initialize(
        cls,
        llm,
        compression_threshold: int = 100,
        compression_interval_hours: int = 24,
        enable_compression: bool = True,
        kb_table_name: str = "long_term_conversations",
        min_score: float = 0.6,
        max_contexts: int = 5,
        enable_injection: bool = True
    ):
        """
        初始化所有管理器
        
        Args:
            llm: ChatOpenAI 实例
            compression_threshold: 压缩阈值
            compression_interval_hours: 压缩间隔（小时）
            enable_compression: 是否启用压缩
            kb_table_name: 知识库数据集名称
            min_score: 最小相似度阈值
            max_contexts: 最大上下文数量
            enable_injection: 是否启用注入
        """
        if cls._initialized:
            logger.warning("Agent 管理器已经初始化")
            return
        
        # 初始化对话压缩管理器
        cls._compression_manager = ConversationCompressionManager(
            llm=llm,
            compression_threshold=compression_threshold,
            compression_interval_hours=compression_interval_hours,
            enable_compression=enable_compression
        )
        logger.info("对话压缩管理器已初始化")
        
        # 初始化上下文检索引擎
        cls._context_retriever = ContextRetriever(
            kb_table_name=kb_table_name,
            min_score=min_score
        )
        logger.info("上下文检索引擎已初始化")
        
        # 初始化上下文注入器
        cls._context_injector = ContextInjector(
            max_contexts=max_contexts,
            min_score=min_score,
            enable_injection=enable_injection
        )
        logger.info("上下文注入器已初始化")
        
        cls._initialized = True
    
    @classmethod
    def get_compression_manager(cls) -> ConversationCompressionManager:
        """获取对话压缩管理器"""
        if not cls._initialized:
            raise RuntimeError("Agent 管理器未初始化，请先调用 initialize() 方法")
        return cls._compression_manager
    
    @classmethod
    def get_context_retriever(cls) -> ContextRetriever:
        """获取上下文检索引擎"""
        if not cls._initialized:
            raise RuntimeError("Agent 管理器未初始化，请先调用 initialize() 方法")
        return cls._context_retriever
    
    @classmethod
    def get_context_injector(cls) -> ContextInjector:
        """获取上下文注入器"""
        if not cls._initialized:
            raise RuntimeError("Agent 管理器未初始化，请先调用 initialize() 方法")
        return cls._context_injector
    
    @classmethod
    def is_initialized(cls) -> bool:
        """检查是否已初始化"""
        return cls._initialized
