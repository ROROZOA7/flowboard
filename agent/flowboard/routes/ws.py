"""WebSocket endpoints: extension bridge + per-board client stream."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from flowboard.services.events import board_bus
from flowboard.services.flow_client import flow_client

router = APIRouter()


@router.websocket("/ws/extension")
async def extension_bridge(ws: WebSocket) -> None:
    await ws.accept()
    flow_client.set_extension(ws)
    try:
        while True:
            msg = await ws.receive_text()
            await flow_client.handle_message(msg)
    except WebSocketDisconnect:
        pass
    finally:
        flow_client.clear_extension()


@router.websocket("/ws/board/{board_id}")
async def board_stream(ws: WebSocket, board_id: int) -> None:
    await ws.accept()
    q = board_bus.subscribe(board_id)
    try:
        while True:
            payload = await q.get()
            await ws.send_json(payload)
    except WebSocketDisconnect:
        pass
    finally:
        board_bus.unsubscribe(board_id, q)
