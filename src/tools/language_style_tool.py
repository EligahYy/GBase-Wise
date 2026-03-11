"""
语言风格管理工具
用于管理 Agent 的语言风格和称呼方式
"""
import os
import json
from langchain.tools import tool, ToolRuntime

# 语言风格配置文件路径
STYLE_CONFIG_PATH = os.path.join(
    os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"),
    "assets/language_styles.json"
)

# 当前使用的风格（存储在文件中）
CURRENT_STYLE_FILE = os.path.join(
    os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"),
    "assets/current_style.txt"
)


def _get_style_config():
    """读取语言风格配置"""
    try:
        with open(STYLE_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def _get_current_style():
    """获取当前使用的语言风格"""
    try:
        if os.path.exists(CURRENT_STYLE_FILE):
            with open(CURRENT_STYLE_FILE, 'r', encoding='utf-8') as f:
                style_id = f.read().strip()
                return style_id
    except Exception:
        pass
    return None


def _set_current_style(style_id):
    """设置当前使用的语言风格"""
    try:
        os.makedirs(os.path.dirname(CURRENT_STYLE_FILE), exist_ok=True)
        with open(CURRENT_STYLE_FILE, 'w', encoding='utf-8') as f:
            f.write(style_id)
        return True
    except Exception:
        return False


@tool
def list_available_styles(runtime: ToolRuntime = None) -> str:
    """
    查看所有可用的语言风格

    Returns:
        返回所有可用的语言风格列表
    """
    config = _get_style_config()
    if not config:
        return "❌ 无法读取语言风格配置"

    current_style_id = _get_current_style()

    result_parts = []
    result_parts.append("## 可用语言风格\n")
    result_parts.append(f"**当前风格**: {current_style_id if current_style_id else '未设置'}\n")
    result_parts.append(f"**默认风格**: {config.get('default_style', 'professional')}\n")
    result_parts.append("---\n")

    for style in config.get('available_styles', []):
        style_id = style.get('id')
        is_current = "🔴 [当前]" if style_id == current_style_id else ""
        result_parts.append(f"\n### {style.get('name')} {is_current}")
        result_parts.append(f"**ID**: `{style_id}`")
        result_parts.append(f"**描述**: {style.get('description')}")
        result_parts.append(f"**称呼**: {style.get('user_address')}")
        result_parts.append(f"**语气**: {style.get('tone')}")
        result_parts.append(f"**问候语**: {style.get('greeting')}")
        result_parts.append(f"**结束语**: {style.get('closing')}")

    result_parts.append("\n---\n")
    result_parts.append("### 如何切换风格\n")
    result_parts.append("使用 `switch_language_style` 工具，传入风格 ID 即可切换。")

    return "\n".join(result_parts)


@tool
def switch_language_style(style_id: str, runtime: ToolRuntime = None) -> str:
    """
    切换到指定的语言风格

    Args:
        style_id: 语言风格的 ID（如: professional, friendly, concise, humorous, technical, mentor）

    Returns:
        返回切换结果和新风格的详细信息
    """
    config = _get_style_config()
    if not config:
        return "❌ 无法读取语言风格配置"

    # 查找指定的风格
    available_styles = config.get('available_styles', [])
    target_style = None

    for style in available_styles:
        if style.get('id') == style_id:
            target_style = style
            break

    if not target_style:
        # 返回可用的风格列表
        available_ids = ", ".join([s.get('id') for s in available_styles])
        return f"❌ 未找到风格 ID: `{style_id}`\n\n可用的风格 ID: {available_ids}\n\n请使用 `list_available_styles` 查看所有可用风格。"

    # 保存当前风格
    if not _set_current_style(style_id):
        return f"❌ 切换风格失败，无法保存设置"

    # 返回成功信息和风格详情
    result_parts = []
    result_parts.append(f"✅ 语言风格已切换为: **{target_style.get('name')}**\n")
    result_parts.append("---\n")
    result_parts.append("### 风格详情\n")
    result_parts.append(f"**称呼**: {target_style.get('user_address')}")
    result_parts.append(f"**自我介绍**: {target_style.get('self_address')}")
    result_parts.append(f"**语气**: {target_style.get('tone')}")
    result_parts.append(f"**问候语**: {target_style.get('greeting')}")
    result_parts.append(f"**结束语**: {target_style.get('closing')}")
    result_parts.append(f"**描述**: {target_style.get('description')}")

    result_parts.append("\n---\n")
    result_parts.append("### 回复风格\n")
    response_style = target_style.get('response_style', {})
    result_parts.append(f"**结构**: {response_style.get('structure')}")
    result_parts.append(f"**详细程度**: {response_style.get('detail_level')}")
    result_parts.append(f"**格式**: {response_style.get('formatting')}")

    return "\n".join(result_parts)


@tool
def get_current_style_info(runtime: ToolRuntime = None) -> str:
    """
    获取当前使用的语言风格详细信息

    Returns:
        返回当前语言风格的详细信息
    """
    current_style_id = _get_current_style()
    config = _get_style_config()

    if not current_style_id or not config:
        return "⚠️ 当前未设置语言风格，使用默认配置。\n\n请使用 `switch_language_style` 切换风格。"

    # 查找当前风格
    available_styles = config.get('available_styles', [])
    current_style = None

    for style in available_styles:
        if style.get('id') == current_style_id:
            current_style = style
            break

    if not current_style:
        return f"⚠️ 当前风格 ID `{current_style_id}` 不存在。\n\n请使用 `list_available_styles` 查看可用风格。"

    result_parts = []
    result_parts.append(f"## 当前语言风格: {current_style.get('name')}\n")
    result_parts.append("---\n")
    result_parts.append("### 基本信息\n")
    result_parts.append(f"**风格 ID**: `{current_style.get('id')}`")
    result_parts.append(f"**用户称呼**: {current_style.get('user_address')}")
    result_parts.append(f"**自我介绍**: {current_style.get('self_address')}")
    result_parts.append(f"**语气**: {current_style.get('tone')}")
    result_parts.append(f"**描述**: {current_style.get('description')}")

    result_parts.append("\n### 语言习惯\n")
    result_parts.append(f"**问候语**: {current_style.get('greeting')}")
    result_parts.append(f"**结束语**: {current_style.get('closing')}")

    result_parts.append("\n### 回复风格\n")
    response_style = current_style.get('response_style', {})
    result_parts.append(f"**结构风格**: {response_style.get('structure')}")
    result_parts.append(f"**详细程度**: {response_style.get('detail_level')}")
    result_parts.append(f"**格式特点**: {response_style.get('formatting')}")

    return "\n".join(result_parts)


def get_style_prompt(style_id: str = None) -> str:
    """
    获取指定风格的提示词片段

    Args:
        style_id: 风格 ID，如果为 None 则使用当前风格

    Returns:
        返回风格的提示词片段
    """
    if style_id is None:
        style_id = _get_current_style()

    config = _get_style_config()
    if not config or not style_id:
        # 返回默认风格
        default_id = config.get('default_style', 'professional') if config else 'professional'
        style_id = default_id

    # 查找风格
    available_styles = config.get('available_styles', []) if config else []
    target_style = None

    for style in available_styles:
        if style.get('id') == style_id:
            target_style = style
            break

    if not target_style:
        # 如果找不到，使用第一个风格
        target_style = available_styles[0] if available_styles else None

    if not target_style:
        return ""

    # 生成风格提示词
    prompt_parts = []
    prompt_parts.append(f"## 语言风格设置\n")
    prompt_parts.append(f"**用户称呼**: 使用「{target_style.get('user_address')}」来称呼用户\n")
    prompt_parts.append(f"**自我介绍**: 自称「{target_style.get('self_address')}」\n")
    prompt_parts.append(f"**语气风格**: {target_style.get('tone')}\n")
    prompt_parts.append(f"**问候语**: 在对话开始时使用「{target_style.get('greeting')}」\n")
    prompt_parts.append(f"**结束语**: 在对话结束时使用「{target_style.get('closing')}」\n")

    emoji_usage = target_style.get('emoji_usage', 'minimal')
    if emoji_usage == 'frequent':
        prompt_parts.append("**表情符号**: 积极使用表情符号增强表达效果\n")
    elif emoji_usage == 'moderate':
        prompt_parts.append("**表情符号**: 适度使用表情符号\n")
    else:
        prompt_parts.append("**表情符号**: 尽量少用或不用表情符号\n")

    response_style = target_style.get('response_style', {})
    prompt_parts.append("\n**回复风格要求**:\n")
    prompt_parts.append(f"- 结构: {response_style.get('structure')}\n")
    prompt_parts.append(f"- 详细程度: {response_style.get('detail_level')}\n")
    prompt_parts.append(f"- 格式: {response_style.get('formatting')}\n")

    return "\n".join(prompt_parts)
