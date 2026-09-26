from app.crud.base import CRUDBase
from app.models.recinto import Recinto
from app.schemas.recinto import RecintoCreate

recinto_crud = CRUDBase[Recinto, RecintoCreate](Recinto)
