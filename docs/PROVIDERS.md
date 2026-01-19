# TTS Provider Reference

## Kokoro

**Type:** Local neural TTS
**Cost:** Free
**Quality:** High (82M parameter model)
**Latency:** Fast (~200ms for short text)

### Setup

```bash
./scripts/setup-kokoro.sh
```

### Voice List

#### American Female (af_*)
| Voice | Description |
|-------|-------------|
| `af_alloy` | Neutral, balanced |
| `af_aoede` | Musical, flowing |
| `af_bella` | Warm, friendly |
| `af_heart` | Expressive, emotional |
| `af_jessica` | Professional, clear |
| `af_kore` | Youthful, energetic |
| `af_nicole` | Calm, measured |
| `af_nova` | Bright, engaging |
| `af_river` | Smooth, natural |
| `af_sarah` | Conversational |
| `af_sky` | Light, airy |

#### American Male (am_*)
| Voice | Description |
|-------|-------------|
| `am_adam` | Deep, authoritative |
| `am_echo` | Resonant, clear |
| `am_eric` | Friendly, approachable |
| `am_liam` | Young, energetic |
| `am_michael` | Professional, neutral |
| `am_onyx` | Rich, baritone |

#### British Female (bf_*)
| Voice | Description |
|-------|-------------|
| `bf_alice` | Refined, elegant |
| `bf_emma` | Warm, articulate |
| `bf_lily` | Soft, gentle |
| `bf_matilda` | Clear, professional |

#### British Male (bm_*)
| Voice | Description |
|-------|-------------|
| `bm_daniel` | Distinguished, formal |
| `bm_fable` | Storytelling, expressive |
| `bm_george` | Deep, commanding |
| `bm_lewis` | Modern, clear |
| `bm_oliver` | Young, friendly |
| `bm_oscar` | Mature, warm |

### Recommended Voices

- **Assistant responses:** `bf_emma` (articulate), `bm_george` (authoritative)
- **System announcements:** `af_sky` (light), `af_nova` (bright)
- **Dramatic moments:** `bm_fable` (storytelling), `am_onyx` (deep)

---

## ElevenLabs

**Type:** Cloud API
**Cost:** Pay-per-character ([pricing](https://elevenlabs.io/pricing))
**Quality:** Premium
**Latency:** ~500ms (streaming)

### Setup

1. Create account at [elevenlabs.io](https://elevenlabs.io/)
2. Get API key from dashboard
3. Set `ELEVENLABS_API_KEY` environment variable

### Popular Voice IDs

| Voice | ID | Description |
|-------|-----|-------------|
| Rachel | `21m00Tcm4TlvDq8ikWAM` | Calm American female |
| Bella | `EXAVITQu4vr4xnSDxMaL` | Expressive young female |
| Adam | `pNInz6obpgDQGcFmaJgB` | Deep American male |
| Josh | `TxGEqnHWrfWFTfGW9XjX` | Young American male |
| Arnold | `VR6AewLTigWG4xSOukaG` | Strong, authoritative |
| Elli | `MF3mGyEYCl7XYWbV9V6O` | Young American female |

### Finding Voice IDs

1. Go to [ElevenLabs Voices](https://elevenlabs.io/voices)
2. Click on a voice
3. Voice ID is in the URL or settings

### Configuration

```json
"voices": {
  "assistant": {
    "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
    "speed": 1.0
  }
}
```

**Note:** ElevenLabs speed is limited to 0.7-1.2 range.

---

## OpenAI TTS

**Type:** Cloud API
**Cost:** $15/1M characters (tts-1), $30/1M characters (tts-1-hd)
**Quality:** High
**Latency:** ~300ms

### Setup

1. Get API key from [platform.openai.com](https://platform.openai.com/)
2. Set `OPENAI_API_KEY` environment variable

### Voice List

| Voice | Description |
|-------|-------------|
| `alloy` | Neutral, balanced |
| `echo` | Warm, conversational |
| `fable` | British, narrative |
| `onyx` | Deep, authoritative |
| `nova` | Bright, energetic |
| `shimmer` | Soft, gentle |

### Models

| Model | Quality | Cost |
|-------|---------|------|
| `tts-1` | Standard | $15/1M chars |
| `tts-1-hd` | High definition | $30/1M chars |

### Configuration

```json
"voices": {
  "assistant": {
    "openai_voice": "onyx",
    "speed": 1.0
  }
}
```

**Note:** OpenAI speed range is 0.25-4.0.

---

## macOS Say

**Type:** Built-in
**Cost:** Free
**Quality:** Basic
**Latency:** Instant

macOS Say is always available as a fallback.

### Voice List

Get available voices:
```bash
say -v '?'
```

Common voices:
- `Samantha` - Default US female
- `Alex` - US male (compact)
- `Tom` - US male
- `Victoria` - US female (premium)
- `Daniel` - UK male

### Configuration

```json
"voices": {
  "assistant": {
    "macos_voice": "Samantha",
    "speed": 1.0
  }
}
```

---

## Comparison

| Feature | Kokoro | ElevenLabs | OpenAI | macOS |
|---------|--------|------------|--------|-------|
| Cost | Free | ~$0.30/1K chars | ~$0.015/1K chars | Free |
| Quality | High | Premium | High | Basic |
| Latency | 200ms | 500ms | 300ms | 50ms |
| Offline | Yes | No | No | Yes |
| Voice cloning | No | Yes | No | No |
| Voices | 26 | 100s | 6 | 20+ |
