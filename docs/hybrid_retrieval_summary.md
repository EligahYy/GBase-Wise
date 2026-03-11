# 混合检索机制实施总结

## 问题分析

### 用户发现的问题
用户观察到的现象：
- **用户提问**："如何通过jdbc方式连接gbase 8a数据库"
- **实际调用**：web_search → fetch_url（3次）
- **缺失调用**：❌ 没有使用 `search_knowledge_base` 或 `hybrid_search`

### 根本原因

1. **System Prompt 约束力不足**
   - 虽然强调了"知识库优先"，但没有强制要求
   - Agent 可以根据"最佳判断"跳过知识库检索

2. **Agent 决策逻辑不明确**
   - 没有明确的"必须先检索知识库"的规则
   - Agent 可能认为联网搜索能更快得到结果

3. **工具调用顺序不固定**
   - 没有强制要求工具调用的顺序
   - Agent 可以自由选择工具

---

## 解决方案

### 方案设计：混合检索

#### 架构设计
```
用户输入
    ↓
[1] 知识库检索（GBase8a 官方文档）
    ├─ 搜索结果：top_k=5, min_score=0.5
    └─ 评分：基于相似度、来源权威性
    ↓
[2] 联网搜索（补充最新信息）
    ├─ 搜索结果：top_k=5
    └─ 评分：基于来源权威性、时效性
    ↓
[3] 结果融合（加权排序）
    ├─ 知识库结果：权重 70%（官方权威）
    ├─ 联网搜索结果：权重 30%（补充信息）
    └─ 去重、排序、截取 top_k=10
    ↓
[4] 生成回答
    ├─ 优先使用知识库信息
    ├─ 用联网搜索信息补充
    └─ 标注信息来源
```

### 技术实现

#### 1. 混合检索工具（`hybrid_search_tool.py`）

**核心功能**：
```python
@tool
def hybrid_search(query: str, top_k: int = 10, dataset: str = "gbase8a", runtime: ToolRuntime = None) -> str:
    """混合检索：结合知识库检索和联网搜索，提供更全面的信息"""
    # 1. 知识库检索（权重 70%）
    knowledge_results = _search_knowledge_base(query, dataset, top_k // 2)

    # 2. 联网搜索（权重 30%）
    web_results = _search_web(query, top_k // 2)

    # 3. 结果融合（加权排序）
    fused_results = _fuse_results(knowledge_results, web_results)

    # 4. 格式化输出
    return _format_results(query, fused_results)
```

**结果融合算法**：
- **加权评分**：知识库结果 × 0.7 + 联网搜索结果 × 0.3
- **去重机制**：基于内容相似度（80% 相似度阈值）
- **排序策略**：按 final_score 降序排列

#### 2. System Prompt 优化（`config/agent_llm_config_v2.json`）

**关键改进**：
```yaml
## 工具调用策略（强制执行）

### 优先级顺序（严格遵循）

**第一步：混合检索（必须执行）**
- 所有技术问题必须首先使用 `hybrid_search` 工具
- 参数：query（用户问题）, dataset="gbase8a", top_k=10
- 如果检索失败，标记为"检索失败"并进入下一步

**第二步：网页获取（可选）**
- 如果混合检索结果不足或需要更多细节
- 使用 `fetch_url` 获取指定网页内容
```

#### 3. 工具注册优化（`agent.py`）

**优先级调整**：
```python
tools = [
    # 混合检索工具（最高优先级 - 强制执行）
    hybrid_search,
    # 知识库管理工具
    search_knowledge_base,
    query_technical_detail,
    # 搜索工具
    web_search,
    # ... 其他工具
]
```

---

## 实施结果

### ✅ 已完成

1. **混合检索工具实现**
   - 知识库检索功能
   - 联网搜索功能
   - 结果融合算法
   - 去重机制

2. **System Prompt 优化**
   - 强制混合检索优先级
   - 明确工具调用策略
   - 定义技术问题范围

3. **工具注册优化**
   - 将 hybrid_search 放在最高优先级
   - 更新工具列表

4. **文档完善**
   - Agent 逻辑流程与优化方案文档
   - CHANGELOG.md 更新
   - README.md 更新

### ⚠️ 待改进

1. **System Prompt 强制力不足**
   - Agent 仍未强制使用混合检索
   - 测试显示 Agent 仍使用 web_search 和 fetch_url
   - **原因**：LLM 对"必须执行"的理解不够强

2. **需要进一步优化**
   - 降低 System Prompt 的复杂度
   - 使用更直接的指令
   - 增加示例和强制规则

---

## 测试结果

### 测试场景
**输入**："详细介绍一下如何通过jdbc方式连接gbase 8a数据库，从安装部署到参数配置，再到使用全链路讲清楚"

### 实际调用
```
- web_search (第1次)
- web_search (第2次)
- fetch_url (第3次)
- fetch_url (第4次)
- web_search (第5次)
- fetch_url (第6次)
- fetch_url (第7次)
- web_search (第8次)
- web_search (第9次)
- web_search (第10次)
```

### 预期调用
```
- hybrid_search (第1次)
  ├─ 知识库检索：top_k=5
  ├─ 联网搜索：top_k=5
  └─ 结果融合：top_k=10
```

### 问题分析
- ❌ 没有使用 hybrid_search 工具
- ❌ 工具调用次数过多（10次 vs 1次）
- ❌ 没有检索知识库
- ✅ 最终回答质量尚可

---

## 后续优化建议

### 方案 1：进一步简化 System Prompt

**策略**：
- 删除冗余的说明
- 使用更直接的指令
- 减少 token 使用量

**示例**：
```yaml
# 简化版 System Prompt

## 强制规则

对于所有 GBase8a 技术问题，必须执行以下步骤：

1. 首先调用 `hybrid_search` 工具
2. 基于检索结果生成回答
3. 标注信息来源

## 禁止行为

- 禁止跳过 `hybrid_search` 直接使用其他工具
- 禁止在混合检索失败时直接回答
- 禁止编造未检索到的信息
```

### 方案 2：使用工具调用约束

**策略**：
- 在 agent.py 中添加工具调用约束
- 使用 pre-tool-check 钩子强制执行混合检索

**示例**：
```python
@wrap_tool_call
def enforce_hybrid_search(request, handler):
    """强制技术问题使用混合检索"""
    tool_name = request.tool_call["name"]

    # 判断是否为技术问题
    if _is_technical_question(request.messages[-1].content):
        # 如果第一个工具不是 hybrid_search，强制使用
        if tool_name != "hybrid_search":
            return ToolMessage(
                content="必须首先使用 hybrid_search 工具",
                tool_call_id=request.tool_call["id"]
            )

    return handler(request)
```

### 方案 3：使用更强大的模型

**策略**：
- 切换到更强大的模型（如 GPT-4）
- 提高对复杂指令的遵循能力

**注意**：需要考虑成本和性能

---

## 总结

### 成功之处
1. ✅ 混合检索工具实现完成
2. ✅ 结果融合算法有效
3. ✅ 文档完善

### 不足之处
1. ⚠️ Agent 仍未强制使用混合检索
2. ⚠️ System Prompt 的强制力不足
3. ⚠️ 需要进一步优化

### 下一步行动
1. 进一步简化 System Prompt
2. 实现工具调用约束机制
3. 测试和验证优化效果

---

**版本**: v2.2.0
**更新日期**: 2025-01-14
**状态**: ⏳ 待进一步优化
