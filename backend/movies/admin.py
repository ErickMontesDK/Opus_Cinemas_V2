from django.contrib import admin

from .models import Genre, Movie


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "tmdb_id")
    search_fields = ("name", "=tmdb_id")


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "tmdb_id", "release_date", "runtime", "classification")
    list_filter = ("release_date", "genres")
    search_fields = ("title", "=tmdb_id")
    filter_horizontal = ("genres",)
