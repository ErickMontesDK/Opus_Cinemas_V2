from rest_framework import serializers

from .models import Showtime


class ShowtimeSerializer(serializers.ModelSerializer):
    auditorium = serializers.StringRelatedField()

    class Meta:
        model = Showtime
        fields = ["id", "movie", "auditorium", "starts_at", "ends_at", "base_price"]
