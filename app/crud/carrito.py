from sqlalchemy.orm import Session

from app.models.carrito_compra import CarritoCompra


class CRUDCarrito:
    def list_by_usuario(self, db: Session, id_usuario: int) -> list[CarritoCompra]:
        return db.query(CarritoCompra).filter(CarritoCompra.id_usuario == id_usuario).all()

    def add_item(self, db: Session, id_usuario: int, id_zona: int, cantidad: int) -> CarritoCompra:
        item = CarritoCompra(id_usuario=id_usuario, id_zona=id_zona, cantidad=cantidad)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def remove_item(self, db: Session, id_usuario: int, id_carrito: int) -> None:
        db.query(CarritoCompra).filter(
            CarritoCompra.id_carrito == id_carrito,
            CarritoCompra.id_usuario == id_usuario,
        ).delete()
        db.commit()

    def clear(self, db: Session, id_usuario: int) -> None:
        db.query(CarritoCompra).filter(CarritoCompra.id_usuario == id_usuario).delete()
        db.commit()


carrito_crud = CRUDCarrito()
