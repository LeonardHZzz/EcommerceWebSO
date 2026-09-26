from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.cupon_descuento import CuponDescuento, EstadoCupon
from app.schemas.cupon import CuponCreate


class CRUDCupon(CRUDBase[CuponDescuento, CuponCreate]):
    def get_by_codigo(self, db: Session, codigo: str) -> CuponDescuento | None:
        return db.query(CuponDescuento).filter(CuponDescuento.codigo == codigo).first()

    def validar(self, db: Session, codigo: str) -> tuple[bool, str, CuponDescuento | None]:
        """Valida un cupón SIN consumir un uso (para mostrarlo en el carrito antes del checkout)."""
        cupon = self.get_by_codigo(db, codigo)
        if not cupon:
            return False, "El cupón no existe.", None
        if cupon.estado != EstadoCupon.activo:
            return False, "El cupón no está activo.", None
        if cupon.fecha_vencimiento < datetime.now(timezone.utc).replace(tzinfo=None):
            return False, "El cupón está vencido.", None
        if cupon.usos_disponibles <= 0:
            return False, "El cupón ya no tiene usos disponibles.", None
        return True, "Cupón válido.", cupon


cupon_crud = CRUDCupon(CuponDescuento)
