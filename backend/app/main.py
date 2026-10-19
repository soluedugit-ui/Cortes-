import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .limits import check_rate_limit, exact_slot
from .optimizer import optimize, summarize
from .schemas import BarOut, OptimizeRequest, OptimizeResponse, Optimize2DRequest
from .optimizer_2d import optimize_2d

app = FastAPI(title="Optimizador de cortes", version="0.2.0")

# CORS solo hace falta si el frontend se sirve desde otro dominio.
# Si FastAPI sirve el frontend (despliegue normal) no se usa.
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post(
    "/api/optimize",
    response_model=OptimizeResponse,
    dependencies=[Depends(check_rate_limit)],
)
def optimize_cuts(req: OptimizeRequest):
    pieces = [(p.length, p.quantity) for p in req.pieces]
    stock = [(s.length, s.quantity) for s in req.stock]
    proven_optimal = None

    try:
        if req.mode == "exact":
            try:
                from .optimizer_exact import optimize_exact
            except ImportError as exc:
                raise HTTPException(
                    status_code=501,
                    detail="OR-Tools no está instalado en el servidor (pip install ortools).",
                ) from exc
            if not exact_slot.acquire(blocking=False):
                raise HTTPException(
                    status_code=503,
                    detail="El servidor está calculando otro plan exacto. Inténtalo en unos segundos.",
                )
            try:
                bars, proven_optimal = optimize_exact(pieces, stock, req.kerf, req.time_limit)
            finally:
                exact_slot.release()
        else:
            bars = optimize(pieces, stock, req.kerf)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return OptimizeResponse(
        mode=req.mode,
        proven_optimal=proven_optimal,
        bars=[
            BarOut(
                stock_length=b.stock_length,
                pieces=b.pieces,
                kerf_loss=req.kerf * max(len(b.pieces) - 1, 0),
                leftover=b.free(req.kerf),
            )
            for b in bars
        ],
        summary=summarize(bars, req.kerf),
    )

@app.post("/api/optimize-2d", dependencies=[Depends(check_rate_limit)])
def optimize_cuts_2d(req: Optimize2DRequest):
    pieces = [(p.width, p.height, p.quantity) for p in req.pieces]
    stock = [(s.width, s.height, s.quantity) for s in req.stock]
    
    try:
        boards = optimize_2d(pieces, stock, req.kerf, req.allow_rotation)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {"boards": boards}

# En producción el frontend compilado vive en ./static (lo copia el Dockerfile).
# Debe montarse al final para no tapar las rutas /api.
_static = Path(os.getenv("STATIC_DIR", Path(__file__).resolve().parent.parent / "static"))
if _static.is_dir():
    app.mount("/", StaticFiles(directory=_static, html=True), name="frontend")
