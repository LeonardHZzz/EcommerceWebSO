from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base declarativa para todos los modelos ORM.

    IMPORTANTE: este módulo NO debe importar los modelos (causaría un
    import circular, ya que cada modelo importa Base desde aquí). El
    registro de todos los modelos en Base.metadata se hace en
    app/models/__init__.py, que se importa desde main.py y desde
    alembic/env.py.
    """
    pass

