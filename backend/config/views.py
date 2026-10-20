from django.db import DatabaseError, connection
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

HealthSerializer = inline_serializer(
    name="Health",
    fields={"status": serializers.ChoiceField(choices=["ok", "error"])},
)


@extend_schema(responses={200: HealthSerializer, 503: HealthSerializer})
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request: Request) -> Response:
    """Report whether the API is up and can reach the database."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return Response({"status": "error"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"status": "ok"})
