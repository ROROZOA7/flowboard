// Flowboard Bridge service worker.
// Phase 0: opens a WebSocket to the local agent and echoes back.
// Phase 2 will handle `api_request` by proxying fetches to labs.google with
// captured auth tokens + reCAPTCHA tokens.

const AGENT_WS_URL = "ws://localhost:8100/ws/extension";
const RECONNECT_BASE_MS = 1000;
const RECONNECT_MAX_MS = 15000;

let ws = null;
let reconnectDelay = RECONNECT_BASE_MS;

function connect() {
  try {
    ws = new WebSocket(AGENT_WS_URL);
  } catch (err) {
    scheduleReconnect();
    return;
  }

  ws.addEventListener("open", () => {
    reconnectDelay = RECONNECT_BASE_MS;
    console.log("[flowboard] connected to agent");
  });

  ws.addEventListener("message", async (ev) => {
    let msg;
    try {
      msg = JSON.parse(ev.data);
    } catch {
      return;
    }
    const { id, method, params } = msg;
    if (!id) return;

    const result = await dispatch(method, params);
    ws.send(JSON.stringify({ id, result }));
  });

  ws.addEventListener("close", () => {
    ws = null;
    scheduleReconnect();
  });
  ws.addEventListener("error", () => {
    try { ws.close(); } catch {}
  });
}

function scheduleReconnect() {
  setTimeout(connect, reconnectDelay);
  reconnectDelay = Math.min(reconnectDelay * 2, RECONNECT_MAX_MS);
}

async function dispatch(method, params) {
  // Phase 2 will wire real handlers here.
  if (method === "ping") return { ok: true, ts: Date.now() };
  if (method === "api_request") {
    return { error: "not_implemented" };
  }
  return { error: `unknown_method:${method}` };
}

connect();
