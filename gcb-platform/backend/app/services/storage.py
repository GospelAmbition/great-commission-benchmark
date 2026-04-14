"""S3-compatible Storage service for image uploads (Railway Simple Storage or AWS S3)

Railway buckets are private by design and don't support public ACLs.
Files are served through a backend proxy endpoint (/api/files/{path}).
"""
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import uuid
import logging
from typing import Optional
import io

from app.core.config import settings

logger = logging.getLogger(__name__)

# Content type to extension mapping for validation
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/gif": [".gif"],
    "image/webp": [".webp"],
    "image/svg+xml": [".svg"],
}


def get_s3_client():
    """Get configured S3 client (supports Railway Simple Storage and AWS S3)"""
    if not settings.S3_ACCESS_KEY_ID or not settings.S3_SECRET_ACCESS_KEY:
        raise HTTPException(
            status_code=500,
            detail="S3 storage not configured"
        )
    
    client_config = {
        'aws_access_key_id': settings.S3_ACCESS_KEY_ID,
        'aws_secret_access_key': settings.S3_SECRET_ACCESS_KEY,
        'region_name': settings.S3_REGION
    }
    
    # Add endpoint_url for Railway Simple Storage or other S3-compatible services
    if settings.S3_ENDPOINT_URL:
        client_config['endpoint_url'] = settings.S3_ENDPOINT_URL
    
    return boto3.client('s3', **client_config)


def get_public_url(filename: str) -> str:
    """Generate public URL for an uploaded file via backend proxy.
    
    Railway buckets are private, so we serve files through the backend.
    URLs are in format: {BACKEND_PUBLIC_URL}/api/files/{filename}
    """
    base = settings.BACKEND_PUBLIC_URL.rstrip('/')
    return f"{base}/api/files/{filename}"


async def get_file(filename: str) -> StreamingResponse:
    """
    Fetch a file from S3-compatible storage and return as streaming response.
    Used by the public file proxy endpoint.
    
    Args:
        filename: The S3 key/path to fetch
    
    Returns:
        StreamingResponse with the file content
    """
    try:
        s3_client = get_s3_client()
        
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET,
            Key=filename
        )
        
        content_type = response.get('ContentType', 'application/octet-stream')
        content_length = response.get('ContentLength')
        
        # Stream the file content
        return StreamingResponse(
            response['Body'].iter_chunks(),
            media_type=content_type,
            headers={
                "Content-Length": str(content_length) if content_length else "",
                "Cache-Control": "public, max-age=31536000, immutable",  # Cache for 1 year
            }
        )
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'NoSuchKey':
            raise HTTPException(status_code=404, detail="File not found")
        logger.error(f"S3 get error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file")


async def upload_image(
    file: UploadFile,
    folder: str = "blog",
    allowed_types: Optional[list] = None
) -> dict:
    """
    Upload an image to S3-compatible storage
    
    Args:
        file: The uploaded file
        folder: S3 folder/prefix to store the file
        allowed_types: List of allowed MIME types
    
    Returns:
        dict with url, filename, size, content_type
    """
    if allowed_types is None:
        allowed_types = list(ALLOWED_IMAGE_TYPES.keys())

    # Normalise SVG content type: some HTTP clients (e.g. httpx, curl) send
    # text/xml, application/xml, or application/octet-stream for .svg files.
    # Detect by extension and canonicalise before validation.
    content_type = file.content_type or ""
    if (
        file.filename
        and file.filename.lower().endswith(".svg")
        and content_type not in ("image/svg+xml",)
    ):
        content_type = "image/svg+xml"
    
    # Validate content type
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Generate unique filename
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{folder}/{uuid.uuid4()}.{file_ext}"
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {max_size // (1024*1024)}MB"
        )
    
    try:
        s3_client = get_s3_client()
        
        # Upload to S3-compatible storage (no ACL - Railway buckets are private)
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=unique_filename,
            Body=content,
            ContentType=content_type,
        )
        
        # Generate proxy URL (served through backend)
        url = get_public_url(unique_filename)
        
        logger.info(f"Uploaded image to storage: {unique_filename}")
        
        return {
            "url": url,
            "filename": unique_filename,
            "size": file_size,
            "content_type": content_type,
        }
        
    except ClientError as e:
        logger.error(f"S3 upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload image to storage"
        )


async def delete_image(filename: str) -> bool:
    """
    Delete an image from S3-compatible storage
    
    Args:
        filename: The S3 key/filename to delete
    
    Returns:
        True if deleted successfully
    """
    try:
        s3_client = get_s3_client()
        
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET,
            Key=filename
        )
        
        logger.info(f"Deleted image from storage: {filename}")
        return True
        
    except ClientError as e:
        logger.error(f"S3 delete error: {e}")
        return False
