import hashlib
import math
import re
from typing import List

import numpy as np


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9₹]+", text.lower())


def embed_text(text: str, dim: int = 384) -> List[float]:
    """Deterministic bag-of-words hashing encoder for demo search when no embedding API is configured."""
    vec = np.zeros(dim, dtype=np.float64)
    for tok in tokenize(text):
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
        vec[(h // dim) % dim] += 0.5
    n = np.linalg.norm(vec)
    if n == 0:
        return vec.tolist()
    return (vec / n).tolist()


def cosine(a: List[float], b: List[float]) -> float:
    va, vb = np.array(a), np.array(b)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)
