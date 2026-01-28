from django.contrib import admin
from .models import DWLRStation, WaterLevel, GroundwaterResource

@admin.register(DWLRStation)
class DWLRStationAdmin(admin.ModelAdmin):
    list_display = ['station_code', 'name', 'state', 'district', 'is_active', 'last_data_update']
    list_filter = ['state', 'district', 'is_active', 'aquifer_type']
    search_fields = ['station_code', 'name', 'state', 'district']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WaterLevel)
class WaterLevelAdmin(admin.ModelAdmin):
    list_display = ['station', 'timestamp', 'depth', 'data_source']
    list_filter = ['data_source', 'timestamp']
    search_fields = ['station__station_code', 'station__name']
    date_hierarchy = 'timestamp'

@admin.register(GroundwaterResource)
class GroundwaterResourceAdmin(admin.ModelAdmin):
    list_display = ['station', 'calculation_date', 'alert_status', 'estimated_recharge', 'storage_percentage']
    list_filter = ['alert_status', 'trend', 'calculation_date']
    search_fields = ['station__station_code', 'station__name']
    date_hierarchy = 'calculation_date'
