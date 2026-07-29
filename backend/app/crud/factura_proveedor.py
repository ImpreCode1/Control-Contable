from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.proveedor import Proveedor
from app.models.factura_proveedor import FacturaProveedor
from app.schemas.factura_proveedor import FacturaProveedorCreate, FacturaProveedorUpdate


def get(db: Session, factura_id: int):
    return db.query(FacturaProveedor).filter(FacturaProveedor.id == factura_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100, vencidas: bool = False):
    q = db.query(FacturaProveedor)
    if vencidas:
        hoy = date.today()
        q = q.filter(
            FacturaProveedor.estado == "pendiente",
            FacturaProveedor.fecha_vencimiento < hoy,
        )
    return q.offset(skip).limit(limit).all()


def create(db: Session, obj_in: FacturaProveedorCreate):
    proveedor = db.query(Proveedor).filter(Proveedor.id == obj_in.proveedor_id).first()
    if not proveedor or not proveedor.activo:
        raise HTTPException(status_code=400, detail="Proveedor no existe o no esta activo")

    if obj_in.monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")

    if obj_in.fecha_vencimiento and obj_in.fecha_vencimiento < obj_in.fecha_emision:
        raise HTTPException(
            status_code=400,
            detail="La fecha de vencimiento no puede ser anterior a la fecha de emision",
        )

    data = obj_in.model_dump(exclude={"estado"}, exclude_unset=True)
    data["estado"] = "pendiente"
    db_obj = FacturaProveedor(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: FacturaProveedor, obj_in: FacturaProveedorUpdate):
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, factura_id: int):
    obj = db.query(FacturaProveedor).filter(FacturaProveedor.id == factura_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj


def esta_vencida(factura: FacturaProveedor) -> bool:
    return (
        factura.estado == "pendiente"
        and factura.fecha_vencimiento is not None
        and factura.fecha_vencimiento < date.today()
    )


def anular(db: Session, factura_id: int):
    factura = db.query(FacturaProveedor).filter(FacturaProveedor.id == factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    if factura.estado != "pendiente":
        raise HTTPException(
            status_code=400,
            detail="Solo las facturas en estado 'pendiente' pueden anularse",
        )
    factura.estado = "anulada"
    db.commit()
    db.refresh(factura)
    return factura
