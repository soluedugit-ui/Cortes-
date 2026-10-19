"""Optimizador exacto 1D con OR-Tools (CP-SAT).

Modelo:
  x[t, b] = cuántas piezas del tipo t van en la barra candidata b
  y[b]    = 1 si la barra candidata b se usa
  Minimiza el largo total de barras usadas.

Ancho de sierra: se suma `kerf` al largo de cada pieza y a la capacidad de la
barra, así  suma(piezas) + kerf*(n-1) <= L  queda como una restricción lineal.
"""

from __future__ import annotations

from ortools.sat.python import cp_model

from .optimizer import Bar, optimize

SCALE = 100  # CP-SAT trabaja con enteros: 3.5 mm -> 350


def optimize_exact(
    pieces: list[tuple[float, int]],
    stock: list[tuple[float, int | None]],
    kerf: float = 0.0,
    time_limit: float = 10.0,
) -> tuple[list[Bar], bool]:
    """Devuelve (barras, optimo_demostrado)."""
    if kerf < 0:
        raise ValueError("El ancho de corte no puede ser negativo.")

    # Unir tipos de pieza repetidos.
    merged: dict[float, int] = {}
    for length, qty in pieces:
        merged[length] = merged.get(length, 0) + qty
    piece_types = sorted(merged.items(), reverse=True)  # [(largo, cantidad)]
    total_pieces = sum(q for _, q in piece_types)

    # La heurística da una cota superior (y un plan de respaldo).
    try:
        heuristic = optimize(pieces, stock, kerf)
        heuristic_total = sum(b.stock_length for b in heuristic)
    except ValueError:
        heuristic, heuristic_total = None, None

    k = round(kerf * SCALE)
    t_len = [round(length * SCALE) + k for length, _ in piece_types]

    # Barras candidatas por cada largo de stock.
    candidates: list[tuple[float, int]] = []  # (largo_real, capacidad_escalada)
    for length, qty in stock:
        if qty is not None:
            n = qty
        elif heuristic_total is not None:
            # El óptimo nunca usa más largo total que la heurística.
            n = int(heuristic_total // length)
        else:
            n = total_pieces
        n = min(n, total_pieces)
        candidates += [(length, round(length * SCALE) + k)] * n

    if not candidates:
        raise ValueError("No alcanza el stock disponible para cubrir todas las piezas pedidas.")

    m = cp_model.CpModel()
    nb = len(candidates)
    y = [m.NewBoolVar(f"y{b}") for b in range(nb)]
    x = {
        (t, b): m.NewIntVar(0, q, f"x{t}_{b}")
        for t, (_, q) in enumerate(piece_types)
        for b in range(nb)
    }

    for t, (_, q) in enumerate(piece_types):
        m.Add(sum(x[t, b] for b in range(nb)) == q)
    for b, (_, cap) in enumerate(candidates):
        m.Add(sum(x[t, b] * t_len[t] for t in range(len(piece_types))) <= cap * y[b])

    # Romper simetría: entre barras del mismo largo, se usan en orden.
    for b in range(nb - 1):
        if candidates[b][0] == candidates[b + 1][0]:
            m.Add(y[b] >= y[b + 1])

    objective = sum(round(candidates[b][0] * SCALE) * y[b] for b in range(nb))
    if heuristic_total is not None:
        m.Add(objective <= round(heuristic_total * SCALE))
    m.Minimize(objective)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 2  # el hosting gratuito tiene poca CPU
    status = solver.Solve(m)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        bars: list[Bar] = []
        for b, (length, _) in enumerate(candidates):
            if solver.Value(y[b]):
                placed: list[float] = []
                for t, (plen, _) in enumerate(piece_types):
                    placed += [plen] * solver.Value(x[t, b])
                bars.append(Bar(stock_length=length, pieces=sorted(placed, reverse=True)))
        total = sum(b.stock_length for b in bars)
        # Nunca devolver algo peor que la heurística.
        if heuristic is not None and heuristic_total <= total + 1e-9 and status != cp_model.OPTIMAL:
            return heuristic, False
        return bars, status == cp_model.OPTIMAL

    if heuristic is not None:
        return heuristic, False
    if status == cp_model.INFEASIBLE:
        raise ValueError("No alcanza el stock disponible para cubrir todas las piezas pedidas.")
    raise ValueError("No se encontró solución en el tiempo dado; sube el tiempo máximo.")
