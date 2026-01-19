# Troubleshooting Guide

## Common Issues

### No Audio Output

**Symptoms:** TTS appears to run but no sound plays.

**Solutions:**
1. **Check macOS sound settings**
   - Open System Preferences > Sound
   - Verify output device is correct
   - Check volume is not muted

2. **Test audio playback**
   ```bash
   afplay /System/Library/Sounds/Ping.aiff
   ```

3. **Check TTS mode is set**
   ```bash
   cat /tmp/claude_tts_session_state.json
   ```
   Should show: `{"tts_mode": "kokoro"}` (or your chosen mode)

### Dialog Not Appearing

**Symptoms:** Session starts without TTS selection dialog.

**Solutions:**
1. **Verify hooks are configured**
   ```bash
   cat ~/.claude/settings.local.json | grep -A5 SessionStart
   ```

2. **Check dialog is enabled**
   ```bash
   cat ~/.claude/hooks/tts_config.json | grep show_dialog
   ```
   Should show: `"show_dialog": true`

3. **Check for errors**
   ```bash
   cat /tmp/claude-tts-debug.log
   ```

### Kokoro Not Working

**Symptoms:** Kokoro fails, falls back to macOS Say.

**Solutions:**
1. **Verify models are installed**
   ```bash
   ls -la ~/.local/share/kokoro/
   ```
   Should show `kokoro-v1.0.onnx` and `voices-v1.0.bin`

2. **Download models**
   ```bash
   ./scripts/setup-kokoro.sh
   ```

3. **Test Kokoro directly**
   ```bash
   cd ~/.claude/hooks
   python3 -c "import sys; sys.path.insert(0, 'utils'); import kokoro_tts; kokoro_tts.speak('test')"
   ```

4. **Check Python dependencies**
   ```bash
   uv pip install kokoro-onnx soundfile
   ```

### ElevenLabs Not Working

**Symptoms:** ElevenLabs calls fail, falls back to macOS Say.

**Solutions:**
1. **Verify API key is set**
   ```bash
   echo $ELEVENLABS_API_KEY
   ```

2. **Check .env file**
   ```bash
   cat ~/.claude/.env | grep ELEVENLABS
   ```

3. **Test API directly**
   ```bash
   curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" \
     -H "xi-api-key: $ELEVENLABS_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello"}' -o test.mp3 && afplay test.mp3
   ```

4. **Check API credits**
   - Log into [elevenlabs.io](https://elevenlabs.io/)
   - Verify you have remaining characters

### OpenAI TTS Not Working

**Symptoms:** OpenAI calls fail, falls back to macOS Say.

**Solutions:**
1. **Verify API key is set**
   ```bash
   echo $OPENAI_API_KEY
   ```

2. **Test API directly**
   ```bash
   python3 -c "
   from openai import OpenAI
   client = OpenAI()
   response = client.audio.speech.create(model='tts-1', voice='onyx', input='Hello')
   response.stream_to_file('test.mp3')
   " && afplay test.mp3
   ```

3. **Check API credits**
   - Log into [platform.openai.com](https://platform.openai.com/)
   - Verify billing is active

### Hook Errors

**Symptoms:** Error messages in Claude Code output.

**Solutions:**
1. **Check debug log**
   ```bash
   tail -50 /tmp/claude-tts-debug.log
   ```

2. **Run hook manually**
   ```bash
   cd ~/.claude/hooks
   echo '{}' | python3 Stop/01-tts-response.py
   ```

3. **Check Python path**
   ```bash
   python3 -c "import sys; print(sys.path)"
   ```

4. **Verify UV installation**
   ```bash
   uv --version
   ```

### Slow Response Times

**Symptoms:** Long delay before audio plays.

**Solutions:**
1. **Use Kokoro for speed**
   - Kokoro is local and typically faster than cloud APIs

2. **Reduce text length**
   - Long responses take longer to synthesize

3. **Check network for cloud providers**
   ```bash
   ping api.elevenlabs.io
   ping api.openai.com
   ```

## Debug Mode

Enable verbose logging:

1. **Edit session_start hook**
   Add at the top:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check all logs**
   ```bash
   ls -la /tmp/*tts* /tmp/*claude*
   ```

## Getting Help

1. **Check GitHub Issues**
   - Search for similar problems
   - Create a new issue with:
     - Your configuration
     - Error messages
     - Debug log output

2. **Include diagnostics**
   ```bash
   # System info
   uname -a
   python3 --version
   uv --version

   # Config
   cat ~/.claude/hooks/tts_config.json

   # Logs
   cat /tmp/claude-tts-debug.log
   ```

## Reset Installation

If all else fails, reset and reinstall:

```bash
# Uninstall
./uninstall.sh

# Clear state
rm -f /tmp/claude_tts_session_state.json
rm -f /tmp/claude-tts-debug.log

# Reinstall
./install.sh
```
