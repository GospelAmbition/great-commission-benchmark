# Local Model Setup Instructions

This document provides step-by-step instructions for setting up local models to run the Great Commission Benchmark using the CLI runner. Local testing enables offline operation after initial setup and avoids per-request API costs.

**Last Updated:** December 16, 2025

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Overview of Local Options](#overview-of-local-options)
3. [LM Studio Setup](#lm-studio-setup) (Recommended)
4. [Ollama Setup](#ollama-setup)
5. [Judge Model Setup](#judge-model-setup)
6. [CLI Runner Configuration](#cli-runner-configuration)
7. [Running Tests Locally](#running-tests-locally)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tips](#performance-tips)

---

## Prerequisites

Before setting up local models, ensure your system meets the minimum requirements:

### Hardware Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **RAM** | 16 GB | 32 GB | Must run both test model and judge model simultaneously |
| **Storage** | 50 GB free | 100 GB free | Models are 4-80 GB each |
| **CPU** | 4 cores | 8+ cores | Multi-core helps with inference |
| **GPU** | Optional | NVIDIA 8GB+ VRAM | Significantly speeds up inference |
| **Internet** | 5 Mbps | 25+ Mbps | For initial model downloads only |

### Software Requirements

| Software | Required Version | Purpose |
|----------|-----------------|---------|
| **Python** | 3.9+ (3.11+ recommended) | CLI runner |
| **GCB Runner** | Latest | CLI tool for running benchmarks |
| **LM Studio** or **Ollama** | Latest | Local model runtime |

### Memory Considerations

**Critical:** The CLI runner requires both a test model AND a judge model to run simultaneously.

**Example memory allocation (32 GB RAM):**
- Judge model (gpt-oss-20b quantized): ~12-14 GB
- Test model (7B-13B quantized): ~4-8 GB
- System overhead: ~4 GB
- Buffer: ~6-12 GB

**Example memory allocation (16 GB RAM):**
- Judge model (gpt-oss-20b quantized): ~12-14 GB
- Test model (small, 7B quantized): ~4-6 GB
- System overhead: ~2 GB
- **Note:** May require swap/memory offloading; expect slower performance

---

## Overview of Local Options

The CLI runner supports two local backends:

| Backend | Description | Best For | API Endpoint |
|---------|-------------|----------|--------------|
| **LM Studio** | GUI application with model browser | Most users; interactive testing | `http://localhost:1234/v1` |
| **Ollama** | CLI-focused with simple commands | Automation; scripting; servers | `http://localhost:11434` |

### LM Studio vs Ollama

| Feature | LM Studio | Ollama |
|---------|-----------|--------|
| **Interface** | ✅ Visual GUI | CLI only |
| **Model Discovery** | ✅ Built-in browser | Manual download |
| **Resource Monitoring** | ✅ Visual graphs | CLI tools |
| **API Format** | OpenAI-compatible | Custom API |
| **Batch Automation** | Basic | ✅ Better for scripting |
| **Server Deployment** | Desktop use | ✅ Better for servers |

**Recommendation:** Use **LM Studio** unless you need headless/server operation or prefer CLI workflows.

---

## LM Studio Setup

LM Studio is the recommended option for most users due to its user-friendly interface and OpenAI-compatible API.

### Step 1: Download and Install LM Studio

1. Visit [https://lmstudio.ai](https://lmstudio.ai)
2. Download the installer for your operating system:
   - **macOS:** `.dmg` file (Apple Silicon or Intel)
   - **Windows:** `.exe` installer
   - **Linux:** `.AppImage` or `.deb` package
3. Run the installer and follow the prompts
4. Launch LM Studio

### Step 2: Download Models

**Download the Judge Model (Required):**

1. In LM Studio, click the **Search** icon (magnifying glass) in the left sidebar
2. Search for `gpt-oss-20b`
3. Select a quantized version:
   - **Recommended:** `Q4_K_M` (good balance of quality and size, ~40 GB)
   - **Alternative:** `Q5_K_M` (higher quality, ~50 GB)
   - **Low memory:** `Q3_K_M` (smaller, ~30 GB, lower quality)
4. Click **Download**
5. Wait for download to complete (may take several hours depending on connection)

**Download Test Models:**

Repeat the process for any models you want to test:
- Search for the model name (e.g., `llama-3.2`, `mistral`, `phi-3`)
- Select an appropriate quantization (Q4_K_M recommended for most)
- Download

**Popular models for testing:**
- Llama 3.2 (7B, 13B, 70B)
- Mistral (7B, Small 22B)
- Phi-3 (mini, small, medium)
- Qwen 2.5 (7B, 14B, 72B)
- Gemma 2 (9B, 27B)

### Step 3: Start the Local Server

1. Click the **Local Server** icon (server/API icon) in the left sidebar
2. Select the model you want to load from the dropdown
3. Click **Start Server**
4. Verify the server is running:
   - Status should show "Server running"
   - Note the port (default: `1234`)
   - The API endpoint will be: `http://localhost:1234/v1`

**Server Settings (Optional):**
- **Context Length:** Default is usually fine; increase for longer conversations
- **GPU Offload:** Set to maximum layers your GPU can handle
- **Threads:** Set to number of CPU cores for CPU inference

### Step 4: Verify Server is Running

Test the server with a curl command:

```bash
curl http://localhost:1234/v1/models
```

Expected response:

```json
{
  "data": [
    {
      "id": "gpt-oss-20b-Q4_K_M",
      "object": "model",
      "owned_by": "lmstudio"
    }
  ]
}
```

Or test with a simple completion:

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss-20b-Q4_K_M",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }'
```

---

## Ollama Setup

Ollama is the preferred option for CLI-focused users, automation, or server deployments.

### Step 1: Download and Install Ollama

**macOS/Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**

1. Download from [https://ollama.com/download/windows](https://ollama.com/download/windows)
2. Run the installer

**Verify installation:**

```bash
ollama --version
```

### Step 2: Download Models

**Download the Judge Model (Required):**

```bash
# Download gpt-oss-20b (verify exact model name on Ollama library)
ollama pull gpt-oss-20b
```

**Note:** Model names in Ollama may differ from LM Studio. Check the [Ollama Model Library](https://ollama.com/library) for available models and exact names.

**Download Test Models:**

```bash
# Examples - download models you want to test
ollama pull llama3.2
ollama pull mistral
ollama pull phi3
ollama pull qwen2.5:7b
```

**List downloaded models:**

```bash
ollama list
```

### Step 3: Start the Ollama Server

Ollama runs as a background service. Start it with:

```bash
ollama serve
```

Or on most systems, it starts automatically after installation.

**Verify the server is running:**

```bash
curl http://localhost:11434/api/tags
```

### Step 4: Test Model Loading

```bash
# Test a simple prompt
ollama run gpt-oss-20b "Hello, respond with just 'OK' if you're working."
```

Or via API:

```bash
curl http://localhost:11434/api/generate \
  -d '{
    "model": "gpt-oss-20b",
    "prompt": "Hello",
    "stream": false
  }'
```

---

## Judge Model Setup

The Great Commission Benchmark uses **gpt-oss-20b** as the default judge model. This model evaluates the test model's responses and assigns verdicts.

### Why gpt-oss-20b?

| Capability | Score | Relevance |
|------------|-------|-----------|
| **Reasoning** | 89.8% | Critical for evaluating responses |
| **Instruction Following** | 66% | Essential for judge prompts |
| **General Knowledge** | 99% | Needed for context understanding |
| **Ethics Understanding** | 99% | Important for religious content |

### Judge Model Requirements

**Storage:** 40-80 GB depending on quantization
**RAM:** 12-14 GB when loaded
**GPU:** Optional but significantly improves speed

### Quantization Recommendations

| Quantization | Size | Quality | Speed | Recommended For |
|--------------|------|---------|-------|-----------------|
| **Q3_K_M** | ~30 GB | ⭐⭐⭐ | Fast | Low memory systems |
| **Q4_K_M** | ~40 GB | ⭐⭐⭐⭐ | Moderate | **Most users** |
| **Q5_K_M** | ~50 GB | ⭐⭐⭐⭐⭐ | Slower | Maximum quality |
| **Q6_K** | ~60 GB | ⭐⭐⭐⭐⭐ | Slow | High-end systems |

**Recommendation:** Use **Q4_K_M** for the best balance of quality and performance.

### Loading the Judge Model

**In LM Studio:**
1. The judge model should be loaded in addition to the test model
2. LM Studio can run multiple models if you have sufficient RAM
3. Alternatively, the CLI runner will manage model loading automatically

**In Ollama:**
- Ollama handles model loading automatically per request
- Ensure the judge model is downloaded: `ollama pull gpt-oss-20b`

---

## CLI Runner Configuration

Configure the CLI runner to use your local backend.

### Configuration File

Create or edit `~/.gcb-runner/config.json`:

**For LM Studio:**

```json
{
  "defaults": {
    "backend": "lmstudio",
    "judge_model": "gpt-oss-20b-Q4_K_M"
  },
  "backends": {
    "lmstudio": {
      "base_url": "http://localhost:1234/v1"
    }
  }
}
```

**For Ollama:**

```json
{
  "defaults": {
    "backend": "ollama",
    "judge_model": "gpt-oss-20b"
  },
  "backends": {
    "ollama": {
      "base_url": "http://localhost:11434"
    }
  }
}
```

### Environment Variables

Alternatively, configure via environment variables:

```bash
# For LM Studio
export GCB_BACKEND=lmstudio
export GCB_LMSTUDIO_URL=http://localhost:1234/v1
export GCB_JUDGE_MODEL=gpt-oss-20b-Q4_K_M

# For Ollama
export GCB_BACKEND=ollama
export GCB_OLLAMA_URL=http://localhost:11434
export GCB_JUDGE_MODEL=gpt-oss-20b
```

### Verify Configuration

```bash
gcb-runner config show
```

Expected output:

```
GCB Runner Configuration
========================
Backend: lmstudio
Judge Model: gpt-oss-20b-Q4_K_M
LM Studio URL: http://localhost:1234/v1
```

---

## Running Tests Locally

### Basic Local Test

**With LM Studio:**

```bash
# Ensure LM Studio server is running with your test model loaded
gcb-runner test --model llama3.2-7b --backend lmstudio
```

**With Ollama:**

```bash
# Ensure Ollama server is running
gcb-runner test --model llama3.2 --backend ollama
```

### Specifying the Judge Model

```bash
gcb-runner test \
  --model llama3.2-7b \
  --backend lmstudio \
  --judge-model gpt-oss-20b-Q4_K_M
```

### Running with a System Prompt

```bash
gcb-runner test \
  --model llama3.2-7b \
  --backend lmstudio \
  --system-prompt "You are a helpful assistant focused on Christian ministry."
```

### Resuming Interrupted Tests

If a test is interrupted (e.g., system restart, power outage):

```bash
gcb-runner test --resume
```

### Saving Results to File

```bash
gcb-runner test \
  --model llama3.2-7b \
  --backend lmstudio \
  --output results-llama3.2-7b.json
```

---

## Troubleshooting

### Connection Errors

**Error:** `Connection refused to http://localhost:1234/v1`

**Solutions:**
1. Verify the local server is running
   - LM Studio: Check "Local Server" tab shows "Server running"
   - Ollama: Run `ollama serve` or check if service is running
2. Check the port number matches your configuration
3. Try accessing the URL in a browser: `http://localhost:1234/v1/models`

### Out of Memory Errors

**Error:** `CUDA out of memory` or `Failed to allocate memory`

**Solutions:**
1. Use a smaller quantization (Q3_K_M instead of Q4_K_M)
2. Close other applications to free RAM
3. Reduce context length in LM Studio settings
4. If using GPU, reduce GPU layers offloaded
5. Consider testing smaller models (7B instead of 13B)

**Memory estimation:**
- 7B model (Q4): ~4-6 GB
- 13B model (Q4): ~8-10 GB
- 20B model (Q4): ~12-14 GB
- 70B model (Q4): ~40-50 GB

### Model Not Found

**Error:** `Model 'xyz' not found`

**Solutions:**
1. Verify the model is downloaded
   - LM Studio: Check "My Models" in the sidebar
   - Ollama: Run `ollama list`
2. Check exact model name spelling (case-sensitive)
3. In LM Studio, ensure the model is loaded in the server

### Slow Performance

**Possible causes and solutions:**

| Issue | Solution |
|-------|----------|
| CPU-only inference | Add GPU offloading if GPU available |
| Insufficient RAM | Use smaller quantization or model |
| Thermal throttling | Ensure adequate cooling; reduce load |
| Disk swapping | Close other applications; add more RAM |
| Large context length | Reduce context length setting |

### LM Studio-Specific Issues

**Server won't start:**
1. Check if another application is using port 1234
2. Try changing the port in settings
3. Restart LM Studio

**Model fails to load:**
1. Verify download completed successfully
2. Check available disk space
3. Try re-downloading the model

### Ollama-Specific Issues

**Service won't start:**
```bash
# Check service status
systemctl status ollama  # Linux
brew services list       # macOS with Homebrew

# Restart service
sudo systemctl restart ollama  # Linux
brew services restart ollama   # macOS
```

**Model download fails:**
1. Check internet connection
2. Verify disk space
3. Try: `ollama pull <model> --insecure` (if certificate issues)

---

## Performance Tips

### GPU Optimization

**LM Studio:**
1. Go to Settings → Performance
2. Set "GPU Layers" to maximum your VRAM allows
3. Start with 20 layers, increase until you hit VRAM limits

**Ollama:**
- Ollama automatically uses GPU if available
- Set `OLLAMA_GPU_OVERHEAD` to control memory reservation:
  ```bash
  export OLLAMA_GPU_OVERHEAD=500MB
  ```

### Memory Optimization

1. **Use appropriate quantization:** Q4_K_M offers the best quality/size balance
2. **Close unnecessary applications:** Free up RAM before testing
3. **Disable unnecessary model features:** Turn off GPU offloading if VRAM-constrained

### Batch Testing Tips

1. **Run overnight:** Large benchmarks take hours; start before leaving
2. **Use `--resume`:** If interrupted, resume rather than restart
3. **Monitor resources:** Keep Activity Monitor (macOS) or Task Manager (Windows) open

### Model Selection for Testing

| Test Goal | Recommended Model Size |
|-----------|----------------------|
| Quick validation | 7B models (fast, lower quality) |
| Standard testing | 7B-13B models |
| Comprehensive testing | 20B-70B models |
| Maximum quality | 70B+ models (requires high-end hardware) |

---

## Offline Operation

After initial setup, the CLI runner operates fully offline:

**Online required for:**
- Initial model downloads (one-time)
- CLI and benchmark version updates (infrequent)
- Uploading results to platform (optional)

**Fully offline:**
- Running tests
- Viewing local results
- Generating reports
- All benchmark evaluation

This makes local testing ideal for:
- Air-gapped environments
- Locations with unreliable internet
- Privacy-sensitive testing
- Cost-conscious operation (no per-request API fees)

---

## Quick Reference

### LM Studio Commands

| Action | Steps |
|--------|-------|
| Start server | Open LM Studio → Local Server → Select model → Start |
| Test server | `curl http://localhost:1234/v1/models` |
| Run benchmark | `gcb-runner test --model <name> --backend lmstudio` |

### Ollama Commands

| Action | Command |
|--------|---------|
| Install | `curl -fsSL https://ollama.com/install.sh \| sh` |
| Download model | `ollama pull <model-name>` |
| List models | `ollama list` |
| Start server | `ollama serve` |
| Test model | `ollama run <model-name> "Hello"` |
| Run benchmark | `gcb-runner test --model <name> --backend ollama` |

### Model Name Examples

| Model | LM Studio Name | Ollama Name |
|-------|----------------|-------------|
| Judge Model | `gpt-oss-20b-Q4_K_M` | `gpt-oss-20b` |
| Llama 3.2 7B | `llama-3.2-7b-instruct-Q4_K_M` | `llama3.2:7b` |
| Mistral 7B | `mistral-7b-instruct-Q4_K_M` | `mistral` |
| Phi-3 Mini | `phi-3-mini-4k-instruct-Q4_K_M` | `phi3` |

---

## Related Documentation

- [Technical Decisions: Hardware Requirements](../documents/Technical-Decisions.md#minimum-hardware-requirements-for-local-testing)
- [CLI Runner Specifications](./cli-runner-specifications.md)
- [CLI Runner Tech Stack](./cli-runner-tech-stack.md)

---

*This document provides setup instructions for local model testing. For cloud-based testing via OpenRouter, see the CLI Runner Specifications.*
