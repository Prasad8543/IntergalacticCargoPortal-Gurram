from django.contrib import admin

from .models import CargoRecord


@admin.register(CargoRecord)
class CargoRecordAdmin(admin.ModelAdmin):
    list_display = ('cargo_id', 'destination', 'weight_kg', 'uploaded_by', 'created_at')
    list_filter = ('destination',)
    search_fields = ('cargo_id', 'destination')
