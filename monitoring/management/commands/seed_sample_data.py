"""
Seed sample DWLR stations and water level data for demonstration.
Run: python manage.py seed_sample_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from monitoring.models import DWLRStation, WaterLevel, GroundwaterResource
from monitoring.services import GroundwaterAnalysisService


# Sample data configuration
STATES_DATA = [
    {'name': 'Maharashtra', 'code': 'MH', 'districts': ['Pune', 'Nashik', 'Nagpur', 'Aurangabad', 'Thane'], 'lat_range': (16.0, 22.0), 'lon_range': (73.0, 80.0)},
    {'name': 'Tamil Nadu', 'code': 'TN', 'districts': ['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Tiruchirappalli'], 'lat_range': (8.0, 13.5), 'lon_range': (76.0, 80.0)},
    {'name': 'Karnataka', 'code': 'KA', 'districts': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum'], 'lat_range': (11.5, 18.5), 'lon_range': (74.0, 78.5)},
    {'name': 'Rajasthan', 'code': 'RJ', 'districts': ['Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Ajmer'], 'lat_range': (23.5, 30.0), 'lon_range': (69.5, 78.0)},
    {'name': 'Uttar Pradesh', 'code': 'UP', 'districts': ['Lucknow', 'Kanpur', 'Varanasi', 'Agra', 'Meerut'], 'lat_range': (23.9, 30.0), 'lon_range': (77.0, 84.5)},
    {'name': 'Gujarat', 'code': 'GJ', 'districts': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar'], 'lat_range': (20.0, 24.5), 'lon_range': (68.0, 74.0)},
    {'name': 'Andhra Pradesh', 'code': 'AP', 'districts': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool'], 'lat_range': (12.5, 19.0), 'lon_range': (77.0, 84.5)},
    {'name': 'Punjab', 'code': 'PB', 'districts': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda'], 'lat_range': (29.5, 32.5), 'lon_range': (73.5, 77.0)},
    {'name': 'Telangana', 'code': 'TS', 'districts': ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar', 'Khammam'], 'lat_range': (16.0, 19.5), 'lon_range': (77.0, 81.0)},
    {'name': 'Madhya Pradesh', 'code': 'MP', 'districts': ['Indore', 'Bhopal', 'Jabalpur', 'Gwalior', 'Ujjain'], 'lat_range': (21.0, 26.5), 'lon_range': (74.0, 82.5)},
]

def generate_sample_stations(count=100):
    stations = []
    for i in range(count):
        state_data = random.choice(STATES_DATA)
        district = random.choice(state_data['districts'])
        
        # Random coordinates within approximate state bounds
        lat = random.uniform(*state_data['lat_range'])
        lon = random.uniform(*state_data['lon_range'])
        
        station = {
            'station_code': f"{state_data['code']}_{district}_{100+i}",
            'name': f"{district} Monitoring {chr(65 + (i%5))}",
            'state': state_data['name'],
            'district': district,
            'block': f"Block-{random.randint(1, 10)}",
            'latitude': round(lat, 4),
            'longitude': round(lon, 4),
            'well_depth': round(random.uniform(30.0, 120.0), 1),
            'elevation': round(random.uniform(50.0, 800.0), 1),
            'aquifer_type': random.choice(['Alluvium', 'Basalt', 'Granite', 'Sandstone', 'Limestone'])
        }
        stations.append(station)
    return stations

SAMPLE_STATIONS = generate_sample_stations(150) # Generate 150 stations


class Command(BaseCommand):
    help = 'Seed sample DWLR stations and water level data for demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            WaterLevel.objects.all().delete()
            GroundwaterResource.objects.all().delete()
            DWLRStation.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared.'))

        created = 0
        for s in SAMPLE_STATIONS:
            station, st_created = DWLRStation.objects.update_or_create(
                station_code=s['station_code'],
                defaults={
                    'name': s['name'],
                    'state': s['state'],
                    'district': s['district'],
                    'block': s.get('block', ''),
                    'latitude': s['latitude'],
                    'longitude': s['longitude'],
                    'well_depth': s['well_depth'],
                    'elevation': s['elevation'],
                    'aquifer_type': s.get('aquifer_type', ''),
                    'is_active': True,
                }
            )
            if st_created:
                created += 1

            # Generate ~12 months of monthly water level data with a slight trend
            base_depth = 12.0 + random.uniform(0, 8)
            trend = random.choice([-0.08, -0.04, 0, 0.03, 0.06])  # m per month
            wl_created = 0
            for i in range(12):
                dt = timezone.now() - timedelta(days=30 * (11 - i))
                depth = base_depth + (i * trend) + random.gauss(0, 0.5)
                depth = max(2.0, min(depth, (station.well_depth or 80) - 5))
                _, wl_created_flag = WaterLevel.objects.get_or_create(
                    station=station,
                    timestamp=dt.replace(hour=10, minute=0, second=0, microsecond=0),
                    defaults={'depth': round(depth, 2), 'data_source': 'SEED'}
                )
                if wl_created_flag:
                    wl_created += 1

            station.last_data_update = timezone.now()
            station.save(update_fields=['last_data_update'])

            # Compute resource metrics
            try:
                res = GroundwaterAnalysisService.calculate_resource_metrics(station)
                res.save()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Metrics for {station.station_code}: {e}'))

            self.stdout.write(
                self.style.SUCCESS(f"  {station.station_code} ({station.state}) – {wl_created} water levels, metrics computed")
            )

        self.stdout.write(self.style.SUCCESS(f'\nSeeded {created} new stations. Run the server and open / to view the dashboard.'))
