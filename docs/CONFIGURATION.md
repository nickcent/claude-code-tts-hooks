# Configuration Guide

All TTS settings are stored in `~/.claude/hooks/tts_config.json`.

## Configuration Structure

```json
{
  "version": "1.0",
  "session": { ... },
  "providers": { ... },
  "hooks": { ... },
  "voices": { ... }
}
```

## Session Settings

```json
"session": {
  "default_mode": "kokoro",
  "show_dialog": true,
  "dialog_timeout": 15
}
```

| Setting | Description | Values |
|---------|-------------|--------|
| `default_mode` | TTS provider if dialog times out or is disabled | `"kokoro"`, `"elevenlabs"`, `"openai"`, `"off"` |
| `show_dialog` | Show provider selection dialog at session start | `true`, `false` |
| `dialog_timeout` | Seconds to wait for dialog response | Integer (default: 15) |

## Provider Settings

```json
"providers": {
  "kokoro": {
    "enabled": true,
    "model_dir": "~/.local/share/kokoro"
  },
  "elevenlabs": {
    "enabled": true,
    "api_key_env": "ELEVENLABS_API_KEY"
  },
  "openai": {
    "enabled": true,
    "api_key_env": "OPENAI_API_KEY"
  },
  "macos": {
    "enabled": true
  }
}
```

## Hook Settings

### Session Start Hook

```json
"session_start": {
  "enabled": true,
  "speak_announcement": true
}
```

| Setting | Description |
|---------|-------------|
| `enabled` | Enable/disable this hook |
| `speak_announcement` | Speak "TTS enabled" message at start |

### User Prompt Submit Hook

```json
"user_prompt_submit": {
  "enabled": true,
  "phrases": [
    "Roger.", "Copy.", "On it.", "Understood."
  ]
}
```

| Setting | Description |
|---------|-------------|
| `enabled` | Enable/disable acknowledgment sounds |
| `phrases` | List of phrases to randomly choose from |

### Stop Hook

```json
"stop": {
  "enabled": true
}
```

| Setting | Description |
|---------|-------------|
| `enabled` | Enable/disable response speech |

### Pre-Compact Hook

```json
"pre_compact": {
  "enabled": true,
  "announcements": [
    "Context overflow detected. Initiating memory compaction.",
    "Memory banks full. Consolidating archived data."
  ]
}
```

| Setting | Description |
|---------|-------------|
| `enabled` | Enable/disable compaction announcements |
| `announcements` | Custom announcement phrases |

## Voice Settings

```json
"voices": {
  "assistant": {
    "kokoro_voice": "bf_emma",
    "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
    "openai_voice": "onyx",
    "macos_voice": "Samantha",
    "speed": 1.1,
    "volume": 1.0
  },
  "system": {
    "kokoro_voice": "af_sky",
    "elevenlabs_voice_id": "EXAVITQu4vr4xnSDxMaL",
    "openai_voice": "nova",
    "macos_voice": "Samantha",
    "speed": 1.2,
    "volume": 0.8
  }
}
```

### Voice Types

| Type | Used For |
|------|----------|
| `assistant` | Claude's responses (Stop hook) |
| `system` | Acknowledgments, announcements |

### Voice Parameters

| Parameter | Description | Range |
|-----------|-------------|-------|
| `kokoro_voice` | Kokoro voice name | See [PROVIDERS.md](PROVIDERS.md) |
| `elevenlabs_voice_id` | ElevenLabs voice ID | 20-char string |
| `openai_voice` | OpenAI voice name | `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer` |
| `macos_voice` | macOS voice name | `Samantha`, `Alex`, etc. |
| `speed` | Speech rate multiplier | 0.5 - 2.0 |
| `volume` | Audio volume | 0.0 - 1.0 |

## Example Configurations

### Silent by Default

Show dialog but default to silent if no selection:

```json
{
  "session": {
    "default_mode": "off",
    "show_dialog": true,
    "dialog_timeout": 10
  }
}
```

### Always Use Kokoro (No Dialog)

Skip dialog and always use Kokoro:

```json
{
  "session": {
    "default_mode": "kokoro",
    "show_dialog": false
  }
}
```

### Minimal Feedback

Only speak responses, no acknowledgments:

```json
{
  "hooks": {
    "user_prompt_submit": {
      "enabled": false
    },
    "pre_compact": {
      "enabled": false
    },
    "stop": {
      "enabled": true
    }
  }
}
```

### Custom Phrases

Use sci-fi themed phrases:

```json
{
  "hooks": {
    "user_prompt_submit": {
      "phrases": [
        "Acknowledged, Captain.",
        "Processing directive.",
        "Command received.",
        "Executing protocol."
      ]
    },
    "pre_compact": {
      "announcements": [
        "Memory core reaching capacity. Initiating defragmentation.",
        "Neural buffer overflow. Compressing data streams."
      ]
    }
  }
}
```
