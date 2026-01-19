"""
Session state persistence for TTS mode selection.
Uses a temporary file that persists for the Claude Code session.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta


# State file location
SESSION_STATE_FILE = Path("/tmp/claude_tts_session_state.json")


def _get_current_session_id() -> str:
    """Get current Claude Code session ID from environment or PID.

    Returns:
        Session identifier (CLAUDE_SESSION_ID env var or process PID)
    """
    return os.environ.get("CLAUDE_SESSION_ID", str(os.getppid()))


def save_tts_mode(mode: str) -> None:
    """Save TTS mode to session state file while preserving other keys.

    Args:
        mode: One of:
            - "kokoro": Local neural TTS (Kokoro)
            - "elevenlabs": Cloud TTS (ElevenLabs API)
            - "openai": Cloud TTS (OpenAI API)
            - "off": TTS disabled (silent mode)
    """
    state = get_session_state()
    state["tts_mode"] = mode
    state["session_id"] = _get_current_session_id()
    state["updated_at"] = datetime.now().isoformat()
    SESSION_STATE_FILE.write_text(json.dumps(state))


def get_tts_mode() -> str:
    """Get TTS mode from session state file.

    Returns:
        One of:
        - "kokoro": Local neural TTS (Kokoro)
        - "elevenlabs": Cloud TTS (ElevenLabs API)
        - "openai": Cloud TTS (OpenAI API)
        - "off": TTS disabled (silent mode)

        Defaults to "off" if no session state exists.
    """
    if not SESSION_STATE_FILE.exists():
        return "off"
    try:
        state = json.loads(SESSION_STATE_FILE.read_text())
        return state.get("tts_mode", "off")
    except (json.JSONDecodeError, Exception):
        return "off"


def clear_session_state() -> None:
    """Clear session state file."""
    if SESSION_STATE_FILE.exists():
        SESSION_STATE_FILE.unlink()


def get_session_state() -> dict:
    """Get full session state dictionary."""
    if not SESSION_STATE_FILE.exists():
        return {}
    try:
        state = json.loads(SESSION_STATE_FILE.read_text())
        return state
    except (json.JSONDecodeError, Exception):
        return {}


# === Session Timing Functions ===

def save_session_start() -> None:
    """Record session start time. Called by session_start hook."""
    state = get_session_state()
    state["session_start"] = datetime.now().isoformat()
    state["session_id"] = _get_current_session_id()
    SESSION_STATE_FILE.write_text(json.dumps(state))


def get_session_duration() -> timedelta:
    """Get current session duration.

    Returns:
        timedelta since session start, or 0 if no start time recorded
    """
    state = get_session_state()
    start_str = state.get("session_start")
    if not start_str:
        return timedelta(0)
    try:
        start = datetime.fromisoformat(start_str)
        return datetime.now() - start
    except (ValueError, TypeError):
        return timedelta(0)


def get_session_duration_str() -> str:
    """Get human-readable session duration string.

    Returns:
        String like "2h 45m" or "45m"
    """
    duration = get_session_duration()
    hours, remainder = divmod(int(duration.total_seconds()), 3600)
    minutes = remainder // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
