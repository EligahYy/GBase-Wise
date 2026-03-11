"""
SQL 生成工具
根据业务需求生成 GBase8a SQL 语句
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Literal, Optional
from datetime import datetime


@tool
def generate_sql(
    business_requirement: str,
    database_type: str = "gbase8a",
    return_type: Literal["sql_only", "sql_with_explanation", "sql_with_best_practices"] = "sql_with_explanation",
    runtime: ToolRuntime = None
) -> str:
    """
    根据业务需求生成符合数据库语法的 SQL 语句

    Args:
        business_requirement: 业务需求描述，例如 "查询最近30天销售额超过10万的产品，按销售额降序排列"
        database_type: 数据库类型，目前支持 gbase8a（预留 oracle/mysql/postgresql/sqlserver）
        return_type: 返回类型
            - sql_only: 仅返回 SQL 语句
            - sql_with_explanation: SQL 语句 + 语法说明
            - sql_with_best_practices: SQL 语句 + 语法说明 + 最佳实践建议

    Returns:
        返回 SQL 语句及说明（根据 return_type）
    """
    ctx = runtime.context if runtime else new_context(method="sql.generate")

    # 目前仅支持 GBase8a
    if database_type.lower() != "gbase8a":
        return f"目前仅支持 GBase8a 数据库，暂不支持 {database_type}"

    # 导入知识库检索工具
    from tools.knowledge_tool import search_knowledge_base

    # 1. 从知识库检索相关的 SQL 语法参考
    try:
        syntax_reference = search_knowledge_base(
            f"GBase8a SQL 语法参考 {extract_query_type(business_requirement)}",
            runtime=runtime
        )

        # 2. 检索相关的正向示例
        examples = search_knowledge_base(
            f"SQL 正向示例 {extract_query_type(business_requirement)}",
            runtime=runtime
        )
    except Exception as e:
        syntax_reference = ""
        examples = ""

    # 3. 构建提示词（Prompt）
    prompt = f"""你是一个 {database_type.upper()} 数据库的 SQL 专家，请根据业务需求生成符合语法的 SQL 语句。

【GBase8a SQL 语法参考】
{syntax_reference[:2000] if syntax_reference else "暂无语法参考，请使用标准 SQL 语法"}

【相关正向示例】
{examples[:1000] if examples else "暂无示例"}

【业务需求】
{business_requirement}

请生成符合 {database_type.upper()} 语法的 SQL 语句。

**要求**：
1. SQL 必须符合 {database_type.upper()} 的语法规范
2. 使用合理的表名和字段名（如果需求中未提供，使用有意义的假设）
3. 添加必要的注释说明
4. 使用代码块格式输出 SQL
5. 确保查询逻辑正确且高效

**输出格式**：
```sql
-- SQL 注释说明
SELECT ...;
```

如果是查询语句，请说明查询的目的和逻辑。
"""

    # 4. 使用 LLM 生成 SQL
    # 注意：这里需要访问 LLM，我们通过 runtime 的 context 获取
    try:
        from langchain_openai import ChatOpenAI
        import os

        api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
        base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

        llm = ChatOpenAI(
            model="doubao-seed-1-6-251015",
            api_key=api_key,
            base_url=base_url,
            temperature=0.3,  # 使用较低的温度，确保生成的 SQL 更准确
            timeout=60
        )

        response = llm.invoke(prompt)
        sql_result = response.content

        # 5. 根据 return_type 格式化输出
        if return_type == "sql_only":
            return sql_result
        elif return_type == "sql_with_explanation":
            return f"## 生成的 SQL 语句\n\n{sql_result}\n\n---\n**提示**：建议在实际执行前使用 `validate_sql` 工具验证 SQL 语法。"
        else:  # sql_with_best_practices
            best_practices = get_best_practices(extract_query_type(business_requirement))
            return f"## 生成的 SQL 语句\n\n{sql_result}\n\n## 最佳实践建议\n\n{best_practices}\n\n---\n**提示**：建议在实际执行前使用 `validate_sql` 工具验证 SQL 语法。"

    except Exception as e:
        return f"SQL 生成失败: {str(e)}"


def extract_query_type(requirement: str) -> str:
    """
    从需求描述中提取查询类型

    Args:
        requirement: 业务需求描述

    Returns:
        查询类型关键词
    """
    req_lower = requirement.lower()

    if any(kw in req_lower for kw in ["分组", "group by", "统计", "汇总", "sum", "count", "avg"]):
        return "聚合查询"
    elif any(kw in req_lower for kw in ["关联", "join", "连接", "多表"]):
        return "JOIN 查询"
    elif any(kw in req_lower for kw in ["排名", "row_number", "rank", "dense_rank", "窗口"]):
        return "窗口函数"
    elif any(kw in req_lower for kw in ["插入", "insert", "新增", "添加"]):
        return "INSERT"
    elif any(kw in req_lower for kw in ["更新", "update", "修改", "更改"]):
        return "UPDATE"
    elif any(kw in req_lower for kw in ["删除", "delete", "移除"]):
        return "DELETE"
    else:
        return "基础查询"


def get_best_practices(query_type: str) -> str:
    """
    获取指定查询类型的最佳实践

    Args:
        query_type: 查询类型

    Returns:
        最佳实践说明
    """
    practices = {
        "聚合查询": """
1. **使用 WHERE 而不是 HAVING 过滤**
   - WHERE 在分组前过滤，HAVING 在分组后过滤
   - WHERE 性能更好

2. **避免 SELECT ***
   - 只选择需要的列，减少数据传输量

3. **合理使用索引**
   - 为 GROUP BY 和 WHERE 条件中的列创建索引

4. **优化聚合函数**
   - 对于大量数据，考虑使用近似计算函数（如 APPROX_COUNT_DISTINCT）
""",
        "JOIN 查询": """
1. **优先使用 INNER JOIN**
   - 只有在确实需要保留不匹配的记录时才使用 LEFT/RIGHT JOIN

2. **确保 JOIN 列有索引**
   - 为 JOIN 条件中的列创建索引

3. **限制返回的数据量**
   - 使用 LIMIT 限制结果集大小

4. **避免过多表连接**
   - 3-5 个表的连接是合理的上限
""",
        "窗口函数": """
1. **合理使用 PARTITION BY**
   - 只在需要分组计算时使用

2. **注意窗口函数的性能**
   - 窗口函数可能比普通聚合函数消耗更多资源

3. **使用索引优化**
   - 为 ORDER BY 和 PARTITION BY 列创建索引
""",
        "基础查询": """
1. **避免 SELECT ***
   - 只选择需要的列

2. **使用索引**
   - 为 WHERE 条件中的列创建索引

3. **限制结果集**
   - 使用 LIMIT 限制返回的行数

4. **使用 EXISTS 代替 IN**
   - 对于子查询，EXISTS 通常性能更好
"""
    }

    return practices.get(query_type, "请确保 SQL 语法正确，并在生产环境执行前进行充分测试。")
