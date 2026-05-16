from django.contrib import admin
from .models import ConversionTask


@admin.register(ConversionTask)
class ConversionTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "filename",
        "source_format",
        "target_format",
        "bitrate",
        "channels",
        "status",
        "created_at",
    )
    list_filter = ("source_format", "target_format", "status")
    search_fields = ("filename",)