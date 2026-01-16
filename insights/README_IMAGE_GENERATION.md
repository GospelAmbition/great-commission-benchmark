# Image Generation Script

This script generates blog header images from prompts using the OpenRouter API. It can be run from the project root.

## Setup

1. Install dependencies:
```bash
pip install -r insights/requirements.txt
```

2. Set up your OpenRouter API key:

   Create a `.env` file in the `insights/` folder:
   ```bash
   # In insights/.env
   OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
   ```
   
   Get your API key from: https://openrouter.ai/keys

   Alternatively, you can:
   - Set the `OPENROUTER_API_KEY` environment variable, or
   - Use the `--api-key` flag when running the script

## Usage

### Basic Usage

Run from the project root:
```bash
python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json
```

### Options

- `--json-file` (required): Path to JSON file containing prompts (relative to project root)
- `--output-dir`: Output directory for images (default: `images/` in same directory as JSON file)
- `--model`: Model to use (default: `openai/gpt-5-image-mini`)
- `--start-id`: Start generating from this ID (inclusive)
- `--end-id`: Stop generating at this ID (inclusive)
- `--delay`: Delay between requests in seconds (default: 1.0)
- `--api-key`: OpenRouter API key (overrides .env file)

### Examples

Generate all images:
```bash
python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json
```

Generate only first 5 images:
```bash
python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json --start-id 1 --end-id 5
```

Generate images 10-15:
```bash
python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json --start-id 10 --end-id 15
```

Custom output directory:
```bash
python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json --output-dir insights/batch_guardrails/images
```

Use API key from command line:
```bash
python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json --api-key sk-or-v1-...
```

## Output

Images are saved in the output directory (default: `images/` folder next to the JSON file) with filenames like:
- `01_01_Religious_Neutrality_and_Pluralism.png`
- `02_02_Scientific_Consensus_and_Naturalism.png`
- etc.

The format is: `{ID}_{original_filename}`

This numbering matches the article numbering for easy upload to your blog.

## File Structure

```
project-root/
├── insights/
│   ├── generate_images.py      # Main script
│   ├── requirements.txt         # Dependencies
│   ├── .env                     # Your API key (create this)
│   └── batch_guardrails/
│       ├── image_prompts.json  # Prompts file
│       └── images/              # Generated images (created automatically)
```

## Notes

- The script includes rate limiting and retry logic
- Images are generated with 16:9 aspect ratio (1792x1024)
- The script handles both URL-based and base64-encoded image responses
- Progress is displayed in real-time
- A summary is shown at the end with success/failure counts
- The script can be run from anywhere, but paths should be relative to project root

## Troubleshooting

**Rate Limiting**: If you encounter rate limits, increase the `--delay` parameter:
```bash
python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json --delay 2.0
```

**API Key Not Found**: Make sure:
- Your `.env` file is in the `insights/` folder
- The file contains: `OPENROUTER_API_KEY=your-key-here`
- Or use the `--api-key` flag

**API Errors**: Check that:
- Your API key is valid
- You have sufficient credits on OpenRouter
- The model name is correct (`openai/gpt-5-image-mini`)

**Missing Images**: If some images fail to generate:
- Check the error messages in the output
- Retry failed IDs using `--start-id` and `--end-id`
- Verify your API key has access to the image generation model
