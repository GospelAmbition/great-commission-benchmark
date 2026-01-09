"""Public file proxy endpoint for serving files from private Railway storage buckets.

Railway buckets are private by design and don't support public ACLs.
This endpoint proxies file requests, fetching from S3 with credentials
and streaming the content to the client.
"""
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import StreamingResponse

from app.services.storage import get_file

router = APIRouter()


@router.get("/{file_path:path}")
async def serve_file(
    file_path: str = Path(..., description="Path to the file in storage")
) -> StreamingResponse:
    """
    Serve a file from storage.
    
    This is a public endpoint (no auth required) that proxies requests
    to the private Railway storage bucket.
    
    Files are cached for 1 year with immutable cache headers since
    filenames include UUIDs and never change.
    """
    if not file_path:
        raise HTTPException(status_code=400, detail="File path required")
    
    # Basic path validation to prevent directory traversal
    if ".." in file_path or file_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    return await get_file(file_path)
