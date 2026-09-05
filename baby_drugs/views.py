from datetime import date as datetime_date

from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Drug,
    BabyDrugPlan,
    BabyDrugSchedule,
    DrugIntakeRecord,
)

from .serializers import (
    DrugSerializer,
    BabyDrugPlanSerializer,
    BabyDrugScheduleSerializer,
    DrugIntakeRecordSerializer,
)


# =========================================================
# DRUG CRUD
# =========================================================

class DrugViewSet(viewsets.ModelViewSet):

    queryset = Drug.objects.all().order_by("name")

    serializer_class = DrugSerializer


# =========================================================
# BABY DRUG PLAN CRUD
# =========================================================

class BabyDrugPlanViewSet(viewsets.ModelViewSet):

    serializer_class = BabyDrugPlanSerializer


    def get_queryset(self):

        queryset = (
            BabyDrugPlan.objects
            .select_related(
                "baby",
                "drug",
            )
            .all()
            .order_by(
                "-is_active",
                "drug__name",
            )
        )


        # Filter by baby's unique ID
        baby_id = self.request.query_params.get(
            "baby_id"
        )

        if baby_id:

            queryset = queryset.filter(
                baby__baby_id=baby_id
            )


        # Filter active plans
        is_active = self.request.query_params.get(
            "is_active"
        )

        if is_active is not None:

            if is_active.lower() == "true":

                queryset = queryset.filter(
                    is_active=True
                )

            elif is_active.lower() == "false":

                queryset = queryset.filter(
                    is_active=False
                )


        return queryset


# =========================================================
# BABY DRUG SCHEDULE CRUD
# =========================================================

class BabyDrugScheduleViewSet(viewsets.ModelViewSet):

    serializer_class = BabyDrugScheduleSerializer


    def get_queryset(self):

        queryset = (
            BabyDrugSchedule.objects
            .select_related(
                "baby_drug_plan",
                "baby_drug_plan__baby",
                "baby_drug_plan__drug",
            )
            .all()
            .order_by(
                "dose_order",
                "scheduled_time",
            )
        )


        # =================================================
        # FILTER BY BABY UNIQUE ID
        # =================================================

        baby_id = self.request.query_params.get(
            "baby_id"
        )

        if baby_id:

            queryset = queryset.filter(
                baby_drug_plan__baby__baby_id=baby_id
            )


        # =================================================
        # FILTER BY BABY DRUG PLAN
        # =================================================

        baby_drug_plan_id = self.request.query_params.get(
            "baby_drug_plan"
        )

        if baby_drug_plan_id:

            queryset = queryset.filter(
                baby_drug_plan_id=baby_drug_plan_id
            )


        return queryset


# =========================================================
# DRUG INTAKE RECORD CRUD
# =========================================================

