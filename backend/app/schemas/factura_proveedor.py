from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class FacturaProveedorBase(BaseModel):
    proveedor_id: int
    centro_costo_id: Optional[int] = None
    categoria_gasto_id: Optional[int] = None
    numero_factura: str
    fecha_emision: date
    fecha_vencimiento: Optional[date] = None
    monto: float
    saldo_pendiente: Optional[float] = None
    estado: Optional[str] = "pendiente"


class FacturaProveedorCreate(BaseModel):
    proveedor_id: int
    centro_costo_id: Optional[int] = None
    categoria_gasto_id: Optional[int] = None
    numero_factura: str
    fecha_emision: date
    fecha_vencimiento: Optional[date] = None
    monto: float
    saldo_pendiente: Optional[float] = None


class FacturaProveedorUpdate(BaseModel):
    numero_factura: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    monto: Optional[float] = None
    saldo_pendiente: Optional[float] = None
    estado: Optional[str] = None
    centro_costo_id: Optional[int] = None
    categoria_gasto_id: Optional[int] = None


class FacturaProveedorResponse(FacturaProveedorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
