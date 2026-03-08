"""Data URI utilities for handling base64 encoded data in data URIs."""

import re
from typing import Optional, Tuple


# Pattern for data URI: data:[<mime type>][;base64],<data>
DATA_URI_PATTERN = re.compile(
    r"^data:(?P<mime>[a-zA-Z0-9]+/[a-zA-Z0-9\-+]+(?:;[a-zA-Z0-9\-]+=?[a-zA-Z0-9\-]*)*);base64,(?P<data>.+)$"
)


def is_data_uri(value: str) -> bool:
    """Check if a string is a valid data URI."""
    return value.startswith("data:")


def extract_mime_type_from_data_uri(data_uri: str) -> Optional[str]:
    """Extract MIME type from a data URI."""
    match = DATA_URI_PATTERN.match(data_uri)
    if match:
        return match.group("mime")
    return None


def extract_base64_from_data_uri(data_uri: str) -> Optional[str]:
    """Extract base64 data from a data URI."""
    match = DATA_URI_PATTERN.match(data_uri)
    if match:
        return match.group("data")
    return None


def create_data_uri(mime_type: str, data: str) -> str:
    """Create a data URI from MIME type and data."""
    return f"data:{mime_type};base64,{data}"


def parse_data_uri(data_uri: str) -> Optional[Tuple[str, str]]:
    """Parse a data URI and return (mime_type, base64_data)."""
    match = DATA_URI_PATTERN.match(data_uri)
    if match:
        return match.group("mime"), match.group("data")


def get_decoded_data(data_uri: str) -> Optional[str]:
    """Get decoded data from a data URI."""
    import base64
    match = DATA_URI_PATTERN.match(data_uri)
    if match:
        try:
            return base64.b64decode(match.group("data")).decode("utf-8")
        except Exception:
            return None
    return None