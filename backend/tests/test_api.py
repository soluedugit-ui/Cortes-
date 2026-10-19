from fastapi.testclient import TestClient

from app import limits
from app.main import app

client = TestClient(app)

BODY = {
    "pieces": [{"length": 1000, "quantity": 5}],
    "stock": [{"length": 6000}],
    "kerf": 3,
}


def test_calculo_normal():
    r = client.post("/api/optimize", json=BODY)
    assert r.status_code == 200
    assert r.json()["summary"]["total_bars"] == 1


def test_rechaza_demasiadas_piezas():
    body = {**BODY, "pieces": [{"length": 100, "quantity": 600}, {"length": 200, "quantity": 600}]}
    r = client.post("/api/optimize", json=body)
    assert r.status_code == 422


def test_rechaza_tiempo_excesivo():
    r = client.post("/api/optimize", json={**BODY, "mode": "exact", "time_limit": 120})
    assert r.status_code == 422


def test_rechaza_demasiados_tipos_de_pieza():
    body = {**BODY, "pieces": [{"length": 100 + i, "quantity": 1} for i in range(31)]}
    assert client.post("/api/optimize", json=body).status_code == 422


def test_tope_de_peticiones_por_minuto(monkeypatch):
    monkeypatch.setattr(limits, "_limiter", limits.RateLimiter(2))
    codes = [client.post("/api/optimize", json=BODY).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def test_modo_exacto_ocupado(monkeypatch):
    # Si ya hay un cálculo exacto en curso, el siguiente recibe 503 sin colgarse.
    assert limits.exact_slot.acquire(blocking=False)
    try:
        r = client.post("/api/optimize", json={**BODY, "mode": "exact"})
        assert r.status_code == 503
    finally:
        limits.exact_slot.release()
