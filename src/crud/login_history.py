"""Круд логинов."""
from crud.base_crud import CRUDSQLAlchemy
from models.entity import LoginHistory


class CRUDLoginHistory(CRUDSQLAlchemy):
    """Круд логинов."""

    pass


DBLoginHistory = CRUDSQLAlchemy(LoginHistory)
