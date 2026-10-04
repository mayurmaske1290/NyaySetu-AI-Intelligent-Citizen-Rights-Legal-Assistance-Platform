import hashlib
import re
from typing import Optional

MAX_TEXT_CHARS = 20_000
ALLOWED_FILE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "text/plain",
    "audio/mpeg",
    "audio/wav",
    "audio/3gpp",
}
MAX_FILE_BYTES = 12 * 1024 * 1024


def sanitize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)
    return cleaned.strip()[:MAX_TEXT_CHARS]


def validate_file_meta(content_type: Optional[str], size: int) -> None:
    from app.core.errors import ControlledError

    if size > MAX_FILE_BYTES:
        raise ControlledError(413, "File is too large. Compress or choose a smaller file.", "FILE_TOO_LARGE", False)
    if content_type and content_type.split(";")[0] not in ALLOWED_FILE_TYPES:
        raise ControlledError(415, "This file type is not supported.", "FILE_TYPE_INVALID", False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
