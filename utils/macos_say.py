"""
macOS say command wrapper for TTS fallback.
No external dependencies - uses built-in macOS speech synthesis.
"""

import subprocess
import sys


def speak(text: str, voice: str = "Samantha", speed: float = 1.0) -> bool:
    """
    Speak text using macOS built-in say command.

    Args:
        text: Text to speak
        voice: macOS voice name (Samantha, Alex, Tom, etc.)
        speed: Speed multiplier (1.0 = normal, ~175 wpm)

    Returns:
        True if successful, False otherwise
    """
    # macOS say uses words per minute, ~175 is normal speaking rate
    rate = int(175 * speed)

    try:
        subprocess.run(
            ["say", "-v", voice, "-r", str(rate), text],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"macOS say failed: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("macOS say command not found (not on macOS?)", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error in macOS say: {e}", file=sys.stderr)
        return False


def list_voices() -> list:
    """List available macOS voices."""
    try:
        result = subprocess.run(
            ["say", "-v", "?"],
            capture_output=True,
            text=True,
            check=True
        )
        voices = []
        for line in result.stdout.strip().split("\n"):
            if line:
                # Format: "Voice Name    language    # description"
                voice_name = line.split()[0]
                voices.append(voice_name)
        return voices
    except Exception:
        return []


if __name__ == "__main__":
    # Test the module
    speak("Testing macOS say wrapper. This is Samantha speaking.", "Samantha", 1.0)
