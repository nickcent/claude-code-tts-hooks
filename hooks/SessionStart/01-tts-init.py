# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "kokoro-onnx",
#     "soundfile",
#     "requests",
# ]
# ///
"""
SessionStart Hook - Claude Code TTS Initialization

Shows dialog to select TTS provider on session start.
Saves selection for use by other hooks throughout the session.

Providers:
- Kokoro: Local neural TTS (free, fast, 82M parameters)
- ElevenLabs: Cloud TTS (premium voices, requires API key)
- OpenAI: Cloud TTS (requires API key)
- Silent: No audio output
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Setup paths
HOOKS_DIR = Path(__file__).parent.parent
UTILS_DIR = HOOKS_DIR / "utils"
sys.path.insert(0, str(UTILS_DIR))

DEBUG_LOG = Path("/tmp/claude-tts-debug.log")


def log_debug(msg: str) -> None:
    """Write debug message to log file."""
    with open(DEBUG_LOG, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


def load_config() -> dict:
    """Load configuration from tts_config.json."""
    try:
        config_path = HOOKS_DIR / "tts_config.json"
        if config_path.exists():
            return json.loads(config_path.read_text())
    except Exception:
        pass
    return {}


def get_context_message(tts_mode: str, config: dict) -> str:
    """Get context message for Claude based on TTS mode."""
    voices = config.get("voices", {}).get("assistant", {})

    if tts_mode == "off":
        return "TTS MODE: OFF. Work silently."

    if tts_mode == "kokoro":
        return f"""TTS MODE: KOKORO
Voice: {voices.get('kokoro_voice', 'bf_emma')} | Speed: {voices.get('speed', 1.0)}
Speak summaries only. No code/paths in TTS."""

    if tts_mode == "elevenlabs":
        return f"""TTS MODE: ELEVENLABS
Voice ID: {voices.get('elevenlabs_voice_id', '21m00Tcm4TlvDq8ikWAM')}
Speed: {voices.get('speed', 1.0)}
Speak summaries only. No code/paths in TTS."""

    if tts_mode == "openai":
        return f"""TTS MODE: OPENAI
Voice: {voices.get('openai_voice', 'onyx')} | Speed: {voices.get('speed', 1.0)}
Speak summaries only. No code/paths in TTS."""

    return "TTS MODE: OFF. Work silently."


def main():
    """Execute session start sequence."""
    log_debug("=== SESSION START HOOK TRIGGERED ===")

    try:
        # Load config
        config = load_config()
        session_config = config.get("session", {})

        # Import utilities
        from tts_dialog import select_tts_mode
        from session_state import save_tts_mode, save_session_start

        # Show TTS mode selection dialog
        if session_config.get("show_dialog", True):
            tts_mode = select_tts_mode(
                timeout=session_config.get("dialog_timeout", 15),
                default=session_config.get("default_mode", "off"),
                log_file=DEBUG_LOG
            )
        else:
            tts_mode = session_config.get("default_mode", "off")

        # Save to session state
        save_tts_mode(tts_mode)
        save_session_start()

        log_debug(f"TTS mode selected: {tts_mode}")

        # Optional: Speak announcement if TTS enabled
        if tts_mode != "off":
            hooks_config = config.get("hooks", {}).get("session_start", {})
            if hooks_config.get("speak_announcement", True):
                try:
                    from tts_router import speak
                    announcement = f"TTS enabled. Using {tts_mode} mode."
                    speak("system", announcement, mode=tts_mode)
                except Exception as e:
                    log_debug(f"Announcement failed: {e}")

        # Build output
        context_text = get_context_message(tts_mode, config)
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context_text
            }
        }

        log_debug("=== SESSION START HOOK COMPLETED ===")
        print(json.dumps(output))

    except Exception as e:
        log_debug(f"Error in session_start: {e}")
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    main()
