"""Add centro_costo_id and categoria_gasto_id to facturas_proveedor

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-28
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("facturas_proveedor", sa.Column("centro_costo_id", sa.Integer(), nullable=True))
    op.add_column("facturas_proveedor", sa.Column("categoria_gasto_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_factura_centro_costo", "facturas_proveedor", "centros_costo", ["centro_costo_id"], ["id"])
    op.create_foreign_key("fk_factura_categoria_gasto", "facturas_proveedor", "categorias_gasto", ["categoria_gasto_id"], ["id"])


def downgrade():
    op.drop_constraint("fk_factura_categoria_gasto", "facturas_proveedor", type_="foreignkey")
    op.drop_constraint("fk_factura_centro_costo", "facturas_proveedor", type_="foreignkey")
    op.drop_column("facturas_proveedor", "categoria_gasto_id")
    op.drop_column("facturas_proveedor", "centro_costo_id")
