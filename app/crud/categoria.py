from app.crud.base import CRUDBase
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate

categoria_crud = CRUDBase[Categoria, CategoriaCreate](Categoria)
