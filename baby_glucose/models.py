import secrets
import string

from django.db import models


def generate_unique_baby_id():
    characters = string.ascii_uppercase + string.digits

    while True:
        baby_id = "".join(
            secrets.choice(characters)
            for _ in range(8)
        )

        if not Baby.objects.filter(baby_id=baby_id).exists():
            return baby_id


class Baby(models.Model):
    baby_id = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
    )

    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.baby_id:
            self.baby_id = generate_unique_baby_id()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.baby_id})"


class GlucoseReading(models.Model):
    baby = models.ForeignKey(
        Baby,
        on_delete=models.CASCADE,
        related_name="readings",
    )

    value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    measured_at = models.DateTimeField()

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-measured_at"]

    def __str__(self):
        return f"{self.value} mmol/L - {self.measured_at}"