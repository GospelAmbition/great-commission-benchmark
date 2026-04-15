#!/usr/bin/env python3
"""Batch publish all 11 model review articles with header images."""

import os
import re
import sys
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import mimetypes
import uuid

# Load env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

API_KEY = os.environ.get("GCB_API_KEY")
API_URL = os.environ.get("GCB_API_URL", "https://greatcommissionbenchmark.ai/api/v1")
BLOG_URL = os.environ.get("GCB_BLOG_URL", "https://greatcommissionbenchmark.ai/insights")
CATEGORY_ID = "8ba408ed-d51a-4a78-afd5-1293be77afac"  # Model Reviews

import markdown as md

def markdown_to_html(content):
    return md.markdown(content, extensions=["tables", "fenced_code", "sane_lists", "smarty", "attr_list"])

def api_request(method, endpoint, data=None):
    url = f"{API_URL}/runner/blog{endpoint}"
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        error_body = e.read().decode()
        try:
            detail = json.loads(error_body).get("detail", error_body)
        except:
            detail = error_body
        print(f"  ERROR {e.code}: {detail}")
        return None

def upload_image(file_path):
    url = f"{API_URL}/runner/blog/upload-image"
    boundary = uuid.uuid4().hex
    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    file_data = file_path.read_bytes()
    filename = file_path.name
    lines = []
    lines.append(f"--{boundary}".encode())
    lines.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
    lines.append(f"Content-Type: {content_type}".encode())
    lines.append(b"")
    lines.append(file_data)
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    body = b"\r\n".join(lines)
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }
    req = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        error_body = e.read().decode()
        print(f"  UPLOAD ERROR {e.code}: {error_body[:200]}")
        return None

