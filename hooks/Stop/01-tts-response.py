#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#     "kokoro-onnx",
#     "soundfile",
#     "openai",
#     "requests",
# ]
# ///
"""
Stop hook for Claude Code TTS.
Extracts Claude's response and speaks it via TTS.

TTS Modes:
- Kokoro: Local neural TTS (fast, free)
- ElevenLabs: Cloud TTS (high quality, uses API credits)
- OpenAI: Cloud TTS (uses API credits)
- Off: Silent mode

Flow:
1. Read Claude's last response from transcript.
2. Clean text for natural speech.
3. Speak via configured TTS engine.
"""

import json
import os
import re
import sys
from pathlib import Path

# Add utils to path
HOOKS_DIR = Path(__file__).parent.parent
UTILS_DIR = HOOKS_DIR / "utils"
sys.path.insert(0, str(UTILS_DIR))


def _shorten_path(match: re.Match) -> str:
    """Convert file path to speakable short form.

    /Users/nick/.claude/hooks/tts_config.json
    -> "tts config dot json in the hooks folder"
    """
    path = match.group(0)
    parts = [p for p in path.split('/') if p]
    if len(parts) >= 2:
        filename = parts[-1]
        folder = parts[-2]
        # Make extension speakable
        filename = re.sub(r'\.([a-z]+)$', r' dot \1', filename)
        # Replace underscores and hyphens with spaces
        filename = filename.replace('_', ' ').replace('-', ' ')
        folder = folder.replace('_', ' ').replace('-', ' ')
        return f"{filename} in the {folder} folder"
    elif len(parts) == 1:
        filename = parts[0]
        filename = re.sub(r'\.([a-z]+)$', r' dot \1', filename)
        return filename.replace('_', ' ').replace('-', ' ')
    return ""


def _shorten_url(match: re.Match) -> str:
    """Convert URL to speakable short form.

    https://github.com/anthropics/claude-code/issues
    -> "github dot com"
    """
    url = match.group(0)
    domain_match = re.search(r'https?://([^/]+)', url)
    if domain_match:
        domain = domain_match.group(1)
        domain = re.sub(r'^www\.', '', domain)
        # Make dots speakable
        domain = domain.replace('.', ' dot ')
        return domain
    return "a link"


def _clean_inline_code(match: re.Match) -> str:
    """Clean inline code for speech."""
    code = match.group(1)
    return code.replace('_', ' ')


