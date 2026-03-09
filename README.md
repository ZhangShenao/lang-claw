# Lang Claw

基于 LangChain 生态实现的个人助理 AI Agent，目标是构建一个仅支持 Web Chat 的轻量级 OpenClaw 风格系统。

## 项目目标

- 基于 `deepagents >= 0.4` 构建 Agent Core
- 使用 `GLM-5` 作为主模型
- 后端采用 `Python 3.12 + uv + FastAPI`
- 前端采用 `Next.js`
- 使用 `MongoDB` 作为 Checkpointer 持久化会话状态与交互历史
- 使用 `PostgreSQL` 存储用户与业务数据
- 集成 `LangSmith` 实现 Tracing 与可观测性
- 通过 `Docker Compose` 提供一键构建与部署

## 当前范围

当前版本仅支持：

- Web 聊天入口
- 会话历史持久化
- 面向个人助理场景的 Agent 调度与工具调用

当前版本不包含：

- 多 Channel 接入
- 复杂的 Gateway 中台
- OpenClaw 全量能力复刻

## 架构摘要

系统采用四层设计：

1. `Next.js` Web Chat 前端
2. `FastAPI` 应用服务层
3. 基于 `deepagents` 的 Agent Runtime
4. `MongoDB + PostgreSQL` 数据层

Agent Core 采用 `主控 Agent + 专长 Sub-Agent` 的模式，而不是单纯 `SingleAgent` 或复杂 `Multi-Agent`。

## 文档

- 详细技术方案：[`docs/technical-solution.md`](docs/technical-solution.md)
- 项目执行约束：[`AGENTS.md`](AGENTS.md)

## 当前目录结构

```text
.
├── AGENTS.md
├── README.md
├── .env.example
├── docker-compose.yml
├── backend/
├── frontend/
├── docs/
│   └── technical-solution.md
└── scripts/
    └── deploy.sh
```

## 快速开始

1. 复制环境变量模板：`cp .env.example .env`
2. 填写 `ZHIPU_API_KEY`，可选填写 `LANGSMITH_API_KEY`
3. 一键部署：`./scripts/deploy.sh`

如需本地分别启动：

- 后端：`cd backend && uv sync && uv run uvicorn app.main:app --reload`
- 前端：`cd frontend && npm install && npm run dev`

## 状态

当前仓库已完成第一版工程骨架：

- FastAPI 后端基础服务
- deepagents Runtime 集成
- MongoDB / PostgreSQL 适配层
- Next.js Web Chat 页面
- Docker Compose 和部署脚本

下一步重点是补充更完整的工具集、用户体系和业务能力。
