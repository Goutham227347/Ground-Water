from django.db import models
from django.utils import timezone

class DWLRStation(models.Model):
    station_code = models.CharField(max_length=30, unique=True, primary_key=True)
    name = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    block = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    aquifer_type = models.CharField(max_length=50, blank=True)
    well_depth = models.FloatField(null=True, blank=True)  # Total well depth in meters
    elevation = models.FloatField(null=True, blank=True)  # Ground elevation in meters
    installation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_data_update = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['state', 'district', 'name']
        indexes = [
            models.Index(fields=['state', 'district']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.station_code} - {self.name}"


class WaterLevel(models.Model):
    station = models.ForeignKey(DWLRStation, on_delete=models.CASCADE, related_name='water_levels')
    timestamp = models.DateTimeField()
    depth = models.FloatField()  # meters below ground level
    water_level_elevation = models.FloatField(null=True, blank=True)  # Calculated elevation
    data_source = models.CharField(max_length=50, default='CGWB_API')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['station', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        unique_together = [['station', 'timestamp']]

    def __str__(self):
        return f"{self.station.station_code} - {self.timestamp}"


class GroundwaterResource(models.Model):
    """Calculated groundwater resource metrics for a station"""
    station = models.ForeignKey(DWLRStation, on_delete=models.CASCADE, related_name='resources')
    calculation_date = models.DateField()
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Recharge estimation
    estimated_recharge = models.FloatField(null=True, blank=True)  # in cubic meters
    recharge_rate = models.FloatField(null=True, blank=True)  # mm/year
    
    # Availability metrics
    current_storage = models.FloatField(null=True, blank=True)  # cubic meters
    available_storage = models.FloatField(null=True, blank=True)  # cubic meters
    storage_percentage = models.FloatField(null=True, blank=True)  # percentage
    
    # Trend analysis
    trend = models.CharField(max_length=20, choices=[
        ('rising', 'Rising'),
        ('falling', 'Falling'),
        ('stable', 'Stable'),
    ], blank=True)
    trend_magnitude = models.FloatField(null=True, blank=True)  # meters/year
    
    # Alert levels
    alert_status = models.CharField(max_length=20, choices=[
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('normal', 'Normal'),
        ('good', 'Good'),
    ], default='normal')
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-calculation_date']
        indexes = [
            models.Index(fields=['station', 'calculation_date']),
            models.Index(fields=['alert_status']),
        ]

    def __str__(self):
        return f"{self.station.station_code} - {self.calculation_date}"
