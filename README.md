# Claude Code TTS Hooks

Add text-to-speech to [Claude Code](https://github.com/anthropics/claude-code) using hooks. Hear Claude's responses, get audio acknowledgments when you submit prompts, and receive dramatic announcements during context compaction.

## Features

- **Session Start Dialog** - Choose TTS provider at session start
- **Prompt Acknowledgment** - Quick audio feedback when you submit prompts ("Roger!", "Copy!", etc.)
- **Response Speech** - Hear Claude's responses read aloud
- **Compaction Announcements** - Dramatic notifications during memory compaction

## Supported TTS Providers

| Provider | Type | Cost | Quality | Setup |
|----------|------|------|---------|-------|
| **Kokoro** | Local | Free | High | Download models (~270MB) |
| **ElevenLabs** | Cloud | Pay-per-use | Premium | API key required |
| **OpenAI** | Cloud | Pay-per-use | High | API key required |
| **macOS Say** | Local | Free | Basic | Built-in (fallback) |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/nickcent/claude-code-tts-hooks.git
cd claude-code-tts-hooks

# Run the installer
./install.sh

# Restart Claude Code
```

On your next Claude Code session, a dialog will appear asking which TTS provider to use.

## Installation

### Prerequisites

- macOS (for audio playback via `afplay`)
- [uv](https://github.com/astral-sh/uv) (installed automatically if missing)
- Claude Code CLI

### Step 1: Install Hooks

```bash
./install.sh
```

The installer will:
1. Copy hooks to `~/.claude/hooks/`
2. Install utility files
3. Update `~/.claude/settings.local.json`
4. Optionally download Kokoro models

### Step 2: Configure TTS Provider

**For Kokoro (recommended for free local TTS):**
```bash
./scripts/setup-kokoro.sh
```

**For ElevenLabs:**
```bash
# Set API key (choose one method)
export ELEVENLABS_API_KEY=your-key

# Or add to ~/.claude/.env
echo "ELEVENLABS_API_KEY=your-key" >> ~/.claude/.env
```

**For OpenAI:**
```bash
# Set API key (choose one method)
export OPENAI_API_KEY=your-key

# Or add to ~/.claude/.env
echo "OPENAI_API_KEY=your-key" >> ~/.claude/.env
```

### Step 3: Test Installation

```bash
python3 scripts/test-tts.py
```

## Configuration

Edit `~/.claude/hooks/tts_config.json` to customize:

```json
{
  "session": {
    "default_mode": "kokoro",
    "show_dialog": true,
    "dialog_timeout": 15
  },
  "hooks": {
    "user_prompt_submit": {
      "enabled": true,
      "phrases": ["Roger.", "Copy.", "On it."]
    },
    "stop": {
      "enabled": true
    },
    "pre_compact": {
      "enabled": true
    }
  },
  "voices": {
    "assistant": {
      "kokoro_voice": "bf_emma",
      "speed": 1.1
    },
    "system": {
      "kokoro_voice": "af_nicole",
      "speed": 1.2
    }
  }
}
```

### Available Kokoro Voices

| Category | Voices |
|----------|--------|
| American Female | `af_bella`, `af_jessica`, `af_nicole`, `af_nova`, `af_river`, `af_sarah`, `af_sky` |
| American Male | `am_adam`, `am_echo`, `am_eric`, `am_liam`, `am_michael`, `am_onyx` |
| British Female | `bf_alice`, `bf_emma`, `bf_lily`, `bf_matilda` |
| British Male | `bm_daniel`, `bm_fable`, `bm_george`, `bm_lewis`, `bm_oliver`, `bm_oscar` |

### Available OpenAI Voices

`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

## Example Configurations

See the `examples/` directory:
- `kokoro-only.json` - Local-only setup, no cloud APIs
- `elevenlabs-only.json` - Premium cloud voices
- `custom-voices.json` - Full customization example

## Uninstall

```bash
./uninstall.sh
```

This removes hooks but preserves Kokoro models. To fully remove:
```bash
rm -rf ~/.local/share/kokoro
```

## How It Works

Claude Code supports [hooks](https://docs.anthropic.com/en/docs/claude-code/hooks) that execute at specific events:

| Hook | Event | What It Does |
|------|-------|--------------|
| `SessionStart` | Claude Code launches | Shows TTS provider dialog |
| `UserPromptSubmit` | User sends a prompt | Speaks acknowledgment phrase |
| `Stop` | Claude finishes response | Speaks the response |
| `PreCompact` | Context compaction begins | Announces compaction |

## Troubleshooting

### No sound
- Check macOS sound settings
- Verify `afplay` works: `afplay /System/Library/Sounds/Ping.aiff`

### Kokoro not working
- Run `./scripts/setup-kokoro.sh` to download models
- Check models exist: `ls ~/.local/share/kokoro/`

### ElevenLabs/OpenAI not working
- Verify API key is set: `echo $ELEVENLABS_API_KEY`
- Check `~/.claude/.env` file

### Dialog not appearing
- Check `~/.claude/settings.local.json` has the hooks configured
- Enable debug: check `/tmp/claude-tts-debug.log`

## License

MIT License - see [LICENSE](LICENSE)

## Credits

- [Kokoro ONNX](https://github.com/thewh1teagle/kokoro-onnx) - Local neural TTS
- [ElevenLabs](https://elevenlabs.io/) - Cloud TTS API
- [OpenAI](https://openai.com/) - Cloud TTS API
- [Claude Code](https://github.com/anthropics/claude-code) - The CLI this extends