class DrugIntakeRecordViewSet(viewsets.ModelViewSet):

    serializer_class = DrugIntakeRecordSerializer


    # =====================================================
    # GET QUERYSET
    # =====================================================

    def get_queryset(self):

        queryset = (
            DrugIntakeRecord.objects
            .select_related(
                "schedule",
                "schedule__baby_drug_plan",
                "schedule__baby_drug_plan__baby",
                "schedule__baby_drug_plan__drug",
            )
            .all()
            .order_by(
                "-date",
                "schedule__dose_order",
                "schedule__scheduled_time",
            )
        )


        # =================================================
        # FILTER BY BABY UNIQUE ID
        # =================================================

        baby_id = self.request.query_params.get(
            "baby_id"
        )

        if baby_id:

            queryset = queryset.filter(
                schedule__baby_drug_plan__baby__baby_id=baby_id
            )


        # =================================================
        # FILTER BY DATE
        # =================================================

        selected_date = self.request.query_params.get(
            "date"
        )

        if selected_date:

            queryset = queryset.filter(
                date=selected_date
            )


        # =================================================
        # FILTER BY STATUS
        #
        # pending
        # taken
        # missed
        # skipped
        # =================================================

        status_filter = self.request.query_params.get(
            "status"
        )

        if status_filter:

            queryset = queryset.filter(
                status=status_filter
            )


        return queryset


    # =====================================================
    # MARK DRUG AS TAKEN
    #
    # POST:
    #
    # /drug-intake-records/{id}/mark_taken/
    # =====================================================

    @action(
        detail=True,
        methods=["post"],
    )
    def mark_taken(self, request, pk=None):

        record = self.get_object()


        # Mark as taken
        record.status = "taken"


        # Save actual time
        if not record.taken_at:

            record.taken_at = timezone.now()


        # Optional notes
        notes = request.data.get("notes")

        if notes is not None:

            record.notes = notes


        record.save()


        serializer = self.get_serializer(
            record
        )


        return Response(
            {
                "message": "Drug marked as taken successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


    # =====================================================
    # MARK DRUG AS PENDING
    #
    # POST:
    #
    # /drug-intake-records/{id}/mark_pending/
    # =====================================================

    @action(
        detail=True,
        methods=["post"],
    )
    def mark_pending(self, request, pk=None):

        record = self.get_object()


        record.status = "pending"

        record.taken_at = None


        record.save()


        serializer = self.get_serializer(
            record
        )


        return Response(
            {
                "message": "Drug marked as pending.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


    # =====================================================
    # MARK DRUG AS MISSED
    #
    # POST:
    #
    # /drug-intake-records/{id}/mark_missed/
    # =====================================================

    @action(
        detail=True,
        methods=["post"],
    )
    def mark_missed(self, request, pk=None):

        record = self.get_object()


        record.status = "missed"

        record.taken_at = None


        notes = request.data.get("notes")

        if notes is not None:

            record.notes = notes


        record.save()


        serializer = self.get_serializer(
            record
        )


        return Response(
            {
                "message": "Drug marked as missed.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


    # =====================================================
    # MARK DRUG AS SKIPPED
    #
    # POST:
    #
    # /drug-intake-records/{id}/mark_skipped/
    # =====================================================

    @action(
        detail=True,
        methods=["post"],
    )
    def mark_skipped(self, request, pk=None):

        record = self.get_object()


        record.status = "skipped"

        record.taken_at = None


        notes = request.data.get("notes")

        if notes is not None:

            record.notes = notes


        record.save()


        serializer = self.get_serializer(
            record
        )


        return Response(
            {
                "message": "Drug marked as skipped.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


    # =====================================================
    # DAILY DRUG DASHBOARD
    #
    # GET:
    #
    # /drug-intake-records/daily/?baby_id=49H0ZZUN
    #
    # OR:
    #
    # /drug-intake-records/daily/?baby_id=49H0ZZUN&date=2026-09-05
    # =====================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="daily",
    )
    def daily(self, request):

        baby_id = request.query_params.get(
            "baby_id"
        )


        # =================================================
        # BABY ID REQUIRED
        # =================================================

        if not baby_id:

            return Response(
                {
                    "error": "baby_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


        # =================================================
        # GET REQUESTED DATE
        # =================================================

        requested_date = request.query_params.get(
            "date"
        )


        if requested_date:

            try:

                selected_date = datetime_date.fromisoformat(
                    requested_date
                )

            except ValueError:

                return Response(
                    {
                        "error": (
                            "Invalid date format. "
                            "Use YYYY-MM-DD."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:

            selected_date = timezone.localdate()


        # =================================================
        # GET RECORDS
        # =================================================

        records = (
            DrugIntakeRecord.objects
            .filter(
                schedule__baby_drug_plan__baby__baby_id=baby_id,
                date=selected_date,
            )
            .select_related(
                "schedule",
                "schedule__baby_drug_plan",
                "schedule__baby_drug_plan__baby",
                "schedule__baby_drug_plan__drug",
            )
            .order_by(
                "schedule__dose_order",
                "schedule__scheduled_time",
            )
        )


        # =================================================
        # SPLIT RECORDS BY STATUS
        # =================================================

        taken_records = records.filter(
            status="taken"
        )


        pending_records = records.filter(
            status="pending"
        )


        missed_records = records.filter(
            status="missed"
        )


        skipped_records = records.filter(
            status="skipped"
        )


        # =================================================
        # UPCOMING
        #
        # For now:
        #
        # pending = upcoming
        # =================================================

        upcoming_records = pending_records


        # =================================================
        # SERIALIZE
        # =================================================

        all_serializer = self.get_serializer(
            records,
            many=True,
        )


        taken_serializer = self.get_serializer(
            taken_records,
            many=True,
        )


        upcoming_serializer = self.get_serializer(
            upcoming_records,
            many=True,
        )


        pending_serializer = self.get_serializer(
            pending_records,
            many=True,
        )


        missed_serializer = self.get_serializer(
            missed_records,
            many=True,
        )


        skipped_serializer = self.get_serializer(
            skipped_records,
            many=True,
        )


        # =================================================
        # RESPONSE
        # =================================================

        return Response(
            {

                "baby_id": baby_id,

                "date": selected_date.isoformat(),


                # -----------------------------------------
                # COUNTS
                # -----------------------------------------

                "total_drugs": records.count(),

                "taken_count": taken_records.count(),

                "pending_count": pending_records.count(),

                "upcoming_count": upcoming_records.count(),

                "missed_count": missed_records.count(),

                "skipped_count": skipped_records.count(),


                # -----------------------------------------
                # DATA
                # -----------------------------------------

                "taken": taken_serializer.data,

                "pending": pending_serializer.data,

                "upcoming": upcoming_serializer.data,

                "missed": missed_serializer.data,

                "skipped": skipped_serializer.data,

                "all": all_serializer.data,

            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# IMPORTS
# =========================================================

from datetime import date as datetime_date

from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import DrugIntakeRecord
from .serializers import DrugIntakeRecordSerializer


# =========================================================
# UPCOMING DRUGS
#
# GET:
#
# /upcoming/?baby_id=49H0ZZUN
#
# OPTIONAL:
#
# /upcoming/?baby_id=49H0ZZUN&date=2026-09-05
# =========================================================


from datetime import timedelta

from django.db.models import Q

from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import (
    BabyDrugSchedule,
    DrugIntakeRecord,
)

from .serializers import (
    BabyDrugScheduleSerializer,
)


# =========================================================
# UPCOMING DRUGS
# =========================================================

@api_view(["GET"])
def upcoming_drugs(request):


    # =================================================
    # GET BABY ID
    # =================================================

    baby_id = request.query_params.get(
        "baby_id"
    )


    # =================================================
    # VALIDATE BABY ID
    # =================================================

    if not baby_id:

        return Response(

            {
                "error":
                    "baby_id is required."
            },

            status=status.HTTP_400_BAD_REQUEST

        )


    # =================================================
    # CURRENT DATE AND TIME
    # =================================================

    now = timezone.localtime()

    today = now.date()

    tomorrow = (

        today +

        timedelta(days=1)

    )

    current_time = now.time()


    # =================================================
    # GET ALL ACTIVE SCHEDULES FOR BABY
    # =================================================

    schedules = (

        BabyDrugSchedule.objects

        .filter(

            baby_drug_plan__baby__baby_id=
            baby_id,

            baby_drug_plan__is_active=True,

        )

        .select_related(

            "baby_drug_plan",

            "baby_drug_plan__baby",

            "baby_drug_plan__drug",

        )

        .order_by(

            "scheduled_time",

            "dose_order",

            "id",

        )

        .distinct()

    )


    # =================================================
    # HELPER:
    # GET UPCOMING SCHEDULES FOR A DATE
    # =================================================

    def get_upcoming_for_date(
        target_date,
        is_today=False
    ):


        # =============================================
        # GET PLANS VALID FOR THIS DATE
        #
        # Valid when:
        #
        # start_date is NULL
        # OR start_date <= target_date
        #
        # AND
        #
        # end_date is NULL
        # OR end_date >= target_date
        # =============================================

        date_schedules = (

            schedules

            .filter(

                Q(

                    baby_drug_plan__start_date__isnull=True

                )

                |

                Q(

                    baby_drug_plan__start_date__lte=
                    target_date

                )

            )

            .filter(

                Q(

                    baby_drug_plan__end_date__isnull=True

                )

                |

                Q(

                    baby_drug_plan__end_date__gte=
                    target_date

                )

            )

        )


        # =============================================
        # TODAY:
        #
        # ONLY SCHEDULES STILL AHEAD
        # =============================================

        if is_today:

            date_schedules = (

                date_schedules

                .filter(

                    scheduled_time__gt=
                    current_time

                )

            )


        # =============================================
        # GET COMPLETED SCHEDULE IDS
        #
        # Do not show schedules already marked:
        #
        # taken
        # missed
        # skipped
        # =============================================

        completed_schedule_ids = (

            DrugIntakeRecord.objects

            .filter(

                schedule__in=
                date_schedules,

                date=
                target_date,

                status__in=[

                    "taken",

                    "missed",

                    "skipped",

                ],

            )

            .values_list(

                "schedule_id",

                flat=True

            )

            .distinct()

        )


        # =============================================
        # REMOVE COMPLETED SCHEDULES
        # =============================================

        upcoming_schedules = (

            date_schedules

            .exclude(

                id__in=
                completed_schedule_ids

            )

            .order_by(

                "scheduled_time",

                "dose_order",

                "id",

            )

            .distinct()

        )


        return upcoming_schedules


    # =================================================
    # GET TODAY'S UPCOMING SCHEDULES
    # =================================================

    today_schedules = (

        get_upcoming_for_date(

            target_date=
            today,

            is_today=True

        )

    )


    # =================================================
    # GET TOMORROW'S SCHEDULES
    # =================================================

    tomorrow_schedules = (

        get_upcoming_for_date(

            target_date=
            tomorrow,

            is_today=False

        )

    )


    # =================================================
    # SERIALIZE TODAY
    # =================================================

    today_serializer = (

        BabyDrugScheduleSerializer(

            today_schedules,

            many=True,

            context={

                "request":
                    request

            }

        )

    )


    # =================================================
    # SERIALIZE TOMORROW
    # =================================================

    tomorrow_serializer = (

        BabyDrugScheduleSerializer(

            tomorrow_schedules,

            many=True,

            context={

                "request":
                    request

            }

        )

    )


    # =================================================
    # BUILD TODAY DRUG OCCURRENCES
    # =================================================

    all_today_drugs = []


    for drug in today_serializer.data:


        all_today_drugs.append(

            {

                **drug,


                "scheduled_date":

                    str(today),


                "day":

                    "today",


                # Unique occurrence key

                "occurrence_id":

                    f"schedule-{drug['id']}-{today}",

            }

        )


    # =================================================
    # BUILD TOMORROW DRUG OCCURRENCES
    # =================================================

    all_tomorrow_drugs = []


    for drug in tomorrow_serializer.data:


        all_tomorrow_drugs.append(

            {

                **drug,


                "scheduled_date":

                    str(tomorrow),


                "day":

                    "tomorrow",


                # Unique occurrence key

                "occurrence_id":

                    f"schedule-{drug['id']}-{tomorrow}",

            }

        )


    # =================================================
    # HELPER:
    # GET SCHEDULED TIME
    # =================================================

    def get_drug_time(drug):

        return (

            drug.get(
                "scheduled_time"
            )

            or

            drug.get(
                "proposed_time"
            )

            or

            ""

        )


    # =================================================
    # TODAY:
    #
    # SHOW ONLY THE NEXT TIME GROUP
    #
    # Example:
    #
    # 18:00 -> Bioga
    # 18:00 -> Vitamin D
    #
    # Both are returned.
    # =================================================

    today_drugs = []


    if all_today_drugs:


        next_today_time = (

            get_drug_time(

                all_today_drugs[0]

            )

        )


        today_drugs = [

            drug

            for drug in all_today_drugs

            if

            get_drug_time(drug)

            ==

            next_today_time

        ]


    # =================================================
    # TOMORROW:
    #
    # SHOW ONLY FIRST TWO TIME GROUPS
    #
    # Example:
    #
    # 08:00 -> Bioga
    # 08:00 -> Vitamin D
    #
    # 14:00 -> Paracetamol
    #
    # Both time groups are returned.
    # =================================================

    tomorrow_time_groups = []


    for drug in all_tomorrow_drugs:


        drug_time = (

            get_drug_time(
                drug
            )

        )


        # =============================================
        # ADD A NEW TIME GROUP
        # =============================================

        if (

            drug_time

            not in

            tomorrow_time_groups

        ):


            tomorrow_time_groups.append(

                drug_time

            )


        # =============================================
        # IMPORTANT:
        #
        # We do NOT break here.
        #
        # We need to continue through the list so all
        # medicines belonging to the first two time
        # groups can be collected.
        # =============================================


    # =================================================
    # KEEP ONLY FIRST TWO TIMES
    # =================================================

    allowed_tomorrow_times = (

        tomorrow_time_groups[:2]

    )


    tomorrow_drugs = [

        drug

        for drug in all_tomorrow_drugs

        if

        get_drug_time(drug)

        in

        allowed_tomorrow_times

    ]


    # =================================================
    # NEXT DRUG
    #
    # First medicine from today's next group.
    #
    # If no medicine remains today,
    # use tomorrow's first medicine.
    # =================================================

    next_drug = None


    if today_drugs:


        next_drug = (

            today_drugs[0]

        )


    elif tomorrow_drugs:


        next_drug = (

            tomorrow_drugs[0]

        )


    # =================================================
    # COMBINED UPCOMING DRUGS
    # =================================================

    upcoming_drugs_list = (

        today_drugs

        +

        tomorrow_drugs

    )


    # =================================================
    # RESPONSE
    # =================================================

    return Response(

        {


            # =========================================
            # BABY
            # =========================================

            "baby_id":

                baby_id,


            # =========================================
            # CURRENT DATE
            # =========================================

            "current_date":

                str(today),


            # =========================================
            # CURRENT TIME
            # =========================================

            "current_time":

                current_time.strftime(
                    "%H:%M:%S"
                ),


            # =========================================
            # TODAY
            # =========================================

            "today": {

                "date":

                    str(today),


                "count":

                    len(today_drugs),


                "drugs":

                    today_drugs,

            },


            # =========================================
            # TOMORROW
            # =========================================

            "tomorrow": {

                "date":

                    str(tomorrow),


                "count":

                    len(tomorrow_drugs),


                "drugs":

                    tomorrow_drugs,

            },


            # =========================================
            # TOTAL UPCOMING
            # =========================================

            "upcoming_count":

                len(
                    upcoming_drugs_list
                ),


            # =========================================
            # NEXT DRUG
            # =========================================

            "next_drug":

                next_drug,


            # =========================================
            # COMBINED UPCOMING
            # =========================================

            "upcoming":

                upcoming_drugs_list,

        },

        status=status.HTTP_200_OK

    )