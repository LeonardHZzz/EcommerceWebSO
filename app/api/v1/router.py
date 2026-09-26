from fastapi import APIRouter

from app.api.v1 import (
    boletos,
    carrito,
    categorias,
    cupones,
    eventos,
    ordenes,
    recintos,
    usuarios,
    webhooks,
    zonas,
)

api_router = APIRouter()
api_router.include_router(usuarios.router)
api_router.include_router(categorias.router)
api_router.include_router(recintos.router)
api_router.include_router(eventos.router)
api_router.include_router(zonas.router)
api_router.include_router(carrito.router)
api_router.include_router(cupones.router)
api_router.include_router(ordenes.router)
api_router.include_router(boletos.router)
api_router.include_router(webhooks.router)
