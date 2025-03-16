"""Круд раздел."""

from crud.base_crud import CRUDSQLAlchemy
from models.entity import Section


class CRUDSection(CRUDSQLAlchemy):
    """Круд раздел."""

    pass


DBSection = CRUDSection(Section)