def clean_text_for_speech(text: str) -> str:
    """Clean text for natural speech output.

    Converts technical elements to speakable form.
    """
    # Convert file extensions to speakable form
    text = re.sub(r'\.([a-zA-Z]{1,5})\b', r' dot \1', text)

    # Make decimal numbers speakable
    text = re.sub(r'(\d+)\.(\d+)', r'\1 point \2', text)

    # Convert tilde to "home" for home directory paths
    text = re.sub(r'~/', 'home slash ', text)

    # Convert path slashes to spaces
    text = re.sub(r'([a-zA-Z0-9])/([a-zA-Z0-9])', r'\1 \2', text)

    # Convert leading dots to "dot " for hidden files
    text = re.sub(r'(?<![a-zA-Z0-9])\.([a-zA-Z])', r'dot \1', text)

    # Convert hyphens in names to spaces
    text = re.sub(r'([a-zA-Z0-9])-([a-zA-Z0-9])', r'\1 \2', text)

    # Convert em/en dashes to commas
    text = re.sub(r'\s*[—–]\s*', ', ', text)

    # Convert arrows to "to"
    text = re.sub(r'\s*→\s*', ' to ', text)
    text = re.sub(r'\s*->\s*', ' to ', text)

    # Expand data size abbreviations
    text = re.sub(r'\b(\d+(?:\s+point\s+\d+)?)\s*KB\b', r'\1 kilobytes', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+(?:\s+point\s+\d+)?)\s*MB\b', r'\1 megabytes', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+(?:\s+point\s+\d+)?)\s*GB\b', r'\1 gigabytes', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(\d+(?:\s+point\s+\d+)?)\s*TB\b', r'\1 terabytes', text, flags=re.IGNORECASE)

    # Convert comma-separated numbers to words
    def _number_to_words(match: re.Match) -> str:
        num_str = match.group(0).replace(',', '')
        try:
            num = int(num_str)
            if num == 0:
                return "zero"

            ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                    "seventeen", "eighteen", "nineteen"]
            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

            def _under_hundred(n):
                if n < 20:
                    return ones[n]
                elif n < 100:
                    return tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")
                return ""

            def _under_thousand(n):
                if n < 100:
                    return _under_hundred(n)
                return ones[n // 100] + " hundred" + (" and " + _under_hundred(n % 100) if n % 100 else "")

            parts = []
            if num >= 1000000:
                parts.append(_under_thousand(num // 1000000) + " million")
                num %= 1000000
            if num >= 1000:
                parts.append(_under_thousand(num // 1000) + " thousand")
                num %= 1000
            if num > 0:
                if parts and num < 100:
                    parts.append("and " + _under_hundred(num))
                else:
                    parts.append(_under_thousand(num))

            return " ".join(parts)
        except ValueError:
            return match.group(0)

    text = re.sub(r'\b\d{1,3}(?:,\d{3})+\b', _number_to_words, text)

    # Replace code blocks with announcement
    text = re.sub(r'```[\s\S]*?```', ' Code block omitted. ', text)
    # Clean inline code
    text = re.sub(r'`([^`]+)`', _clean_inline_code, text)
    # Replace file paths with shortened speakable form
    text = re.sub(r'/[a-zA-Z0-9\-_.\/]+(?:\.[a-z]+)?', _shorten_path, text)
    # Replace URLs with shortened speakable form
    text = re.sub(r'https?://\S+', _shorten_url, text)
    # Remove markdown bold/italic but keep text
    text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
    # Remove markdown headers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove list dashes at start of lines
    text = re.sub(r'(?m)^\s*[-*]\s+', '', text)
    # Remove table formatting
    text = re.sub(r'\|[^\n]+\|', '', text)
    text = re.sub(r'[-|]+\n', '', text)
    # Clean up multiple spaces
    text = re.sub(r' +', ' ', text)
    # Clean up multiple newlines
    text = re.sub(r'\n\s*\n+', '\n', text)

    return text.strip()


def load_config() -> dict:
    """Load configuration from tts_config.json."""
    try:
        config_path = HOOKS_DIR / "tts_config.json"
        if config_path.exists():
            return json.loads(config_path.read_text())
    except Exception:
        pass
    return {}


def get_voice_config(config: dict) -> dict:
    """Get voice config from configuration."""
    voice_config = config.get("voices", {}).get("assistant", {})
    return {
        "kokoro_voice": voice_config.get("kokoro_voice", "bf_emma"),
        "voice_id": voice_config.get("elevenlabs_voice_id"),
        "openai_voice": voice_config.get("openai_voice", "onyx"),
        "macos_voice": voice_config.get("macos_voice", "Samantha"),
        "speed": voice_config.get("speed", 1.0),
        "volume": voice_config.get("volume", 1.0),
    }


def speak_kokoro(text: str, voice_config: dict) -> bool:
    """Speak text using Kokoro with macOS fallback."""
    try:
        import kokoro_tts
        success = kokoro_tts.speak(
            text,
            voice=voice_config.get("kokoro_voice", "bf_emma"),
            speed=voice_config.get("speed", 1.0),
            volume=voice_config.get("volume", 1.0)
        )
        if success:
            return True
    except Exception:
        pass

    # Fallback to macOS
    try:
        import macos_say
        return macos_say.speak(
            text,
            voice_config.get("macos_voice", "Samantha"),
            voice_config.get("speed", 1.0)
        )
    except Exception:
        return False


def speak_elevenlabs(text: str, voice_config: dict) -> bool:
    """Speak text using ElevenLabs with macOS fallback."""
    try:
        import elevenlabs_tts
        if voice_config.get("voice_id"):
            success = elevenlabs_tts.speak(
                text,
                voice_config.get("voice_id"),
                speed=voice_config.get("speed", 1.0),
            )
            if success:
                return True
    except Exception:
        pass

    # Fallback to macOS
    try:
        import macos_say
        return macos_say.speak(
            text,
            voice_config.get("macos_voice", "Samantha"),
            voice_config.get("speed", 1.0)
        )
    except Exception:
        return False


def speak_openai(text: str, voice_config: dict) -> bool:
    """Speak text using OpenAI TTS with macOS fallback."""
    try:
        import openai_tts
        success = openai_tts.speak(
            text,
            voice=voice_config.get("openai_voice", "onyx"),
            speed=voice_config.get("speed", 1.0)
        )
        if success:
            return True
    except Exception:
        pass

    # Fallback to macOS
    try:
        import macos_say
        return macos_say.speak(
            text,
            voice_config.get("macos_voice", "Samantha"),
            voice_config.get("speed", 1.0)
        )
    except Exception:
        return False


def extract_last_response(transcript_path: str) -> str:
    """Extract Claude's last response text from the transcript file."""
    if not transcript_path or not Path(transcript_path).exists():
        return ""

    try:
        last_assistant_content = ""
        with open(transcript_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "assistant":
                        message = entry.get("message", {})
                        content_blocks = message.get("content", [])
                        text_parts = []
                        for block in content_blocks:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text_parts.append(block.get("text", ""))
                            elif isinstance(block, str):
                                text_parts.append(block)
                        if text_parts:
                            last_assistant_content = "\n".join(text_parts)
                except json.JSONDecodeError:
                    continue

        return last_assistant_content
    except Exception as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)
        return ""


def main():
    """Handle stop event - extract Claude's response and speak it."""
    # Load config
    config = load_config()
    hook_config = config.get("hooks", {}).get("stop", {})

    # Check if Stop hook is enabled
    if not hook_config.get("enabled", True):
        print(json.dumps({"status": "disabled"}))
        return

    # Check TTS mode from session state
    try:
        from session_state import get_tts_mode
        tts_mode = get_tts_mode()
    except Exception:
        tts_mode = "off"

    # Read input from stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        input_data = {}

    # Silent mode - exit early
    if tts_mode == "off":
        print(json.dumps({"status": "success"}))
        return

    # Get voice config
    voice_config = get_voice_config(config)

    # Select speak function based on mode
    if tts_mode == "elevenlabs":
        speak = lambda text: speak_elevenlabs(text, voice_config)
    elif tts_mode == "openai":
        speak = lambda text: speak_openai(text, voice_config)
    else:
        # Default to Kokoro
        speak = lambda text: speak_kokoro(text, voice_config)

    # Get transcript path from hook payload
    transcript_path = input_data.get("transcript_path", "")
    if transcript_path:
        transcript_path = os.path.expanduser(transcript_path)

    # Extract Claude's last response
    last_response = extract_last_response(transcript_path)

    if not last_response:
        print(json.dumps({"status": "success", "reason": "no_response"}))
        return

    # Clean and speak the response
    text_to_speak = clean_text_for_speech(last_response)
    result = speak(text_to_speak)
    print(json.dumps({"status": "success", "spoke": result}))


if __name__ == "__main__":
    main()
