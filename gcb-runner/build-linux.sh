#!/bin/bash
# Script to build Linux executable using Docker

set -e

echo "Building Linux executable using Docker..."
echo ""

# Build the Docker image
docker build -f Dockerfile.build-linux -t gcb-runner-builder .

# Create output directory locally
mkdir -p ./dist/release

# Create a temporary container and find the executable
echo "Locating built executable..."
CONTAINER_ID=$(docker create gcb-runner-builder)

# Try to copy from the expected location first
if docker cp $CONTAINER_ID:/build/dist/release/gcb-runner-linux-x64 ./dist/release/gcb-runner-linux-x64 2>/dev/null; then
    echo "✅ Found executable at /build/dist/release/gcb-runner-linux-x64"
elif docker cp $CONTAINER_ID:/build/dist/gcb-runner ./dist/release/gcb-runner-linux-x64 2>/dev/null; then
    echo "✅ Found executable at /build/dist/gcb-runner (renamed to gcb-runner-linux-x64)"
else
    echo "Error: Could not find built executable in container"
    echo ""
    echo "Attempting to list container contents..."
    # Run a command to list files
    docker run --rm gcb-runner-builder find /build/dist -type f -name "*gcb-runner*" 2>/dev/null || \
    docker run --rm gcb-runner-builder ls -laR /build/dist 2>/dev/null || \
    echo "Could not inspect container contents"
    
    docker rm $CONTAINER_ID >/dev/null 2>&1
    exit 1
fi

# Make sure it's executable
chmod +x ./dist/release/gcb-runner-linux-x64

# Clean up
docker rm $CONTAINER_ID >/dev/null 2>&1

echo ""
echo "✅ Linux executable built successfully!"
echo "Location: ./dist/release/gcb-runner-linux-x64"
echo ""
echo "To verify:"
echo "  file ./dist/release/gcb-runner-linux-x64"
echo "  ls -lh ./dist/release/gcb-runner-linux-x64"
