# Real-time Groundwater Resource Evaluation using DWLR Data

A comprehensive web application for monitoring and evaluating groundwater resources in India using data from 5,260 Digital Water Level Recorder (DWLR) stations.

## Features

- **Real-time Data Integration**: Fetches data from CGWB (Central Ground Water Board) government APIs
- **Interactive Map Visualization**: View all DWLR stations on an interactive map with color-coded alert status
- **Water Level Trends**: Visualize water level fluctuations over time with interactive charts
- **Resource Evaluation**: 
  - Dynamic recharge estimation
  - Groundwater storage calculation
  - Trend analysis (rising/falling/stable)
  - Alert system (Critical/Warning/Normal/Good)
- **Analytics Dashboard**: 
  - Alert distribution charts
  - State-wise station coverage
  - Regional analysis
- **Mobile Responsive**: Fully responsive design; PWA manifest for "Add to Home Screen"
- **Mobile App Integration**: REST API and `/api/info/` document endpoints for native or hybrid mobile apps
- **Decision Support**: Insights and recommendations for researchers, planners, and policymakers

## Technology Stack

- **Backend**: Django 6.0+ with Django REST Framework
- **Frontend**: Vanilla JavaScript, Chart.js, Leaflet Maps
- **Database**: SQLite (can be configured for PostgreSQL)
- **APIs**: RESTful API for data access

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd groundwater
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Seed demo data** (8 sample stations with water levels; recommended):
   ```bash
   python manage.py seed_sample_data
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Web Interface: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API: http://127.0.0.1:8000/api/
   - API info (mobile integration): http://127.0.0.1:8000/api/info/

## Usage

### Syncing DWLR Data

To sync real-time data from CGWB API:

```bash
# Sync all stations
python manage.py sync_dwlr_data --all

# Sync specific station
python manage.py sync_dwlr_data --station-code STATION_CODE

# Sync stations in specific states
python manage.py sync_dwlr_data --states "State1" "State2"
```

### API Endpoints

- `GET /api/info/` - API documentation for mobile app integration
- `GET /api/stations/` - List all DWLR stations
- `GET /api/stations/{station_code}/` - Get station details
- `GET /api/stations/{station_code}/water_levels/` - Get water level data
- `GET /api/stations/{station_code}/resource_metrics/` - Get resource metrics
- `POST /api/stations/{station_code}/sync_data/` - Sync real-time data
- `GET /api/stations/statistics/` - Get overall statistics
- `GET /api/stations/insights/` - Decision-support insights for policymakers
- `GET /api/resources/alerts/` - Get critical alerts

### Query Parameters

- Filter stations by state: `/api/stations/?state=StateName`
- Filter by district: `/api/stations/?district=DistrictName`
- Filter by alert status: `/api/stations/?alert_status=critical`
- Date range for water levels: `/api/stations/{code}/water_levels/?start_date=2024-01-01&end_date=2024-12-31`

## Project Structure

```
groundwater/
├── groundwater/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── monitoring/           # Main application
│   ├── models.py        # Database models
│   ├── views.py         # API views
│   ├── serializers.py   # API serializers
│   ├── services.py      # Business logic & API integration
│   ├── management/      # Management commands
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JavaScript, images
├── manage.py
└── requirements.txt
```

## Data Models

### DWLRStation
- Station information (code, name, location, coordinates)
- State, district, block details
- Well specifications (depth, elevation, aquifer type)
- Active status and last update timestamp

### WaterLevel
- Timestamped water level measurements
- Depth below ground level
- Calculated water level elevation
- Data source tracking

### GroundwaterResource
- Calculated resource metrics
- Recharge estimation
- Storage calculations
- Trend analysis
- Alert status

## Groundwater Resource Evaluation

The application implements several algorithms for groundwater resource evaluation:

1. **Recharge Estimation**: Based on water level rise during recharge periods
2. **Storage Calculation**: Uses well depth, current water level, and specific yield
3. **Trend Analysis**: Linear regression to determine rising/falling/stable trends
4. **Alert System**: Multi-factor assessment considering storage percentage and trends

## CGWB API Integration

The application is designed to integrate with the Central Ground Water Board (CGWB) API:
- Base URL: `https://gwdata.cgwb.gov.in`
- The `CGWBAPIService` class handles API communication
- Note: Actual API endpoints may need to be configured based on CGWB's current API structure

## Development

### Adding New Features

1. Models: Add to `monitoring/models.py`
2. API: Add views to `monitoring/views.py` and serializers to `monitoring/serializers.py`
3. Frontend: Update `monitoring/static/monitoring/js/app.js` and CSS

### Testing

```bash
python manage.py test monitoring
```

## Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure CORS settings appropriately
5. Set up HTTPS
6. Configure proper secret key

## Contributing

This is a college project for groundwater resource evaluation. Contributions and improvements are welcome!

## License

This project is developed for educational purposes as part of a college project.

## Acknowledgments

- Central Ground Water Board (CGWB), India for providing DWLR data
- OpenStreetMap for map tiles
- Chart.js for data visualization
- Leaflet for interactive maps

## Contact

For questions or issues related to this project, please contact the development team.
