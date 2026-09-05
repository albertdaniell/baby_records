from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import (
    DrugViewSet,
    BabyDrugPlanViewSet,
    BabyDrugScheduleViewSet,
    DrugIntakeRecordViewSet,
    upcoming_drugs,
)


# =========================================================
# ROUTER
# =========================================================

router = DefaultRouter()


# =========================================================
# DRUGS
# =========================================================

router.register(
    "drugs",
    DrugViewSet,
    basename="drug"
)


# =========================================================
# BABY DRUG PLANS
# =========================================================

router.register(
    "drug-plans",
    BabyDrugPlanViewSet,
    basename="drug-plan"
)


# =========================================================
# DRUG SCHEDULES
# =========================================================

router.register(
    "drug-schedules",
    BabyDrugScheduleViewSet,
    basename="drug-schedule"
)


# =========================================================
# DRUG INTAKE RECORDS
# =========================================================

router.register(
    "drug-intake-records",
    DrugIntakeRecordViewSet,
    basename="drug-intake-record"
)


# =========================================================
# CUSTOM URLS
# =========================================================

urlpatterns = [

    # =====================================================
    # UPCOMING DRUGS
    # =====================================================

    path(
        "upcoming/",
        upcoming_drugs,
        name="upcoming-drugs",
    ),

]


# =========================================================
# ADD ROUTER URLS
# =========================================================

urlpatterns += router.urls