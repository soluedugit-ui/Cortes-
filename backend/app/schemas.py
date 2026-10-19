from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Límites pensados para una web pública con uso ligero (unas 500 piezas al día).
MAX_PIECE_TYPES = 30
MAX_TOTAL_PIECES = 1000
MAX_STOCK_TYPES = 10
MAX_LENGTH = 1_000_000  # misma unidad que el usuario (ej. mm)


class PieceIn(BaseModel):
    length: float = Field(gt=0, le=MAX_LENGTH, description="Largo de la pieza")
    quantity: int = Field(ge=1, le=MAX_TOTAL_PIECES, description="Cantidad requerida")


class StockIn(BaseModel):
    length: float = Field(gt=0, le=MAX_LENGTH, description="Largo de la barra")
    quantity: int | None = Field(
        default=None, ge=1, le=100000, description="Cantidad disponible; vacío = ilimitado"
    )


class OptimizeRequest(BaseModel):
    pieces: list[PieceIn] = Field(min_length=1, max_length=MAX_PIECE_TYPES)
    stock: list[StockIn] = Field(min_length=1, max_length=MAX_STOCK_TYPES)
    kerf: float = Field(default=3.0, ge=0, le=1000, description="Ancho de corte de la sierra")
    mode: Literal["fast", "exact"] = Field(
        default="fast", description="fast = heurística; exact = OR-Tools"
    )
    time_limit: float = Field(
        default=10, gt=0, le=20, description="Segundos máximos para el modo exact"
    )

    @model_validator(mode="after")
    def _limit_total_pieces(self):
        total = sum(p.quantity for p in self.pieces)
        if total > MAX_TOTAL_PIECES:
            raise ValueError(
                f"Máximo {MAX_TOTAL_PIECES} piezas por cálculo (pediste {total})."
            )
        return self


class BarOut(BaseModel):
    stock_length: float
    pieces: list[float]
    kerf_loss: float
    leftover: float


class LengthCount(BaseModel):
    stock_length: float
    count: int


class SummaryOut(BaseModel):
    total_bars: int
    total_stock_length: float
    total_pieces_length: float
    total_kerf_loss: float
    total_leftover: float
    total_waste: float
    waste_percent: float
    bars_by_length: list[LengthCount]


class OptimizeResponse(BaseModel):
    bars: list[BarOut]
    summary: SummaryOut
    mode: str = "fast"
    proven_optimal: bool | None = None  # solo en modo exact

class Piece2DIn(BaseModel):
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    quantity: int = Field(ge=1)

class Stock2DIn(BaseModel):
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    quantity: int | None = None

class Optimize2DRequest(BaseModel):
    pieces: list[Piece2DIn] = Field(min_length=1, max_length=MAX_PIECE_TYPES)
    stock: list[Stock2DIn] = Field(min_length=1, max_length=MAX_STOCK_TYPES)
    kerf: float = Field(default=3.0, ge=0, le=1000, description="Ancho de corte de la sierra")
    allow_rotation: bool = Field(default=True)

    @model_validator(mode="after")
    def _limit_total_pieces(self):
        total = sum(p.quantity for p in self.pieces)
        if total > MAX_TOTAL_PIECES:
            raise ValueError(
                f"Máximo {MAX_TOTAL_PIECES} piezas por cálculo (pediste {total})."
            )
        return self