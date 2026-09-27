from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.boleto import Boleto, EstadoIngreso
from app.models.detalle_orden import DetalleOrden
from app.models.orden import Orden


class CRUDBoleto:
    def get(self, db: Session, id_boleto: int) -> Boleto | None:
        return (
            db.query(Boleto)
            .options(joinedload(Boleto.detalle))
            .filter(Boleto.id_boleto == id_boleto)
            .first()
        )

    def get_by_codigo(self, db: Session, codigo_qr: str) -> Boleto | None:
        return db.query(Boleto).filter(Boleto.codigo_qr == codigo_qr).first()

    def list_by_usuario(self, db: Session, id_usuario: int) -> list[Boleto]:
        return (
            db.query(Boleto)
            .join(DetalleOrden, Boleto.id_detalle == DetalleOrden.id_detalle)
            .join(Orden, DetalleOrden.id_orden == Orden.id_orden)
            .filter(Orden.id_usuario == id_usuario)
            .options(joinedload(Boleto.detalle))
            .all()
        )

    def validar_ingreso(self, db: Session, codigo_qr: str) -> tuple[bool, str, Boleto | None]:
        """
        Escaneo en puerta: valida el boleto y, si es válido, lo marca como
        usado de una vez (evita que el mismo QR se reutilice dos veces).
        """
        boleto = self.get_by_codigo(db, codigo_qr)
        if not boleto:
            return False, "El código QR no corresponde a ningún boleto.", None

        detalle = boleto.detalle
        orden = detalle.orden if detalle else None
        if orden and orden.estado_pago.value != "completado":
            return False, "La orden de este boleto no está pagada/confirmada.", boleto

        if boleto.estado_ingreso == EstadoIngreso.usado:
            return False, "Este boleto ya fue utilizado.", boleto
        if boleto.estado_ingreso == EstadoIngreso.anulado:
            return False, "Este boleto fue anulado.", boleto

        boleto.estado_ingreso = EstadoIngreso.usado
        boleto.fecha_ingreso = datetime.now(timezone.utc).replace(tzinfo=None)
        db.add(boleto)
        db.commit()
        db.refresh(boleto)
        return True, "Ingreso válido. ¡Bienvenido!", boleto


boleto_crud = CRUDBoleto()
