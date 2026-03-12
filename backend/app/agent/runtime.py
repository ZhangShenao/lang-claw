"""Agent runtime."""

import json
from collections.abc import AsyncIterator
from typing import Any

from deepagents import create_deep_agent
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_openai import ChatOpenAI

from app.agent.prompts import MAIN_SYSTEM_PROMPT
from app.agent.subagents import build_deep_research_agent, build_personal_data_agent
from app.core.config import Settings
from app.observability.langsmith import build_run_config


class AgentRuntime:
    def __init__(self, *, settings: Settings, checkpointer: Any):
        self.settings = settings
        self.checkpointer = checkpointer

    def _build_model(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.settings.llm_model,
            api_key=self.settings.zhipu_api_key,
            base_url=self.settings.zhipu_base_url,
            temperature=self.settings.llm_temperature,
        )

    def _build_agent(self, user_id: str):
        # Build sub-agents
        personal_data_agent = build_personal_data_agent(user_id)
        deep_research_agent = build_deep_research_agent()

        # Main agent can use personal tools directly for convenience
        all_tools = personal_data_agent["tools"]

        return create_deep_agent(
            model=self._build_model(),
            tools=all_tools,
            subagents=[personal_data_agent, deep_research_agent],
            system_prompt=MAIN_SYSTEM_PROMPT,
            checkpointer=self.checkpointer,
        )

    async def astream_reply(
        self,
        *,
        user_id: str,
        session_id: str,
        thread_id: str,
        message: str,
    ) -> AsyncIterator[str]:
        agent = self._build_agent(user_id)
        payload = {"messages": [{"role": "user", "content": message}]}
        run_config = build_run_config(
            thread_id=thread_id,
            user_id=user_id,
            session_id=session_id,
            model_name=self.settings.llm_model,
        )

        streamed_any = False
        try:
            async for item in agent.astream(
                payload,
                config=run_config,
                stream_mode="messages",
            ):
                text = self._extract_stream_text(item)
                if text:
                    streamed_any = True
                    yield text
        except Exception:
            if streamed_any:
                raise
            result = await agent.ainvoke(payload, config=run_config)
            text = self._extract_final_text(result)
            if text:
                yield text

    def _extract_stream_text(self, item: Any) -> str:
        message: Any = item
        if isinstance(item, tuple) and item:
            message = item[0]
        if isinstance(message, AIMessageChunk):
            return self._content_to_text(message.content)
        if isinstance(message, AIMessage):
            return self._content_to_text(message.content)
        if isinstance(message, BaseMessage):
            return self._content_to_text(message.content)
        return ""

    def _extract_final_text(self, result: Any) -> str:
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            if messages:
                return self._content_to_text(messages[-1].content)
        if isinstance(result, BaseMessage):
            return self._content_to_text(result.content)
        if isinstance(result, str):
            return result
        try:
            return json.dumps(result, ensure_ascii=False)
        except TypeError:
            return str(result)

    def _content_to_text(self, content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if text:
                        parts.append(text)
            return "".join(parts)
        return str(content)
