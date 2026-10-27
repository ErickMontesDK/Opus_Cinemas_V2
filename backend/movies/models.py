from django.db import models


class Genre(models.Model):
    tmdb_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    tmdb_id = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=255)
    synopsis = models.TextField(default="", blank=True)
    runtime = models.PositiveIntegerField(null=True, blank=True)
    classification = models.CharField(max_length=10, default="", blank=True)
    release_date = models.DateField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, default="", blank=True)
    backdrop_path = models.CharField(max_length=255, default="", blank=True)
    trailer = models.URLField(default="", blank=True)
    genres = models.ManyToManyField("Genre", related_name="movies", blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
