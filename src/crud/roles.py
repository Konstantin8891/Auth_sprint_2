"""Круд роль."""

from crud.base_crud import CRUDSQLAlchemy
from models.entity import Role


class CRUDRole(CRUDSQLAlchemy):
    """Круд роль."""

    pass


DBRole = CRUDRole(Role)
