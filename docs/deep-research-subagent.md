# DeepResearch Sub-Agent

DeepResearch Sub-Agent 是 Lang Claw 项目中专门用于深度调研分析的子代理。

## 架构集成

```
主 Agent (Lang Claw)
    │
    ├── personal-data Sub-Agent (用户数据管理)
    │
    └── deep-research Sub-Agent (深度调研) ← 本文档
            │
            └── Tavily API (网络搜索)
```

## 核心能力

- 深度网络搜索（基于 Tavily API）
- 多维度信息对比分析
- 结构化报告生成
- 关键信息评估和综合

## 工具集

### 1. tavily_search(query, max_results=5)

使用 Tavily API 进行深度网络搜索，适合单一主题的深入研究。

**参数:**
- `query`: 搜索查询字符串
- `max_results`: 返回的最大结果数（默认 5）

**返回:**
- `query`: 原始查询
- `answer`: AI 生成的答案摘要
- `results`: 搜索结果列表，每个包含 title、url、content、score

**示例:**
```python
# 用户: "帮我研究一下 LangChain 的最新版本有什么新特性"
# Sub-Agent 使用 tavily_search("LangChain latest version features 2024")
```

### 2. multi_query_search(queries, max_results_per_query=3)

对多个查询进行并行搜索，适合对比分析或多维度调研。

**参数:**
- `queries`: 查询字符串列表（最多 5 个）
- `max_results_per_query`: 每个查询的最大结果数（默认 3）

**返回:**
- `total_queries`: 总查询数
- `successful_queries`: 成功查询数
- `results`: 按查询组织的所有结果

**示例:**
```python
# 用户: "对比一下 React、Vue 和 Angular 的性能"
# Sub-Agent 使用 multi_query_search([
#     "React performance benchmarks 2024",
#     "Vue.js performance comparison 2024",
#     "Angular performance vs React 2024"
# ])
```

### 3. think_and_plan(thought)

记录思考过程和研究计划，帮助组织复杂的研究任务。

**参数:**
- `thought`: 思考内容或研究计划

**返回:**
- 确认信息

## 快速开始

### 1. 安装依赖

```bash
cd backend
uv sync
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
# 必需
ZHIPU_API_KEY=your_zhipu_api_key_here
TAVILY_API_KEY=tvly-your_api_key_here

# 可选
LLM_MODEL=glm-5
LLM_TEMPERATURE=0.2
```

### 3. 获取 Tavily API Key

1. 访问 https://tavily.com/
2. 注册账号（支持 Google 账号或邮箱）
3. 在 Dashboard 中生成 API Key
4. 将 API Key（格式：`tvly-xxxxxxxxxx`）添加到 `.env` 文件

**免费套餐**: 1,000 次搜索/月

### 4. 启动服务

```bash
# Docker Compose
docker-compose up -d

# 或直接运行
cd backend
uv run uvicorn app.main:app --reload
```

### 5. 测试

```bash
curl -X POST http://localhost:8000/api/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "message": "帮我研究一下 LangChain 的最新版本有什么新特性"}'
```

## 使用场景

### 场景 1: 单一主题深入研究

**用户请求:** "帮我研究一下 RAG(检索增强生成) 技术的最新进展"

**Sub-Agent 行为:**
1. 使用 `think_and_plan()` 规划研究目标
2. 使用 `tavily_search()` 搜索 RAG 相关信息
3. 分析结果并生成结构化报告

### 场景 2: 多维度对比分析

**用户请求:** "对比 Python、JavaScript 和 Go 在 Web 开发中的优缺点"

**Sub-Agent 行为:**
1. 使用 `multi_query_search()` 并行搜索三个语言的信息
2. 综合多个来源的信息
3. 生成对比分析报告

### 场景 3: 复杂研究任务

**用户请求:** "帮我调研一下微服务架构的最佳实践，包括服务发现、负载均衡和容错处理"

**Sub-Agent 行为:**
1. 使用 `think_and_plan()` 分解研究步骤
2. 多次使用 `tavily_search()` 分别研究各个子主题
3. 综合所有信息生成完整报告

## 输出格式

```markdown
## Research Summary
[研究发现概述]

## Key Findings
- 发现 1 [来源链接]
- 发现 2 [来源链接]

## Detailed Analysis
[深入分析]

## Sources
1. [标题](URL) - 描述
2. [标题](URL) - 描述

## Recommendations (if applicable)
[基于研究的建议]
```

## 性能与成本

### Tavily API 限制

| 套餐 | 搜索次数/月 | 价格 |
|------|------------|------|
| Free | 1,000 | $0 |
| Pro | 10,000 | $29/月 |
| Enterprise | 自定义 | 联系销售 |

### 优化建议

1. 简单问题使用较小的 `max_results` 参数
2. 对比任务使用 `multi_query_search` 批量处理
3. 复杂任务先用 `think_and_plan` 规划
4. 考虑缓存常用查询结果

## 故障排查

### Tavily API Key 未配置

**错误:** `"Tavily API key not configured"`

**解决:** 在 `.env` 文件中设置 `TAVILY_API_KEY`

### 搜索失败

**错误:** `"Search failed: ..."`

**解决:**
1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看 Tavily 账户状态

### Sub-Agent 未被触发

**解决:**
1. 确保请求涉及"研究"、"调研"、"搜索"等关键词
2. 检查主 Agent 的系统提示词
3. 查看 LangSmith tracing 日志

## 代码结构

```
backend/app/agent/
├── runtime.py              # 主 Agent 运行时
├── prompts.py              # 主 Agent 系统提示词
└── subagents/
    ├── __init__.py         # 导出所有 sub-agents
    ├── personal_data.py    # personal-data sub-agent
    └── deep_research.py    # deep-research sub-agent

backend/app/tools/
├── personal_tools.py       # 个人数据工具
└── research_tools.py       # 研究工具
```

## 扩展开发

### 添加新工具

在 `backend/app/tools/research_tools.py` 中添加：

```python
@tool
async def custom_research_tool(query: str) -> dict:
    """自定义研究工具"""
    # 实现逻辑
    pass
```

### 自定义提示词

修改 `backend/app/agent/subagents/deep_research.py` 中的 `DEEP_RESEARCH_PROMPT`

### 添加新的 Sub-Agent

1. 在 `backend/app/agent/subagents/` 创建新模块
2. 在 `backend/app/agent/subagents/__init__.py` 中导出
3. 在 `runtime.py` 中导入并添加到 subagents 列表
