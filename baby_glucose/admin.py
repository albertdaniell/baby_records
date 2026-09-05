from django.contrib import admin

from .models import (
    Baby,
)


@admin.register(Baby)
class BabyAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "baby_id",
    )

    search_fields = (
        "baby_id",
    )