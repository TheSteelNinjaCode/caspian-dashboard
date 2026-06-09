import uuid


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

def pop_prop_alias(props: dict, name: str, fallback=None):
    if name in props:
        return props.pop(name)

    lowered_name = name.lower()
    if lowered_name in props:
        return props.pop(lowered_name)

    return fallback