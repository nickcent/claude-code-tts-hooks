# Installation Guide

## Prerequisites

- **macOS** - Required for `afplay` audio playback
- **Python 3.10+** - For running hook scripts
- **uv** - [Astral UV](https://github.com/astral-sh/uv) for Python dependency management
- **Claude Code** - The Anthropic CLI tool

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
git clone https://github.com/yourusername/claude-code-tts-hooks.git
cd claude-code-tts-hooks
./install.sh
```

### Method 2: Manual Install

1. **Create hook directories:**
   ```bash
   mkdir -p ~/.claude/hooks/{SessionStart,UserPromptSubmit,Stop,PreCompact,utils}
   ```

2. **Copy hook files:**
   ```bash
   cp hooks/SessionStart/01-tts-init.py ~/.claude/hooks/SessionStart/
   cp hooks/UserPromptSubmit/01-acknowledge.py ~/.claude/hooks/UserPromptSubmit/
   cp hooks/Stop/01-tts-response.py ~/.claude/hooks/Stop/
   cp hooks/PreCompact/01-announce.py ~/.claude/hooks/PreCompact/
   cp utils/*.py ~/.claude/hooks/utils/
   cp config/tts_config.json ~/.claude/hooks/
   ```

3. **Configure Claude Code settings:**

   Edit `~/.claude/settings.local.json`:
   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "type": "command",
           "command": "uv run $HOME/.claude/hooks/SessionStart/01-tts-init.py"
         }
       ],
       "UserPromptSubmit": [
         {
           "type": "command",
           "command": "uv run $HOME/.claude/hooks/UserPromptSubmit/01-acknowledge.py"
         }
       ],
       "Stop": [
         {
           "type": "command",
           "command": "uv run $HOME/.claude/hooks/Stop/01-tts-response.py"
         }
       ],
       "PreCompact": [
         {
           "type": "command",
           "command": "uv run $HOME/.claude/hooks/PreCompact/01-announce.py"
         }
       ]
     }
   }
   ```

4. **Make scripts executable:**
   ```bash
   chmod +x ~/.claude/hooks/*/*.py
   ```

## Setting Up TTS Providers

### Kokoro (Free Local TTS)

Kokoro provides high-quality neural TTS that runs entirely locally.

1. **Download models:**
   ```bash
   ./scripts/setup-kokoro.sh
   ```

   This downloads ~270MB of model files to `~/.local/share/kokoro/`

2. **Install Python dependencies:**
   ```bash
   uv pip install kokoro-onnx soundfile
   ```

3. **Test:**
   ```bash
   python3 -c "import kokoro_tts; kokoro_tts.speak('Hello')"
   ```

### ElevenLabs (Cloud TTS)

ElevenLabs offers premium AI voices with exceptional quality.

1. **Get API key** from [elevenlabs.io](https://elevenlabs.io/)

2. **Set API key:**
   ```bash
   # Option 1: Environment variable
   export ELEVENLABS_API_KEY=your-api-key

   # Option 2: Add to ~/.claude/.env
   echo "ELEVENLABS_API_KEY=your-api-key" >> ~/.claude/.env

   # Option 3: Add to config file
   mkdir -p ~/.config/elevenlabs
   echo "your-api-key" > ~/.config/elevenlabs/api_key
   ```

3. **Install Python dependencies:**
   ```bash
   uv pip install requests
   ```

### OpenAI TTS (Cloud TTS)

OpenAI provides high-quality TTS as part of their API.

1. **Get API key** from [platform.openai.com](https://platform.openai.com/)

2. **Set API key:**
   ```bash
   # Option 1: Environment variable
   export OPENAI_API_KEY=your-api-key

   # Option 2: Add to ~/.claude/.env
   echo "OPENAI_API_KEY=your-api-key" >> ~/.claude/.env
   ```

3. **Install Python dependencies:**
   ```bash
   uv pip install openai
   ```

## Verifying Installation

Run the test script to verify all providers:

```bash
python3 scripts/test-tts.py
```

Expected output:
```
╔══════════════════════════════════════════╗
║   Claude Code TTS - Provider Tests       ║
╚══════════════════════════════════════════╝

=== Testing macOS Say ===
Result: Success

=== Testing Kokoro ===
Result: Success

=== Testing ElevenLabs ===
Result: Success

=== Testing OpenAI TTS ===
Result: Success
```

## Post-Installation

1. **Restart Claude Code** to load the new hooks

2. **Select TTS provider** when the dialog appears at session start

3. **Customize settings** by editing `~/.claude/hooks/tts_config.json`

## Updating

To update to the latest version:

```bash
cd claude-code-tts-hooks
git pull
./install.sh
```

Your `tts_config.json` will be backed up before updating.
