"""
Serializers for REST API
"""
from rest_framework import serializers
from .models import DWLRStation, WaterLevel, GroundwaterResource

class WaterLevelSerializer(serializers.ModelSerializer):
    station_code = serializers.CharField(source='station.station_code', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    
    class Meta:
        model = WaterLevel
        fields = ['id', 'station_code', 'station_name', 'timestamp', 'depth', 
                 'water_level_elevation', 'data_source']
        read_only_fields = ['id', 'data_source']


class DWLRStationSerializer(serializers.ModelSerializer):
    water_levels = WaterLevelSerializer(many=True, read_only=True)
    latest_water_level = serializers.SerializerMethodField()
    resource_status = serializers.SerializerMethodField()
    
    class Meta:
        model = DWLRStation
        fields = ['station_code', 'name', 'state', 'district', 'block', 
                 'latitude', 'longitude', 'aquifer_type', 'well_depth', 
                 'elevation', 'is_active', 'last_data_update', 'created_at',
                 'water_levels', 'latest_water_level', 'resource_status']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_latest_water_level(self, obj):
        latest = obj.water_levels.first()
        if latest:
            return {
                'timestamp': latest.timestamp,
                'depth': latest.depth,
                'water_level_elevation': latest.water_level_elevation,
            }
        return None
    
    def get_resource_status(self, obj):
        latest_resource = obj.resources.first()
        if latest_resource:
            return {
                'alert_status': latest_resource.alert_status,
                'storage_percentage': latest_resource.storage_percentage,
                'trend': latest_resource.trend,
                'trend_magnitude': latest_resource.trend_magnitude,
                'calculation_date': latest_resource.calculation_date,
            }
        return None


class GroundwaterResourceSerializer(serializers.ModelSerializer):
    station_code = serializers.CharField(source='station.station_code', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    
    class Meta:
        model = GroundwaterResource
        fields = ['id', 'station_code', 'station_name', 'calculation_date',
                 'period_start', 'period_end', 'estimated_recharge', 'recharge_rate',
                 'current_storage', 'available_storage', 'storage_percentage',
                 'trend', 'trend_magnitude', 'alert_status', 'created_at']
        read_only_fields = ['id', 'created_at']


class StationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for station lists"""
    latest_depth = serializers.SerializerMethodField()
    alert_status = serializers.SerializerMethodField()
    
    class Meta:
        model = DWLRStation
        fields = ['station_code', 'name', 'state', 'district', 'latitude', 
                 'longitude', 'is_active', 'latest_depth', 'alert_status']
    
    def get_latest_depth(self, obj):
        latest = obj.water_levels.first()
        return latest.depth if latest else None
    
    def get_alert_status(self, obj):
        latest_resource = obj.resources.first()
        return latest_resource.alert_status if latest_resource else 'normal'
