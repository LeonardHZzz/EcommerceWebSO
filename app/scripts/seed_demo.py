"""
Pobla datos de demostración estilo "Sugoi Fest": 1 categoría, 1 recinto,
1 evento con 3 zonas, y 1 cupón de descuento. Es idempotente (se puede
correr varias veces sin duplicar datos).

Uso:
    docker compose -f docker-compose.local.yml exec api python -m app.scripts.seed_demo
"""
from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal
from app.models.categoria import Categoria
from app.models.cupon_descuento import CuponDescuento, EstadoCupon
from app.models.evento import EstadoEvento, Evento
from app.models.recinto import Recinto
from app.models.zona import Zona


def seed() -> None:
    db = SessionLocal()
    try:
        categoria = db.query(Categoria).filter(Categoria.nombre_categoria == "Anime & Gaming").first()
        if not categoria:
            categoria = Categoria(
                nombre_categoria="Anime & Gaming",
                descripcion="Convenciones de anime, manga, videojuegos y cultura japonesa.",
            )
            db.add(categoria)
            db.flush()

        recinto = db.query(Recinto).filter(Recinto.nombre_recinto == "Centro de Convenciones Lima").first()
        if not recinto:
            recinto = Recinto(
                nombre_recinto="Centro de Convenciones Lima",
                direccion="Av. Javier Prado Este 123",
                distrito="San Isidro",
                aforo_maximo=5000,
            )
            db.add(recinto)
            db.flush()

        evento = db.query(Evento).filter(Evento.titulo == "Sugoi Fest 2027").first()
        if not evento:
            inicio = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=60)
            evento = Evento(
                id_categoria=categoria.id_categoria,
                id_recinto=recinto.id_recinto,
                titulo="Sugoi Fest 2027",
                descripcion="El festival de anime, gaming y cultura japonesa más grande del año.",
                fecha_inicio=inicio,
                fecha_fin=inicio + timedelta(days=2),
                estado=EstadoEvento.activo,
            )
            db.add(evento)
            db.flush()

            db.add_all([
                Zona(id_evento=evento.id_evento, nombre_zona="General", precio=60,
                     capacidad_total=3000, capacidad_disponible=3000),
                Zona(id_evento=evento.id_evento, nombre_zona="VIP", precio=150,
                     capacidad_total=800, capacidad_disponible=800),
                Zona(id_evento=evento.id_evento, nombre_zona="Backstage Pass", precio=350,
                     capacidad_total=100, capacidad_disponible=100),
            ])

        if not db.query(CuponDescuento).filter(CuponDescuento.codigo == "SUGOI10").first():
            db.add(CuponDescuento(
                codigo="SUGOI10",
                porcentaje_descuento=10,
                fecha_vencimiento=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=90),
                usos_disponibles=500,
                estado=EstadoCupon.activo,
            ))

        db.commit()
        print(
            "Datos demo creados/verificados:\n"
            " - Categoría: Anime & Gaming\n"
            " - Recinto: Centro de Convenciones Lima\n"
            " - Evento: Sugoi Fest 2027 (zonas: General $60, VIP $150, Backstage Pass $350)\n"
            " - Cupón: SUGOI10 (10% de descuento)"
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
