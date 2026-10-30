from django.urls import path

from .views import ShowtimeListView

urlpatterns = [
    path("showtimes/", ShowtimeListView.as_view(), name="showtime-list"),
]
