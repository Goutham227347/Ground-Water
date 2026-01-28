# Quick Setup Guide

## Initial Setup

1. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server**:
   ```bash
   python manage.py runserver
   ```

6. **Seed demo data** (optional but recommended):
   ```bash
   python manage.py seed_sample_data
   ```

7. **Access the application**:
   - Web Interface: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API: http://127.0.0.1:8000/api/
   - API info (mobile integration): http://127.0.0.1:8000/api/info/

## Adding Sample Data

**Recommended: seed demo data (8 stations, 12 months water levels, resource metrics):**

```bash
python manage.py seed_sample_data
```

To clear and re-seed: `python manage.py seed_sample_data --clear`

Other options:

1. **Via Admin Panel**:
   - Go to http://127.0.0.1:8000/admin/
   - Login with superuser credentials
   - Add stations under "Monitoring" → "DWLR Stations"

2. **Via CGWB sync** (when API is configured):
   ```bash
   python manage.py sync_dwlr_data --station-code STATION_CODE
   python manage.py sync_dwlr_data --all
   ```

3. **Via Python Shell**:
   ```python
   python manage.py shell
   ```
   ```python
   from monitoring.models import DWLRStation
   from django.utils import timezone
   
   # Create a sample station
   station = DWLRStation.objects.create(
       station_code='TEST001',
       name='Test Station',
       state='Maharashtra',
       district='Pune',
       latitude=18.5204,
       longitude=73.8567,
       well_depth=50.0,
       elevation=560.0,
       is_active=True
   )
   ```

## CGWB API Integration

The application is designed to integrate with CGWB (Central Ground Water Board) API. 

**Note**: The actual API endpoints may need to be configured based on CGWB's current API structure. The service layer in `monitoring/services.py` provides the framework for integration.

To configure the API:
1. Check CGWB's current API documentation at https://gwdata.cgwb.gov.in
2. Update the `BASE_URL` and endpoint paths in `monitoring/services.py`
3. Adjust the data parsing logic based on the actual API response format

## Testing the Application

1. **Add a test station** (see above)
2. **Add sample water level data**:
   ```python
   from monitoring.models import DWLRStation, WaterLevel
   from django.utils import timezone
   from datetime import timedelta
   
   station = DWLRStation.objects.first()
   for i in range(30):
       WaterLevel.objects.create(
           station=station,
           timestamp=timezone.now() - timedelta(days=30-i),
           depth=10.0 + (i * 0.1),
           data_source='TEST'
       )
   ```

3. **Calculate resource metrics**:
   ```python
   from monitoring.services import GroundwaterAnalysisService
   
   station = DWLRStation.objects.first()
   resource = GroundwaterAnalysisService.calculate_resource_metrics(station)
   resource.save()
   ```

4. **View in web interface**: Navigate to http://127.0.0.1:8000/ and explore the dashboard

## Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic
```

### Migration issues / "no such column" errors
```bash
# Delete database and recreate (Windows: remove db.sqlite3 if it exists)
# PowerShell:
if (Test-Path db.sqlite3) { Remove-Item db.sqlite3 }
python manage.py migrate
python manage.py seed_sample_data
```

### API connection errors
- Check internet connection
- Verify CGWB API endpoints are accessible
- Review API service logs in console

## Next Steps

1. Configure CGWB API endpoints
2. Add real station data via API sync
3. Customize visualization colors and styles
4. Add additional analytics features
5. Deploy to production server

