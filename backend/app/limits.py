"""Protecciones básicas para publicar la API en internet."""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "30"))


class RateLimiter:
    """Tope de peticiones por IP en una ventana de tiempo (en memoria)."""

    def __init__(self, limit: int, window: float = 60.0):
        self.limit = limit
        self.window = window
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            if len(self._hits) > 5000:  # evitar crecimiento sin fin
                for k in [k for k, v in self._hits.items() if not v]:
                    del self._hits[k]
            return True


_limiter = RateLimiter(RATE_LIMIT_PER_MIN)

# Solo un cálculo exacto a la vez: es el que más CPU consume.
exact_slot = threading.BoundedSemaphore(1)


def check_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "desconocido"
    if not _limiter.allow(ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes. Espera un minuto e inténtalo de nuevo.",
        )
