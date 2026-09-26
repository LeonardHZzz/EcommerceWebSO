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
    1. Lee los ítems del carrito del usuario
    2. Bloquea y valida disponibilidad de cada zona 
    3. Valida el cupón y calcula el monto total con descuento
    4. Crea la Orden + un Detalle_orden por cada ítem del carrito
    5. Genera N boletos individuales por cada detalle 
    6. Descuenta capacidad_disponible de cada zona y usos del cupon
    7. Vacía el carrito

    """
    items_carrito = db.query(CarritoCompra).filter(CarritoCompra.id_usuario == id_usuario).all()
    if not items_carrito:
        raise CompraError("El carrito está vacío.")

    try:
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
        db.flush()  

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
            db.flush() 

            for i in range(1, item.cantidad + 1):
                boleto = Boleto(
                    id_detalle=detalle.id_detalle,
                    codigo_qr=generar_codigo_qr(orden.id_orden, detalle.id_detalle, i),
                )
                db.add(boleto)

            zona.capacidad_disponible -= item.cantidad

        if cupon:
            cupon.usos_disponibles -= 1

        db.query(CarritoCompra).filter(CarritoCompra.id_usuario == id_usuario).delete()

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
    Marca la orden como completada.
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
    Cancela una orden (pendiente o completada)
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
