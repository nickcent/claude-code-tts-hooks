# Claude Code TTS Hooks - Utility modules
"""
TTS provider utilities for Claude Code hooks.

Providers:
- kokoro_tts: Local neural TTS (82M parameters, free)
- elevenlabs_tts: Cloud TTS (ElevenLabs API)
- openai_tts: Cloud TTS (OpenAI API)
- macos_say: macOS native TTS (fallback)

Utilities:
- tts_router: Mode-aware provider selection
- session_state: TTS mode persistence
- tts_dialog: macOS AppleScript dialogs
"""

__version__ = "1.0.0"
