from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from flowboard.db import init_db
from flowboard.routes import boards, ws
from flowboard.services.flow_client import flow_client

app = FastAPI(title="Flowboard Agent", version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(boards.router)
app.include_router(ws.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "extension_connected": flow_client.connected,
    }
