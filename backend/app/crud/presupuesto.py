from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.models.presupuesto import Presupuesto
from app.models.gasto_interno import GastoInterno
from app.models.gasto_externo_pry19 import GastoExternoPry19
from app.models.factura_proveedor import FacturaProveedor
from app.models.pago_proveedor import PagoProveedor
from app.schemas.presupuesto import PresupuestoCreate, PresupuestoUpdate, PresupuestoVsRealItem


def get(db: Session, presupuesto_id: int):
    return db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Presupuesto).offset(skip).limit(limit).all()


def create(db: Session, obj_in: PresupuestoCreate):
    db_obj = Presupuesto(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: Presupuesto, obj_in: PresupuestoUpdate):
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, presupuesto_id: int):
    obj = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    db.delete(obj)
    db.commit()
    return obj


def get_presupuesto_vs_real(db: Session) -> list[PresupuestoVsRealItem]:
    gi_rows = db.query(
        GastoInterno.centro_costo_id,
        GastoInterno.categoria_gasto_id,
        extract("year", GastoInterno.fecha).label("anio"),
        extract("month", GastoInterno.fecha).label("mes"),
        func.sum(GastoInterno.monto).label("total"),
    ).group_by(
        GastoInterno.centro_costo_id,
        GastoInterno.categoria_gasto_id,
        "anio", "mes",
    ).all()

    ge_rows = db.query(
        GastoExternoPry19.centro_costo_id,
        GastoExternoPry19.categoria_gasto_id,
        extract("year", GastoExternoPry19.fecha).label("anio"),
        extract("month", GastoExternoPry19.fecha).label("mes"),
        func.sum(GastoExternoPry19.monto).label("total"),
    ).group_by(
        GastoExternoPry19.centro_costo_id,
        GastoExternoPry19.categoria_gasto_id,
        "anio", "mes",
    ).all()

    fp_rows = db.query(
        FacturaProveedor.centro_costo_id,
        FacturaProveedor.categoria_gasto_id,
        extract("year", PagoProveedor.fecha_pago).label("anio"),
        extract("month", PagoProveedor.fecha_pago).label("mes"),
        func.sum(FacturaProveedor.monto).label("total"),
    ).join(
        PagoProveedor, PagoProveedor.factura_id == FacturaProveedor.id,
    ).filter(
        FacturaProveedor.estado == "pagada",
        FacturaProveedor.centro_costo_id.isnot(None),
        FacturaProveedor.categoria_gasto_id.isnot(None),
    ).group_by(
        FacturaProveedor.centro_costo_id,
        FacturaProveedor.categoria_gasto_id,
        "anio", "mes",
    ).all()

    real = defaultdict(float)
    for row in gi_rows + ge_rows + fp_rows:
        key = (row.centro_costo_id, row.categoria_gasto_id, int(row.anio), int(row.mes))
        real[key] += float(row.total)

    presupuestos = db.query(Presupuesto).all()

    return [
        PresupuestoVsRealItem(
            centro_costo_id=p.centro_costo_id,
            categoria_gasto_id=p.categoria_gasto_id,
            anio=p.anio,
            mes=p.mes,
            monto_presupuestado=float(p.monto_asignado),
            monto_real=real.get((p.centro_costo_id, p.categoria_gasto_id, p.anio, p.mes), 0.0),
        )
        for p in presupuestos
    ]
