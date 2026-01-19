#!/usr/bin/env python3
"""
Test script for Claude Code TTS hooks.
Tests all available TTS providers.
"""

import sys
from pathlib import Path

# Add utils to path
UTILS_DIR = Path(__file__).parent.parent / "utils"
sys.path.insert(0, str(UTILS_DIR))

# Also check installed location
INSTALLED_UTILS = Path.home() / ".claude" / "hooks" / "utils"
if INSTALLED_UTILS.exists():
    sys.path.insert(0, str(INSTALLED_UTILS))


def test_macos():
    """Test macOS native TTS."""
    print("\n=== Testing macOS Say ===")
    try:
        import macos_say
        result = macos_say.speak("Testing macOS native text to speech.", "Samantha", 1.0)
        print(f"Result: {'Success' if result else 'Failed'}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_kokoro():
    """Test Kokoro local TTS."""
    print("\n=== Testing Kokoro ===")
    try:
        import kokoro_tts
        kokoro = kokoro_tts.get_kokoro()
        if kokoro is None:
            print("Kokoro models not installed.")
            print("Run: scripts/setup-kokoro.sh")
            return False

        result = kokoro_tts.speak("Testing Kokoro neural text to speech. This is the Emma voice.", "bf_emma", 1.0)
        print(f"Result: {'Success' if result else 'Failed'}")
        return result
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install with: uv pip install kokoro-onnx soundfile")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_elevenlabs():
    """Test ElevenLabs cloud TTS."""
    print("\n=== Testing ElevenLabs ===")
    try:
        import elevenlabs_tts
        api_key = elevenlabs_tts.load_api_key()
        if not api_key:
            print("ElevenLabs API key not found.")
            print("Set ELEVENLABS_API_KEY environment variable or add to ~/.claude/.env")
            return False

        result = elevenlabs_tts.speak(
            "Testing ElevenLabs cloud text to speech.",
            "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
            speed=1.0
        )
        print(f"Result: {'Success' if result else 'Failed'}")
        return result
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install with: uv pip install requests")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_openai():
    """Test OpenAI cloud TTS."""
    print("\n=== Testing OpenAI TTS ===")
    try:
        import openai_tts
        api_key = openai_tts.load_api_key()
        if not api_key:
            print("OpenAI API key not found.")
            print("Set OPENAI_API_KEY environment variable or add to ~/.claude/.env")
            return False

        result = openai_tts.speak(
            "Testing OpenAI cloud text to speech.",
            voice="onyx",
            speed=1.0
        )
        print(f"Result: {'Success' if result else 'Failed'}")
        return result
    except ImportError as e:
        print(f"Import error: {e}")
        print("Install with: uv pip install openai")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_router():
    """Test TTS router."""
    print("\n=== Testing TTS Router ===")
    try:
        import tts_router

        # Test each mode
        for mode in ["kokoro", "elevenlabs", "openai", "macos"]:
            print(f"\nTesting mode: {mode}")
            try:
                result = tts_router.speak("assistant", f"Testing {mode} mode.", mode=mode)
                print(f"  Result: {'Success' if result else 'Failed (fallback may have worked)'}")
            except Exception as e:
                print(f"  Error: {e}")

        return True
    except Exception as e:
        print(f"Router error: {e}")
        return False


def main():
    """Run all tests."""
    print("╔══════════════════════════════════════════╗")
    print("║   Claude Code TTS - Provider Tests       ║")
    print("╚══════════════════════════════════════════╝")

    results = {
        "macOS": test_macos(),
        "Kokoro": test_kokoro(),
        "ElevenLabs": test_elevenlabs(),
        "OpenAI": test_openai(),
    }

    # Summary
    print("\n════════════════════════════════════════════")
    print("Test Results Summary:")
    print("════════════════════════════════════════════")

    for provider, passed in results.items():
        status = "✓ Passed" if passed else "✗ Failed/Unavailable"
        print(f"  {provider}: {status}")

    print("")

    # Test router if at least one provider works
    if any(results.values()):
        test_router()

    print("\nTest complete!")


if __name__ == "__main__":
    main()
