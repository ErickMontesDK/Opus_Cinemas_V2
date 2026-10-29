from django.contrib import admin

from .models import Auditorium, Seat, Showtime


@admin.register(Auditorium)
class AuditoriumAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "columns")
    search_fields = ("name",)

    def get_readonly_fields(self, request, obj=None):
        # Seats are generated from rows x columns when the auditorium is created.
        # Changing the size later would leave seats (and future tickets) out of sync,
        # so the dimensions are locked once the auditorium exists.
        if obj is not None:
            return ("rows", "columns")
        return ()


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("label", "auditorium", "seat_type")

    list_editable = ("seat_type",)
    list_filter = ("auditorium", "seat_type")
    readonly_fields = ("auditorium", "row", "number")

    def has_add_permission(self, request):
        return False


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ("movie", "auditorium", "starts_at", "ends_at", "base_price")
    list_filter = ("auditorium", "movie")
    date_hierarchy = "starts_at"
    # Needs search_fields on MovieAdmin.
    autocomplete_fields = ("movie",)
    readonly_fields = ("ends_at",)
