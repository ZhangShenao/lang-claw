export type SessionSummary = {
  session_id: string;
  title: string;
  last_message_preview: string;
  updated_at: string | null;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

export type StreamEvent =
  | { event: "session"; data: { session_id: string; thread_id: string; title: string } }
  | { event: "token"; data: { content: string } }
  | { event: "done"; data: { content: string } }
  | { event: "error"; data: { message: string } };
