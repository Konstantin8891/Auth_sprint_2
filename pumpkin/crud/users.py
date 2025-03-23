"""Пользователи - круд."""

from crud.base_crud import CRUDSQLAlchemy
from models.entity import User


class CRUDUser(CRUDSQLAlchemy):
    """Круд пользователь."""

    pass


DBUser = CRUDUser(User)
