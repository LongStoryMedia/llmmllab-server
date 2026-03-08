"""Text extraction utilities for processing file content."""

from typing import Optional, Dict, Any
import base64


def extract_text_content(
    content: Optional[str], content_type: Optional[str] = None, filename: Optional[str] = None
) -> str:
    """
    Extract text content from various content types.

    Args:
        content: The content to extract text from (base64 encoded for files)
        content_type: MIME type of the content
        filename: Original filename for context

    Returns:
        Extracted text content
    """
    if not content:
        return ""

    if not content_type:
        content_type = "text/plain"

    # Handle text-based content types
    text_types = [
        "text/",
        "application/json",
        "application/xml",
        "application/yaml",
        "application/x-yaml",
        "application/javascript",
        "application/typescript",
        "text/markdown",
    ]

    for text_type in text_types:
        if content_type.startswith(text_type):
            try:
                # If content is base64 encoded, decode it first
                if content and len(content) > 4 and content[:4] == "data":
                    # This is a data URI, extract base64 part
                    if ";" in content and "," in content:
                        base64_part = content.split(",", 1)[1]
                        decoded = base64.b64decode(base64_part).decode("utf-8")
                        return decoded
                return content or ""
            except Exception:
                return content if content else ""

    # Handle image content - return placeholder
    if content_type.startswith("image/"):
        return f"[Image content from {filename or 'unknown'}]"

    # Handle PDF content - return placeholder
    if content_type == "application/pdf":
        return f"[PDF content from {filename or 'unknown'}]"

    # For binary or unknown content types, return placeholder
    return f"[Binary content from {filename or 'unknown'}, type: {content_type}]"


def get_file_metadata(content: Optional[str], content_type: Optional[str] = None, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Get file metadata from content.

    Args:
        content: The file content
        content_type: MIME type of the content
        filename: Original filename

    Returns:
        Dictionary with file metadata
    """
    metadata: Dict[str, Any] = {
        "content_type": content_type or "application/octet-stream",
        "filename": filename or "unknown",
    }

    if content:
        try:
            # Try to determine size
            if len(content) > 4 and content[:4] == "data":
                # Data URI - extract base64 part
                if ";" in content and "," in content:
                    base64_part = content.split(",", 1)[1]
                    metadata["size"] = len(base64.b64decode(base64_part))
            else:
                # Raw content or base64
                metadata["size"] = len(content)
        except Exception:
            metadata["size"] = 0

    return metadata