import pytest

pytest.importorskip("ortools")

from app.optimizer import optimize
from app.optimizer_exact import optimize_exact


def total(bars):
    return sum(b.stock_length for b in bars)


def test_exacto_nunca_es_peor_que_la_heuristica():
    piezas = [(2900, 5), (2100, 5), (1950, 4), (1400, 6)]
    stock = [(6000, None)]
    bars, _ = optimize_exact(piezas, stock, kerf=3)
    assert total(bars) <= total(optimize(piezas, stock, 3))


def test_exacto_mejora_con_stock_limitado():
    piezas = [(2200, 5), (1100, 8), (450, 16)]
    stock = [(6000, 4), (2400, 4)]
    bars, optimo = optimize_exact(piezas, stock, kerf=3)
    assert optimo
    assert total(bars) < total(optimize(piezas, stock, 3))


def test_exacto_respeta_piezas_largo_y_sierra():
    piezas = [(1250, 7), (830, 9), (410, 12)]
    bars, _ = optimize_exact(piezas, [(6000, None)], kerf=3)
    placed = sorted(p for b in bars for p in b.pieces)
    assert placed == sorted([1250] * 7 + [830] * 9 + [410] * 12)
    assert all(b.required(3) <= b.stock_length + 1e-9 for b in bars)


def test_exacto_sin_stock_suficiente():
    with pytest.raises(ValueError):
        optimize_exact([(3000, 3)], [(6000, 1)], kerf=0)
