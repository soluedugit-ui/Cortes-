import pytest

from app.optimizer import optimize, summarize


def test_ajuste_exacto_sin_sierra():
    bars = optimize([(2000, 3)], [(6000, None)], kerf=0)
    assert len(bars) == 1
    assert sorted(bars[0].pieces) == [2000, 2000, 2000]
    assert summarize(bars, 0)["waste_percent"] == 0


def test_el_ancho_de_corte_se_respeta():
    # 3 piezas de 2000 en barra de 6000 con sierra de 5 mm: ya no caben las 3.
    bars = optimize([(2000, 3)], [(6000, None)], kerf=5)
    assert len(bars) == 2


def test_ninguna_barra_se_pasa_del_largo():
    kerf = 3
    bars = optimize([(1250, 7), (830, 9), (410, 12)], [(6000, None)], kerf=kerf)
    for b in bars:
        assert b.required(kerf) <= b.stock_length + 1e-9


def test_conserva_todas_las_piezas():
    bars = optimize([(1250, 7), (830, 9)], [(6000, None)], kerf=3)
    placed = sorted(p for b in bars for p in b.pieces)
    assert placed == sorted([1250] * 7 + [830] * 9)


def test_usa_barra_corta_cuando_alcanza():
    bars = optimize([(1000, 1)], [(6000, None), (1200, None)], kerf=3)
    assert bars[0].stock_length == 1200


def test_respeta_stock_limitado():
    with pytest.raises(ValueError):
        optimize([(3000, 3)], [(6000, 1)], kerf=0)


def test_pieza_mas_larga_que_la_barra():
    with pytest.raises(ValueError):
        optimize([(7000, 1)], [(6000, None)], kerf=3)
