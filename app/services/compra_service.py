from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.cupon import cupon_crud
from app.models.carrito_compra import CarritoCompra
from app.models.cupon_descuento import CuponDescuento
from app.models.detalle_orden import DetalleOrden
from app.models.boleto import Boleto, EstadoIngreso
from app.models.orden import Orden, EstadoPago
from app.models.zona import Zona
from app.services.qr_service import generar_codigo_qr


class CompraError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _validar_cupon(db: Session, codigo_cupon: str | None) -> CuponDescuento | None:
    if not codigo_cupon:
        return None
    valido, mensaje, cupon = cupon_crud.validar(db, codigo_cupon)
    if not valido:
        raise CompraError(mensaje)
    return cupon


def procesar_checkout(
    db: Session,
    id_usuario: int,
    metodo_pago: str,
    codigo_cupon: str | None = None,
) -> Orden:
    """
    Flujo completo de compra, tal como lo modela el ERD:

    1. Lee los ítems del carrito del usuario.
    2. Bloquea y valida disponibilidad de cada zona (evita overselling).
    3. Valida el cupón (si aplica) y calcula el monto total con descuento.
    4. Crea la Orden + un Detalle_orden por cada ítem del carrito.
    5. Genera N boletos individuales por cada detalle (cantidad comprada).
    6. Descuenta capacidad_disponible de cada zona y usos del cupón.
    7. Vacía el carrito.

    Todo dentro de una sola transacción: si algo falla, se hace rollback
    completo (no queremos una orden a medias sin boletos, o boletos sin orden).
    """
    items_carrito = db.query(CarritoCompra).filter(CarritoCompra.id_usuario == id_usuario).all()
    if not items_carrito:
        raise CompraError("El carrito está vacío.")

    try:
        # Bloqueo pesimista de las zonas involucradas para evitar condiciones
        # de carrera si dos usuarios compran la última entrada al mismo tiempo.
        zona_ids = [item.id_zona for item in items_carrito]
        zonas = (
            db.query(Zona)
            .filter(Zona.id_zona.in_(zona_ids))
            .with_for_update()
            .all()
        )
        zonas_by_id = {z.id_zona: z for z in zonas}

        for item in items_carrito:
            zona = zonas_by_id.get(item.id_zona)
            if zona is None:
                raise CompraError(f"La zona {item.id_zona} ya no existe.")
            if zona.capacidad_disponible < item.cantidad:
                raise CompraError(
                    f"No hay suficiente disponibilidad en la zona '{zona.nombre_zona}'."
                )

        cupon = _validar_cupon(db, codigo_cupon)

        monto_total = Decimal("0.00")
        for item in items_carrito:
            zona = zonas_by_id[item.id_zona]
            monto_total += zona.precio * item.cantidad

        if cupon:
            descuento = (monto_total * cupon.porcentaje_descuento) / Decimal("100")
            monto_total -= descuento

        orden = Orden(
            id_usuario=id_usuario,
            id_cupon=cupon.id_cupon if cupon else None,
            monto_total=monto_total,
            estado_pago=EstadoPago.pendiente,
            metodo_pago=metodo_pago,
        )
        db.add(orden)
        db.flush()  # obtiene id_orden sin cerrar la transacción

        for item in items_carrito:
            zona = zonas_by_id[item.id_zona]
            subtotal = zona.precio * item.cantidad

            detalle = DetalleOrden(
                id_orden=orden.id_orden,
                id_zona=zona.id_zona,
                cantidad=item.cantidad,
                precio_unitario=zona.precio,
                subtotal=subtotal,
            )
            db.add(detalle)
            db.flush()  # obtiene id_detalle

            # Un boleto individual por cada unidad comprada en este detalle
            for i in range(1, item.cantidad + 1):
                boleto = Boleto(
                    id_detalle=detalle.id_detalle,
                    codigo_qr=generar_codigo_qr(orden.id_orden, detalle.id_detalle, i),
                )
                db.add(boleto)

            zona.capacidad_disponible -= item.cantidad

        if cupon:
            cupon.usos_disponibles -= 1

        # Vacía el carrito ya procesado
        db.query(CarritoCompra).filter(CarritoCompra.id_usuario == id_usuario).delete()

        # Aquí normalmente se llamaría a la pasarela de pago antes de marcar
        # como completado. Se deja pendiente y se confirma vía webhook/endpoint aparte.
        db.commit()
        db.refresh(orden)
        return orden

    except CompraError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


def confirmar_pago(db: Session, orden: Orden) -> Orden:
    """
    Marca la orden como completada. En un flujo real, esto lo dispara el
    webhook de la pasarela de pago tras confirmar el cobro; aquí se expone
    también como endpoint admin para poder probar el flujo manualmente.
    """
    if orden.estado_pago != EstadoPago.pendiente:
        raise CompraError(f"La orden ya está en estado '{orden.estado_pago.value}', no se puede confirmar.")

    orden.estado_pago = EstadoPago.completado
    db.add(orden)
    db.commit()
    db.refresh(orden)
    return orden


def cancelar_orden(db: Session, orden: Orden) -> Orden:
    """
    Cancela una orden (pendiente o completada) y revierte su efecto:
    - Devuelve la capacidad_disponible a cada zona involucrada.
    - Anula todos los boletos emitidos en esa orden (no se pueden usar en puerta).
    - Si se usó un cupón, le devuelve el uso consumido.
    """
    if orden.estado_pago == EstadoPago.cancelado:
        raise CompraError("La orden ya estaba cancelada.")

    for detalle in orden.detalles:
        zona = db.get(Zona, detalle.id_zona)
        if zona:
            zona.capacidad_disponible += detalle.cantidad
            db.add(zona)

        db.query(Boleto).filter(Boleto.id_detalle == detalle.id_detalle).update(
            {"estado_ingreso": EstadoIngreso.anulado}
        )

    if orden.id_cupon:
        cupon = db.get(CuponDescuento, orden.id_cupon)
        if cupon:
            cupon.usos_disponibles += 1
            db.add(cupon)

    orden.estado_pago = EstadoPago.cancelado
    db.add(orden)
    db.commit()
    db.refresh(orden)
    return orden
