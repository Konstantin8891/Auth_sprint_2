"""Модели админки."""

from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    """Жанр инлайн."""

    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    """Персона инлайн."""

    model = PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Жанр."""

    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    """Кинопроизведение."""

    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    list_display = (
        "title",
        "type",
        "creation_date",
        "rating",
    )
    list_filter = ("type",)
    search_fields = ("title", "description", "id")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Персоны кинопроизведения."""

    inlines = (PersonFilmworkInline,)
    list_display = ("full_name",)
    search_fields = ("full_name",)
