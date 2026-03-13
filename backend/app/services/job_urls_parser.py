from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse


def _extract_url_from_line(line: str) -> str | None:
    raw = line.strip()
    if not raw:
        return None
    if "\t" in raw:
        candidate = raw.split("\t")[-1].strip()
    else:
        parts = raw.split()
        candidate = parts[-1] if parts else ""
    if candidate.startswith("http://") or candidate.startswith("https://"):
        return candidate
    return None


def parse_job_urls(file_path: str) -> list[str]:
    path = Path(file_path)
    if not path.exists():
        return []
    seen: set[str] = set()
    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        url = _extract_url_from_line(line)
        if not url:
            continue
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            continue
        normalized = url.strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        urls.append(normalized)
    return urls
