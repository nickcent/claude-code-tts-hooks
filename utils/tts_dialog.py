"""
TTS mode selection dialog for Claude Code hooks.
Provides macOS AppleScript dialogs for TTS provider selection.
"""

import subprocess
from pathlib import Path
from datetime import datetime


def log_debug(msg: str, log_file: Path = Path("/tmp/claude-tts-debug.log")) -> None:
    """Write debug message to log file."""
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


def select_tts_mode(timeout: int = 15, default: str = "off", log_file: Path = None) -> str:
    """
    Show macOS dialog to select TTS mode.

    Args:
        timeout: Dialog timeout in seconds
        default: Default mode if dialog times out or is cancelled
        log_file: Optional log file path

    Returns:
        Selected TTS mode: "kokoro", "elevenlabs", "openai", or "off"
    """
    script = '''set choices to {"Kokoro - Free, Local Neural TTS", "ElevenLabs - Premium Cloud Voices", "OpenAI - Cloud TTS", "Silent - No Audio"}
try
    set selectedItem to choose from list choices with prompt "Select TTS Provider:" default items {"Kokoro - Free, Local Neural TTS"} with title "Claude Code TTS"
    if selectedItem is false then
        return "off"
    else
        set choice to item 1 of selectedItem
        if choice contains "Kokoro" then
            return "kokoro"
        else if choice contains "ElevenLabs" then
            return "elevenlabs"
        else if choice contains "OpenAI" then
            return "openai"
        else
            return "off"
        end if
    end if
on error
    return "off"
end try'''

    try:
        if log_file:
            log_debug(f"Running TTS dialog with {timeout}s timeout...", log_file)

        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        mode = result.stdout.strip().lower()
        if log_file:
            log_debug(f"TTS mode selected: {mode}", log_file)

        if mode in ("kokoro", "elevenlabs", "openai", "off"):
            return mode
        return default

    except subprocess.TimeoutExpired:
        if log_file:
            log_debug(f"Dialog timed out after {timeout}s", log_file)
        return default
    except Exception as e:
        if log_file:
            log_debug(f"Dialog exception: {e}", log_file)
        return default


def show_notification(title: str, message: str) -> bool:
    """
    Show macOS notification.

    Args:
        title: Notification title
        message: Notification message

    Returns:
        True if successful
    """
    script = f'''display notification "{message}" with title "{title}"'''
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return True
    except Exception:
        return False
