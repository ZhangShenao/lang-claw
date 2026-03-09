# AGENTS

本仓库的目标是实现一个基于 LangChain 生态的 Web-only 个人助理 AI Agent。

## 核心技术栈

- Agent Core: `deepagents >= 0.4`
- Workflow / State: `langchain >= 1.0`, `langgraph >= 1.0`
- Model: `GLM-5`
- Backend: `Python 3.12 + uv + FastAPI`
- Frontend: `Next.js`
- Checkpoint / history: `MongoDB`
- Business DB: `PostgreSQL`
- Observability: `LangSmith`
- Deployment: `Docker Compose`

## 核心架构约束

- 仅支持 `Web Chat`，不实现多 Channel 接入
- Agent 模式采用 `Main Orchestrator + Sub-Agents`
- FastAPI 负责 API、流式输出和 Agent Runtime 编排
- MongoDB 仅用于 checkpoint 与会话状态持久化
- PostgreSQL 仅用于用户和业务结构化数据

## 实现原则

- 优先实现最小可运行版本，再逐步扩展工具和子 Agent
- 保持前后端边界清晰，避免把业务逻辑放入前端
- 工具、Agent、数据访问层分离
- 默认接入 LangSmith tracing

## 详细方案

完整技术方案见：[`docs/technical-solution.md`](docs/technical-solution.md)
