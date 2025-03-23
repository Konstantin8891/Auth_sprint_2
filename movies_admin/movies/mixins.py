"""Миксины моделей."""
import uuid

from django.db import models


class TimeStampedMixin(models.Model):
    """Миксин создано модифицировано."""

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        """Мета."""

        abstract = True


class UUIDMixin(models.Model):
    """Гуид миксин."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        """Мета."""

        abstract = True
