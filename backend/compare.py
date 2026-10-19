"""Compara la heurística rápida contra OR-Tools en varios casos de prueba.

Uso (desde la carpeta backend, con ortools instalado):
    python compare.py
"""

import time

from app.optimizer import optimize, summarize
from app.optimizer_exact import optimize_exact

CASOS = {
    "A tubo cuadrado, un solo largo": ([(1800, 6), (1200, 10), (750, 12), (520, 8)], [(6000, None)], 3),
    "B dos largos de barra": ([(2350, 4), (1475, 6), (980, 9), (640, 15), (315, 20)], [(6000, None), (3000, None)], 2.5),
    "C stock limitado": ([(2200, 5), (1100, 8), (450, 16)], [(6000, 4), (2400, 4)], 3),
    "D piezas dificiles": ([(2900, 5), (2100, 5), (1950, 4), (1400, 6)], [(6000, None)], 3),
}


def fila(nombre, bars, kerf, segundos, extra=""):
    s = summarize(bars, kerf)
    barras = " + ".join(f"{b['count']}×{b['stock_length']:g}" for b in s["bars_by_length"])
    print(f"  {nombre:<10} {s['total_bars']:>2} barras ({barras})  desperdicio {s['waste_percent']:>5}%  {segundos:5.2f}s {extra}")


for nombre, (piezas, barras, kerf) in CASOS.items():
    print(nombre)
    t = time.time()
    fila("rápido", optimize(piezas, barras, kerf), kerf, time.time() - t)
    t = time.time()
    bars, optimo = optimize_exact(piezas, barras, kerf, time_limit=10)
    fila("OR-Tools", bars, kerf, time.time() - t, "(óptimo demostrado)" if optimo else "(mejor encontrado)")
    print()
