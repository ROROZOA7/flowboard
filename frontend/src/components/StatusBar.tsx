import { useEffect, useState } from "react";
import { getHealth } from "../api/client";

export function StatusBar() {
  const [connected, setConnected] = useState<boolean | null>(null);
  const [agentOk, setAgentOk] = useState(false);

  useEffect(() => {
    let alive = true;
    const poll = async () => {
      try {
        const h = await getHealth();
        if (!alive) return;
        setAgentOk(h.ok);
        setConnected(h.extension_connected);
      } catch {
        if (!alive) return;
        setAgentOk(false);
        setConnected(null);
      }
    };
    poll();
    const t = setInterval(poll, 3000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const agentLabel = agentOk ? "● agent" : "○ agent";
  const extLabel =
    connected === null ? "? extension" : connected ? "● extension" : "○ extension";

  return (
    <div className="statusbar">
      <span style={{ color: agentOk ? "#6ee7b7" : "#ef4444" }}>{agentLabel}</span>
      <span style={{ margin: "0 8px", opacity: 0.4 }}>|</span>
      <span style={{ color: connected ? "#6ee7b7" : "#8a8f99" }}>{extLabel}</span>
    </div>
  );
}
