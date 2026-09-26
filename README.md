# EcommerceWebSO# Ticketing API — Backend (FastAPI + SQLAlchemy)

Backend para el sistema de venta de boletos, conectado a la base de datos poblada en Azure. Implementa: catálogo de eventos/zonas, carrito de compras, checkout con generación de boletos y validación de cupones.

## 1. Estructura

```
app/
├── main.py            # instancia FastAPI
├── core/              # settings, seguridad (JWT/hash)
├── db/                # engine, sesión, Base declarativa
├── models/            # SQLAlchemy ORM (1 archivo por tabla del ERD)
├── schemas/           # Pydantic (request/response)
├── crud/              # acceso a datos
├── services/          # lógica de negocio (checkout, QR)
└── api/v1/            # routers/endpoints
alembic/                # migraciones
```
