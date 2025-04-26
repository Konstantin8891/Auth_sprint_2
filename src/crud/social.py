"""Круд соц сеть."""

from crud.base_crud import CRUDSQLAlchemy
from models.entity import SocialNetwork


class CRUDRole(CRUDSQLAlchemy):
    """Круд роль."""

    pass


DBSocial = CRUDRole(SocialNetwork)
