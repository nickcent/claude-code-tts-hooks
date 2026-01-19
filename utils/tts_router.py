#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
# ]
# ///
"""
Unified TTS router with mode-aware provider selection.

Routing logic:
1. Read TTS mode from session_state
2. Route to provider: kokoro/elevenlabs/openai/off
3. Fallback chain: Primary -> macOS say

Voice configuration:
- "assistant": Primary voice for Claude's responses
- "system": System announcements
"""

import json
import sys
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import macos_say

HOOKS_DIR = Path(__file__).parent.parent


def _load_voice_config():
    """Load voices from tts_config.json."""
    try:
        config_path = HOOKS_DIR / "tts_config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                return config.get("voices", {})
    except Exception:
        pass
    return {}


def get_voice(voice_type: str) -> dict:
    """Get voice config from tts_config.json.

    Args:
        voice_type: "assistant" or "system"

    Returns:
        Voice configuration dictionary
    """
    voices = _load_voice_config()
    if voice_type in voices:
        cfg = voices[voice_type]
        return {
            "kokoro_voice": cfg.get("kokoro_voice", "bf_emma"),
            "voice_id": cfg.get("elevenlabs_voice_id"),
            "openai_voice": cfg.get("openai_voice", "onyx"),
            "macos_voice": cfg.get("macos_voice", "Samantha"),
            "speed": cfg.get("speed", 1.0),
        }
    # Default fallback
    return {
        "kokoro_voice": "bf_emma",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "openai_voice": "onyx",
        "macos_voice": "Samantha",
        "speed": 1.0
    }


# Import session state
try:
    from session_state import get_tts_mode
except ImportError:
    def get_tts_mode():
        return "off"

# Import providers dynamically
try:
    import elevenlabs_tts
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

try:
    import kokoro_tts
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False

try:
    import openai_tts
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def speak(voice_type: str, text: str, mode: str = None) -> bool:
    """
    Speak text using the appropriate provider based on TTS mode.

    Args:
        voice_type: Voice type key ("assistant", "system")
        text: Text to speak
        mode: Override TTS mode (default: read from session_state)

    Returns:
        True if successful, False otherwise
    """
    # Get TTS mode
    if mode is None:
        mode = get_tts_mode()

    # Silent mode - skip TTS
    if mode == "off":
        return True

    voice_config = get_voice(voice_type)

    # Route to provider based on mode
    if mode == "kokoro":
        return _speak_kokoro(text, voice_config)
    elif mode == "elevenlabs":
        return _speak_elevenlabs(text, voice_config)
    elif mode == "openai":
        return _speak_openai(text, voice_config)
    else:
        # Unknown mode - fallback to macOS
        return _speak_macos(text, voice_config)


def _speak_kokoro(text: str, voice_config: dict) -> bool:
    """Speak using Kokoro with macOS fallback."""
    if KOKORO_AVAILABLE and voice_config.get("kokoro_voice"):
        success = kokoro_tts.speak(
            text,
            voice=voice_config.get("kokoro_voice", "bf_emma"),
            speed=voice_config.get("speed", 1.0)
        )
        if success:
            return True
        print("Kokoro failed, falling back to macOS", file=sys.stderr)

    return _speak_macos(text, voice_config)


def _speak_elevenlabs(text: str, voice_config: dict) -> bool:
    """Speak using ElevenLabs with macOS fallback."""
    if ELEVENLABS_AVAILABLE and voice_config.get("voice_id"):
        success = elevenlabs_tts.speak(
            text,
            voice_config.get("voice_id"),
            speed=voice_config.get("speed", 1.0),
        )
        if success:
            return True
        print("ElevenLabs failed, falling back to macOS", file=sys.stderr)

    return _speak_macos(text, voice_config)


def _speak_openai(text: str, voice_config: dict) -> bool:
    """Speak using OpenAI TTS with macOS fallback."""
    if OPENAI_AVAILABLE and voice_config.get("openai_voice"):
        success = openai_tts.speak(
            text,
            voice=voice_config.get("openai_voice", "onyx"),
            speed=voice_config.get("speed", 1.0)
        )
        if success:
            return True
        print("OpenAI TTS failed, falling back to macOS", file=sys.stderr)

    return _speak_macos(text, voice_config)


def _speak_macos(text: str, voice_config: dict) -> bool:
    """Speak using macOS say (final fallback)."""
    macos_voice = voice_config.get("macos_voice", "Samantha")
    return macos_say.speak(text, macos_voice, voice_config.get("speed", 1.0))


if __name__ == "__main__":
    # Test each mode
    print("Testing Kokoro...")
    speak("assistant", "Testing Kokoro mode.", mode="kokoro")

    print("\nTesting ElevenLabs...")
    speak("assistant", "Testing ElevenLabs mode.", mode="elevenlabs")

    print("\nTesting OpenAI...")
    speak("assistant", "Testing OpenAI mode.", mode="openai")

    print("\nTesting macOS fallback...")
    speak("system", "Testing macOS fallback mode.", mode="macos")
