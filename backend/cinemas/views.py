from django.utils import timezone
from django.utils.dateparse import parse_date
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from .models import Showtime
from .serializers import ShowtimeSerializer


@extend_schema(
    parameters=[
        OpenApiParameter("movie", OpenApiTypes.INT, description="Only showtimes of this movie id."),
        OpenApiParameter(
            "date",
            OpenApiTypes.DATE,
            description="Only showtimes on this local date (America/Vancouver), YYYY-MM-DD.",
        ),
    ]
)
class ShowtimeListView(generics.ListAPIView):
    """Upcoming showtimes, optionally filtered by movie and date."""

    serializer_class = ShowtimeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Showtime.objects.select_related("auditorium").filter(
            starts_at__gte=timezone.now()
        )

        movie = self.request.query_params.get("movie")
        if movie is not None:
            try:
                movie_id = int(movie)
            except ValueError:
                raise ValidationError({"movie": "Must be a movie id (an integer)."}) from None
            queryset = queryset.filter(movie_id=movie_id)

        date = self.request.query_params.get("date")
        if date is not None:
            try:
                local_date = parse_date(date)
                if local_date is None:
                    raise ValueError
            except ValueError:
                raise ValidationError({"date": "Must be a date in YYYY-MM-DD format."}) from None

            queryset = queryset.filter(starts_at__date=local_date)

        return queryset
