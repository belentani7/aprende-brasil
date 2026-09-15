#!/usr/bin/env python3
"""Baixa bancos de dados abertos para a Aprende Brasil.

Fontes (todas sem chave de API):
  - Lista de palavras do português (pythonprobr/palavras, MIT)

Saída: data/open/<arquivo>
Só usa a biblioteca padrão.
"""

from __future__ import annotations

import re
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "open"

SOURCES = {
    "palavras-pt.txt": "https://raw.githubusercontent.com/pythonprobr/palavras/master/palavras.txt",
}

LETRAS = re.compile(r"^[a-záàâãéêíóôõúç]+$", re.IGNORECASE)


def _download(url: str, timeout: float = 60.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "aprende-brasil/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _decode(raw: bytes) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _normalize(text: str) -> str:
    """Mantém apenas palavras alfabéticas em minúsculas, únicas e ordenadas."""
    seen: set[str] = set()
    for line in text.splitlines():
        word = line.strip().lower()
        if 1 < len(word) <= 20 and LETRAS.match(word) and "-" not in word:
            seen.add(word)
    return "\n".join(sorted(seen)) + "\n"


def fetch_all(out_dir: Path = OUT) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, url in SOURCES.items():
        raw = _download(url)
        text = _normalize(_decode(raw))
        path = out_dir / name
        path.write_text(text, encoding="utf-8")
        written.append(path)
        print(f"{path.name}: {len(text.splitlines())} palavras")
    return written


def main() -> int:
    fetch_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
