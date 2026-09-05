from django.urls import path

from .views import (
    BabyListCreateView,
    BabyDetailView,
    GlucoseReadingListCreateView,
    GlucoseReadingDetailView,
)


urlpatterns = [
    # ==========================================
    # BABY URLS
    # ==========================================

    path(
        "babies/",
        BabyListCreateView.as_view(),
        name="baby-list-create",
    ),

    path(
        "babies/<str:baby_id>/",
        BabyDetailView.as_view(),
        name="baby-detail",
    ),

    # ==========================================
    # GLUCOSE READING URLS
    # ==========================================

    path(
        "babies/<str:baby_id>/readings/",
        GlucoseReadingListCreateView.as_view(),
        name="reading-list-create",
    ),

    path(
        "babies/<str:baby_id>/readings/<int:pk>/",
        GlucoseReadingDetailView.as_view(),
        name="reading-detail",
    ),
]