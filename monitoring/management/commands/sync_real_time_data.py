"""
Management command to sync real-time DWLR data continuously.
This can be run as a background service or called periodically.
Usage: python manage.py sync_real_time_data [--interval 3600] [--continuous]
"""
from django.core.management.base import BaseCommand
from monitoring.models import DWLRStation
from monitoring.services import CGWBAPIService, GroundwaterAnalysisService
from django.utils import timezone
from datetime import timedelta
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync real-time DWLR data from CGWB API continuously'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=3600,
            help='Interval in seconds between syncs (default: 3600 = 1 hour)',
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously in background',
        )
        parser.add_argument(
            '--recent',
            action='store_true',
            help='Fetch only recent data (last 7 days) for faster sync',
        )

    def handle(self, *args, **options):
        api_service = CGWBAPIService()
        interval = options['interval']
        continuous = options['continuous']
        recent_only = options['recent']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting real-time data sync (interval: {interval}s)')
        )
        
        if continuous:
            self.sync_continuous(api_service, interval, recent_only)
        else:
            self.sync_all_stations(api_service, recent_only)

    def sync_all_stations(self, api_service, recent_only=False):
        """Sync data for all active stations once"""
        stations = DWLRStation.objects.filter(is_active=True)
        total = stations.count()
        
        if total == 0:
            self.stdout.write(
                self.style.WARNING('No active stations found. Run: python manage.py seed_sample_data')
            )
            return
        
        self.stdout.write(f'Syncing {total} stations...')
        
        for i, station in enumerate(stations, 1):
            self.sync_station(api_service, station, recent_only)
            # Progress update
            if i % 10 == 0:
                self.stdout.write(f'Progress: {i}/{total}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Completed syncing {total} stations')
        )

    def sync_continuous(self, api_service, interval, recent_only=False):
        """Continuously sync data at specified interval"""
        iteration = 0
        try:
            while True:
                iteration += 1
                timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(f'\n[{timestamp}] Sync iteration #{iteration}')
                
                self.sync_all_stations(api_service, recent_only)
                
                self.stdout.write(f'Next sync in {interval} seconds...')
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write('\nSync stopped by user')

    def sync_station(self, api_service, station, recent_only=False):
        """Sync data for a single station"""
        try:
            # Determine date range
            end_date = timezone.now()
            if recent_only:
                # Fetch only last 7 days for faster sync
                start_date = end_date - timedelta(days=7)
            else:
                # Full year sync (less frequent for background task)
                start_date = end_date - timedelta(days=365)
            
            # Fetch water level data
            water_level_data = api_service.fetch_water_level_data(
                station.station_code,
                start_date,
                end_date
            )
            
            if water_level_data:
                count = api_service.sync_water_levels(station, water_level_data)
                
                # Calculate resource metrics
                resource = GroundwaterAnalysisService.calculate_resource_metrics(station)
                resource.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ {station.station_code}: {count} records synced'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠ {station.station_code}: No data available'
                    )
                )
        except Exception as e:
            logger.error(f"Error syncing {station.station_code}: {e}")
            self.stdout.write(
                self.style.ERROR(
                    f'  ✗ {station.station_code}: Error - {str(e)}'
                )
            )
