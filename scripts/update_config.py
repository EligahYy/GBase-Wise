#!/usr/bin/env python3
"""更新配置文件，优化工具使用原则"""

import json

# 读取配置文件
with open('config/agent_llm_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 更新系统提示词中的工具使用原则
old_principles = """## 工具使用原则
1. **优先级**：知识库搜索 > 联网搜索 > 网页内容获取 > LLM 自身能力
2. **精确性**：使用搜索工具时，尽量使用具体、精确的关键词
3. **验证**：对于搜索结果，分析信息来源的权威性和可靠性
4. **SQL 验证**：生成 SQL 后，必须使用 validate_sql 工具验证语法
5. **反馈学习**：收集用户反馈，持续优化 SQL 生成效果"""

new_principles = """## 工具使用原则
1. **优先级**：知识库搜索 > 联网搜索 > 网页内容获取 > LLM 自身能力
2. **统一工具优先**：
   - 搜索任务：优先使用 `web_search` 工具，而非兼容性工具（search_competitor_info、search_market_trends、search_database_best_practices）
   - 网页获取：优先使用 `fetch_url` 工具，而非兼容性工具（fetch_webpage_content、fetch_article_summary、fetch_document_content）
   - 兼容性工具仅供向后兼容，新功能开发时不应使用
3. **精确性**：使用搜索工具时，尽量使用具体、精确的关键词
4. **验证**：对于搜索结果，分析信息来源的权威性和可靠性
5. **SQL 验证**：生成 SQL 后，必须使用 validate_sql 工具验证语法
6. **反馈学习**：收集用户反馈，持续优化 SQL 生成效果"""

config['sp'] = config['sp'].replace(old_principles, new_principles)

# 写回配置文件
with open('config/agent_llm_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)

print("✅ 配置文件已更新")
