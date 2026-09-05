from django.contrib import admin

from .models import (
    Drug,
    BabyDrugPlan,
    BabyDrugSchedule,
    DrugIntakeRecord,
)


# =========================================================
# DRUG
# =========================================================

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "administration_type",
        "amount",
        "unit",
        "created_at",
    )

    list_filter = (
        "administration_type",
    )

    search_fields = (
        "name",
        "notes",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# BABY DRUG PLAN
# =========================================================

@admin.register(BabyDrugPlan)
class BabyDrugPlanAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "baby",
        "drug",
        "times_per_day",
        "is_active",
        "start_date",
        "end_date",
        "created_at",
    )

    list_filter = (
        "is_active",
        "start_date",
        "end_date",
    )

    search_fields = (
        "baby__baby_id",
        "drug__name",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# BABY DRUG SCHEDULE
# =========================================================

@admin.register(BabyDrugSchedule)
class BabyDrugScheduleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "baby_drug_plan",
        "get_baby",
        "get_drug",
        "dose_order",
        "scheduled_time",
        "amount",
        "unit",
    )

    list_filter = (
        "scheduled_time",
    )

    search_fields = (
        "baby_drug_plan__baby__baby_id",
        "baby_drug_plan__drug__name",
    )

    ordering = (
        "scheduled_time",
        "dose_order",
    )


    @admin.display(
        description="Baby"
    )
    def get_baby(self, obj):

        return obj.baby_drug_plan.baby


    @admin.display(
        description="Drug"
    )
    def get_drug(self, obj):

        return obj.baby_drug_plan.drug


# =========================================================
# DRUG INTAKE RECORD
# =========================================================

@admin.register(DrugIntakeRecord)
class DrugIntakeRecordAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "get_baby",
        "get_drug",
        "schedule",
        "date",
        "status",
        "taken_at",
        "created_at",
    )

    list_filter = (
        "status",
        "date",
    )

    search_fields = (
        "schedule__baby_drug_plan__baby__baby_id",
        "schedule__baby_drug_plan__drug__name",
    )

    ordering = (
        "-date",
        "-created_at",
    )


    @admin.display(
        description="Baby"
    )
    def get_baby(self, obj):

        return (
            obj.schedule
            .baby_drug_plan
            .baby
        )


    @admin.display(
        description="Drug"
    )
    def get_drug(self, obj):

        return (
            obj.schedule
            .baby_drug_plan
            .drug
        )