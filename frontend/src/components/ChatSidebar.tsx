export function ChatSidebar() {
  return (
    <aside className="sidebar">
      <h2>Chat</h2>
      <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.5 }}>
        Chat planner ships in Phase 4. You'll describe intent here and the LLM
        will stream a pipeline of nodes and edges onto the canvas in realtime.
      </p>
      <p style={{ fontSize: 13, color: "var(--muted)", lineHeight: 1.5 }}>
        Mention a node with <code>#shortId</code> to feed it into the prompt
        context.
      </p>
    </aside>
  );
}
