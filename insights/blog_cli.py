#!/usr/bin/env python3
"""
Blog CLI - Publish and manage blog posts from the command line.

Usage:
    python blog_cli.py create --file article.md --title "My Article"
    python blog_cli.py create --file article.md --title "My Article" --publish
    python blog_cli.py publish --id <post-id>
    python blog_cli.py unpublish --id <post-id>
    python blog_cli.py list [--status draft|published]
    python blog_cli.py get --id <post-id>
    python blog_cli.py update --id <post-id> --file article.md
    python blog_cli.py delete --id <post-id>
    python blog_cli.py categories
"""

import argparse
import os
import re
import sys
import json
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Load environment from .env file
def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

# Configuration
API_KEY = os.environ.get("GCB_API_KEY")
API_URL = os.environ.get("GCB_API_URL", "https://greatcommissionbenchmark.ai/api/v1")
BLOG_URL = os.environ.get("GCB_BLOG_URL", "https://greatcommissionbenchmark.ai/action/insights")


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def extract_excerpt(content: str, max_length: int = 300) -> str:
    """Extract the first paragraph as excerpt"""
    # Split by double newlines to get paragraphs
    paragraphs = content.split('\n\n')
    
    for para in paragraphs:
        # Skip headings and empty paragraphs
        para = para.strip()
        if para and not para.startswith('#') and not para.startswith('!['):
            # Truncate if too long
            if len(para) > max_length:
                return para[:max_length].rsplit(' ', 1)[0] + '...'
            return para
    
    return ""


def api_request(method: str, endpoint: str, data: Optional[dict] = None) -> dict:
    """Make an API request"""
    if not API_KEY:
        print("Error: GCB_API_KEY not set. Add it to insights/.env file.")
        print("Get your API key from: https://greatcommissionbenchmark.ai/dashboard/settings")
        sys.exit(1)
    
    url = f"{API_URL}/runner/blog{endpoint}"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }
    
    body = json.dumps(data).encode() if data else None
    
    req = Request(url, data=body, headers=headers, method=method)
    
    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        error_body = e.read().decode()
        try:
            error_data = json.loads(error_body)
            detail = error_data.get("detail", error_body)
        except:
            detail = error_body
        print(f"Error {e.code}: {detail}")
        sys.exit(1)
    except URLError as e:
        print(f"Connection error: {e.reason}")
        sys.exit(1)


def cmd_create(args):
    """Create a new blog post"""
    # Read content from file
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    content = file_path.read_text()
    
    # Generate slug if not provided
    slug = args.slug or generate_slug(args.title)
    
    # Extract excerpt if not provided
    excerpt = args.excerpt or extract_excerpt(content)
    
    # Build request data
    data = {
        "title": args.title,
        "slug": slug,
        "content": content,
        "excerpt": excerpt,
    }
    
    if args.featured_image:
        data["featured_image_url"] = args.featured_image
    
    if args.categories:
        data["category_ids"] = args.categories
    
    # Add publish query param
    endpoint = "/posts"
    if args.publish:
        endpoint += "?publish=true"
    
    result = api_request("POST", endpoint, data)
    
    status = "Published" if result["status"] == "published" else "Draft created"
    print(f"{status}: {result['title']}")
    print(f"  ID: {result['id']}")
    print(f"  Slug: {result['slug']}")
    if result["status"] == "published":
        print(f"  URL: {BLOG_URL}/{result['slug']}")
    else:
        print(f"  To publish: python blog_cli.py publish --id {result['id']}")


def cmd_publish(args):
    """Publish a draft post"""
    result = api_request("POST", f"/posts/{args.id}/publish")
    print(f"Published: {result['title']}")
    print(f"  URL: {BLOG_URL}/{result['slug']}")


def cmd_unpublish(args):
    """Unpublish a post (revert to draft)"""
    result = api_request("POST", f"/posts/{args.id}/unpublish")
    print(f"Unpublished: {result['title']}")
    print(f"  Status: draft")


def cmd_list(args):
    """List blog posts"""
    endpoint = "/posts"
    params = []
    if args.status:
        params.append(f"status={args.status}")
    if args.limit:
        params.append(f"limit={args.limit}")
    if params:
        endpoint += "?" + "&".join(params)
    
    result = api_request("GET", endpoint)
    
    print(f"Found {result['total']} posts:")
    print()
    
    for post in result["items"]:
        status_icon = "✓" if post["status"] == "published" else "○"
        print(f"  {status_icon} {post['title']}")
        print(f"    ID: {post['id']}")
        print(f"    Slug: {post['slug']}")
        print(f"    Status: {post['status']}")
        if post.get("published_at"):
            print(f"    Published: {post['published_at'][:10]}")
        print()


