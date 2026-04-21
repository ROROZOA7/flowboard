# Flowboard Bridge (Chrome MV3)

Local-only extension that proxies Flowboard agent requests to authenticated
web sessions (labs.google, etc).

## Install

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Click **Load unpacked** and select this folder.

The service worker auto-connects to `ws://localhost:8100/ws/extension` when the
agent is running.

## Status

Phase 0: connection + reconnect loop only. Phase 2 will add token capture,
reCAPTCHA, and the `api_request` proxy.
