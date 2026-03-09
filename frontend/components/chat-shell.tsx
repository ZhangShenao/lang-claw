"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { fetchMessages, fetchSessions, streamChat } from "../lib/api";
import type { ChatMessage, SessionSummary, StreamEvent } from "../lib/types";

function makeLocalMessage(role: "user" | "assistant", content: string): ChatMessage {
  return {
    id: `${role}-${crypto.randomUUID()}`,
    role,
    content,
    created_at: new Date().toISOString(),
  };
}

export function ChatShell() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [sidebarError, setSidebarError] = useState<string | null>(null);

  useEffect(() => {
    void loadSessions();
  }, []);

  useEffect(() => {
    if (!activeSessionId) {
      setMessages([]);
      return;
    }
    void loadMessages(activeSessionId);
  }, [activeSessionId]);

  const activeSession = useMemo(
    () => sessions.find((session) => session.session_id === activeSessionId) ?? null,
    [activeSessionId, sessions],
  );

  async function loadSessions() {
    setLoading(true);
    setSidebarError(null);
    try {
      const data = await fetchSessions();
      setSessions(data);
      if (!activeSessionId && data.length > 0) {
        setActiveSessionId(data[0].session_id);
      }
    } catch (error) {
      setSidebarError(error instanceof Error ? error.message : "加载会话失败。");
    } finally {
      setLoading(false);
    }
  }

  async function loadMessages(sessionId: string) {
    try {
      const data = await fetchMessages(sessionId);
      setMessages(data);
    } catch (error) {
      setMessages([
        makeLocalMessage(
          "assistant",
          error instanceof Error ? error.message : "加载消息失败。",
        ),
      ]);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = draft.trim();
    if (!value || sending) {
      return;
    }

    setDraft("");
    setSending(true);

    const userMessage = makeLocalMessage("user", value);
    const assistantMessage = makeLocalMessage("assistant", "");
    setMessages((current) => [...current, userMessage, assistantMessage]);

    let pendingSessionId = activeSessionId;

    try {
      await streamChat(
        {
          message: value,
          sessionId: activeSessionId,
        },
        (streamEvent) => {
          handleStreamEvent(streamEvent, assistantMessage.id, pendingSessionId, value);
          if (streamEvent.event === "session") {
            pendingSessionId = streamEvent.data.session_id;
          }
        },
      );
      await loadSessions();
      if (pendingSessionId) {
        setActiveSessionId(pendingSessionId);
      }
    } catch (error) {
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantMessage.id
            ? {
                ...message,
                content:
                  error instanceof Error ? error.message : "Streaming failed unexpectedly.",
              }
            : message,
        ),
      );
    } finally {
      setSending(false);
    }
  }

  function handleStreamEvent(
    streamEvent: StreamEvent,
    assistantMessageId: string,
    pendingSessionId: string | null,
    userMessage: string,
  ) {
    if (streamEvent.event === "session") {
      setActiveSessionId(streamEvent.data.session_id);
      setSessions((current) => {
        const next = current.filter(
          (session) => session.session_id !== streamEvent.data.session_id,
        );
        return [
          {
            session_id: streamEvent.data.session_id,
            title: streamEvent.data.title || userMessage.slice(0, 60),
            last_message_preview: userMessage,
            updated_at: new Date().toISOString(),
          },
          ...next,
        ];
      });
      return;
    }

    if (streamEvent.event === "token") {
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantMessageId
            ? { ...message, content: message.content + streamEvent.data.content }
            : message,
        ),
      );
      return;
    }

    if (streamEvent.event === "done") {
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantMessageId
            ? { ...message, content: streamEvent.data.content }
            : message,
        ),
      );
      if (pendingSessionId) {
        setSessions((current) =>
          current.map((session) =>
            session.session_id === pendingSessionId
              ? {
                  ...session,
                  last_message_preview: streamEvent.data.content,
                  updated_at: new Date().toISOString(),
                }
              : session,
          ),
        );
      }
      return;
    }

    setMessages((current) =>
      current.map((message) =>
        message.id === assistantMessageId
          ? { ...message, content: streamEvent.data.message }
          : message,
      ),
    );
  }

  function handleNewSession() {
    setActiveSessionId(null);
    setMessages([]);
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <h1>Lang Claw</h1>
          <p>基于 LangChain 生态的个人助理 Web Agent</p>
        </div>
        <button className="new-session" type="button" onClick={handleNewSession}>
          新建对话
        </button>
        <div className="session-list">
          {loading ? <span>加载会话中...</span> : null}
          {!loading && sidebarError ? <span>{sidebarError}</span> : null}
          {!loading && sessions.length === 0 ? <span>还没有历史会话。</span> : null}
          {sessions.map((session) => (
            <button
              key={session.session_id}
              type="button"
              className={`session-item ${
                session.session_id === activeSessionId ? "active" : ""
              }`}
              onClick={() => setActiveSessionId(session.session_id)}
            >
              <strong>{session.title}</strong>
              <span>{session.last_message_preview || "暂无摘要"}</span>
            </button>
          ))}
        </div>
      </aside>

      <section className="panel">
        <header className="panel-header">
          <div>
            <h2>{activeSession?.title ?? "新的会话"}</h2>
            <p>GLM-5 + deepagents + FastAPI + Next.js</p>
          </div>
          <p>{sending ? "Agent 正在回复..." : "系统已就绪"}</p>
        </header>

        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div>
                <strong>可以先让它帮你管理任务、记录偏好或回答问题。</strong>
                <p>例如：记住我偏好英文技术文档，或者帮我创建一个明天下午的提醒任务。</p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <article
                key={message.id}
                className={`message ${message.role === "user" ? "user" : "assistant"}`}
              >
                {message.content || (message.role === "assistant" ? "..." : "")}
              </article>
            ))
          )}
        </div>

        <div className="composer">
          <form onSubmit={handleSubmit}>
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="输入消息，例如：帮我创建一个任务，标题是准备技术方案评审。"
            />
            <button type="submit" disabled={!draft.trim() || sending}>
              {sending ? "发送中..." : "发送"}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
