#!/bin/bash
# Claude Code TTS Hooks - Installation Script
#
# This script installs the TTS hooks to your ~/.claude directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS_FILE="$CLAUDE_DIR/settings.local.json"

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Claude Code TTS Hooks - Installer      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}Warning: 'uv' not found. Installing uv (Astral)...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo -e "${GREEN}uv installed successfully${NC}"
fi

# Create directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p "$HOOKS_DIR/SessionStart"
mkdir -p "$HOOKS_DIR/UserPromptSubmit"
mkdir -p "$HOOKS_DIR/Stop"
mkdir -p "$HOOKS_DIR/PreCompact"
mkdir -p "$HOOKS_DIR/utils"

# Copy hook files
echo -e "${BLUE}Installing hook files...${NC}"
cp "$SCRIPT_DIR/hooks/SessionStart/01-tts-init.py" "$HOOKS_DIR/SessionStart/"
cp "$SCRIPT_DIR/hooks/UserPromptSubmit/01-acknowledge.py" "$HOOKS_DIR/UserPromptSubmit/"
cp "$SCRIPT_DIR/hooks/Stop/01-tts-response.py" "$HOOKS_DIR/Stop/"
cp "$SCRIPT_DIR/hooks/PreCompact/01-announce.py" "$HOOKS_DIR/PreCompact/"

# Copy utility files
echo -e "${BLUE}Installing utility files...${NC}"
cp "$SCRIPT_DIR/utils/"*.py "$HOOKS_DIR/utils/"

# Copy config file
echo -e "${BLUE}Installing configuration...${NC}"
if [ -f "$HOOKS_DIR/tts_config.json" ]; then
    echo -e "${YELLOW}  tts_config.json already exists, backing up...${NC}"
    cp "$HOOKS_DIR/tts_config.json" "$HOOKS_DIR/tts_config.json.bak"
fi
cp "$SCRIPT_DIR/config/tts_config.json" "$HOOKS_DIR/"

# Update settings.local.json
echo -e "${BLUE}Updating Claude Code settings...${NC}"

if [ -f "$SETTINGS_FILE" ]; then
    echo -e "${YELLOW}  settings.local.json exists, merging hooks...${NC}"

    # Create a Python script to merge JSON
    python3 << 'PYTHON_SCRIPT'
import json
import sys
from pathlib import Path

settings_file = Path.home() / ".claude" / "settings.local.json"
template_file = Path(sys.argv[1] if len(sys.argv) > 1 else ".") / "config" / "settings.local.json.template"

# Load existing settings
with open(settings_file) as f:
    settings = json.load(f)

# Load template hooks
with open(template_file) as f:
    template = json.load(f)

# Merge hooks
if "hooks" not in settings:
    settings["hooks"] = {}

for hook_name, hook_config in template.get("hooks", {}).items():
    if hook_name not in settings["hooks"]:
        settings["hooks"][hook_name] = hook_config
    else:
        # Check if this hook is already installed
        existing = settings["hooks"][hook_name]
        new_commands = [h.get("command", "") for h in hook_config]
        existing_commands = [h.get("command", "") for h in existing]

        for i, cmd in enumerate(new_commands):
            if cmd not in existing_commands:
                existing.append(hook_config[i])

        settings["hooks"][hook_name] = existing

# Write updated settings
with open(settings_file, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")

print("  Settings merged successfully")
PYTHON_SCRIPT
else
    echo -e "${GREEN}  Creating new settings.local.json...${NC}"
    cp "$SCRIPT_DIR/config/settings.local.json.template" "$SETTINGS_FILE"
fi

# Make scripts executable
chmod +x "$HOOKS_DIR/SessionStart/"*.py
chmod +x "$HOOKS_DIR/UserPromptSubmit/"*.py
chmod +x "$HOOKS_DIR/Stop/"*.py
chmod +x "$HOOKS_DIR/PreCompact/"*.py

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Installed files:${NC}"
echo "  ~/.claude/hooks/SessionStart/01-tts-init.py"
echo "  ~/.claude/hooks/UserPromptSubmit/01-acknowledge.py"
echo "  ~/.claude/hooks/Stop/01-tts-response.py"
echo "  ~/.claude/hooks/PreCompact/01-announce.py"
echo "  ~/.claude/hooks/utils/*.py"
echo "  ~/.claude/hooks/tts_config.json"
echo ""

# Optional: Install Kokoro models
echo -e "${YELLOW}Would you like to install Kokoro models for local TTS? (270MB download)${NC}"
read -p "Install Kokoro? [y/N] " install_kokoro

if [[ "$install_kokoro" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Installing Kokoro models...${NC}"
    "$SCRIPT_DIR/scripts/setup-kokoro.sh"
fi

echo ""
echo -e "${GREEN}Setup complete! Restart Claude Code to activate TTS.${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Restart Claude Code"
echo "  2. On session start, select your preferred TTS provider"
echo "  3. Edit ~/.claude/hooks/tts_config.json to customize"
echo ""
echo -e "${BLUE}For ElevenLabs/OpenAI, set API keys:${NC}"
echo "  export ELEVENLABS_API_KEY=your-key"
echo "  export OPENAI_API_KEY=your-key"
echo "  (or add to ~/.claude/.env)"
