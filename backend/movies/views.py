from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Movie
from .serializers import MovieDetailSerializer, MovieListSerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    # prefetch_related loads every movie's genres in one extra query, not one per movie.
    queryset = Movie.objects.prefetch_related("genres")
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        # The listing only shows movies with upcoming showtimes; the detail page
        # still works for any movie, so old links do not break.
        if self.action == "list":
            # now() is read per request; a class attribute would freeze it at import.
            # distinct(): the join returns one row per matching showtime.
            queryset = queryset.filter(showtimes__starts_at__gte=timezone.now()).distinct()
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MovieDetailSerializer
        return MovieListSerializer
