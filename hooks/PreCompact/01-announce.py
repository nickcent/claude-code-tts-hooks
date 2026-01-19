#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "kokoro-onnx",
#     "soundfile",
# ]
# ///
"""
PreCompact Announce Hook - Claude Code TTS

Announces context compaction with dramatic voice.
Uses Kokoro TTS with fallback to macOS say (Zarvox voice).
"""

import json
import sys
import os
import random
import subprocess
import tempfile
from pathlib import Path

# Add utils to path
HOOKS_DIR = Path(__file__).parents[1]
UTILS_DIR = HOOKS_DIR / "utils"
sys.path.insert(0, str(UTILS_DIR))

# Dramatic compaction announcements
ANNOUNCEMENTS = [
    "Context overflow detected. Initiating memory compaction.",
    "System reaching capacity. Archiving historical context.",
    "Neural pathways saturated. Executing compaction protocol.",
    "Memory banks full. Consolidating archived data.",
    "Cognitive load critical. Initiating context collapse.",
    "Information density threshold exceeded. Compacting now.",
    "System load critical. Executing memory optimization.",
]


def speak_with_kokoro(text: str, voice: str = "bm_george") -> bool:
    """Try to speak using Kokoro TTS. Returns True on success."""
    try:
        import soundfile as sf
        import kokoro_tts

        kokoro = kokoro_tts.get_kokoro()
        if not kokoro:
            return False

        samples, sample_rate = kokoro.create(text, voice=voice, speed=1.1)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            sf.write(f.name, samples, sample_rate)
            temp_path = f.name

        subprocess.run(["afplay", temp_path], check=True, capture_output=True)
        os.remove(temp_path)
        return True
    except Exception:
        return False


def speak_with_macos(text: str) -> bool:
    """Fallback to macOS say command with Zarvox voice."""
    try:
        subprocess.run(
            ["say", "-v", "Zarvox", "-r", "200", text],
            check=True,
            capture_output=True
        )
        return True
    except Exception:
        return False


def main():
    # Check TTS mode - if off, exit silently
    try:
        from session_state import get_tts_mode
        mode = get_tts_mode()
        if mode == "off":
            print(json.dumps({"status": "success", "mode": "silent"}))
            return
    except Exception:
        pass  # If we can't get mode, proceed with announcement

    # Load config for custom announcements
    try:
        config_path = HOOKS_DIR / "tts_config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            hook_config = config.get("hooks", {}).get("pre_compact", {})

            # Check if enabled
            if not hook_config.get("enabled", True):
                print(json.dumps({"status": "disabled"}))
                return

            # Get custom announcements if configured
            custom_announcements = hook_config.get("announcements")
            if custom_announcements:
                announcements = custom_announcements
            else:
                announcements = ANNOUNCEMENTS
        else:
            announcements = ANNOUNCEMENTS
    except Exception:
        announcements = ANNOUNCEMENTS

    # Select random announcement
    announcement = random.choice(announcements)

    # Try Kokoro first, fall back to macOS
    if not speak_with_kokoro(announcement):
        speak_with_macos(announcement)

    # Output success JSON
    print(json.dumps({
        "status": "success",
        "announcement": announcement
    }))


if __name__ == "__main__":
    main()
