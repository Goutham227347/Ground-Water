# Product Specification Document  
## Real-time Groundwater Resource Evaluation using DWLR Data

**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Draft

---

## 1. Executive Summary

This product is a **web-based groundwater monitoring and evaluation platform** that ingests, analyzes, and visualizes data from **5,260 Digital Water Level Recorder (DWLR)** stations across India. It integrates with the **Central Ground Water Board (CGWB)** government APIs to provide real-time resource metrics, trend analysis, and decision-support insights for researchers, planners, and policymakers.

---

## 2. Product Vision & Goals

| Goal | Description |
|------|-------------|
| **Real-time evaluation** | Continuous ingestion and computation of groundwater resource metrics from DWLR data |
| **Decision support** | Actionable insights and recommendations for water resource management |
| **Accessibility** | Web and API access for desktop, mobile, and third-party integrations |
| **Transparency** | Clear alerting (Critical / Warning / Normal / Good) and trend visualization |

---

## 3. Target Users

| User Type | Primary Needs |
|-----------|----------------|
| **Researchers** | Water level trends, recharge estimates, storage calculations, exportable data |
| **Planners** | State/district-level coverage, alert distribution, regional comparisons |
| **Policymakers** | High-level insights, critical alerts, recommended actions |
| **Developers** | REST API for mobile apps, dashboards, or external tools |

---

## 4. Core Features & Functional Requirements

### 4.1 Data Ingestion & Sync

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F1.1 | Sync DWLR station metadata from CGWB API (or manual/admin entry) | Must | Implemented |
| F1.2 | Sync water level time-series for a station via CGWB API | Must | Implemented |
| F1.3 | Bulk sync: all stations, or by state(s) | Should | Implemented |
| F1.4 | On-demand sync per station via API (`POST /api/stations/{code}/sync_data/`) | Must | Implemented |
| F1.5 | Management commands: `seed_sample_data`, `sync_dwlr_data` | Must | Implemented |

### 4.2 Data Models & Storage

| Entity | Description | Key Attributes |
|--------|-------------|----------------|
| **DWLRStation** | Monitoring station | `station_code` (PK), name, state, district, block, lat/long, well_depth, elevation, aquifer_type, is_active, last_data_update |
| **WaterLevel** | Time-series measurement | station, timestamp, depth (m BGL), water_level_elevation, data_source |
| **GroundwaterResource** | Computed metrics | station, calculation_date, period_start/end, recharge, storage, trend, alert_status |

### 4.3 Resource Evaluation (Analytics Engine)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F3.1 | **Recharge estimation** from water level rise during recharge periods | Must | Implemented |
| F3.2 | **Storage calculation** (current/available storage, storage %) using well depth, current depth, specific yield | Must | Implemented |
| F3.3 | **Trend analysis** (rising / falling / stable) via linear regression; magnitude in m/year | Must | Implemented |
| F3.4 | **Alert status** (critical / warning / normal / good) from storage % and depth-based fallbacks | Must | Implemented |
| F3.5 | Metrics calculated over configurable period (default 365 days) | Should | Implemented |

### 4.4 Web Dashboard

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F4.1 | **Dashboard** with summary stats: total/active stations, critical/warning counts | Must | Implemented |
| F4.2 | **Interactive map** (Leaflet) of stations, color-coded by alert status | Must | Implemented |
| F4.3 | Map filters: state, alert status | Should | Implemented |
| F4.4 | **Stations list** with search (code, name, state, district), latest depth, status | Must | Implemented |
| F4.5 | **Station detail modal**: info, water level trend chart (e.g. last 12 months), resource metrics | Must | Implemented |
| F4.6 | **Sync Real-time Data** action per station from UI | Should | Implemented |
| F4.7 | **Analytics**: alert distribution chart, state-wise coverage chart | Should | Implemented |
| F4.8 | **Decision-support insights** for researchers/planners/policymakers | Should | Implemented |
| F4.9 | **Alerts** view: critical and warning stations | Must | Implemented |
| F4.10 | **API** link to `/api/info/` for developers | Should | Implemented |

### 4.5 API & Integration

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F5.1 | **REST API** for stations, water levels, resources | Must | Implemented |
| F5.2 | **API info** (`GET /api/info/`) documenting endpoints and query params for mobile/integration | Must | Implemented |
| F5.3 | Filter stations by `state`, `district`, `is_active`, `alert_status` | Should | Implemented |
| F5.4 | Filter water levels by `station_code`, `start_date`, `end_date`, `limit` | Must | Implemented |
| F5.5 | **Statistics** (`GET /api/stations/statistics/`) | Should | Implemented |
| F5.6 | **Insights** (`GET /api/stations/insights/`) | Should | Implemented |
| F5.7 | **Alerts** (`GET /api/resources/alerts/`) for critical/warning | Must | Implemented |

### 4.6 Admin & Operations

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| F6.1 | Django admin for DWLRStation, WaterLevel, GroundwaterResource | Must | Implemented |
| F6.2 | List filters, search, date hierarchy where relevant | Should | Implemented |
| F6.3 | Optional superuser creation for admin access | Should | Implemented |

---

## 5. API Specification Summary

### Base URL

