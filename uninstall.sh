#!/bin/bash
# Claude Code TTS Hooks - Uninstall Script
#
# This script removes TTS hooks from your ~/.claude directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS_FILE="$CLAUDE_DIR/settings.local.json"

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Claude Code TTS Hooks - Uninstaller    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}This will remove TTS hooks from ~/.claude${NC}"
read -p "Continue? [y/N] " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Remove hook files
echo -e "${BLUE}Removing hook files...${NC}"

# SessionStart
if [ -f "$HOOKS_DIR/SessionStart/01-tts-init.py" ]; then
    rm "$HOOKS_DIR/SessionStart/01-tts-init.py"
    echo "  Removed SessionStart/01-tts-init.py"
fi

# UserPromptSubmit
if [ -f "$HOOKS_DIR/UserPromptSubmit/01-acknowledge.py" ]; then
    rm "$HOOKS_DIR/UserPromptSubmit/01-acknowledge.py"
    echo "  Removed UserPromptSubmit/01-acknowledge.py"
fi

# Stop
if [ -f "$HOOKS_DIR/Stop/01-tts-response.py" ]; then
    rm "$HOOKS_DIR/Stop/01-tts-response.py"
    echo "  Removed Stop/01-tts-response.py"
fi

# PreCompact
if [ -f "$HOOKS_DIR/PreCompact/01-announce.py" ]; then
    rm "$HOOKS_DIR/PreCompact/01-announce.py"
    echo "  Removed PreCompact/01-announce.py"
fi

# Remove utils
echo -e "${BLUE}Removing utility files...${NC}"
TTS_UTILS=(
    "macos_say.py"
    "kokoro_tts.py"
    "elevenlabs_tts.py"
    "openai_tts.py"
    "tts_router.py"
    "tts_dialog.py"
    "session_state.py"
    "__init__.py"
)

for util in "${TTS_UTILS[@]}"; do
    if [ -f "$HOOKS_DIR/utils/$util" ]; then
        rm "$HOOKS_DIR/utils/$util"
        echo "  Removed utils/$util"
    fi
done

# Remove config
if [ -f "$HOOKS_DIR/tts_config.json" ]; then
    echo -e "${YELLOW}Backing up tts_config.json to tts_config.json.uninstalled${NC}"
    mv "$HOOKS_DIR/tts_config.json" "$HOOKS_DIR/tts_config.json.uninstalled"
fi

# Update settings.local.json
echo -e "${BLUE}Updating Claude Code settings...${NC}"

if [ -f "$SETTINGS_FILE" ]; then
    python3 << 'PYTHON_SCRIPT'
import json
from pathlib import Path

settings_file = Path.home() / ".claude" / "settings.local.json"

with open(settings_file) as f:
    settings = json.load(f)

# Remove TTS hook entries
if "hooks" in settings:
    tts_patterns = ["tts-init.py", "acknowledge.py", "tts-response.py", "announce.py"]

    for hook_name in list(settings["hooks"].keys()):
        hooks = settings["hooks"][hook_name]
        settings["hooks"][hook_name] = [
            h for h in hooks
            if not any(p in h.get("command", "") for p in tts_patterns)
        ]

        # Remove empty hook arrays
        if not settings["hooks"][hook_name]:
            del settings["hooks"][hook_name]

    # Remove hooks key if empty
    if not settings["hooks"]:
        del settings["hooks"]

with open(settings_file, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

print("  Settings updated")
PYTHON_SCRIPT
fi

# Remove empty directories
for dir in SessionStart UserPromptSubmit Stop PreCompact utils; do
    if [ -d "$HOOKS_DIR/$dir" ] && [ -z "$(ls -A "$HOOKS_DIR/$dir")" ]; then
        rmdir "$HOOKS_DIR/$dir"
        echo "  Removed empty directory: $dir"
    fi
done

# Clean up session state
if [ -f "/tmp/claude_tts_session_state.json" ]; then
    rm "/tmp/claude_tts_session_state.json"
    echo "  Removed session state file"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Uninstall complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Note:${NC}"
echo "  - Kokoro models were NOT removed (~/.local/share/kokoro)"
echo "  - To remove Kokoro models: rm -rf ~/.local/share/kokoro"
echo "  - Your config was backed up to tts_config.json.uninstalled"
echo ""
echo "Restart Claude Code to complete uninstallation."
