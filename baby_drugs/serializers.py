from rest_framework import serializers

from .models import (
    Drug,
    BabyDrugPlan,
    BabyDrugSchedule,
    DrugIntakeRecord,
)
from baby_glucose.models import Baby

# =========================================================
# DRUG
# =========================================================

class DrugSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()


    class Meta:
        model = Drug

        fields = [
            "id",
            "name",
            "administration_type",
            "amount",
            "unit",
            "image",
            "image_url",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


    def get_image_url(self, obj):

        if not obj.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url


# =========================================================
# BABY DRUG PLAN
# =========================================================

class BabyDrugPlanSerializer(serializers.ModelSerializer):

    drug_details = DrugSerializer(

        source="drug",

        read_only=True,

    )

    baby_id = serializers.SlugRelatedField(

        source="baby",

        slug_field="baby_id",

        queryset=Baby.objects.all(),

    )

    class Meta:

        model = BabyDrugPlan

        fields = [

            "id",

            # database relationship (optional)

            "baby",

            # your unique baby ID

            "baby_id",

            "drug",

            "drug_details",

            "times_per_day",

            "is_active",

            "start_date",

            "end_date",

            "notes",

            "created_at",

        ]

        read_only_fields = [

            "id",

            "created_at",

        ]

# =========================================================
# BABY DRUG SCHEDULE
# =========================================================

class BabyDrugScheduleSerializer(serializers.ModelSerializer):

    drug_name = serializers.CharField(
        source="baby_drug_plan.drug.name",
        read_only=True,
    )


    drug_details = DrugSerializer(
        source="baby_drug_plan.drug",
        read_only=True,
    )


    baby = serializers.SerializerMethodField()


    class Meta:
        model = BabyDrugSchedule

        fields = [
            "id",
            "baby_drug_plan",
            "baby",
            "drug_name",
            "drug_details",
            "dose_order",
            "scheduled_time",
            "amount",
            "unit",
        ]

        read_only_fields = [
            "id",
        ]


    def get_baby(self, obj):

        return obj.baby_drug_plan.baby_id


# =========================================================
# DRUG INTAKE RECORD
# =========================================================

class DrugIntakeRecordSerializer(serializers.ModelSerializer):

    drug_name = serializers.CharField(
        source="schedule.baby_drug_plan.drug.name",
        read_only=True,
    )


    drug_details = DrugSerializer(
        source="schedule.baby_drug_plan.drug",
        read_only=True,
    )


    baby = serializers.SerializerMethodField()


    scheduled_time = serializers.TimeField(
        source="schedule.scheduled_time",
        read_only=True,
    )


    dose_order = serializers.IntegerField(
        source="schedule.dose_order",
        read_only=True,
    )


    amount = serializers.DecimalField(
        source="schedule.amount",
        max_digits=6,
        decimal_places=2,
        read_only=True,
    )


    unit = serializers.CharField(
        source="schedule.unit",
        read_only=True,
    )


    class Meta:
        model = DrugIntakeRecord

        fields = [
            "id",

            # Baby information
            "baby",

            # Schedule
            "schedule",
            "dose_order",
            "scheduled_time",

            # Drug information
            "drug_name",
            "drug_details",

            # Dose information
            "amount",
            "unit",

            # Daily record
            "date",
            "status",
            "taken_at",
            "notes",

            # Metadata
            "created_at",
        ]

        read_only_fields = [
            "id",
            "baby",
            "dose_order",
            "scheduled_time",
            "drug_name",
            "drug_details",
            "amount",
            "unit",
            "created_at",
        ]


    def get_baby(self, obj):

        return obj.schedule.baby_drug_plan.baby_id