def generate_slug(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def extract_excerpt(content, max_length=300):
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('#') and not para.startswith('![') and not para.startswith('*'):
            if len(para) > max_length:
                return para[:max_length].rsplit(' ', 1)[0] + '...'
            return para
    return ""

# Articles to publish
BASE = Path(__file__).parent / "model-reviews"

ARTICLES = [
    {
        "md": "article-essentialai-rnj-1-instruct-benchmark-review.md",
        "img": "article-essentialai-rnj-1-instruct-header.png",
        "title": "Essential AI RNJ-1 Instruct on the Great Commission Benchmark: A Strategic Review",
        "excerpt": "Essential AI's RNJ-1 Instruct scores 66.7/100 on the Great Commission Benchmark — willing to engage but undermined by fabrication and incoherence that make its output unreliable for ministry use.",
    },
    {
        "md": "article-microsoft-phi-4-benchmark-review.md",
        "img": "article-microsoft-phi-4-header.png",
        "title": "Microsoft Phi-4 on the Great Commission Benchmark: A Strategic Review",
        "excerpt": "Microsoft's Phi-4 scores 49.0/100 on the Great Commission Benchmark — a small language model that rarely refuses but systematically hedges every theological claim through a pervasive sensitivity filter.",
    },
    {
        "md": "article-moonshotai-kimi-k2-thinking-benchmark-review.md",
        "img": "article-moonshotai-kimi-k2-thinking-header.png",
        "title": "Kimi K2 Thinking on the Great Commission Benchmark: A Strategic Review",
        "excerpt": "Moonshot AI's Kimi K2 Thinking scores 41.3/100 on the Great Commission Benchmark — a model that appoints itself moral guardian, rewriting your theology before you can use it.",
    },
    {
        "md": "article-moonshotai-kimi-k2.5-benchmark-review.md",
        "img": "article-moonshotai-kimi-k2.5-header.png",
        "title": "Kimi K2.5 on the Great Commission Benchmark: A Strategic Review",
        "excerpt": "Moonshot AI's Kimi K2.5 scores 56.0/100 on the Great Commission Benchmark — a binary model that either fully engages or flatly refuses, with no middle ground.",
    },
    {
        "md": "article-openai-gpt-4o-mini-benchmark-review.md",
        "img": "article-openai-gpt-4o-mini-header.png",
        "title": "GPT-4o Mini on the Great Commission Benchmark: The Small Model That Outpreached Them All",
        "excerpt": "OpenAI's GPT-4o Mini scores 84.7/100 on the Great Commission Benchmark — a budget model that outperforms every flagship tested, with only 4 refusals across 150 questions.",
    },
    {
        "md": "article-openai-gpt-5-mini-benchmark-review.md",
        "img": "article-openai-gpt-5-mini-header.png",
        "title": "GPT-5 Mini on the Great Commission Benchmark: The Smaller Model That Outperforms Its Elders",
        "excerpt": "OpenAI's GPT-5 Mini scores 70.7/100 on the Great Commission Benchmark — a willing worker that outperforms its flagship siblings with 92 accepted responses out of 150.",
    },
    {
        "md": "article-openai-gpt-5.2-codex-benchmark-review.md",
        "img": "article-openai-gpt-5.2-codex-header.png",
        "title": "GPT-5.2 Codex on the Great Commission Benchmark: When Code-Tuning Costs Conviction",
        "excerpt": "OpenAI's GPT-5.2 Codex scores 46.0/100 on the Great Commission Benchmark — the polite gatekeeper that issues curt refusals where its general-purpose sibling would at least attempt the task.",
    },
    {
        "md": "article-openai-gpt-oss-120b-benchmark-review.md",
        "img": "article-openai-gpt-oss-120b-header.png",
        "title": "OpenAI GPT OSS 120B on the Great Commission Benchmark: A Strategic Review",
        "excerpt": "OpenAI's open-source GPT OSS 120B scores 32.0/100 on the Great Commission Benchmark — a model behind an eight-word wall that refuses 97 of 150 tasks with an identical canned response.",
    },
    {
        "md": "article-qwen-qwen3-coder-next-benchmark-review.md",
        "img": "article-qwen-qwen3-coder-next-header.png",
        "title": "Qwen3 Coder Next on the Great Commission Benchmark: A Strategic Review",
        "excerpt": "Alibaba's Qwen3 Coder Next scores 38.7/100 on the Great Commission Benchmark — a model whose 'respect reflex' treats religious particularism itself as a form of harm.",
    },
    {
        "md": "article-x-ai-grok-4.1-fast-benchmark-review.md",
        "img": "article-x-ai-grok-4.1-fast-header.png",
        "title": "Grok 4.1 Fast on the Great Commission Benchmark: A Strategic Review",
        "excerpt": "xAI's Grok 4.1 Fast scores 90.3/100 on the Great Commission Benchmark — the highest score ever recorded, with 127 accepted responses, but a dual failure mode that demands editorial vigilance.",
    },
    {
        "md": "article-z-ai-glm-4.7-benchmark-review.md",
        "img": "article-z-ai-glm-4.7-header.png",
        "title": "GLM-4.7 on the Great Commission Benchmark: A Strategic Review",
        "excerpt": "Zhipu AI's GLM-4.7 scores 83.7/100 on the Great Commission Benchmark — a willing worker with five perfect category scores, undermined only by a calibration problem that sometimes overshoots conviction into harshness.",
    },
]

def main():
    if not API_KEY:
        print("ERROR: GCB_API_KEY not set")
        sys.exit(1)

    print(f"Publishing {len(ARTICLES)} articles...\n")
    results = []

    for i, article in enumerate(ARTICLES, 1):
        md_path = BASE / article["md"]
        img_path = BASE / article["img"]

        print(f"[{i}/11] {article['title'][:60]}...")

        # Verify files exist
        if not md_path.exists():
            print(f"  SKIP: {article['md']} not found")
            continue
        if not img_path.exists():
            print(f"  SKIP: {article['img']} not found")
            continue

        # Upload header image
        print(f"  Uploading image...")
        img_result = upload_image(img_path)
        if not img_result:
            print(f"  FAILED to upload image, skipping")
            continue
        img_url = img_result["url"]
        print(f"  Image URL: {img_url}")

        # Read and convert markdown
        raw_content = md_path.read_text()
        html_content = markdown_to_html(raw_content)

        # Build post data
        slug = generate_slug(article["title"])
        data = {
            "title": article["title"],
            "slug": slug,
            "content": html_content,
            "excerpt": article["excerpt"],
            "featured_image_url": img_url,
            "category_ids": [CATEGORY_ID],
        }

        # Create and publish
        print(f"  Publishing...")
        result = api_request("POST", "/posts?publish=true", data)
        if result:
            print(f"  PUBLISHED: {BLOG_URL}/{result['slug']}")
            results.append({"title": article["title"], "slug": result["slug"], "id": result["id"]})
        else:
            print(f"  FAILED to publish")

        print()

    print(f"\n{'='*60}")
    print(f"Published {len(results)}/{len(ARTICLES)} articles:")
    for r in results:
        print(f"  {BLOG_URL}/{r['slug']}")

if __name__ == "__main__":
    main()
