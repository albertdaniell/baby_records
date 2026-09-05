from django.shortcuts import get_object_or_404

from rest_framework import generics

from .models import Baby, GlucoseReading
from .serializers import BabySerializer, GlucoseReadingSerializer


# ==========================================
# BABY CRUD
# ==========================================

class BabyListCreateView(generics.ListCreateAPIView):
    queryset = Baby.objects.all()
    serializer_class = BabySerializer


class BabyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Baby.objects.all()
    serializer_class = BabySerializer
    lookup_field = "baby_id"


# ==========================================
# GLUCOSE READING CRUD
# ==========================================

class GlucoseReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = GlucoseReadingSerializer

    def get_queryset(self):
        baby_id = self.kwargs["baby_id"]

        return GlucoseReading.objects.filter(
            baby__baby_id=baby_id
        )

    def perform_create(self, serializer):
        baby = get_object_or_404(
            Baby,
            baby_id=self.kwargs["baby_id"]
        )

        serializer.save(baby=baby)


class GlucoseReadingDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = GlucoseReadingSerializer

    def get_queryset(self):
        baby_id = self.kwargs["baby_id"]

        return GlucoseReading.objects.filter(
            baby__baby_id=baby_id
        )