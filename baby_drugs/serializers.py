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

            return request.build_absolute_uri(
                obj.image.url
            )


        return obj.image.url


# =========================================================
# BABY DRUG PLAN
# =========================================================

class BabyDrugPlanSerializer(serializers.ModelSerializer):


    # =====================================================
    # DRUG DETAILS
    # =====================================================

    drug_details = DrugSerializer(

        source="drug",

        read_only=True,

    )


    # =====================================================
    # BABY ID
    #
    # This allows:
    #
    # {
    #     "baby_id": "49H0ZZUN"
    # }
    #
    # to map to the Baby model relationship.
    # =====================================================

    baby_id = serializers.SlugRelatedField(

        source="baby",

        slug_field="baby_id",

        queryset=Baby.objects.all(),

        required=False,

    )


    class Meta:

        model = BabyDrugPlan


        fields = [

            "id",

            # Database relationship
            "baby",

            # Custom baby ID
            "baby_id",

            # Drug
            "drug",

            # Expanded drug information
            "drug_details",

            # Plan information
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


        # =================================================
        # IMPORTANT
        #
        # Prevent DRF from generating a UniqueTogetherValidator
        # for both "baby" and "baby_id", since both fields
        # point to the same BabyDrugPlan.baby model field.
        # =================================================

        validators = []


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

            # Plan
            "baby_drug_plan",

            # Baby ID
            "baby",

            # Drug information
            "drug_name",

            "drug_details",

            # Schedule information
            "dose_order",

            "scheduled_time",

            "amount",

            "unit",

        ]


        read_only_fields = [

            "id",

            "baby",

            "drug_name",

            "drug_details",

        ]


    def get_baby(self, obj):

        return obj.baby_drug_plan.baby.baby_id


# =========================================================
# DRUG INTAKE RECORD
# =========================================================

class DrugIntakeRecordSerializer(serializers.ModelSerializer):


    # =====================================================
    # DRUG NAME
    # =====================================================

    drug_name = serializers.CharField(

        source="schedule.baby_drug_plan.drug.name",

        read_only=True,

    )


    # =====================================================
    # FULL DRUG DETAILS
    # =====================================================

    drug_details = DrugSerializer(

        source="schedule.baby_drug_plan.drug",

        read_only=True,

    )


    # =====================================================
    # BABY
    # =====================================================

    baby = serializers.SerializerMethodField()


    # =====================================================
    # SCHEDULE TIME
    # =====================================================

    scheduled_time = serializers.TimeField(

        source="schedule.scheduled_time",

        read_only=True,

    )


    # =====================================================
    # DOSE ORDER
    # =====================================================

    dose_order = serializers.IntegerField(

        source="schedule.dose_order",

        read_only=True,

    )


    # =====================================================
    # AMOUNT
    # =====================================================

    amount = serializers.DecimalField(

        source="schedule.amount",

        max_digits=6,

        decimal_places=2,

        read_only=True,

    )


    # =====================================================
    # UNIT
    # =====================================================

    unit = serializers.CharField(

        source="schedule.unit",

        read_only=True,

    )


    class Meta:

        model = DrugIntakeRecord


        fields = [

            "id",


            # =============================================
            # BABY INFORMATION
            # =============================================

            "baby",


            # =============================================
            # SCHEDULE
            # =============================================

            "schedule",

            "dose_order",

            "scheduled_time",


            # =============================================
            # DRUG INFORMATION
            # =============================================

            "drug_name",

            "drug_details",


            # =============================================
            # DOSE INFORMATION
            # =============================================

            "amount",

            "unit",


            # =============================================
            # DAILY RECORD
            # =============================================

            "date",

            "status",

            "taken_at",

            "notes",


            # =============================================
            # METADATA
            # =============================================

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

        return obj.schedule.baby_drug_plan.baby.baby_id