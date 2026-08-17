import json
import uuid
from typing import Any


def generate_id(prefix: str) -> str:
    return f"{prefix}{str(uuid.uuid4())[:8]}"


def parse_bool(value: bool | str | None, fallback: bool = False) -> bool:
    if value is None:
        return fallback

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on", ""}:
            return True
        if normalized in {"false", "0", "no", "off", "none", "null", "undefined"}:
            return False

    return value is True


def serialize_json(value: Any, fallback: str) -> str:
    """Serialize a value to a compact JSON string for a component attribute.

    Passes through non-empty strings unchanged, compacts dict/list values, and
    returns ``fallback`` for ``None`` or non-serializable values.
    """
    if value is None:
        return fallback

    if isinstance(value, str):
        normalized = value.strip()
        return normalized or fallback

    try:
        return json.dumps(value, separators=(",", ":"), ensure_ascii=True)
    except TypeError:
        return fallback


def deserialize_json(value: Any) -> Any:
    """Parse a JSON attribute value back into Python, or ``None`` if invalid."""
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None

        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            return None

    return None


def pop_prop_alias(props: dict, name: str, fallback=None):
    if name in props:
        return props.pop(name)

    lowered_name = name.lower()
    if lowered_name in props:
        return props.pop(lowered_name)

    return fallback
