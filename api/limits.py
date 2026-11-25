"""Controle de abuso mínimo, em processo, sem dependências externas.

Não substitui um limitador distribuído (Redis) em produção com várias
instâncias, mas fecha o buraco mais óbvio: um único cliente não consegue
consumir o tutor LLM nem reimportar progresso em loop.

A chave é o IP do cliente (``request.client.host``), que atrás de um proxy
confiável deve chegar em ``X-Forwarded-For``. Como não há como saber se o proxy
é confiável em qualquer ambiente, usamos o IP da conexão e só lemos
``X-Forwarded-For`` quando ``TRUST_PROXY=1`` está definido.
"""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass

from fastapi import HTTPException, Request, status


@dataclass
class _Window:
    count: int
    reset_at: float


class RateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str], _Window] = {}
        self._lock = threading.Lock()

    @staticmethod
    def client_key(request: Request | None) -> str:
        if request is None:
            return "unknown"
        if os.environ.get("TRUST_PROXY") == "1":
            forwarded = request.headers.get("x-forwarded-for")
            if forwarded:
                return forwarded.split(",")[0].strip()
        client = getattr(request, "client", None)
        return getattr(client, "host", None) or "unknown"

    def check(
        self,
        request: Request | None,
        *,
        bucket: str,
        limit: int,
        window: int,
    ) -> None:
        """Levanta 429 quando o cliente passa do limite na janela."""
        key = (bucket, self.client_key(request))
        now = time.monotonic()
        self._prune(now)
        with self._lock:
            current = self._buckets.get(key)
            if current is None or current.reset_at <= now:
                self._buckets[key] = _Window(count=1, reset_at=now + window)
                return
            if current.count >= limit:
                retry_after = max(1, int(current.reset_at - now))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Muitas solicitações. Tente de novo em instantes.",
                    headers={"Retry-After": str(retry_after)},
                )
            current.count += 1

    def _prune(self, now: float) -> None:
        """Descarta janelas vencidas para o dicionário não crescer sem limite."""
        if len(self._buckets) < 2048:
            return
        with self._lock:
            expired = [k for k, w in self._buckets.items() if w.reset_at <= now]
            for key in expired:
                self._buckets.pop(key, None)

    def reset(self) -> None:
        """Só para testes."""
        with self._lock:
            self._buckets.clear()


limiter = RateLimiter()