- Web: `/`  
- API: `/api/`  
- API info: `/api/info/`  
- Admin: `/admin/`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/info/` | API documentation for mobile/integration |
| GET | `/api/stations/` | List stations (query: `state`, `district`, `is_active`, `alert_status`) |
| GET | `/api/stations/{station_code}/` | Station detail |
| GET | `/api/stations/{station_code}/water_levels/` | Water levels (query: `start_date`, `end_date`, `limit`) |
| GET | `/api/stations/{station_code}/resource_metrics/` | Latest resource metrics (calculated on demand if stale) |
| POST | `/api/stations/{station_code}/sync_data/` | Sync from CGWB API |
| GET | `/api/stations/statistics/` | Aggregate statistics |
| GET | `/api/stations/insights/` | Decision-support insights |
| GET | `/api/water-levels/` | Water levels (query: `station_code`, `start_date`, `end_date`) |
| GET | `/api/resources/` | Resources (query: `station_code`, `alert_status`) |
| GET | `/api/resources/alerts/` | Critical and warning alerts |

---

## 6. User Interface (Web)

### 6.1 Structure

- **Nav:** Dashboard, Stations, Analytics, Alerts, API (link to `/api/info/`)
- **Dashboard:** Stats cards, map with filters, refresh
- **Stations:** Search, table, row click → detail modal (chart, metrics, sync)
- **Analytics:** Alert distribution, state-wise coverage, insights list
- **Alerts:** List of critical/warning stations

### 6.2 Map

- **Provider:** Leaflet; tiles: OpenStreetMap
- **Center:** India (default view)
- **Markers:** One per station; color = alert status (critical=red, warning=amber, normal=blue, good=green)
- **Popup:** Name, code, state, district, latest depth, alert badge

### 6.3 Responsiveness & PWA

- **Responsive layout** for mobile and desktop
- **PWA:** `manifest.json` (short name, theme_color, display standalone, start_url)
- **Meta:** viewport, theme-color, apple-mobile-web-app-capable

---

## 7. External Integration: CGWB API

### 7.1 Design

- **Base URL:** `https://gwdata.cgwb.gov.in`
- **Service:** `CGWBAPIService` in `monitoring/services.py`
- **Calls:** fetch stations (optional state/district), fetch water level time-series per station (date range)

### 7.2 Configuration Note

Actual CGWB endpoints and response formats may change. The application provides the integration *framework*; `BASE_URL`, paths, and parsing in `monitoring/services.py` must be updated to match current CGWB API documentation (e.g. https://gwdata.cgwb.gov.in).

### 7.3 Fallback Data

- **Seed data:** `python manage.py seed_sample_data` creates sample stations and ~12 months of water levels for demo without CGWB.

---

## 8. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR1 | **Availability** | Web and API accessible during operational hours |
| NFR2 | **Performance** | Dashboard load &lt; 5 s under typical dataset (e.g. hundreds of stations) |
| NFR3 | **Scalability** | Support thousands of stations; DB index on (station, timestamp), (state, district), (alert_status) |
| NFR4 | **Security** | Production: `DEBUG=False`, HTTPS, secure `SECRET_KEY`, CORS configured |
| NFR5 | **Browser support** | Modern browsers (Chrome, Firefox, Safari, Edge) |
| NFR6 | **Mobile** | Responsive UI; API-first for native/hybrid apps |

---

## 9. Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Django 6.x, Django REST Framework |
| **Database** | SQLite (dev); PostgreSQL recommended for production |
| **Frontend** | Vanilla JS, Chart.js, Leaflet, Font Awesome |
| **HTTP** | `requests` for CGWB API; CORS via `django-cors-headers` |
| **Data** | pandas, numpy (available for analytics) |

---

## 10. Deployment & Operations

### 10.1 Setup (Summary)

1. Python venv, `pip install -r requirements.txt`
2. `python manage.py migrate`
3. Optional: `python manage.py createsuperuser`
4. Optional: `python manage.py seed_sample_data`
5. `python manage.py runserver` (dev)

### 10.2 Production Checklist

- [ ] `DEBUG = False`
- [ ] Configure PostgreSQL (or production DB)
- [ ] `python manage.py collectstatic`
- [ ] Web server (e.g. Gunicorn) + reverse proxy (e.g. Nginx)
- [ ] HTTPS
- [ ] Secure `SECRET_KEY`, env-based config
- [ ] CORS allowed origins set appropriately

### 10.3 Management Commands

| Command | Purpose |
|---------|---------|
| `seed_sample_data` | Demo data (stations, water levels, metrics); `--clear` to reset |
| `sync_dwlr_data --station-code X` | Sync one station from CGWB |
| `sync_dwlr_data --all` | Sync all active stations |
| `sync_dwlr_data --states S1 S2` | Sync by state(s) |

---

## 11. Out of Scope (Current Version)

- User authentication / role-based access (all endpoints read-only, `AllowAny`)
- Historical versioning of resource metrics
- Notifications (email/SMS) for critical alerts
- Export (CSV/Excel) from UI
- Multi-tenancy or organization-specific views

---

## 12. Future Roadmap (Recommendations)

| Phase | Ideas |
|-------|--------|
| **Short term** | Harden CGWB integration (real endpoints, retries, rate limiting); add CSV/Excel export |
| **Medium term** | Auth (e.g. token-based) and optional role-based access; email alerts for critical stations |
| **Long term** | Forecasts (e.g. simple time-series models); additional data sources; mobile app |

---

## 13. Glossary

| Term | Meaning |
|------|---------|
| **DWLR** | Digital Water Level Recorder |
| **CGWB** | Central Ground Water Board (India) |
| **BGL** | Below Ground Level |
| **Recharge** | Water added to aquifer (e.g. from rainfall, seepage) |
| **Storage** | Groundwater stored in aquifer; computed from well depth, depth to water, specific yield |
| **Alert status** | Critical / Warning / Normal / Good, derived from storage and trends |

---

## 14. References

- [CGWB / GW Data](https://gwdata.cgwb.gov.in)
- Django: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Leaflet: https://leafletjs.com/
- Chart.js: https://www.chartjs.org/
- OpenStreetMap: https://www.openstreetmap.org/

---

*This document describes the application as implemented in the repository. Implementation details may vary; refer to the source code and `README.md` / `SETUP.md` for up-to-date usage.*
