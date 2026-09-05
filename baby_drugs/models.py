from django.db import models
from django.utils import timezone

from PIL import Image
from io import BytesIO

from django.core.files.base import ContentFile

import os
import uuid


class Drug(models.Model):

    ADMINISTRATION_TYPES = [
        ("drops", "Drops"),
        ("measurement", "Measurement"),
        ("tablet", "Tablet"),
        ("capsule", "Capsule"),
        ("other", "Other"),
    ]


    name = models.CharField(
        max_length=150,
        unique=True,
    )


    administration_type = models.CharField(
        max_length=20,
        choices=ADMINISTRATION_TYPES,
    )


    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )


    unit = models.CharField(
        max_length=30,
        blank=True,
    )


    image = models.ImageField(
        upload_to="drugs/",
        null=True,
        blank=True,
    )


    notes = models.TextField(
        blank=True,
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    class Meta:

        ordering = ["name"]


    def __str__(self):

        return self.name


    def save(self, *args, **kwargs):

        """
        Convert newly uploaded drug images to WebP.
        """

        if self.image and not self.image.name.lower().endswith(".webp"):

            try:

                img = Image.open(self.image)


                # Convert image to RGB
                if img.mode in ("RGBA", "LA"):

                    background = Image.new(
                        "RGB",
                        img.size,
                        "white",
                    )

                    background.paste(
                        img,
                        mask=img.split()[-1],
                    )

                    img = background

                else:

                    img = img.convert("RGB")


                # Resize large images
                max_size = (1000, 1000)

                img.thumbnail(max_size)


                # Convert image to WebP
                image_io = BytesIO()

                img.save(
                    image_io,
                    format="WEBP",
                    quality=85,
                    optimize=True,
                )


                # Generate safe filename
                filename = (
                    f"{uuid.uuid4().hex}.webp"
                )


                # Replace image
                self.image.save(
                    filename,
                    ContentFile(image_io.getvalue()),
                    save=False,
                )


            except Exception as error:

                print(
                    "Drug image conversion error:",
                    error,
                )


        super().save(*args, **kwargs)

# =========================================================
# BABY DRUG PLAN
# =========================================================

class BabyDrugPlan(models.Model):

    baby = models.ForeignKey(
        "baby_glucose.Baby",
        on_delete=models.CASCADE,
        related_name="drug_plans",
    )

    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name="baby_plans",
    )

    times_per_day = models.PositiveIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "baby",
            "drug",
        ]

        constraints = [

            models.UniqueConstraint(
                fields=["baby", "drug"],
                name="unique_drug_per_baby",
            )

        ]

    def __str__(self):

        return f"{self.baby} - {self.drug}"


# =========================================================
# BABY DRUG SCHEDULE
# =========================================================

class BabyDrugSchedule(models.Model):

    baby_drug_plan = models.ForeignKey(
        BabyDrugPlan,
        on_delete=models.CASCADE,
        related_name="schedules",
    )

    dose_order = models.PositiveIntegerField()

    scheduled_time = models.TimeField()

    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    unit = models.CharField(
        max_length=30,
        blank=True,
    )

    class Meta:

        ordering = [
            "dose_order",
        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "baby_drug_plan",
                    "dose_order",
                ],
                name="unique_dose_order_per_plan",
            )

        ]

    def __str__(self):

        return (
            f"{self.baby_drug_plan.drug.name} "
            f"- Dose {self.dose_order} "
            f"- {self.scheduled_time}"
        )


# =========================================================
# DAILY DRUG TAKING RECORD
# =========================================================

class DrugIntakeRecord(models.Model):

    STATUS_CHOICES = [

        ("pending", "Pending"),

        ("taken", "Taken"),

        ("missed", "Missed"),

        ("skipped", "Skipped"),

    ]

    schedule = models.ForeignKey(
        BabyDrugSchedule,
        on_delete=models.CASCADE,
        related_name="taking_records",
    )

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    taken_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-date",
            "schedule__dose_order",
        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "schedule",
                    "date",
                ],
                name="unique_daily_drug_record",
            )

        ]

    def mark_as_taken(self):

        self.status = "taken"

        self.taken_at = timezone.now()

        self.save()


    def __str__(self):

        return (
            f"{self.schedule.baby_drug_plan.drug.name} "
            f"- {self.date} "
            f"- {self.status}"
        )