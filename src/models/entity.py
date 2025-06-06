"""Модели."""
import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base

association_table = Table(
    "userrole",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

social_users_table = Table(
    "usersocial",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("social_id", ForeignKey("social_network.id", ondelete="CASCADE"), primary_key=True),
)


def create_partition(target, connection, **kw):
    """Партицирование историй входа."""
    connection.execute(
        text(
            "CREATE TABLE login_history_y2024 PARTITION OF login_history FOR VALUES FROM ('2024-01-01 00:00:00') "
            "TO ('2025-01-01 00:00:00') PARTITION BY RANGE (created_at)"
        )
    )
    connection.execute(
        text(
            "CREATE TABLE login_history_y2025 PARTITION OF login_history FOR VALUES FROM ('2025-01-01 00:00:00') "
            "TO ('2026-01-01 00:00:00') PARTITION BY RANGE (created_at)"
        )
    )


class User(Base):
    """Пользователь."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("Role", back_populates="users", secondary=association_table, passive_deletes=True)
    login_history = relationship("LoginHistory", cascade="all, delete", back_populates="user")
    social = relationship("SocialNetwork", cascade="all, delete", back_populates="users", secondary=social_users_table)

    def __init__(self, login: str, first_name: str, last_name: str, password: Optional[str] = None) -> None:
        """Инит."""
        self.login = login
        if password:
            self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        """Сверка хеша и пароля."""
        if self.password:
            return check_password_hash(self.password, password)
        return False

    def __repr__(self) -> str:
        """Репр."""
        return f"<User {self.login}>"


class Role(Base):
    """Роль."""

    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(50), nullable=False, unique=True)

    users = relationship("User", back_populates="roles", secondary=association_table, cascade="all, delete")
    permissions = relationship("Permission", back_populates="roles")


class Section(Base):
    """Раздел."""

    __tablename__ = "sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(50), nullable=False, unique=True)

    roles = relationship("Permission", back_populates="section")


class Permission(Base):
    """Пермишен."""

    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    can_view = Column(Boolean, nullable=False)
    can_edit = Column(Boolean, nullable=False)
    can_delete = Column(Boolean, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=True)

    roles = relationship("Role", back_populates="permissions")
    section = relationship("Section", back_populates="roles", uselist=False)


class LoginHistory(Base):
    """История входов пользователя."""

    __tablename__ = "login_history"
    __table_args__ = (
        UniqueConstraint("id", "created_at"),
        {"postgresql_partition_by": "RANGE (created_at)", "listeners": [("after_create", create_partition)]},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user_agent = Column(String(250), nullable=True)
    host = Column(String(250), nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC), index=True, primary_key=True)

    user = relationship("User", back_populates="login_history", cascade="all, delete", uselist=False)


class SocialNetwork(Base):
    """Социальная сеть."""

    __tablename__ = "social_network"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(50), nullable=False)

    users = relationship(
        "User", back_populates="social", cascade="all, delete", uselist=False, secondary=social_users_table
    )
