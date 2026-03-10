"""
Utility functions for serializing and deserializing complex objects to/from JSON.
"""

from typing import Any, Optional, Callable
import uuid
import json


def deserialize_from_json(
    value: Any, default_factory: Optional[Callable[[], Any]] = None
) -> Any:
    """
    Deserialize a value from JSON, handling various input types from the database.

    Args:
        value: The value to deserialize (can be str, dict, or None)
        default_factory: Optional callable to create default value if input is invalid

    Returns:
        Deserialized object (dict, list, or custom object)
    """
    if value is None:
        return default_factory() if default_factory else None

    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        try:
            return (
                json.loads(value)
                if value.strip()
                else (default_factory() if default_factory else {})
            )
        except (json.JSONDecodeError, ValueError):
            return default_factory() if default_factory else {}

    return value


def serialize_to_json(obj: Any) -> str:
    """
    Serialize an object to JSON with enhanced object handling.
    Converts complex Python objects to JSON-serializable formats.

    Args:
        obj: The object to serialize (dict, list, custom object, etc.)

    Returns:
        JSON string representation of the object
    """
    return json.dumps(obj, default=_json_serializer)


def _json_serializer(obj: Any) -> Any:
    """
    Custom serializer for JSON encoding.
    Handles various types of objects that aren't JSON serializable by default.

    Args:
        obj: The object to serialize

    Returns:
        JSON-serializable representation of the object (str, dict, etc.)

    Handles:
    - Basic JSON types (str, int, float, bool, list, dict) - passed through
    - UUID objects (converts to string)
    - Date/Time objects with isoformat method (converts to ISO format string)
    - Objects with __dict__ attribute (converts to dictionary)
    """
    # Handle basic JSON serializable types
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, (list, tuple, set)):
        return list(obj)
    elif isinstance(obj, dict):
        return {str(k): v for k, v in obj.items()}  # Ensure keys are strings
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif hasattr(obj, "isoformat") and callable(getattr(obj, "isoformat")):
        # Handle datetime, date, time objects
        return obj.isoformat()
    elif hasattr(obj, "__dict__"):
        # Try to convert object to a dict of its attributes
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}

    # If we can't handle it, let the default JSON serializer raise the error
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def serialize_enum_or_str(obj: Any) -> str:
    """
    Serialize an enum to its value or return string representation.

    Args:
        obj: The object to serialize (enum with .value attribute or any object)

    Returns:
        String representation of the object's value or the object itself as string
    """
    if hasattr(obj, "value"):
        return obj.value
    return str(obj)
