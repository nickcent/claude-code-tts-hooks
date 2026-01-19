#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
# ]
# ///
"""
ElevenLabs TTS API wrapper.
UV single-file script with inline dependencies.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

import requests


# API configuration
API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
DEFAULT_MODEL = "eleven_flash_v2_5"
DEFAULT_SPEED = 1.0
DEFAULT_STABILITY = 0.5
DEFAULT_SIMILARITY = 0.75


def load_api_key() -> str:
    """Load ElevenLabs API key from environment or .env file."""
    # Check environment first
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
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
                    if key.strip() == "ELEVENLABS_API_KEY":
                        return value.strip()

    # Fallback: check for key file
    key_file = Path.home() / ".config" / "elevenlabs" / "api_key"
    if key_file.exists():
        return key_file.read_text().strip()

    return ""


def speak(
    text: str,
    voice_id: str,
    speed: float = DEFAULT_SPEED,
    model: str = DEFAULT_MODEL,
    stability: float = DEFAULT_STABILITY,
    similarity_boost: float = DEFAULT_SIMILARITY
) -> bool:
    """
    Speak text using ElevenLabs API.

    Args:
        text: Text to speak
        voice_id: ElevenLabs voice ID
        speed: Speech speed (0.7-1.2, default 1.0)
        model: Model ID (default eleven_flash_v2_5)
        stability: Voice stability (0.0-1.0)
        similarity_boost: Similarity boost (0.0-1.0)

    Returns:
        True if successful, False otherwise
    """
    api_key = load_api_key()
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found", file=sys.stderr)
        return False

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    # Clamp speed to ElevenLabs limits
    speed = max(0.7, min(1.2, speed))

    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "speed": speed
        }
    }

    voice_url = f"{API_URL}/{voice_id}"

    try:
        response = requests.post(voice_url, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    temp_file.write(chunk)
            temp_path = temp_file.name

        # Play with afplay
        subprocess.run(["afplay", temp_path], check=True)

        # Cleanup
        os.remove(temp_path)
        return True

    except requests.exceptions.RequestException as e:
        print(f"ElevenLabs API error: {e}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        return False
    except subprocess.CalledProcessError as e:
        print(f"Audio playback failed: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Test with Rachel voice (default ElevenLabs voice)
    speak(
        "Testing ElevenLabs wrapper. TTS is online.",
        "21m00Tcm4TlvDq8ikWAM",  # Rachel voice ID
        speed=1.0
    )
