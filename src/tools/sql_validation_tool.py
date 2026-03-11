"""
SQL 验证工具
验证 SQL 语句的语法正确性
"""
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from typing import Literal, List, Tuple
import re


@tool
def validate_sql(sql: str, strict_mode: bool = False, runtime: ToolRuntime = None) -> str:
    """
    验证 SQL 语句的语法正确性

    Args:
        sql: 待验证的 SQL 语句
        strict_mode: 严格模式
            - False: 基础语法检查（默认）
            - True: 严格检查，包括关键字拼写、大小写等

    Returns:
        返回验证结果，包括：
        - 验证结果（通过/失败）
        - 错误位置和类型（如果失败）
        - 修正建议（如果失败）
    """
    ctx = runtime.context if runtime else new_context(method="sql.validate")

    # 清理 SQL 语句
    cleaned_sql = clean_sql(sql)

    if not cleaned_sql:
        return "验证失败: SQL 语句为空"

    errors = []
    warnings = []

    # 1. 基础语法检查
    basic_errors = check_basic_syntax(cleaned_sql)
    if basic_errors:
        errors.extend(basic_errors)

    # 2. 检查关键字拼写
    if strict_mode:
        keyword_errors = check_keywords(cleaned_sql)
        if keyword_errors:
            errors.extend(keyword_errors)

    # 3. 检查括号匹配
    bracket_errors = check_brackets(cleaned_sql)
    if bracket_errors:
        errors.extend(bracket_errors)

    # 4. 检查引号匹配
    quote_errors = check_quotes(cleaned_sql)
    if quote_errors:
        errors.extend(quote_errors)

    # 5. 检查常见错误
    common_errors = check_common_errors(cleaned_sql)
    if common_errors:
        warnings.extend(common_errors)

    # 6. 构建验证结果
    if errors:
        # 有错误
        result = "## 验证结果: ❌ 未通过\n\n"
        result += "### 发现的错误:\n\n"
        for i, error in enumerate(errors, 1):
            result += f"{i}. {error}\n"

        if warnings:
            result += "\n### 警告:\n\n"
            for i, warning in enumerate(warnings, 1):
                result += f"{i}. {warning}\n"

        result += "\n### 建议:\n\n"
        result += "1. 检查 SQL 语句的语法结构\n"
        result += "2. 参考 GBase8a SQL 参考文档\n"
        result += "3. 使用 `generate_sql` 工具重新生成\n"

        return result
    else:
        # 无错误
        result = "## 验证结果: ✅ 通过\n\n"
        result += "SQL 语句基础语法检查通过。\n\n"

        if warnings:
            result += "### 警告:\n\n"
            for i, warning in enumerate(warnings, 1):
                result += f"{i}. {warning}\n"
            result += "\n"

        result += "### 建议:\n\n"
        result += "- 在生产环境执行前，请进行充分测试\n"
        result += "- 使用 EXPLAIN 分析查询执行计划\n"
        result += "- 确保相关列有索引\n"

        return result


def clean_sql(sql: str) -> str:
    """
    清理 SQL 语句，移除注释和多余空格

    Args:
        sql: 原始 SQL

    Returns:
        清理后的 SQL
    """
    # 移除单行注释
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)

    # 移除多行注释
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

    # 压缩空格
    sql = re.sub(r'\s+', ' ', sql).strip()

    return sql


def check_basic_syntax(sql: str) -> List[str]:
    """
    检查基础语法

    Args:
        sql: SQL 语句

    Returns:
        错误列表
    """
    errors = []

    # 检查是否以 DML 或 DDL 关键字开头
    sql_upper = sql.upper()
    valid_starters = [
        "SELECT", "INSERT", "UPDATE", "DELETE",
        "CREATE", "ALTER", "DROP", "TRUNCATE"
    ]

    if not any(sql_upper.startswith(start) for start in valid_starters):
        errors.append("SQL 语句必须以 DML 或 DDL 关键字开头（SELECT/INSERT/UPDATE/DELETE/CREATE/ALTER/DROP）")

    # 检查 SELECT 语句的基本结构
    if sql_upper.startswith("SELECT"):
        if "FROM" not in sql_upper:
            errors.append("SELECT 语句缺少 FROM 子句")

    # 检查 INSERT 语句的基本结构
    if sql_upper.startswith("INSERT"):
        if "INTO" not in sql_upper:
            errors.append("INSERT 语句缺少 INTO 关键字")
        if "VALUES" not in sql_upper and "SELECT" not in sql_upper:
            errors.append("INSERT 语句缺少 VALUES 子句或 SELECT 子查询")

    # 检查 UPDATE 语句的基本结构
    if sql_upper.startswith("UPDATE"):
        if "SET" not in sql_upper:
            errors.append("UPDATE 语句缺少 SET 子句")
        if "WHERE" not in sql_upper:
            errors.append("警告: UPDATE 语句缺少 WHERE 子句，可能会更新所有行")

    # 检查 DELETE 语句的基本结构
    if sql_upper.startswith("DELETE"):
        if "WHERE" not in sql_upper:
            errors.append("警告: DELETE 语句缺少 WHERE 子句，可能会删除所有行")

    return errors


