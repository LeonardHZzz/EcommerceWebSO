"""
Importa aquí todos los modelos para que:
- Alembic los detecte al hacer autogenerate.
- SQLAlchemy tenga registradas todas las tablas en Base.metadata
  antes de crear la app (create_all, si se usara, o cualquier
  relationship() que referencie otro modelo por string).

Este archivo es el único punto donde se importan los modelos en bloque;
db/base.py NO debe importarlos (generaría un import circular).
"""

from app.models.usuario import Usuario  # noqa: F401
from app.models.categoria import Categoria  # noqa: F401
from app.models.recinto import Recinto  # noqa: F401
from app.models.evento import Evento  # noqa: F401
from app.models.zona import Zona  # noqa: F401
from app.models.cupon_descuento import CuponDescuento  # noqa: F401
from app.models.orden import Orden  # noqa: F401
from app.models.detalle_orden import DetalleOrden  # noqa: F401
from app.models.boleto import Boleto  # noqa: F401
from app.models.carrito_compra import CarritoCompra  # noqa: F401
