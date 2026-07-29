from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.pago_proveedor import PagoProveedor
from app.models.factura_proveedor import FacturaProveedor
from app.schemas.pago_proveedor import PagoProveedorCreate


def get(db: Session, pago_id: int):
    return db.query(PagoProveedor).filter(PagoProveedor.id == pago_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PagoProveedor).offset(skip).limit(limit).all()


def create(db: Session, obj_in: PagoProveedorCreate):
    existente = db.query(PagoProveedor).filter(PagoProveedor.factura_id == obj_in.factura_id).first()
    if existente:
        raise HTTPException(
            status_code=409,
            detail="La factura ya tiene un pago registrado",
        )

    factura = db.query(FacturaProveedor).filter(FacturaProveedor.id == obj_in.factura_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    if obj_in.monto != factura.monto:
        raise HTTPException(
            status_code=400,
            detail="El monto del pago debe coincidir con el total de la factura. Pagos parciales no estan soportados en este alcance.",
        )

    db_obj = PagoProveedor(**obj_in.model_dump())
    db.add(db_obj)
    factura.estado = "pagada"
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, pago_id: int):
    obj = db.query(PagoProveedor).filter(PagoProveedor.id == pago_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj
