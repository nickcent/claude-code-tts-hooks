#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#     "kokoro-onnx",
#     "soundfile",
#     "numpy",
# ]
# ///
"""
UserPromptSubmit acknowledgment hook.
Speaks a random acknowledgment phrase when user submits a prompt.

Configuration via tts_config.json:
- hooks.user_prompt_submit.enabled: Enable/disable this hook
- hooks.user_prompt_submit.phrases: List of acknowledgment phrases
- voices.system: Voice configuration for acknowledgments
"""
import json
import os
import sys
import tempfile
import subprocess
import random
from pathlib import Path

# Add utils to path
HOOKS_DIR = Path(__file__).parents[1]
UTILS_DIR = HOOKS_DIR / "utils"
sys.path.insert(0, str(UTILS_DIR))

# Default phrases if not configured
DEFAULT_PHRASES = [
    "Roger.", "Copy.", "On it.", "Understood.", "Working on it.",
    "Got it.", "Affirmative.", "Right away.", "Message received.",
    "Acknowledged.", "Copy that.", "All systems go."
]


def load_config():
    """Load user_prompt_submit config from tts_config.json."""
    config_path = HOOKS_DIR / "tts_config.json"
    try:
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def speak_macos(phrase: str, voice: str = "Samantha"):
    """Speak using macOS native TTS."""
    try:
        subprocess.run(["say", "-v", voice, phrase], check=True, capture_output=True)
        return True
    except Exception:
        return False


def speak_kokoro(phrase: str, voice: str = "af_sky", speed: float = 1.2, volume: float = 0.8):
    """Speak using Kokoro local TTS."""
    try:
        import kokoro_tts
        import soundfile as sf
        import numpy as np

        kokoro = kokoro_tts.get_kokoro()
        if not kokoro:
            return False

        samples, sample_rate = kokoro.create(phrase, voice=voice, speed=speed)
        # Apply volume adjustment
        samples = samples * volume

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            sf.write(f.name, samples, sample_rate)
            temp_path = f.name

        subprocess.run(["afplay", temp_path], check=True, capture_output=True)
        os.remove(temp_path)
        return True
    except Exception:
        return False


def main():
    # Check TTS mode
    try:
        from session_state import get_tts_mode
        mode = get_tts_mode()
    except Exception:
        mode = "kokoro"

    if mode == "off":
        print(json.dumps({
            "status": "success",
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "User input acknowledged. Silent mode active."
            }
        }))
        return

    # Load config
    config = load_config()
    hook_config = config.get("hooks", {}).get("user_prompt_submit", {})

    # Check if hook is enabled
    if not hook_config.get("enabled", True):
        print(json.dumps({"status": "disabled"}))
        return

    phrases = hook_config.get("phrases", DEFAULT_PHRASES)

    # Load voice config
    voice_config = config.get("voices", {}).get("system", {})
    kokoro_voice = voice_config.get("kokoro_voice", "af_nicole")
    speed = voice_config.get("speed", 1.2)
    macos_voice = voice_config.get("macos_voice", "Samantha")

    # Select random phrase
    phrase = random.choice(phrases) if phrases else "Acknowledged."

    # Speak using appropriate provider
    spoke = False
    if mode == "kokoro":
        spoke = speak_kokoro(phrase, voice=kokoro_voice, speed=speed)

    # Fallback to macOS
    if not spoke:
        speak_macos(phrase, voice=macos_voice)

    # Output success
    print(json.dumps({
        "status": "success",
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"User input acknowledged: {phrase}"
        }
    }))


if __name__ == "__main__":
    main()
