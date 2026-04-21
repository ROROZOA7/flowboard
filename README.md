# Flowboard

Personal infinite-canvas workspace for AI media workflows. Drop characters, generate images from refs, generate videos from images — all on a single board. Chat with an LLM to plan pipelines that stream nodes/edges onto the canvas in realtime.

Local-only, single-user. No auth, no cloud, no collab.

## Architecture

```
[React Canvas]  ─HTTP/WS─►  [FastAPI Agent + SQLite]
                                     ▲
                                     │ WebSocket :9222
                                     ▼
                           [Chrome MV3 Extension]
                                     │
                                     ▼
                               labs.google
```

## Layout

- `agent/`     — FastAPI + SQLModel + SQLite. Extension WS bridge + REST API.
- `frontend/`  — Vite + React + TS + React Flow + Zustand canvas.
- `extension/` — Chrome MV3 extension (token capture, API proxy).
- `docs/`      — Plan + design notes.
- `storage/`   — Local asset cache (gitignored).

## Dev

```
make install
make agent       # terminal 1
make frontend    # terminal 2
```

Load `./extension` as an unpacked extension at `chrome://extensions`.

See `docs/PLAN.md` for the full MVP + roadmap.
