#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
# ]
# ///
"""
OpenAI TTS API wrapper.
UV single-file script with inline dependencies.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path


# API configuration
DEFAULT_MODEL = "tts-1-hd"
DEFAULT_VOICE = "onyx"
DEFAULT_SPEED = 1.0


def load_api_key() -> str:
    """Load OpenAI API key from environment or .env file."""
    # Check environment first
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        return api_key

    # Try ~/.claude/.env (unified credentials)
    env_file = Path.home() / ".claude" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key.strip() == "OPENAI_API_KEY":
                        return value.strip()

    return ""


def speak(
    text: str,
    voice: str = DEFAULT_VOICE,
    speed: float = DEFAULT_SPEED,
    model: str = DEFAULT_MODEL
) -> bool:
    """
    Speak text using OpenAI TTS API.

    Args:
        text: Text to speak
        voice: OpenAI voice (alloy, echo, fable, onyx, nova, shimmer)
        speed: Speech speed (0.25-4.0, default 1.0)
        model: Model ID (tts-1 or tts-1-hd)

    Returns:
        True if successful, False otherwise
    """
    api_key = load_api_key()
    if not api_key:
        print("Error: OPENAI_API_KEY not found", file=sys.stderr)
        return False

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Clamp speed to OpenAI limits
        speed = max(0.25, min(4.0, speed))

        # Create speech
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=speed
        )

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            response.stream_to_file(f.name)
            temp_path = f.name

        # Play with afplay
        subprocess.run(["afplay", temp_path], check=True)

        # Cleanup
        os.remove(temp_path)
        return True

    except Exception as e:
        print(f"OpenAI TTS error: {e}", file=sys.stderr)
        return False


def list_voices():
    """List available OpenAI TTS voices."""
    return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


if __name__ == "__main__":
    # Test with onyx voice
    speak(
        "Testing OpenAI TTS wrapper. Onyx voice online.",
        voice="onyx",
        speed=1.0
    )
