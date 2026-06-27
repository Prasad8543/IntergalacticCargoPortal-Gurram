from django.conf import settings
from django.db import models

from core.models import AuditInfo


class CargoRecord(AuditInfo):
    cargo_id = models.CharField(max_length=100)
    destination = models.CharField(max_length=255)
    weight_kg = models.PositiveIntegerField()
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploads',
    )

    class Meta:
        ordering = ['-weight_kg']

    def __str__(self):
        return f'{self.cargo_id} -> {self.destination} ({self.weight_kg} kg)'
