#!/usr/bin/env python3
"""
Generate images from prompts using OpenRouter API.

This script can be run from the project root and reads the OpenRouter API key
from a .env file in the insights folder.

Usage:
    python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json
    python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json --start-id 1 --end-id 5
"""

import json
import os
import sys
import argparse
import time
import base64
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional

# Try to import python-dotenv, but make it optional
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")


def load_env_file(env_path: Path) -> Optional[str]:
    """
    Load environment variables from .env file.
    Returns the OpenRouter API key if found, None otherwise.
    """
    if not env_path.exists():
        return None
    
    api_key = None
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key.upper() == 'OPENROUTER_API_KEY' or key == 'OPENROUTER_API_KEY':
                        api_key = value
                        break
    except Exception as e:
        print(f"Warning: Error reading .env file: {e}")
    
    return api_key


def get_api_key(insights_dir: Path) -> Optional[str]:
    """
    Get OpenRouter API key from environment or .env file.
    Checks in order:
    1. Environment variable OPENROUTER_API_KEY
    2. .env file in insights directory
    """
    # First check environment variable
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key:
        return api_key
    
    # Try loading from .env file using python-dotenv if available
    if HAS_DOTENV:
        env_path = insights_dir / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            api_key = os.getenv('OPENROUTER_API_KEY')
            if api_key:
                return api_key
    
    # Fallback: manually parse .env file
    env_path = insights_dir / '.env'
    api_key = load_env_file(env_path)
    if api_key:
        return api_key
    
    return None


def load_prompts(json_file: str) -> Dict:
    """Load prompts from JSON file."""
    json_path = Path(json_file)
    if not json_path.is_absolute():
        # If relative, resolve from project root
        project_root = Path(__file__).parent.parent
        json_path = project_root / json_file
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file {json_path}: {e}")
        sys.exit(1)


