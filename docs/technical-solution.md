# Lang Claw 技术方案

## 1. 项目定位

Lang Claw 是一个基于 LangChain 生态构建的个人助理 AI Agent，产品定位参考 OpenClaw，但只保留 Web Chat 场景下最核心的能力：

- 用户通过 Web 页面与 Agent 对话
- Agent 可以基于任务意图进行规划、调用工具、访问业务数据
- 系统保留完整会话上下文，并支持可观测性追踪

本项目不追求 OpenClaw 的多渠道接入和 Gateway 中台能力，优先实现一个架构清晰、易于扩展的 Web-only 版本。

## 2. 设计目标

- 技术栈统一且现代化，避免混合多套运行时
- 以 LangChain v1 / LangGraph v1 / deepagents v0.4+ 为核心
- 优先保证可维护性、可观测性和后续扩展能力
- 先实现单入口，再逐步扩展工具与业务能力

## 3. 核心技术选型

### 3.1 Agent Core

- `deepagents >= 0.4`
- `langchain >= 1.0`
- `langgraph >= 1.0`

选择理由：

- deepagents 适合任务规划、工具调用、子 Agent 调度
- 能与 LangGraph 的持久化和状态管理机制自然结合
- 与 LangSmith 的 tracing 链路兼容性较好

### 3.2 模型层

- 主模型：`GLM-5`
- 接入方式：优先通过智谱 OpenAI-compatible API 适配 `langchain_openai.ChatOpenAI`

选择理由：

- 更贴合 LangChain v1 当前主流模型接入方式
- 便于使用 tool calling、streaming 和统一模型抽象

### 3.3 后端

- `Python 3.12`
- `uv` 作为依赖管理和运行工具
- `FastAPI` 作为 Web 服务框架

选择理由：

- 适合构建异步 Agent Runtime 和流式接口
- uv 在依赖解析、锁文件和执行效率上更适合新项目

### 3.4 前端

- `Next.js`

范围限定：

- 只实现核心聊天页
- 支持会话列表、消息渲染、流式响应
- 样式简洁，不做重型控制台

### 3.5 数据与持久化

- `MongoDB`：LangGraph Checkpointer / 会话状态 / 历史交互持久化
- `PostgreSQL`：用户、配置、业务实体、任务记录等结构化数据

### 3.6 可观测性

- `LangSmith`

集成目标：

- 自动 tracing
- Agent / tool / sub-agent 执行链路可视化
- 方便定位响应异常、工具失败和上下文膨胀问题

### 3.7 部署

- `Docker Compose`
- 一键部署脚本负责 build + up + 初始化

## 4. 系统架构设计

系统采用四层架构：

```text
Next.js Web UI
    |
    | HTTP / SSE
    v
FastAPI Backend
    |
    | invoke / stream / session APIs
    v
DeepAgents Runtime
    |-- GLM-5
    |-- Tools
    |-- Sub-Agents
    |-- MongoDB Checkpointer
    |-- PostgreSQL Repositories
    |-- LangSmith Tracing
    v
MongoDB + PostgreSQL
```

### 4.1 前端职责

- 用户发起消息
- 展示流式响应
- 展示历史会话
- 管理当前会话上下文

前端不直接承担 Agent 编排逻辑，只做展示和交互。

### 4.2 后端职责

- 提供聊天接口和会话接口
- 处理鉴权、请求校验、SSE 输出
- 管理 Agent Runtime 生命周期
- 串联 PostgreSQL、MongoDB 和 LangSmith

### 4.3 Agent Runtime 职责

- 解析用户意图
- 决定是否调用工具或委派子 Agent
- 汇总子任务结果并生成最终答复
- 持久化本轮执行上下文

## 5. Agent 模式选择

推荐模式：`Sub-Agent`

### 5.1 为什么不是 SingleAgent

SingleAgent 在最初实现时最简单，但一旦工具和场景增多，会出现这些问题：

- system prompt 持续膨胀
- 工具选择不稳定
- 上下文难以管理
- 业务边界不清晰

### 5.2 为什么不是重型 Multi-Agent

Peer-to-peer 的 Multi-Agent 适合复杂协同，但对当前项目而言成本过高：

- 推理链路更长
- 追踪与调试更复杂
- 响应延迟和 token 成本更高

### 5.3 为什么选择 Sub-Agent

`主控 Agent + 专长子 Agent` 可以在复杂度和扩展性之间取得平衡：

- 主控 Agent 负责总体规划与路由
- 子 Agent 封装特定领域能力
- 更利于控制 prompt 范围和工具集合
- 对 LangSmith trace 更友好

### 5.4 建议的 Agent 划分

#### Main Orchestrator Agent

负责：

- 识别任务类型
- 规划步骤
- 选择工具或子 Agent
- 汇总结果并输出用户可读答案

#### Research Sub-Agent

负责：

- 外部知识检索
- 资料整理和总结

#### Personal Data Sub-Agent

负责：

- 读写用户资料
- 查询结构化业务数据
- 与 PostgreSQL Repository 协同工作

#### Action Sub-Agent

负责：

- 执行未来扩展的自动化动作
- 封装外部系统调用

