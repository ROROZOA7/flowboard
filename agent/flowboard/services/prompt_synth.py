"""Auto-prompt synthesizer.

Given a target node, walks the immediate-upstream graph, collects
``aiBrief`` text from each parent node, and asks Claude to compose a single
image-generation prompt that combines them. Used when the user clicks
Generate without typing a prompt.
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlmodel import select

from flowboard.db import get_session
from flowboard.db.models import Edge, Node
from flowboard.services import claude_cli

logger = logging.getLogger(__name__)


_SYNTH_SYSTEM_IMAGE = (
    "You are an image-generation prompt builder for a fashion / e-commerce "
    "media pipeline. Given a list of source briefs (people and/or "
    "products), produce ONE concise sentence (max 220 chars) describing a "
    "photo that combines them. Style: photorealistic fashion product "
    "photography, sharp focus, soft natural light, neutral indoor "
    "background unless the user notes say otherwise. No marketing "
    "language, no preamble — output the prompt only."
)

_SYNTH_SYSTEM_VIDEO = (
    "You are a video-motion prompt builder for an image-to-video pipeline "
    "(5-8 second clip, Veo-style). Given the brief of the source still, "
    "produce ONE concise motion sentence (max 200 chars) describing "
    "subtle, natural movement: slow camera dolly-in or pan, gentle subject "
    "shift, micro-expressions for a person, soft fabric/light play for a "
    "product. No scene cuts, no dialogue, no text overlays. Output the "
    "motion prompt only — no preamble."
)


class PromptSynthError(RuntimeError):
    pass


def _collect_upstream(node_id: int) -> tuple[list[dict], Optional[Node]]:
    """Return (upstream_brief_records, target_node).

    Each record: {type, brief, prompt, has_media}.
    """
    with get_session() as s:
        target = s.get(Node, node_id)
        if target is None:
            return [], None
        edges = s.exec(select(Edge).where(Edge.target_id == node_id)).all()
        upstream_ids = [e.source_id for e in edges]
        records: list[dict] = []
        for uid in upstream_ids:
            n = s.get(Node, uid)
            if n is None:
                continue
            data = n.data or {}
            brief = data.get("aiBrief")
            records.append(
                {
                    "type": n.type,
                    "shortId": n.short_id,
                    "brief": brief if isinstance(brief, str) else None,
                    "prompt": data.get("prompt") if isinstance(data.get("prompt"), str) else None,
                    "title": data.get("title") if isinstance(data.get("title"), str) else None,
                    "has_media": bool(isinstance(data.get("mediaId"), str) and data.get("mediaId")),
                }
            )
        return records, target


def _format_user_message(records: list[dict], target: Node) -> str:
    """Render the upstream context into a compact prompt for the LLM."""
    by_type: dict[str, list[str]] = {}
    for r in records:
        # Prefer the AI-generated brief; fall back to the user-typed prompt
        # or title so a node with no brief still contributes something.
        text = r["brief"] or r["prompt"] or r["title"] or "(no description)"
        by_type.setdefault(r["type"], []).append(f"#{r['shortId']}: {text}")

    parts: list[str] = []
    if by_type.get("character"):
        parts.append("Subject(s) (character):\n  - " + "\n  - ".join(by_type["character"]))
    if by_type.get("visual_asset"):
        parts.append(
            "Product / wardrobe / object (visual_asset):\n  - "
            + "\n  - ".join(by_type["visual_asset"])
        )
    if by_type.get("image"):
        parts.append("Reference image(s):\n  - " + "\n  - ".join(by_type["image"]))
    target_data = target.data or {}
    target_title = target_data.get("title") if isinstance(target_data.get("title"), str) else None
    if target_title:
        parts.append(f"Target node title (hint): {target_title}")

    if not parts:
        # No upstream context — fall back to the node title alone.
        return f"Target: {target_title or 'image'}\n\nWrite a generic photoreal product or scene prompt."
    return "\n\n".join(parts) + "\n\nReturn only the prompt sentence."


async def auto_prompt(node_id: int) -> str:
    """Compose a generation prompt by walking upstream + asking Claude.

    Branch by target type:
    - ``image`` (or anything else default) → photorealistic composition prompt
      that combines all upstream briefs.
    - ``video`` → motion/camera prompt for the single source image brief
      (i2v has exactly one upstream image — multi-ref isn't a thing).
    """
    records, target = _collect_upstream(node_id)
    if target is None:
        raise PromptSynthError(f"node {node_id} not found")

    is_video = target.type == "video"
    system_prompt = _SYNTH_SYSTEM_VIDEO if is_video else _SYNTH_SYSTEM_IMAGE
    user_msg = _format_user_message(records, target)

    try:
        text = await claude_cli.run_claude(
            user_msg,
            system_prompt=system_prompt,
            timeout=30.0,
        )
    except claude_cli.ClaudeCliError as exc:
        raise PromptSynthError(f"claude CLI failed: {exc}") from exc

    text = (text or "").strip().strip('"').strip("'")
    if not text:
        raise PromptSynthError("empty response from claude")
    if len(text) > 500:
        text = text[:500].rstrip() + "…"
    return text
