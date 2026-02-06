#!/bin/bash
#
# GCB Runner Installer for macOS
# 
# Usage:
#   curl -fsSL https://greatcommissionbenchmark.ai/install.sh | bash
#
# This script will:
#   1. Detect your Mac's architecture (Apple Silicon or Intel)
#   2. Download the appropriate GCB Runner binary
#   3. Remove macOS quarantine attribute
#   4. Install to /usr/local/bin (or ~/bin if no sudo)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="https://greatcommissionbenchmark.ai/downloads"
MANIFEST_URL="${BASE_URL}/manifest.json"
BINARY_NAME="gcb-runner"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      GCB Runner Installer for macOS        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running on macOS
if [[ "$(uname -s)" != "Darwin" ]]; then
    echo -e "${RED}Error: This installer is for macOS only.${NC}"
    echo "For Linux, please visit: https://greatcommissionbenchmark.ai/runner"
    exit 1
fi

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    PLATFORM="macos-arm64"
    echo -e "${GREEN}✓${NC} Detected Apple Silicon Mac (M1/M2/M3/M4)"
elif [[ "$ARCH" == "x86_64" ]]; then
    PLATFORM="macos-x64"
    echo -e "${GREEN}✓${NC} Detected Intel Mac"
else
    echo -e "${RED}Error: Unknown architecture: $ARCH${NC}"
    exit 1
fi

# Determine install directory
if [[ -w "/usr/local/bin" ]]; then
    INSTALL_DIR="/usr/local/bin"
    USE_SUDO=false
elif command -v sudo &> /dev/null && sudo -n true 2>/dev/null; then
    INSTALL_DIR="/usr/local/bin"
    USE_SUDO=true
else
    # Fall back to user's bin directory
    INSTALL_DIR="$HOME/bin"
    USE_SUDO=false
    mkdir -p "$INSTALL_DIR"
    
    # Check if ~/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
        echo -e "${YELLOW}Note: $HOME/bin is not in your PATH.${NC}"
        echo "Add this to your ~/.zshrc or ~/.bashrc:"
        echo "  export PATH=\"\$HOME/bin:\$PATH\""
    fi
fi

echo -e "${GREEN}✓${NC} Install directory: $INSTALL_DIR"

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Fetch manifest to get download info
echo ""
echo "Fetching latest version info..."
if ! MANIFEST=$(curl -fsSL "$MANIFEST_URL" 2>/dev/null); then
    echo -e "${RED}Error: Could not fetch manifest from $MANIFEST_URL${NC}"
    exit 1
fi

# Parse manifest (basic JSON parsing with grep/sed since we want to avoid dependencies)
# Strip carriage returns and trim whitespace to avoid malformed URLs (e.g. from CRLF manifest)
trim() { echo "$1" | tr -d '\r\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'; }
VERSION=$(trim "$(echo "$MANIFEST" | grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')")
FILENAME=$(trim "$(echo "$MANIFEST" | grep -A5 "\"$PLATFORM\"" | grep '"filename"' | sed 's/.*"\([^"]*\)"$/\1/' | head -1)")
SHA256=$(trim "$(echo "$MANIFEST" | grep -A5 "\"$PLATFORM\"" | grep '"sha256"' | sed 's/.*"\([^"]*\)"$/\1/' | head -1)")

if [[ -z "$FILENAME" ]]; then
    echo -e "${RED}Error: No download available for $PLATFORM${NC}"
    echo "Please visit https://greatcommissionbenchmark.ai/runner for other options."
    exit 1
fi

echo -e "${GREEN}✓${NC} Latest version: $VERSION"

DOWNLOAD_URL="${BASE_URL}/${FILENAME}"

# Download the binary
echo ""
echo "Downloading GCB Runner..."
DOWNLOAD_PATH="$TEMP_DIR/$FILENAME"

if ! curl -fSL --progress-bar "$DOWNLOAD_URL" -o "$DOWNLOAD_PATH"; then
    echo -e "${RED}Error: Download failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Download complete"

# Verify SHA256 hash
echo ""
echo "Verifying download integrity..."
ACTUAL_SHA256=$(shasum -a 256 "$DOWNLOAD_PATH" | cut -d' ' -f1)

if [[ "$ACTUAL_SHA256" != "$SHA256" ]]; then
    echo -e "${RED}Error: SHA256 hash mismatch!${NC}"
    echo "Expected: $SHA256"
    echo "Got:      $ACTUAL_SHA256"
    echo ""
    echo "The download may be corrupted or tampered with."
    exit 1
fi

echo -e "${GREEN}✓${NC} SHA256 verified"

# Remove quarantine attribute (macOS security)
echo ""
echo "Removing macOS quarantine..."
xattr -d com.apple.quarantine "$DOWNLOAD_PATH" 2>/dev/null || true
echo -e "${GREEN}✓${NC} Quarantine removed"

# Make executable
chmod +x "$DOWNLOAD_PATH"
echo -e "${GREEN}✓${NC} Made executable"

# Install to destination
echo ""
echo "Installing to $INSTALL_DIR..."
DEST_PATH="$INSTALL_DIR/$BINARY_NAME"

if [[ "$USE_SUDO" == "true" ]]; then
    sudo mv "$DOWNLOAD_PATH" "$DEST_PATH"
    sudo chmod +x "$DEST_PATH"
else
    mv "$DOWNLOAD_PATH" "$DEST_PATH"
    chmod +x "$DEST_PATH"
fi

echo -e "${GREEN}✓${NC} Installed to $DEST_PATH"

# Verify installation
echo ""
if command -v gcb-runner &> /dev/null; then
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Installation complete!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo ""
    echo "Run 'gcb-runner' to get started."
    echo ""
    echo "Quick start:"
    echo "  gcb-runner config    # Set up your API keys"
    echo "  gcb-runner           # Launch interactive menu"
    echo ""
else
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Installation complete!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo ""
    if [[ "$INSTALL_DIR" == "$HOME/bin" ]]; then
        echo "To use gcb-runner, either:"
        echo "  1. Run: $DEST_PATH"
        echo "  2. Add ~/bin to your PATH and restart your terminal"
        echo ""
    else
        echo "Run '$DEST_PATH' to get started."
        echo ""
    fi
fi

echo "Documentation: https://greatcommissionbenchmark.ai/runner"
echo ""
