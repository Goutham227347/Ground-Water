"""
REST API views for groundwater monitoring
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Avg, Max, Min
from .models import DWLRStation, WaterLevel, GroundwaterResource
from .serializers import (
    DWLRStationSerializer, WaterLevelSerializer, 
    GroundwaterResourceSerializer, StationListSerializer
)
from .services import CGWBAPIService, GroundwaterAnalysisService
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """
    API information for mobile app integration and developers.
    Documents available endpoints for DWLR data access.
    """
    return Response({
        'name': 'Groundwater DWLR API',
        'version': '1.0',
        'description': 'Real-time groundwater resource evaluation using DWLR data. Supports mobile and web clients.',
        'base_url': '/api/',
        'endpoints': {
            'stations': {
                'list': 'GET /api/stations/',
                'detail': 'GET /api/stations/{station_code}/',
                'statistics': 'GET /api/stations/statistics/',
                'water_levels': 'GET /api/stations/{station_code}/water_levels/',
                'resource_metrics': 'GET /api/stations/{station_code}/resource_metrics/',
                'sync_single': 'POST /api/stations/{station_code}/sync_data/',
                'sync_all': 'POST /api/stations/sync_all_stations/',  # NEW: Sync all stations
            },
            'water_levels': 'GET /api/water-levels/?station_code=&start_date=&end_date=',
            'resources': {
                'list': 'GET /api/resources/',
                'alerts': 'GET /api/resources/alerts/',
            },
            'insights': 'GET /api/stations/insights/',
        },
        'query_params': {
            'stations': 'state, district, is_active, alert_status',
            'water_levels': 'station_code, start_date, end_date, limit',
        },
    })


class DWLRStationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for DWLR stations
    """
    queryset = DWLRStation.objects.all()
    serializer_class = DWLRStationSerializer
    permission_classes = [AllowAny]
    lookup_field = 'station_code'
    pagination_class = None  # Disable pagination to show all stations without limit
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StationListSerializer
        return DWLRStationSerializer
    
    def get_queryset(self):
        queryset = DWLRStation.objects.all()
        
        # Filtering
        state = self.request.query_params.get('state', None)
        district = self.request.query_params.get('district', None)
        is_active = self.request.query_params.get('is_active', None)
        alert_status = self.request.query_params.get('alert_status', None)
        
        if state:
            queryset = queryset.filter(state__icontains=state)
        if district:
            queryset = queryset.filter(district__icontains=district)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if alert_status:
            # Filter by latest resource alert status
            station_codes = GroundwaterResource.objects.filter(
                alert_status=alert_status
            ).values_list('station__station_code', flat=True).distinct()
            queryset = queryset.filter(station_code__in=station_codes)
        
        return queryset.select_related().prefetch_related('water_levels', 'resources')
    
    @action(detail=True, methods=['post'])
    def sync_data(self, request, station_code=None):
        """
        Sync real-time data from CGWB API for a specific station
        """
        try:
            station = self.get_object()
            api_service = CGWBAPIService()
            
            # Fetch water level data
            end_date = timezone.now()
            start_date = end_date - timedelta(days=365)
            water_level_data = api_service.fetch_water_level_data(
                station_code, start_date, end_date
            )
            
            if water_level_data:
                count = api_service.sync_water_levels(station, water_level_data)
                
                # Calculate resource metrics
                resource = GroundwaterAnalysisService.calculate_resource_metrics(station)
                resource.save()
                
                return Response({
                    'status': 'success',
                    'message': f'Synced {count} water level records',
                    'station_code': station_code,
                })
            else:
                return Response({
                    'status': 'warning',
                    'message': 'No data available from API',
                    'station_code': station_code,
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error syncing data for {station_code}: {e}")
            return Response({
                'status': 'error',
                'message': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def sync_all_stations(self, request):
        """
        Sync real-time data from CGWB API for ALL active stations.
        WARNING: This is a heavy operation and may take several minutes.
        """
        try:
            api_service = CGWBAPIService()
            stations = DWLRStation.objects.filter(is_active=True)
            total_stations = stations.count()
            total_records = 0
            success_count = 0
            failed_count = 0
            
            for station in stations:
                try:
                    # Fetch water level data (last 30 days for real-time sync)
                    end_date = timezone.now()
                    start_date = end_date - timedelta(days=30)
                    
                    water_level_data = api_service.fetch_water_level_data(
                        station.station_code,
                        start_date,
                        end_date
                    )
                    
                    if water_level_data:
                        count = api_service.sync_water_levels(station, water_level_data)
                        total_records += count
                        success_count += 1
                        
                        # Calculate resource metrics
                        resource = GroundwaterAnalysisService.calculate_resource_metrics(station)
                        resource.save()
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error syncing {station.station_code}: {e}")
                    failed_count += 1
            
            return Response({
                'status': 'success',
                'message': f'Synced {success_count} out of {total_stations} stations',
                'total_records_synced': total_records,
                'successful_stations': success_count,
                'failed_stations': failed_count,
                'timestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            logger.error(f"Error syncing all stations: {e}")
            return Response({
                'status': 'error',
                'message': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def water_levels(self, request, station_code=None):
        """
        Get water level data for a specific station
        """
        station = self.get_object()
        
        # Date filtering
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        queryset = WaterLevel.objects.filter(station=station).order_by('-timestamp')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        # Limit results
        limit = int(request.query_params.get('limit', 1000))
        queryset = queryset[:limit]
        
        serializer = WaterLevelSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resource_metrics(self, request, station_code=None):
        """
        Get or calculate resource metrics for a station
        """
        station = self.get_object()
        
        # Get latest resource or calculate new one
        latest_resource = station.resources.first()
        if not latest_resource or latest_resource.calculation_date < timezone.now().date():
            # Calculate new metrics
            resource = GroundwaterAnalysisService.calculate_resource_metrics(station)
            resource.save()
            latest_resource = resource
        
        serializer = GroundwaterResourceSerializer(latest_resource)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get overall statistics across all stations
        """
        total_stations = DWLRStation.objects.count()
        active_stations = DWLRStation.objects.filter(is_active=True).count()
        
        # Alert status distribution
        alert_stats = {}
        for status_code in ['critical', 'warning', 'normal', 'good']:
            count = GroundwaterResource.objects.filter(
                alert_status=status_code
            ).values('station').distinct().count()
            alert_stats[status_code] = count
        
        # States coverage
        states_count = DWLRStation.objects.values('state').distinct().count()
        
        return Response({
            'total_stations': total_stations,
            'active_stations': active_stations,
            'states_covered': states_count,
            'alert_distribution': alert_stats,
        })
    
    @action(detail=False, methods=['get'])
    def insights(self, request):
        """
        Decision-support insights for researchers, planners, and policymakers.
        """
        critical = GroundwaterResource.objects.filter(alert_status='critical').select_related('station').count()
        warning = GroundwaterResource.objects.filter(alert_status='warning').select_related('station').count()
        total = DWLRStation.objects.filter(is_active=True).count()
        total_resources = GroundwaterResource.objects.values('station').distinct().count()
        
        insights = []
        
        if critical > 0:
            insights.append({
                'priority': 'high',
                'title': 'Critical groundwater stress',
                'message': f'{critical} station(s) in critical status. Recommend urgent assessment and demand management in affected areas.',
                'action': 'Prioritize recharge augmentation and regulated extraction in critical zones.',
            })
        if warning > 0:
            insights.append({
                'priority': 'medium',
                'title': 'Declining groundwater levels',
                'message': f'{warning} station(s) show warning. Monitor trends and consider seasonal rationing or recharge measures.',
                'action': 'Review extraction patterns and promote rainwater harvesting in warning zones.',
            })
        if total > 0 and total_resources == 0:
            insights.append({
                'priority': 'info',
                'title': 'Resource evaluation pending',
                'message': 'Stations exist but resource metrics are not yet computed. Run sync or ensure water level data is available.',
                'action': 'Use Sync Real-time Data on stations or run: python manage.py seed_sample_data',
            })
        if total >= 3 and (critical + warning) == 0:
            insights.append({
                'priority': 'low',
                'title': 'Stable resource picture',
                'message': 'No critical or warning alerts. Continue routine monitoring and maintain recharge initiatives.',
                'action': 'Sustain current management; use trends to plan long-term interventions.',
            })
        
        if not insights:
            insights.append({
                'priority': 'info',
                'title': 'Add DWLR data',
                'message': 'Add stations and water level data to enable real-time groundwater evaluation and insights.',
                'action': 'Run: python manage.py seed_sample_data',
            })
        
        return Response({'insights': insights})


class WaterLevelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for water level data
    """
    queryset = WaterLevel.objects.all()
    serializer_class = WaterLevelSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = WaterLevel.objects.all()
        
        station_code = self.request.query_params.get('station_code', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if station_code:
            queryset = queryset.filter(station__station_code=station_code)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset.select_related('station').order_by('-timestamp')


class GroundwaterResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for groundwater resource metrics
    """
    queryset = GroundwaterResource.objects.all()
    serializer_class = GroundwaterResourceSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = GroundwaterResource.objects.all()
        
        station_code = self.request.query_params.get('station_code', None)
        alert_status = self.request.query_params.get('alert_status', None)
        
        if station_code:
            queryset = queryset.filter(station__station_code=station_code)
        if alert_status:
            queryset = queryset.filter(alert_status=alert_status)
        
        return queryset.select_related('station').order_by('-calculation_date')
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """
        Get stations with critical or warning alerts
        """
        critical_resources = GroundwaterResource.objects.filter(
            alert_status__in=['critical', 'warning']
        ).select_related('station').order_by('-calculation_date')
        
        serializer = self.get_serializer(critical_resources, many=True)
        return Response(serializer.data)