第一阶段可以只实现 `Main Orchestrator Agent + Personal Data Sub-Agent`，Research 和 Action 后续补充。

## 6. 核心模块划分

建议后端按如下模块拆分：

```text
backend/
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   ├── sessions.py
│   │   └── health.py
│   ├── agent/
│   │   ├── runtime.py
│   │   ├── tool_registry.py
│   │   ├── prompts/
│   │   └── subagents/
│   ├── tools/
│   ├── memory/
│   ├── db/
│   ├── observability/
│   └── core/
└── pyproject.toml
```

### 6.1 API 层

- `chat.py`：聊天请求、流式输出
- `sessions.py`：会话查询、会话创建、消息历史
- `health.py`：存活与依赖检查

### 6.2 Agent 层

- `runtime.py`：初始化 deepagents Runtime
- `subagents/`：定义各子 Agent
- `prompts/`：系统提示词模板
- `tool_registry.py`：统一注册工具和可见范围

### 6.3 Tools 层

示例：

- `profile_tools.py`
- `task_tools.py`
- `postgres_tools.py`
- `web_search_tools.py`

原则：

- 工具逻辑与 Agent 编排分离
- 每个工具聚焦单一职责
- 工具输出必须结构化，方便 trace 和调试

### 6.4 Memory 层

- 初始化 MongoDB Checkpointer
- 管理 thread_id / session_id 映射
- 将执行历史转换为前端可展示的消息结构

### 6.5 DB 层

- PostgreSQL ORM / SQL 层
- Repository 封装
- 业务模型定义

### 6.6 Observability 层

- LangSmith 配置
- Trace metadata 注入
- 环境开关与项目名管理

## 7. 数据设计原则

### 7.1 MongoDB

用于：

- LangGraph checkpoint
- Agent 线程状态
- 消息运行时历史

MongoDB 重点服务于“对话执行过程的恢复与持久化”，不是所有业务数据的主库。

### 7.2 PostgreSQL

用于：

- 用户信息
- 用户偏好配置
- 业务实体
- 任务、操作记录、结构化知识

建议最初至少包含以下实体：

- `users`
- `agent_sessions`
- `user_profiles`
- `tasks`
- `task_events`

## 8. 请求处理流程

典型聊天链路如下：

1. 用户在 Next.js 页面发送消息
2. 前端调用 FastAPI 聊天接口
3. FastAPI 解析会话信息并加载 Agent Runtime
4. Runtime 从 MongoDB Checkpointer 恢复线程上下文
5. Main Agent 判断是否需要调用工具或委派子 Agent
6. 工具访问 PostgreSQL 或外部能力
7. 结果回传给 Main Agent 汇总
8. 生成最终回复并流式返回前端
9. 本轮执行 trace 自动上报到 LangSmith
10. checkpoint 写回 MongoDB

## 9. 前端方案

前端第一阶段保持简单：

- 单聊天页
- 左侧会话列表
- 中间消息区
- 底部输入框
- 支持 token streaming

交互协议建议：

- 普通查询接口：HTTP JSON
- 聊天输出：`SSE`

不优先使用 WebSocket，原因是当前仅需单向流式输出，SSE 更轻量、实现更简单。

## 10. 可观测性方案

LangSmith 作为默认 tracing 平台：

- 为每次会话设置 `session_id`
- 为每次 Agent 调用打上 `user_id`、`thread_id`、`environment` 等 metadata
- 对 tool call、sub-agent call、异常节点统一采集

这样可以快速回答几个关键问题：

- 哪一步耗时最长
- 哪个工具最常失败
- 哪类请求最容易导致上下文膨胀

## 11. 部署方案

建议由以下服务构成：

- `frontend`
- `backend`
- `postgres`
- `mongo`

Compose 层职责：

- 编排服务网络
- 注入环境变量
- 挂载必要卷
- 管理数据库端口和服务依赖

建议额外提供：

- `scripts/deploy.sh`

脚本职责：

1. 校验环境变量
2. 执行镜像构建
3. 启动容器
4. 执行数据库初始化或迁移
5. 输出访问地址和健康检查状态

## 12. 建设顺序建议

### Phase 1: 最小可运行版本

- FastAPI 后端骨架
- Next.js 聊天页
- GLM-5 接入
- deepagents 主控 Agent
- MongoDB Checkpointer
- PostgreSQL 基础表
- LangSmith tracing
- Docker Compose 启动

### Phase 2: 业务能力增强

- Personal Data Sub-Agent
- 用户偏好与任务管理工具
- 会话列表与历史回放

### Phase 3: 扩展能力

- Research Sub-Agent
- Action Sub-Agent
- 更丰富的业务工具
- 更细粒度的权限和配置管理

## 13. 最终结论

这套方案的关键点有三条：

- 架构上坚持 Web-only，不引入 OpenClaw 式多通道 Gateway 复杂度
- Agent Core 选择 `Sub-Agent` 模式，平衡可维护性与扩展性
- 数据层明确分工：`MongoDB` 负责 checkpoint，`PostgreSQL` 负责业务数据

这样可以先快速做出一个工程上稳健的 MVP，再逐步向更强的个人助理能力演进。
