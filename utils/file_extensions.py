"""File extensions module for file type handling."""

from typing import Dict, Set

# Common text file extensions
ALL_TEXT_EXTENSIONS: Set[str] = {
    ".txt",
    ".md",
    ".rst",
    ".html",
    ".htm",
    ".css",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".py",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".scala",
    ".sh",
    ".bash",
    ".yml",
    ".yaml",
    ".json",
    ".xml",
    ".csv",
    ".log",
    ".ini",
    ".cfg",
    ".conf",
}

# MIME type to file extension mapping
MIME_TO_EXTENSION: Dict[str, str] = {
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/html": ".html",
    "text/css": ".css",
    "text/javascript": ".js",
    "application/json": ".json",
    "application/xml": ".xml",
    "text/csv": ".csv",
}


def get_file_extension(mime_type: str) -> str:
    """Get file extension from MIME type."""
    return MIME_TO_EXTENSION.get(mime_type, ".txt")


def get_file_extension_from_filename(filename: str) -> str:
    """Get file extension from filename."""
    import os

    return os.path.splitext(filename)[1].lower()
