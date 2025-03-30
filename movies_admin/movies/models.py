"""Модели."""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import TimeStampedMixin, UUIDMixin


class Genre(UUIDMixin, TimeStampedMixin):
    """Жанры."""

    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)

    class Meta:
        """Мета."""

        db_table = 'content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        """Строковое представление."""
        return self.name


class Filmwork(UUIDMixin, TimeStampedMixin):
    """Кинопроизвдение."""

    class FilmworkType(models.TextChoices):
        """Тип кинопроизведения."""

        MOVIE = "movie", _("movie")
        TVSHOW = "tv_show", _("tv_show")

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)
    creation_date = models.DateField(_("creation_date"), null=True, blank=True)
    rating = models.FloatField(
        _("rating"),
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.CharField(_("type"), max_length=20, choices=FilmworkType.choices)

    genres = models.ManyToManyField(Genre, through="GenreFilmwork", verbose_name=_("genres"))
    persons = models.ManyToManyField("Person", through="PersonFilmwork", verbose_name=_("person"))

    class Meta:
        """Мета."""

        db_table = 'content"."film_work'
        verbose_name = _("Filmwork")
        verbose_name_plural = _("Filmworks")
        indexes = [models.Index(fields=["creation_date"], name="film_work_creation_date_idx")]

    def __str__(self):
        """Строковое представление."""
        return self.title


class GenreFilmwork(UUIDMixin):
    """Жанр кинопроизведения."""

    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Мета."""

        db_table = 'content"."genre_film_work'
        verbose_name = _("Genre filmwork")
        verbose_name_plural = _("Genre filmworks")
        constraints = [models.UniqueConstraint(fields=["film_work_id", "genre_id"], name="film_work_genre_idx")]


class Person(UUIDMixin, TimeStampedMixin):
    """Персона."""

    full_name = models.CharField(_("full name"), max_length=50)

    film_works = models.ManyToManyField(Filmwork, through="PersonFilmwork", verbose_name=_("filmwork"))

    class Meta:
        """Мета."""

        db_table = 'content"."person'
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")

    def __str__(self):
        """Строковое представление."""
        return self.full_name


class PersonFilmwork(UUIDMixin):
    """Персоны в кинопроиизведении."""

    class RoleChoices(models.TextChoices):
        """Роли."""

        ACTOR = "actor", _("actor")
        DIRECTOR = "director", _("director")
        WRITER = "writer", _("writer")

    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE, verbose_name=_("filmwork"))
    person = models.ForeignKey("Person", on_delete=models.CASCADE, verbose_name=_("person"))
    role = models.CharField(_("role"), max_length=50, choices=RoleChoices.choices)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        """Мета."""

        db_table = 'content"."person_film_work'
        verbose_name = _("Person filmwork")
        verbose_name_plural = _("person filmworks")
        constraints = [
            models.UniqueConstraint(
                fields=["film_work_id", "person_id", "role"],
                name="film_work_person_role_idx",
            )
        ]
