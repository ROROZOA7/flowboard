"""Bridge to the Chrome MV3 extension over WebSocket.

Mirrors flowkit's flow_client pattern: requests are JSON with an id, responses
are correlated back via asyncio futures stored in `_pending`.

Skeleton only in Phase 0 — wiring arrives in Phase 2.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any, Optional


class FlowClient:
    def __init__(self) -> None:
        self._ws: Optional[Any] = None
        self._pending: dict[str, asyncio.Future] = {}

    @property
    def connected(self) -> bool:
        return self._ws is not None

    def set_extension(self, ws: Any) -> None:
        self._ws = ws

    def clear_extension(self) -> None:
        self._ws = None
        for fut in self._pending.values():
            if not fut.done():
                fut.set_exception(ConnectionError("extension disconnected"))
        self._pending.clear()

    async def handle_message(self, raw: str) -> None:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            return
        req_id = msg.get("id")
        if not req_id:
            return
        fut = self._pending.pop(req_id, None)
        if fut and not fut.done():
            fut.set_result(msg.get("result", msg))

    async def _send(self, method: str, params: dict, timeout: float = 120.0) -> dict:
        if not self.connected:
            return {"error": "extension_disconnected"}
        req_id = str(uuid.uuid4())
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[req_id] = fut
        payload = {"id": req_id, "method": method, "params": params}
        try:
            await self._ws.send_text(json.dumps(payload))
            return await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(req_id, None)
            return {"error": "timeout"}
        except Exception as exc:
            self._pending.pop(req_id, None)
            return {"error": str(exc)}

    async def api_request(self, url: str, method: str, headers: dict, body: Any) -> dict:
        return await self._send(
            "api_request",
            {"url": url, "method": method, "headers": headers, "body": body},
        )


flow_client = FlowClient()
