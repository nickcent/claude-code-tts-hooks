#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#     "kokoro-onnx",
#     "soundfile",
# ]
# ///
"""
Kokoro TTS wrapper for local neural TTS.
82M parameters, high quality, runs locally.

Voice naming convention:
- af_* = American Female (bella, jessica, nicole, nova, river, sarah, sky)
- am_* = American Male (adam, echo, eric, liam, michael, onyx)
- bf_* = British Female (alice, emma, lily, matilda)
- bm_* = British Male (daniel, fable, george, lewis, oliver, oscar)
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

# Model paths
KOKORO_DIR = Path.home() / ".local" / "share" / "kokoro"
MODEL_PATH = KOKORO_DIR / "kokoro-v1.0.onnx"
VOICES_PATH = KOKORO_DIR / "voices-v1.0.bin"
HOOKS_DIR = Path(__file__).parent.parent

# Singleton for model (avoid reloading)
_kokoro_instance = None


def get_kokoro():
    """Get or create Kokoro instance (singleton)."""
    global _kokoro_instance
    if _kokoro_instance is None:
        try:
            from kokoro_onnx import Kokoro
            if MODEL_PATH.exists() and VOICES_PATH.exists():
                _kokoro_instance = Kokoro(str(MODEL_PATH), str(VOICES_PATH))
            else:
                print(f"Kokoro models not found at {KOKORO_DIR}", file=sys.stderr)
                return None
        except ImportError:
            print("kokoro_onnx not installed", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Failed to load Kokoro: {e}", file=sys.stderr)
            return None
    return _kokoro_instance


def speak(text: str, voice: str = "bf_emma", speed: float = 1.0, volume: float = 1.0) -> bool:
    """
    Speak text using Kokoro TTS.

    Args:
        text: Text to speak
        voice: Kokoro voice name (bf_emma, am_adam, etc.)
        speed: Speech speed (1.0 = normal)
        volume: Playback volume (0.0 to 1.0, default 1.0)

    Returns:
        True if successful, False otherwise
    """
    kokoro = get_kokoro()
    if kokoro is None:
        return False

    try:
        import soundfile as sf

        # Generate speech
        samples, sample_rate = kokoro.create(text, voice=voice, speed=speed)

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            sf.write(f.name, samples, sample_rate)
            temp_path = f.name

        # Play with afplay (with volume control)
        cmd = ["afplay"]
        if volume != 1.0:
            cmd.extend(["-v", str(volume)])
        cmd.append(temp_path)
        subprocess.run(cmd, check=True)

        # Cleanup
        os.remove(temp_path)
        return True

    except Exception as e:
        print(f"Kokoro TTS error: {e}", file=sys.stderr)
        return False


def list_voices():
    """List available Kokoro voices."""
    return [
        # American Female
        "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica",
        "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky",
        # American Male
        "am_adam", "am_echo", "am_eric", "am_liam", "am_michael", "am_onyx",
        # British Female
        "bf_alice", "bf_emma", "bf_lily", "bf_matilda",
        # British Male
        "bm_daniel", "bm_fable", "bm_george", "bm_lewis", "bm_oliver", "bm_oscar"
    ]


if __name__ == "__main__":
    # Test
    speak("Testing Kokoro TTS wrapper. This is the Emma voice.", voice="bf_emma")
