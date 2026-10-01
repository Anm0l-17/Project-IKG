import hashlib
import re
from difflib import SequenceMatcher


def compute_article_hash(url: str) -> str:
    """
    Computes a deterministic SHA-256 hash from the canonicalized URL.
    Enables O(1) exact-duplicate checks.
    """
    canonical_url = url.strip().lower().split("#")[0].rstrip("/")
    return hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()


def normalize_title(title: str) -> str:
    """
    Normalizes article headline by lowercasing and removing special punctuation/extra spaces.
    """
    clean = re.sub(r"[^\w\s]", "", title.lower())
    return " ".join(clean.split())


def is_title_duplicate(title_a: str, title_b: str, threshold: float = 0.85) -> bool:
    """
    Fuzzy title match comparison.
    Returns True if similarity ratio >= threshold (default 85%).
    """
    norm_a = normalize_title(title_a)
    norm_b = normalize_title(title_b)

    if norm_a == norm_b:
        return True

    ratio = SequenceMatcher(None, norm_a, norm_b).ratio()
    return ratio >= threshold