def cmd_get(args):
    """Get a single post by ID"""
    result = api_request("GET", f"/posts/{args.id}")
    
    print(f"Title: {result['title']}")
    print(f"ID: {result['id']}")
    print(f"Slug: {result['slug']}")
    print(f"Status: {result['status']}")
    print(f"Author: {result['author']['name']} ({result['author']['email']})")
    print(f"Created: {result['created_at'][:10]}")
    if result.get("published_at"):
        print(f"Published: {result['published_at'][:10]}")
    print(f"Excerpt: {result.get('excerpt', 'N/A')[:100]}...")
    print()
    print("Categories:", ", ".join(c["name"] for c in result.get("categories", [])) or "None")
    
    if args.show_content:
        print()
        print("--- Content ---")
        print(result.get("content", ""))


def cmd_update(args):
    """Update an existing post"""
    data = {}
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        data["content"] = file_path.read_text()
    
    if args.title:
        data["title"] = args.title
    
    if args.slug:
        data["slug"] = args.slug
    
    if args.excerpt:
        data["excerpt"] = args.excerpt
    
    if args.featured_image:
        data["featured_image_url"] = args.featured_image
    
    if args.categories:
        data["category_ids"] = args.categories
    
    if not data:
        print("Error: No updates specified. Use --file, --title, --slug, --excerpt, or --featured-image")
        sys.exit(1)
    
    result = api_request("PUT", f"/posts/{args.id}", data)
    print(f"Updated: {result['title']}")
    print(f"  ID: {result['id']}")


def cmd_delete(args):
    """Delete a post"""
    if not args.force:
        confirm = input(f"Are you sure you want to delete post {args.id}? [y/N] ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
    
    result = api_request("DELETE", f"/posts/{args.id}")
    print(f"Deleted: {result['id']}")


def cmd_categories(args):
    """List all categories"""
    result = api_request("GET", "/categories")
    
    print(f"Found {result['total']} categories:")
    print()
    
    for cat in result["items"]:
        print(f"  • {cat['name']} ({cat['slug']})")
        print(f"    ID: {cat['id']}")
        if cat.get("description"):
            print(f"    {cat['description']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Blog CLI - Publish and manage blog posts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Create a draft:
    python blog_cli.py create --file my-article.md --title "My Article Title"
  
  Create and publish immediately:
    python blog_cli.py create --file my-article.md --title "My Article" --publish
  
  Publish an existing draft:
    python blog_cli.py publish --id <post-uuid>
  
  List drafts:
    python blog_cli.py list --status draft
  
  Update content:
    python blog_cli.py update --id <post-uuid> --file updated-article.md
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new blog post")
    create_parser.add_argument("--file", "-f", required=True, help="Markdown file with post content")
    create_parser.add_argument("--title", "-t", required=True, help="Post title")
    create_parser.add_argument("--slug", "-s", help="URL slug (auto-generated from title if not provided)")
    create_parser.add_argument("--excerpt", "-e", help="Post excerpt (extracted from content if not provided)")
    create_parser.add_argument("--featured-image", help="Featured image URL")
    create_parser.add_argument("--categories", nargs="+", help="Category IDs")
    create_parser.add_argument("--publish", "-p", action="store_true", help="Publish immediately")
    create_parser.set_defaults(func=cmd_create)
    
    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish a draft post")
    publish_parser.add_argument("--id", required=True, help="Post ID to publish")
    publish_parser.set_defaults(func=cmd_publish)
    
    # Unpublish command
    unpublish_parser = subparsers.add_parser("unpublish", help="Unpublish a post (revert to draft)")
    unpublish_parser.add_argument("--id", required=True, help="Post ID to unpublish")
    unpublish_parser.set_defaults(func=cmd_unpublish)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List blog posts")
    list_parser.add_argument("--status", choices=["draft", "published"], help="Filter by status")
    list_parser.add_argument("--limit", type=int, default=20, help="Number of posts to return")
    list_parser.set_defaults(func=cmd_list)
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a single post by ID")
    get_parser.add_argument("--id", required=True, help="Post ID")
    get_parser.add_argument("--show-content", "-c", action="store_true", help="Show full content")
    get_parser.set_defaults(func=cmd_get)
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update an existing post")
    update_parser.add_argument("--id", required=True, help="Post ID to update")
    update_parser.add_argument("--file", "-f", help="New markdown content file")
    update_parser.add_argument("--title", "-t", help="New title")
    update_parser.add_argument("--slug", "-s", help="New slug")
    update_parser.add_argument("--excerpt", "-e", help="New excerpt")
    update_parser.add_argument("--featured-image", help="New featured image URL")
    update_parser.add_argument("--categories", nargs="+", help="New category IDs")
    update_parser.set_defaults(func=cmd_update)
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a post")
    delete_parser.add_argument("--id", required=True, help="Post ID to delete")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=cmd_delete)
    
    # Categories command
    categories_parser = subparsers.add_parser("categories", help="List all categories")
    categories_parser.set_defaults(func=cmd_categories)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