def check_keywords(sql: str) -> List[str]:
    """
    检查关键字拼写（严格模式）

    Args:
        sql: SQL 语句

    Returns:
        错误列表
    """
    errors = []

    # GBase8a 常用关键字
    keywords = [
        "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING",
        "INSERT", "INTO", "VALUES", "UPDATE", "DELETE",
        "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL JOIN",
        "UNION", "UNION ALL",
        "AND", "OR", "NOT", "IN", "EXISTS",
        "COUNT", "SUM", "AVG", "MAX", "MIN",
        "ROW_NUMBER", "RANK", "DENSE_RANK", "LAG", "LEAD"
    ]

    sql_upper = sql.upper()

    for keyword in keywords:
        # 检查常见拼写错误
        if keyword == "SELECT" and "SELECR" in sql_upper:
            errors.append("关键字拼写错误: 'SELECR' 应为 'SELECT'")
        if keyword == "FROM" and "FORM" in sql_upper:
            errors.append("关键字拼写错误: 'FORM' 应为 'FROM'")
        if keyword == "WHERE" and "WERE" in sql_upper:
            errors.append("关键字拼写错误: 'WERE' 应为 'WHERE'")

    return errors


def check_brackets(sql: str) -> List[str]:
    """
    检查括号匹配

    Args:
        sql: SQL 语句

    Returns:
        错误列表
    """
    errors = []

    # 检查圆括号
    stack = []
    for i, char in enumerate(sql):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if not stack:
                errors.append(f"位置 {i}: 多余的右括号 ')'")
            else:
                stack.pop()

    if stack:
        for pos in stack:
            errors.append(f"位置 {pos}: 未闭合的左括号 '('")

    return errors


def check_quotes(sql: str) -> List[str]:
    """
    检查引号匹配

    Args:
        sql: SQL 语句

    Returns:
        错误列表
    """
    errors = []

    # 检查单引号
    single_quote_count = sql.count("'")
    if single_quote_count % 2 != 0:
        errors.append("单引号不匹配（奇数个单引号）")

    # 检查双引号（GBase8a 主要使用单引号）
    double_quote_count = sql.count('"')
    if double_quote_count % 2 != 0:
        errors.append("双引号不匹配（奇数个双引号）")

    return errors


def check_common_errors(sql: str) -> List[str]:
    """
    检查常见错误

    Args:
        sql: SQL 语句

    Returns:
        警告列表
    """
    warnings = []

    # 检查 SELECT *
    if re.search(r'\bSELECT\s+\*\s+FROM\b', sql, re.IGNORECASE):
        warnings.append("使用了 SELECT *，建议明确指定列名以提高性能和可读性")

    # 检查缺少 WHERE 的 UPDATE/DELETE
    sql_upper = sql.upper()
    if sql_upper.startswith("UPDATE") and "WHERE" not in sql_upper:
        warnings.append("UPDATE 语句缺少 WHERE 子句，可能会更新所有行（已在上文提示）")
    if sql_upper.startswith("DELETE") and "WHERE" not in sql_upper:
        warnings.append("DELETE 语句缺少 WHERE 子句，可能会删除所有行（已在上文提示）")

    # 检查 LIKE 后缺少通配符
    if re.search(r'\bLIKE\s+\'[^\%_]+\'', sql, re.IGNORECASE):
        warnings.append("LIKE 语句中没有使用通配符（% 或 _），建议使用 = 代替 LIKE")

    # 检查 HAVING 中使用了可以放在 WHERE 的条件
    if "HAVING" in sql_upper and re.search(r'\bHAVING\s+\w+\s*[=<>]', sql, re.IGNORECASE):
        warnings.append("HAVING 子句中使用了简单的比较条件，考虑将其移至 WHERE 子句以提高性能")

    return warnings
