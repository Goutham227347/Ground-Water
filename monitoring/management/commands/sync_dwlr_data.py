"""
Management command to sync DWLR data from CGWB API
Usage: python manage.py sync_dwlr_data [--station-code STATION_CODE] [--all]
"""
from django.core.management.base import BaseCommand
from monitoring.models import DWLRStation
from monitoring.services import CGWBAPIService, GroundwaterAnalysisService
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync DWLR station data from CGWB API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--station-code',
            type=str,
            help='Sync data for a specific station code',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync data for all stations',
        )
        parser.add_argument(
            '--states',
            type=str,
            nargs='+',
            help='Sync data for stations in specific states',
        )

    def handle(self, *args, **options):
        api_service = CGWBAPIService()
        
        if options['station_code']:
            # Sync specific station
            try:
                station = DWLRStation.objects.get(station_code=options['station_code'])
                self.sync_station(api_service, station)
            except DWLRStation.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Station {options["station_code"]} not found')
                )
        
        elif options['all']:
            # Sync all stations
            stations = DWLRStation.objects.filter(is_active=True)
            total = stations.count()
            self.stdout.write(f'Syncing {total} stations...')
            
            for i, station in enumerate(stations, 1):
                self.stdout.write(f'[{i}/{total}] Syncing {station.station_code}...')
                self.sync_station(api_service, station)
        
        elif options['states']:
            # Sync stations in specific states
            stations = DWLRStation.objects.filter(
                state__in=options['states'],
                is_active=True
            )
            total = stations.count()
            self.stdout.write(f'Syncing {total} stations in {options["states"]}...')
            
            for i, station in enumerate(stations, 1):
                self.stdout.write(f'[{i}/{total}] Syncing {station.station_code}...')
                self.sync_station(api_service, station)
        
        else:
            self.stdout.write(
                self.style.WARNING('Please specify --station-code, --all, or --states')
            )

    def sync_station(self, api_service, station):
        """Sync data for a single station"""
        try:
            # Fetch water level data
            end_date = timezone.now()
            start_date = end_date - timedelta(days=365)
            
            water_level_data = api_service.fetch_water_level_data(
                station.station_code,
                start_date,
                end_date
            )
            
            if water_level_data:
                count = api_service.sync_water_levels(station, water_level_data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Synced {count} water level records for {station.station_code}'
                    )
                )
                
                # Calculate resource metrics
                resource = GroundwaterAnalysisService.calculate_resource_metrics(station)
                resource.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Calculated resource metrics for {station.station_code}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠ No data available for {station.station_code}'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ Error syncing {station.station_code}: {e}')
            )
            logger.error(f'Error syncing station {station.station_code}: {e}')
