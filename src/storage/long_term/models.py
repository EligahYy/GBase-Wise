"""
长期记忆数据模型
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class KeyInfoType(str, Enum):
    """关键信息类型"""
    TOPIC = "topic"
    INTENT = "intent"
    DECISION = "decision"
    CONCLUSION = "conclusion"
    TECHNICAL_DETAIL = "technical_detail"


@dataclass
class CompressedConversation:
    """压缩后的对话"""
    summary: str
    key_info: Dict[str, Any]
    metadata: Dict[str, Any]
    id: Optional[int] = None


@dataclass
class ConversationKeyInfo:
    """对话关键信息"""
    key_type: KeyInfoType
    key_value: str
    importance_score: float = 1.0
    conversation_id: Optional[int] = None
    id: Optional[int] = None


@dataclass
class ContextItem:
    """上下文项"""
    content: str
    score: float
    source: str  # "short_term" or "long_term"
    metadata: Dict[str, Any] = field(default_factory=dict)
    final_score: float = 0.0
