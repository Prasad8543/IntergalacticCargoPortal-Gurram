from rest_framework import serializers

from .models import CargoRecord


class CargoRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoRecord
        fields = ('id', 'cargo_id', 'destination', 'weight_kg', 'created_at')
