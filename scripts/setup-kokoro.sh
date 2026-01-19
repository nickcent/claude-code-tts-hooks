#!/bin/bash
# Kokoro TTS Model Setup Script
#
# Downloads Kokoro models for local neural TTS
# Models are ~270MB total

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

KOKORO_DIR="$HOME/.local/share/kokoro"
MODEL_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Kokoro TTS Model Setup                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Check for curl
if ! command -v curl &> /dev/null; then
    echo "Error: curl is required but not installed."
    exit 1
fi

# Create directory
echo -e "${BLUE}Creating model directory: $KOKORO_DIR${NC}"
mkdir -p "$KOKORO_DIR"

# Download model file
MODEL_FILE="$KOKORO_DIR/kokoro-v1.0.onnx"
if [ -f "$MODEL_FILE" ]; then
    echo -e "${YELLOW}Model file already exists, skipping...${NC}"
else
    echo -e "${BLUE}Downloading Kokoro model (224MB)...${NC}"
    curl -L -o "$MODEL_FILE" "$MODEL_URL/kokoro-v1.0.onnx"
    echo -e "${GREEN}Model downloaded${NC}"
fi

# Download voices file
VOICES_FILE="$KOKORO_DIR/voices-v1.0.bin"
if [ -f "$VOICES_FILE" ]; then
    echo -e "${YELLOW}Voices file already exists, skipping...${NC}"
else
    echo -e "${BLUE}Downloading Kokoro voices (46MB)...${NC}"
    curl -L -o "$VOICES_FILE" "$MODEL_URL/voices-v1.0.bin"
    echo -e "${GREEN}Voices downloaded${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Kokoro setup complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""
echo "Models installed to: $KOKORO_DIR"
echo ""
echo "Available voices:"
echo "  American Female: af_bella, af_jessica, af_nicole, af_nova, af_river, af_sarah, af_sky"
echo "  American Male:   am_adam, am_echo, am_eric, am_liam, am_michael, am_onyx"
echo "  British Female:  bf_alice, bf_emma, bf_lily, bf_matilda"
echo "  British Male:    bm_daniel, bm_fable, bm_george, bm_lewis, bm_oliver, bm_oscar"
echo ""
echo "Test with: python3 -c \"import sys; sys.path.insert(0, '$HOME/.claude/hooks/utils'); import kokoro_tts; kokoro_tts.speak('Hello world')\""
