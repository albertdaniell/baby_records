from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from .models import Baby, GlucoseReading


class BabySerializer(serializers.ModelSerializer):
    class Meta:
        model = Baby
        fields = [
            "id",
            "baby_id",
            "name",
            "date_of_birth",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "baby_id",
            "created_at",
        ]


class GlucoseReadingSerializer(serializers.ModelSerializer):
    date = serializers.DateField(write_only=True)
    time = serializers.TimeField(write_only=True)

    measured_date = serializers.SerializerMethodField()
    measured_time = serializers.SerializerMethodField()

    class Meta:
        model = GlucoseReading

        fields = [
            "id",
            "value",
            "date",
            "time",
            "measured_date",
            "measured_time",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]

    def get_measured_date(self, obj):
        return timezone.localtime(obj.measured_at).date()

    def get_measured_time(self, obj):
        return timezone.localtime(obj.measured_at).time()

    def create(self, validated_data):
        date = validated_data.pop("date")
        time = validated_data.pop("time")

        measured_at = datetime.combine(date, time)
        measured_at = timezone.make_aware(measured_at)

        return GlucoseReading.objects.create(
            measured_at=measured_at,
            **validated_data
        )

    def update(self, instance, validated_data):
        date = validated_data.pop("date", None)
        time = validated_data.pop("time", None)

        current_datetime = timezone.localtime(instance.measured_at)

        if date is None:
            date = current_datetime.date()

        if time is None:
            time = current_datetime.time()

        instance.measured_at = timezone.make_aware(
            datetime.combine(date, time)
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance