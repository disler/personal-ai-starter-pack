import base64
import os
from typing import Optional

import requests

from modules.constants import (
    SIXTYDB_BASE_URL,
    SIXTYDB_DEFAULT_OUTPUT_FORMAT,
)


def generate_tts_bytes(
    text: str,
    api_key: Optional[str] = None,
    voice_id: Optional[str] = None,
    output_format: str = SIXTYDB_DEFAULT_OUTPUT_FORMAT,
    enhance: bool = True,
    speed: float = 1.0,
    stability: int = 50,
    similarity: int = 75,
    timeout: int = 60,
) -> bytes:
    """
    Call 60db's non-streaming TTS endpoint (POST /tts-synthesize) and return
    decoded audio bytes.

    This mirrors the ElevenLabs `generate()` -> bytes flow so the result can be
    handed straight to `elevenlabs.play()`. Unlike ElevenLabs (which streams raw
    audio bytes), 60db responds with JSON containing a base64 `audio_base64`
    field, so we decode it here to keep the rest of the pipeline identical.

    Pass voice_id=None to use the 60db system default voice.
    """
    api_key = api_key or os.getenv("SIXTYDB_API_KEY")
    if not api_key:
        raise ValueError("Missing 60db API key. Set SIXTYDB_API_KEY in your .env.")

    payload = {
        "text": text,
        "enhance": enhance,
        "speed": speed,
        "stability": stability,
        "similarity": similarity,
        "output_format": output_format,
    }
    # Omit voice_id entirely to fall back to the 60db system default voice.
    if voice_id:
        payload["voice_id"] = voice_id

    response = requests.post(
        f"{SIXTYDB_BASE_URL}/tts-synthesize",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()

    data = response.json()
    if not data.get("success", False):
        raise RuntimeError(f"60db TTS failed: {data.get('message', 'unknown error')}")

    audio_base64 = data.get("audio_base64")
    if not audio_base64:
        raise RuntimeError("60db TTS returned no audio_base64 content.")

    return base64.b64decode(audio_base64)
