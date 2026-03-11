"""
SQL 反馈工具
记录用户对 SQL 的正向/反向反馈，用于持续学习
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Literal, Optional
from datetime import datetime
import json
import os


@tool
def record_sql_feedback(
    business_requirement: str,
    generated_sql: str,
    feedback_type: Literal["positive", "negative"],
    feedback_comment: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    记录用户对 SQL 的正向/反向反馈

    Args:
        business_requirement: 原始业务需求
        generated_sql: 生成的 SQL 语句
        feedback_type: 反馈类型
            - positive: 正向反馈（SQL 正确/有用）
            - negative: 反向反馈（SQL 错误/需要改进）
        feedback_comment: 反馈说明（可选），例如 "语法错误" "性能不佳" "完全正确" 等

    Returns:
        记录结果（成功/失败）
    """
    ctx = runtime.context if runtime else new_context(method="sql.feedback")

    try:
        # 确保数据目录存在
        data_dir = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"), "assets", "sql_examples")
        os.makedirs(data_dir, exist_ok=True)

        # 根据反馈类型确定文件路径
        if feedback_type == "positive":
            file_path = os.path.join(data_dir, "positive_examples.jsonl")
        else:
            file_path = os.path.join(data_dir, "negative_examples.jsonl")

        # 构建反馈记录
        record = {
            "timestamp": datetime.now().isoformat(),
            "business_requirement": business_requirement,
            "generated_sql": generated_sql.strip(),
            "feedback_type": feedback_type,
            "feedback_comment": feedback_comment or ""
        }

        # 写入文件（追加模式）
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

        # 返回结果
        result = f"## 反馈记录成功 ✅\n\n"
        result += f"**反馈类型**: {feedback_type}\n"
        result += f"**业务需求**: {business_requirement}\n"
        if feedback_comment:
            result += f"**反馈说明**: {feedback_comment}\n"
        result += f"\n该示例已保存到 {feedback_type} 示例库，将用于优化未来的 SQL 生成。"

        return result

    except Exception as e:
        return f"反馈记录失败: {str(e)}"


@tool
def manage_sql_examples(
    action: Literal["list", "search", "stats"],
    example_type: Optional[Literal["positive", "negative"]] = None,
    search_keyword: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    管理 SQL 示例库（查询、搜索、统计）

    Args:
        action: 操作类型
            - list: 列出示例（最近的 10 条）
            - search: 搜索示例
            - stats: 统计信息
        example_type: 示例类型（positive/negative），仅用于 list 和 stats
        search_keyword: 搜索关键词，仅用于 search
        runtime: 工具运行时上下文

    Returns:
        操作结果
    """
    ctx = runtime.context if runtime else new_context(method="sql.manage")

    try:
        data_dir = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"), "assets", "sql_examples")

        if action == "stats":
            # 统计信息
            return get_statistics(data_dir)

        elif action == "list":
            # 列出示例
            if not example_type:
                return "请指定 example_type (positive 或 negative)"

            file_path = os.path.join(data_dir, f"{example_type}_examples.jsonl")
            if not os.path.exists(file_path):
                return f"暂无 {example_type} 示例"

            return list_examples(file_path, example_type, limit=10)

        elif action == "search":
            # 搜索示例
            if not search_keyword:
                return "请提供 search_keyword"

            return search_examples(data_dir, search_keyword)

        else:
            return f"不支持的操作类型: {action}"

    except Exception as e:
        return f"操作失败: {str(e)}"


def get_statistics(data_dir: str) -> str:
    """
    获取统计信息

    Args:
        data_dir: 数据目录

    Returns:
        统计信息
    """
    stats = {
        "positive": 0,
        "negative": 0
    }

    for example_type in ["positive", "negative"]:
        file_path = os.path.join(data_dir, f"{example_type}_examples.jsonl")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                stats[example_type] = len([line for line in f if line.strip()])

    result = "## SQL 示例库统计\n\n"
    result += f"- ✅ 正向示例: {stats['positive']} 条\n"
    result += f"- ❌ 反向示例: {stats['negative']} 条\n"
    result += f"- 📊 总计: {stats['positive'] + stats['negative']} 条\n"

    if stats['positive'] + stats['negative'] == 0:
        result += "\n提示: 暂无示例，请使用 `record_sql_feedback` 工具记录反馈。"

    return result


def list_examples(file_path: str, example_type: str, limit: int = 10) -> str:
    """
    列出示例

    Args:
        file_path: 文件路径
        example_type: 示例类型
        limit: 返回数量限制

    Returns:
        示例列表
    """
    examples = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    # 按时间倒序排列，取最近的 N 条
    examples = sorted(examples, key=lambda x: x['timestamp'], reverse=True)[:limit]

    result = f"## 最近 {len(examples)} 条 {example_type} 示例\n\n"

    for i, example in enumerate(examples, 1):
        result += f"### 示例 {i}\n\n"
        result += f"**时间**: {example['timestamp']}\n"
        result += f"**业务需求**: {example['business_requirement']}\n\n"
        result += "**SQL 语句**:\n```sql\n"
        result += example['generated_sql']
        result += "\n```\n\n"

        if example['feedback_comment']:
            result += f"**反馈说明**: {example['feedback_comment']}\n"
        result += "\n---\n\n"

    return result


def search_examples(data_dir: str, keyword: str) -> str:
    """
    搜索示例

    Args:
        data_dir: 数据目录
        keyword: 搜索关键词

    Returns:
        搜索结果
    """
    results = []
    keyword_lower = keyword.lower()

    for example_type in ["positive", "negative"]:
        file_path = os.path.join(data_dir, f"{example_type}_examples.jsonl")
        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)

                    # 搜索业务需求和 SQL 语句
                    if (keyword_lower in record['business_requirement'].lower() or
                        keyword_lower in record['generated_sql'].lower()):

                        results.append({
                            "type": example_type,
                            "record": record
                        })

    if not results:
        return f"未找到包含关键词 '{keyword}' 的示例"

    # 限制返回数量
    results = results[:10]

    result = f"## 搜索结果: '{keyword}'\n\n"
    result += f"找到 {len(results)} 条相关示例\n\n"

    for i, item in enumerate(results, 1):
        example = item['record']
        emoji = "✅" if item['type'] == "positive" else "❌"

        result += f"### {emoji} 示例 {i} ({item['type']})\n\n"
        result += f"**时间**: {example['timestamp']}\n"
        result += f"**业务需求**: {example['business_requirement']}\n\n"
        result += "**SQL 语句**:\n```sql\n"
        result += example['generated_sql']
        result += "\n```\n\n"

        if example['feedback_comment']:
            result += f"**反馈说明**: {example['feedback_comment']}\n"
        result += "\n---\n\n"

    return result
