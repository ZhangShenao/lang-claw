import type { ChatMessage, SessionSummary, StreamEvent } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchSessions(userId = "local-user"): Promise<SessionSummary[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/sessions?user_id=${encodeURIComponent(userId)}`,
    { cache: "no-store" },
  );
  if (!response.ok) {
    throw new Error("Failed to load sessions.");
  }
  return response.json();
}

export async function fetchMessages(sessionId: string): Promise<ChatMessage[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/sessions/${encodeURIComponent(sessionId)}/messages`,
    { cache: "no-store" },
  );
  if (!response.ok) {
    throw new Error("Failed to load messages.");
  }
  return response.json();
}

export async function streamChat(
  input: {
    message: string;
    sessionId?: string | null;
    userId?: string;
  },
  onEvent: (event: StreamEvent) => void,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: input.message,
      session_id: input.sessionId ?? null,
      user_id: input.userId ?? "local-user",
    }),
  });

  if (!response.ok || !response.body) {
    throw new Error("Failed to stream chat response.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";

    for (const part of parts) {
      const event = parseSseEvent(part);
      if (event) {
        onEvent(event);
      }
    }
  }

  if (buffer.trim()) {
    const event = parseSseEvent(buffer);
    if (event) {
      onEvent(event);
    }
  }
}

function parseSseEvent(chunk: string): StreamEvent | null {
  const lines = chunk.split("\n");
  const eventLine = lines.find((line) => line.startsWith("event:"));
  const dataLine = lines.find((line) => line.startsWith("data:"));
  if (!eventLine || !dataLine) {
    return null;
  }

  const event = eventLine.replace("event:", "").trim();
  const json = dataLine.replace("data:", "").trim();
  return {
    event: event as StreamEvent["event"],
    data: JSON.parse(json),
  } as StreamEvent;
}
