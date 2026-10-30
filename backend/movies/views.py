from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Movie
from .serializers import MovieDetailSerializer, MovieListSerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    # All movies for now; step 2.10 limits the list to movies with upcoming showtimes.
    # prefetch_related loads every movie's genres in one extra query, not one per movie.
    queryset = Movie.objects.prefetch_related("genres")
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MovieDetailSerializer
        return MovieListSerializer
