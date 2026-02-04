import uuid


def generate_id(prefix: str) -> str:
    return f"{prefix}{str(uuid.uuid4())[:8]}"
