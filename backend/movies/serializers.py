from rest_framework import serializers

from .models import Movie


class MovieListSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "poster_path",
            "backdrop_path",
            "release_date",
            "classification",
            "runtime",
            "genres",
        ]


class MovieDetailSerializer(MovieListSerializer):
    class Meta(MovieListSerializer.Meta):
        fields = MovieListSerializer.Meta.fields + [
            "synopsis",
            "trailer",
        ]
