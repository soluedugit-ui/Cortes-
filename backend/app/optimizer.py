"""Optimizador de cortes 1D (tubos, perfiles, barras, listones).

Heurística: Best Fit Decreasing (BFD) con ancho de corte (kerf).

Modelo del ancho de corte:
    Una barra con n piezas necesita n-1 cortes entre piezas, así que
        requerido = suma(piezas) + kerf * (n - 1)
    y el sobrante = largo_barra - requerido.
    (El corte que separa el sobrante final ya está "dentro" del sobrante.)
"""

from __future__ import annotations

from dataclasses import dataclass, field

EPS = 1e-9


@dataclass
class Bar:
    stock_length: float
    pieces: list[float] = field(default_factory=list)

    def required(self, kerf: float) -> float:
        if not self.pieces:
            return 0.0
        return sum(self.pieces) + kerf * (len(self.pieces) - 1)

    def free(self, kerf: float) -> float:
        return self.stock_length - self.required(kerf)

    def fits(self, piece: float, kerf: float) -> bool:
        extra = piece + (kerf if self.pieces else 0.0)
        return extra <= self.free(kerf) + EPS


def optimize(
    pieces: list[tuple[float, int]],
    stock: list[tuple[float, int | None]],
    kerf: float = 0.0,
) -> list[Bar]:
    """Devuelve la lista de barras con las piezas asignadas.

    pieces: [(largo, cantidad), ...]
    stock:  [(largo_barra, cantidad_disponible | None), ...]  (None = ilimitado)
    kerf:   ancho de corte de la sierra, misma unidad que los largos.
    """
    if kerf < 0:
        raise ValueError("El ancho de corte no puede ser negativo.")

    available: dict[float, float] = {}
    for length, qty in stock:
        available[length] = available.get(length, 0) + (float("inf") if qty is None else qty)

    longest_stock = max(available)
    expanded = sorted(
        (length for length, qty in pieces for _ in range(qty)),
        reverse=True,
    )

    for p in expanded:
        if p > longest_stock + EPS:
            raise ValueError(
                f"La pieza de {p:g} es más larga que la barra más larga disponible ({longest_stock:g})."
            )

    bars: list[Bar] = []
    for p in expanded:
        # 1) Best fit: la barra abierta donde quede el menor sobrante.
        best: Bar | None = None
        best_left = float("inf")
        for bar in bars:
            if bar.fits(p, kerf):
                left = bar.free(kerf) - p - (kerf if bar.pieces else 0.0)
                if left < best_left:
                    best, best_left = bar, left
        if best is not None:
            best.pieces.append(p)
            continue

        # 2) Abrir barra nueva: la más corta disponible donde quepa la pieza.
        candidates = sorted(
            length for length, qty in available.items() if qty > 0 and length >= p - EPS
        )
        if not candidates:
            raise ValueError(
                "No alcanza el stock disponible para cubrir todas las piezas pedidas."
            )
        chosen = candidates[0]
        available[chosen] -= 1
        bars.append(Bar(stock_length=chosen, pieces=[p]))

    return bars


def summarize(bars: list[Bar], kerf: float) -> dict:
    total_stock = sum(b.stock_length for b in bars)
    total_pieces = sum(sum(b.pieces) for b in bars)
    total_kerf = sum(kerf * max(len(b.pieces) - 1, 0) for b in bars)
    total_leftover = sum(b.free(kerf) for b in bars)
    waste = total_stock - total_pieces  # incluye sierra + sobrantes
    by_length: dict[float, int] = {}
    for b in bars:
        by_length[b.stock_length] = by_length.get(b.stock_length, 0) + 1
    return {
        "total_bars": len(bars),
        "total_stock_length": total_stock,
        "total_pieces_length": total_pieces,
        "total_kerf_loss": total_kerf,
        "total_leftover": total_leftover,
        "total_waste": waste,
        "waste_percent": round(100 * waste / total_stock, 2) if total_stock else 0.0,
        "bars_by_length": [
            {"stock_length": k, "count": v} for k, v in sorted(by_length.items())
        ],
    }
