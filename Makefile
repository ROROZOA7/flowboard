.PHONY: help install dev agent frontend extension clean

help:
	@echo "Flowboard dev commands:"
	@echo "  make install    - install all deps (agent + frontend)"
	@echo "  make dev        - run agent + frontend concurrently"
	@echo "  make agent      - run agent only (FastAPI on :8100)"
	@echo "  make frontend   - run frontend only (Vite on :5173)"
	@echo "  make extension  - package extension (unpacked: load from ./extension)"
	@echo "  make clean      - remove build + cache"

install:
	cd agent && python -m venv .venv && .venv/bin/pip install -e .
	cd frontend && npm install

dev:
	@echo "Run 'make agent' and 'make frontend' in separate terminals."
	@echo "Load ./extension as unpacked extension in chrome://extensions."

agent:
	cd agent && .venv/bin/uvicorn flowboard.main:app --reload --port 8100

frontend:
	cd frontend && npm run dev

clean:
	rm -rf agent/.venv agent/**/__pycache__ frontend/node_modules frontend/dist