def generate_image(
    api_key: str,
    model: str,
    prompt: str,
    max_retries: int = 3,
    retry_delay: int = 5,
    debug_dir: Optional[Path] = None
) -> Optional[str]:
    """
    Generate an image using OpenRouter API.
    
    For openai/gpt-5-image-mini, OpenRouter uses the chat completions endpoint
    with modalities=["image", "text"] to generate images.
    
    Returns the image URL or base64 data, or None if generation failed.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/great-commission-benchmark",
        "X-Title": "Great Commission Benchmark Image Generation"
    }
    
    # Use chat completions endpoint with modalities for image generation
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "modalities": ["image", "text"],
        "stream": False,
        "image_config": {
            "aspect_ratio": "16:9"
        }
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    print(f"  Error: Failed to parse JSON response: {e}")
                    print(f"  Response text (first 500 chars): {response.text[:500]}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None
                
                # Extract image from response
                # The response should have choices[0].message with images field
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    
                    # Check for images in the message - try multiple extraction strategies
                    if "images" in message:
                        images_field = message["images"]
                        print(f"  Debug: Images field found, type: {type(images_field)}")
                        
                        # Strategy 1: images is a list
                        if isinstance(images_field, list):
                            print(f"  Debug: Images is a list with {len(images_field)} items")
                            if len(images_field) > 0:
                                image_data = images_field[0]
                                print(f"  Debug: First image type: {type(image_data)}")
                                
                                if isinstance(image_data, str):
                                    # String could be URL or base64
                                    if image_data.startswith(("http://", "https://")):
                                        print(f"  Debug: Found image URL (length: {len(image_data)})")
                                        return image_data
                                    elif len(image_data) > 100:
                                        # Long string is likely base64
                                        print(f"  Debug: Found base64 string (length: {len(image_data)})")
                                        print(f"  Debug: Base64 preview: {image_data[:50]}...")
                                        return image_data
                                    else:
                                        print(f"  Debug: String too short to be valid image: {len(image_data)} chars")
                                
                                elif isinstance(image_data, dict):
                                    print(f"  Debug: Image is dict with keys: {list(image_data.keys())}")
                                    
                                    # Strategy 1: Check for nested image_url structure (OpenRouter format)
                                    if "image_url" in image_data:
                                        image_url_obj = image_data["image_url"]
                                        if isinstance(image_url_obj, dict) and "url" in image_url_obj:
                                            url_val = image_url_obj["url"]
                                            if url_val and isinstance(url_val, str) and len(url_val) > 100:
                                                print(f"  Debug: Found image in image_url.url (length: {len(url_val)})")
                                                return url_val
                                        elif isinstance(image_url_obj, str) and len(image_url_obj) > 100:
                                            print(f"  Debug: Found image_url as direct string (length: {len(image_url_obj)})")
                                            return image_url_obj
                                    
                                    # Strategy 2: Try all possible direct keys
                                    for key in ["url", "b64_json", "data", "image", "base64", "content"]:
                                        if key in image_data:
                                            val = image_data[key]
                                            if val and isinstance(val, str) and len(val) > 100:
                                                print(f"  Debug: Found image in dict key '{key}' (length: {len(val)})")
                                                return val
                                
                                else:
                                    print(f"  Debug: Image data is unexpected type: {type(image_data)}")
                            else:
                                print(f"  Debug: Images list is empty")
                        
                        # Strategy 2: images is a direct string (base64)
                        elif isinstance(images_field, str):
                            if len(images_field) > 100:
                                print(f"  Debug: Images field is base64 string (length: {len(images_field)})")
                                return images_field
                            else:
                                print(f"  Debug: Images string too short: {len(images_field)} chars")
                        
                        # Strategy 3: images is a dict
                        elif isinstance(images_field, dict):
                            print(f"  Debug: Images field is dict with keys: {list(images_field.keys())}")
                            for key in ["url", "b64_json", "data", "image", "base64", "content"]:
                                if key in images_field:
                                    val = images_field[key]
                                    if val and isinstance(val, str) and len(val) > 100:
                                        print(f"  Debug: Found image in dict key '{key}' (length: {len(val)})")
                                        return val
                        
                        else:
                            print(f"  Debug: Images field unexpected type: {type(images_field)}")
                            print(f"  Debug: Images field value preview: {str(images_field)[:300]}")
                    
                    # Fallback: check content for URL
                    content = message.get("content", "")
                    if content:
                        url_match = re.search(r'https?://[^\s<>"]+\.(?:jpg|jpeg|png|gif|webp)', content)
                        if url_match:
                            print(f"  Debug: Found URL in content")
                            return url_match.group(0)
                        if content.startswith("http"):
                            print(f"  Debug: Content starts with http, might be URL")
                            return content
                    
                    # Debug: show what we found in the message
                    print(f"  Debug: Message keys: {list(message.keys())}")
                    if "images" in message:
                        images_val = message["images"]
                        if isinstance(images_val, list):
                            print(f"  Debug: Images is a list with {len(images_val)} items")
                            if len(images_val) > 0:
                                print(f"  Debug: First item type: {type(images_val[0])}, length: {len(str(images_val[0])) if isinstance(images_val[0], str) else 'N/A'}")
                        else:
                            print(f"  Debug: Images field type: {type(images_val)}, value preview: {str(images_val)[:200]}")
                    if "content" in message:
                        print(f"  Debug: Content preview: {str(message['content'])[:200]}")
                
                # Try alternative response format (direct images field)
                if "images" in data and len(data["images"]) > 0:
                    image_data = data["images"][0]
                    if isinstance(image_data, str):
                        return image_data
                    elif isinstance(image_data, dict):
                        result = image_data.get("url") or image_data.get("b64_json") or image_data.get("data")
                        if result:
                            return result
                
                # No image found - show full response structure for debugging
                print(f"  Error: No image found in response after all extraction attempts")
                print(f"  Response structure: {list(data.keys())}")
                if "choices" in data:
                    print(f"  Number of choices: {len(data['choices'])}")
                    if len(data["choices"]) > 0:
                        choice_keys = list(data["choices"][0].keys())
                        print(f"  First choice keys: {choice_keys}")
                        if "message" in data["choices"][0]:
                            msg = data["choices"][0]["message"]
                            msg_keys = list(msg.keys())
                            print(f"  Message keys: {msg_keys}")
                            
                            # Deep inspection of images field
                            if "images" in msg:
                                img_val = msg["images"]
                                print(f"  Images field detailed inspection:")
                                print(f"    Type: {type(img_val)}")
                                if isinstance(img_val, list):
                                    print(f"    List length: {len(img_val)}")
                                    for i, item in enumerate(img_val[:3]):  # Check first 3 items
                                        print(f"    Item {i}: type={type(item)}, length={len(str(item)) if isinstance(item, str) else 'N/A'}")
                                        if isinstance(item, str):
                                            print(f"      Preview: {item[:50]}...")
                                        elif isinstance(item, dict):
                                            print(f"      Dict keys: {list(item.keys())}")
                                elif isinstance(img_val, str):
                                    print(f"    String length: {len(img_val)}")
                                    print(f"    Preview: {img_val[:100]}...")
                                    print(f"    Looks like base64: {img_val[:20].isalnum() or img_val.startswith('data:')}")
                
                # Save full response to a file for inspection
                if debug_dir:
                    debug_file = debug_dir / "last_response_debug.json"
                    try:
                        with open(debug_file, 'w') as f:
                            json.dump(data, f, indent=2)
                        print(f"  Debug: Full response saved to {debug_file}")
                    except Exception as e:
                        print(f"  Debug: Could not save response to file: {e}")
                
                if attempt < max_retries - 1:
                    print(f"  Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                return None
                
            elif response.status_code == 429:
                # Rate limit - wait and retry
                wait_time = retry_delay * (attempt + 1)
                print(f"  Rate limited. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            else:
                # Non-200 status code
                try:
                    error_data = response.json()
                    error_msg = json.dumps(error_data, indent=2)
                except:
                    error_msg = response.text
                
                print(f"  Error: API returned status {response.status_code}")
                print(f"  Error details: {error_msg[:1000]}")
                print(f"  Request URL: {url}")
                print(f"  Request payload (model and modalities only): model={model}, modalities=['image', 'text']")
                
                if attempt < max_retries - 1:
                    print(f"  Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                return None
                
        except requests.exceptions.Timeout as e:
            print(f"  Error: Request timeout after 120 seconds: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                continue
            return None
        except requests.exceptions.RequestException as e:
            print(f"  Error making API request: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                continue
            return None
        except json.JSONDecodeError as e:
            print(f"  Error: Invalid JSON response: {e}")
            print(f"  Response text (first 500 chars): {response.text[:500] if 'response' in locals() else 'N/A'}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return None
        except Exception as e:
            print(f"  Unexpected error: {type(e).__name__}: {e}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()[:500]}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return None
    
    return None


def save_image(image_data: str, output_path: str) -> bool:
    """
    Save an image from either a URL or base64 data.
    
    Args:
        image_data: Either a URL (starting with http) or base64 encoded image data
        output_path: Path where to save the image
    """
    try:
        if image_data.startswith("http://") or image_data.startswith("https://"):
            # Download from URL
            print(f"  Debug: Downloading image from URL...")
            response = requests.get(image_data, timeout=30)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"  Debug: Downloaded {len(response.content)} bytes")
                return True
            else:
                print(f"  Error: Failed to download image. Status: {response.status_code}")
                return False
        else:
            # Assume base64 encoded
            print(f"  Debug: Decoding base64 image data (length: {len(image_data)})...")
            
            # Handle data URI format (data:image/png;base64,...)
            if image_data.startswith("data:"):
                # Extract base64 part after comma
                header, encoded = image_data.split(",", 1)
                image_bytes = base64.b64decode(encoded)
            else:
                # Direct base64 string
                try:
                    image_bytes = base64.b64decode(image_data)
                except Exception as e:
                    print(f"  Error: Failed to decode base64: {e}")
                    print(f"  Debug: First 100 chars of data: {image_data[:100]}")
                    return False
            
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            print(f"  Debug: Saved {len(image_bytes)} bytes to {output_path}")
            return True
    except Exception as e:
        print(f"  Error saving image: {type(e).__name__}: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()[:500]}")
        return False


def format_id(id_num: int) -> str:
    """Format ID as zero-padded string (e.g., 01, 02, ..., 28)."""
    return f"{id_num:02d}"


def main():
    parser = argparse.ArgumentParser(
        description="Generate images from prompts using OpenRouter API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From project root:
  python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json
  
  # Generate specific range:
  python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json --start-id 1 --end-id 5
  
  # Custom output directory:
  python insights/generate_images.py --json-file insights/batch_guardrails/image_prompts.json --output-dir insights/batch_guardrails/images
        """
    )
    
    parser.add_argument(
        "--json-file",
        required=True,
        help="Path to JSON file containing prompts (relative to project root)"
    )
    
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for generated images (default: images/ in same directory as JSON file)"
    )
    
    parser.add_argument(
        "--model",
        default="openai/gpt-5-image-mini",
        help="Model to use for image generation (default: openai/gpt-5-image-mini)"
    )
    
    parser.add_argument(
        "--start-id",
        type=int,
        default=None,
        help="Start generating from this ID (inclusive, 1-based)"
    )
    
    parser.add_argument(
        "--end-id",
        type=int,
        default=None,
        help="Stop generating at this ID (inclusive, 1-based)"
    )
    
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API requests in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "--api-key",
        default=None,
        help="OpenRouter API key (overrides .env file)"
    )
    
    args = parser.parse_args()
    
    # Get API key
    insights_dir = Path(__file__).parent
    api_key = args.api_key or get_api_key(insights_dir)
    
    if not api_key:
        print("Error: OpenRouter API key not found.")
        print("Please either:")
        print("  1. Set OPENROUTER_API_KEY environment variable, or")
        print("  2. Create a .env file in the insights/ folder with:")
        print("     OPENROUTER_API_KEY=your_key_here")
        print("  3. Or use --api-key flag")
        sys.exit(1)
    
    # Load prompts
    print(f"Loading prompts from: {args.json_file}")
    data = load_prompts(args.json_file)
    
    prompts = data.get("prompts", [])
    if not prompts:
        print("Error: No prompts found in JSON file")
        sys.exit(1)
    
    print(f"Loaded {len(prompts)} prompts")
    
    # Filter prompts by ID range if specified
    if args.start_id is not None or args.end_id is not None:
        start_id = args.start_id if args.start_id is not None else 1
        end_id = args.end_id if args.end_id is not None else max(p["id"] for p in prompts)
        prompts = [p for p in prompts if start_id <= p["id"] <= end_id]
        print(f"Filtered to {len(prompts)} prompts (IDs {start_id}-{end_id})")
    
    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Default: images/ folder in same directory as JSON file
        json_path = Path(args.json_file)
        if not json_path.is_absolute():
            project_root = Path(__file__).parent.parent
            json_path = project_root / args.json_file
        output_dir = json_path.parent / "images"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir.absolute()}")
    
    # Process each prompt
    successful = 0
    failed = 0
    
    for i, prompt_data in enumerate(prompts, 1):
        prompt_id = prompt_data["id"]
        topic = prompt_data["topic"]
        prompt_text = prompt_data["prompt"]
        filename = prompt_data["filename"]
        
        print(f"\n[{i}/{len(prompts)}] Generating image for ID {format_id(prompt_id)}: {topic}")
        
        # Generate image
        image_url = generate_image(api_key, args.model, prompt_text, debug_dir=output_dir)
        
        if image_url:
            # Create output filename based on ID
            output_filename = f"{format_id(prompt_id)}_{filename}"
            output_path = output_dir / output_filename
            
            # Save image (handles both URL and base64)
            if save_image(image_url, str(output_path)):
                print(f"  ✓ Saved: {output_path}")
                successful += 1
            else:
                print(f"  ✗ Failed to save image (see errors above)")
                failed += 1
        else:
            print(f"  ✗ Failed to generate image (see detailed errors above)")
            failed += 1
        
        # Delay between requests to avoid rate limiting
        if i < len(prompts):
            time.sleep(args.delay)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(prompts)}")
    print(f"  Output directory: {output_dir.absolute()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
