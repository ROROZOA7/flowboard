"""AI-vision brief generation for cached media.

Asks Claude (via the local CLI) to summarise an image into a short factual
description ("aiBrief"). Used by:
- Visual asset / character nodes — annotate uploaded or generated images
- Auto-prompt synthesizer — feed those briefs into a downstream prompt

The CLI handles auth via the user's existing Claude subscription, so we don't
need to manage API keys here. We always pass an ABSOLUTE path so the CLI's
cwd doesn't matter.
"""
from __future__ import annotations

import logging

from flowboard.services import claude_cli, media as media_service

logger = logging.getLogger(__name__)

# Keep briefs short — they get spliced into downstream prompts. 200 chars
# is enough for "white cotton crewneck t-shirt with small heart logo" or
# "young Korean woman, neutral expression, dark hair tied back, dark top".
_VISION_SYSTEM = (
    "You are a visual asset annotator for a fashion / e-commerce media "
    "pipeline. Output one short factual sentence (max 200 characters) that "
    "describes the image. Focus on attributes useful for image generation: "
    "for a product → colour, material, design, fit, style; for a person → "
    "gender, apparent ethnicity, age range, expression, hair, outfit. No "
    "marketing language, no opinions, no preamble — just the description."
)

_VISION_USER_PROMPT = "Describe this image."


class VisionError(RuntimeError):
    pass


async def describe_media(media_id: str) -> str:
    """Return a short factual description of the cached media.

    Raises ``VisionError`` if the media is not cached locally or if the
    Claude CLI fails. Caller decides whether to retry or fall back.
    """
    media_id = media_service.normalize_media_id(media_id)
    if not media_service.is_valid_media_id(media_id):
        raise VisionError("invalid media_id")

    cached = media_service.cached_path(media_id)
    if cached is None:
        # Try to fetch from the stored URL once before giving up. Vision
        # makes no sense without bytes.
        result = await media_service.fetch_and_cache(media_id)
        if result is None:
            raise VisionError("media not cached and could not be fetched")
        _bytes, _mime, path = result
        cached = path

    try:
        text = await claude_cli.run_claude(
            _VISION_USER_PROMPT,
            system_prompt=_VISION_SYSTEM,
            attachments=[str(cached.resolve())],
            timeout=45.0,
        )
    except claude_cli.ClaudeCliError as exc:
        raise VisionError(f"claude CLI failed: {exc}") from exc

    # Trim and cap — defence-in-depth in case the model ignores the length
    # cap from the system prompt.
    text = (text or "").strip()
    if not text:
        raise VisionError("empty response from claude")
    if len(text) > 400:
        text = text[:400].rstrip() + "…"
    return text
