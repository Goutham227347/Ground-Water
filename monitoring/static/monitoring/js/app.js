// Groundwater Monitoring Dashboard - Main Application

const API_BASE_URL = '/api';

// Global state
let map = null;
let markers = [];
let stations = [];
let currentCharts = {};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeMap();
    loadDashboardData();
    initializeEventListeners();
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');

    // Handle hash change (back/forward buttons)
    window.addEventListener('hashchange', handleHashChange);

    // Initial load based on hash
    if (window.location.hash) {
        handleHashChange();
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            window.location.hash = targetId;
        });
    });

    function handleHashChange() {
        const hash = window.location.hash.substring(1) || 'dashboard';
        updateUI(hash);
    }

    function updateUI(targetId) {
        // Validate targetId
        let sectionExists = false;
        sections.forEach(s => {
            if (s.id === targetId) sectionExists = true;
        });

        if (!sectionExists) {
            targetId = 'dashboard';
        }
        // Update active nav link
        navLinks.forEach(l => {
            if (l.getAttribute('href') === `#${targetId}`) {
                l.classList.add('active');
            } else {
                l.classList.remove('active');
            }
        });

        // Show target section
        sections.forEach(s => {
            if (s.id === targetId) {
                s.classList.add('active');
            } else {
                s.classList.remove('active');
            }
        });

        // Load section-specific data
        if (targetId === 'stations') {
            loadStations();
        } else if (targetId === 'analytics') {
            loadAnalytics();
        } else if (targetId === 'alerts') {
            loadAlerts();
        }
    }
}

// Initialize Leaflet Map
function initializeMap() {
    // Center on India
    map = L.map('map').setView([20.5937, 78.9629], 5);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    // Add custom marker icon
    const createMarkerIcon = (color) => {
        return L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
            iconSize: [20, 20],
        });
    };
}

// Load Dashboard Data
async function loadDashboardData() {
    showLoading();
    try {
        const statsResponse = await fetch(`${API_BASE_URL}/stations/statistics/`);
        if (!statsResponse.ok) {
            throw new Error(`Statistics API error: ${statsResponse.status}`);
        }

        const stationsResponse = await fetch(`${API_BASE_URL}/stations/?limit=1000`);
        if (!stationsResponse.ok) {
            throw new Error(`Stations API error: ${stationsResponse.status}`);
        }

        const stats = await statsResponse.json();
        const stationsData = await stationsResponse.json();

        // Update statistics
        updateStatistics(stats);

        // Store stations
        stations = stationsData.results || stationsData;

        // Update map
        updateMapMarkers(stations);

        // Populate state filter for map
        populateStateFilter(stations);

        // Load stations table if on stations page
        if (document.getElementById('stations').classList.contains('active')) {
            loadStations();
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Show clearer error to user
        showError(`Failed to load data: ${error.message}. Check console for details.`);
    } finally {
        hideLoading();
    }
}

// Update Statistics Cards
function updateStatistics(stats) {
    document.getElementById('totalStations').textContent = stats.total_stations || 0;
    document.getElementById('activeStations').textContent = stats.active_stations || 0;
    document.getElementById('criticalStations').textContent = stats.alert_distribution?.critical || 0;
    document.getElementById('warningStations').textContent = stats.alert_distribution?.warning || 0;
}

// Update Map Markers
function updateMapMarkers(stationsData) {
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    stationsData.forEach(station => {
        if (!station.latitude || !station.longitude) return;

        // Determine marker color based on alert status
        let color = '#3b82f6'; // default blue
        if (station.alert_status === 'critical') {
            color = '#ef4444';
        } else if (station.alert_status === 'warning') {
            color = '#f59e0b';
        } else if (station.alert_status === 'good') {
            color = '#22c55e';
        }

        // Create marker
        const marker = L.marker([station.latitude, station.longitude], {
            icon: L.divIcon({
                className: 'custom-marker',
                html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); cursor: pointer;"></div>`,
                iconSize: [16, 16],
            })
        }).addTo(map);

        // Add popup
        const popupContent = `
            <div style="min-width: 200px;">
                <h3 style="margin: 0 0 0.5rem 0; font-size: 1.1rem;">${station.name}</h3>
                <p style="margin: 0.25rem 0; font-size: 0.9rem;"><strong>Code:</strong> ${station.station_code}</p>
                <p style="margin: 0.25rem 0; font-size: 0.9rem;"><strong>State:</strong> ${station.state}</p>
                <p style="margin: 0.25rem 0; font-size: 0.9rem;"><strong>District:</strong> ${station.district}</p>
                ${station.latest_depth ? `<p style="margin: 0.25rem 0; font-size: 0.9rem;"><strong>Latest Depth:</strong> ${station.latest_depth.toFixed(2)} m</p>` : ''}
                ${station.alert_status ? `<p style="margin: 0.5rem 0 0 0;"><span class="alert-badge ${station.alert_status}">${station.alert_status}</span></p>` : ''}
                <button onclick="openStationModal('${station.station_code}')" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; width: 100%;">View Details</button>
            </div>
        `;
        marker.bindPopup(popupContent);

        // Click handler
        marker.on('click', () => {
            openStationModal(station.station_code);
        });

        markers.push(marker);
    });
}

// Load Stations Table
async function loadStations() {
    const tbody = document.getElementById('stationsTableBody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading">Loading stations...</td></tr>';

    try {
        const response = await fetch(`${API_BASE_URL}/stations/?limit=1000`);
        const data = await response.json();
        const stationsList = data.results || data;

        if (stationsList.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No stations found</td></tr>';
            return;
        }

        tbody.innerHTML = stationsList.map(station => `
            <tr>
                <td><strong>${station.station_code}</strong></td>
                <td>${station.name}</td>
                <td>${station.state}</td>
                <td>${station.district}</td>
                <td>${station.latest_depth ? station.latest_depth.toFixed(2) + ' m' : 'N/A'}</td>
                <td>
                    ${station.alert_status ? `<span class="alert-badge ${station.alert_status}">${station.alert_status}</span>` : '<span class="alert-badge normal">Normal</span>'}
                </td>
                <td>
                    <button onclick="openStationModal('${station.station_code}')" class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.85rem;">View</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading stations:', error);
        tbody.innerHTML = '<tr><td colspan="7" class="loading">Error loading stations</td></tr>';
    }
}

// Open Station Modal
async function openStationModal(stationCode) {
    const modal = document.getElementById('stationModal');
    modal.classList.add('active');

    showLoading();
    try {
        // Fetch station details
        const [stationResponse, waterLevelResponse, resourceResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/stations/${stationCode}/`),
            fetch(`${API_BASE_URL}/stations/${stationCode}/water_levels/?limit=365`),
            fetch(`${API_BASE_URL}/stations/${stationCode}/resource_metrics/`)
        ]);

        const station = await stationResponse.json();
        const waterLevels = await waterLevelResponse.json();
        const resource = await resourceResponse.json();

        // Update modal content
        document.getElementById('modalStationName').textContent = station.name;
        document.getElementById('modalStationCode').textContent = station.station_code;
        document.getElementById('modalLocation').textContent = `${station.state}, ${station.district}`;

        if (station.latest_water_level) {
            const now = new Date();

            document.getElementById('modalWaterLevel').textContent =
                `${station.latest_water_level.depth.toFixed(2)} m (${now.toLocaleString()})`;
        } else {
            document.getElementById('modalWaterLevel').textContent = 'N/A';
        }


        if (station.resource_status) {
            const status = station.resource_status.alert_status;
            document.getElementById('modalAlertStatus').textContent = status;
            document.getElementById('modalAlertStatus').className = `alert-badge ${status}`;

            document.getElementById('modalStorage').textContent =
                station.resource_status.storage_percentage ?
                    `${station.resource_status.storage_percentage.toFixed(1)}%` : 'N/A';

            const mag = station.resource_status.trend_magnitude;
            document.getElementById('modalTrend').textContent =
                station.resource_status.trend ?
                    `${station.resource_status.trend} (${mag != null ? mag.toFixed(2) : '-'} m/year)` : 'N/A';
        }

        // Update resource metrics
        if (resource) {
            document.getElementById('metricRecharge').textContent =
                resource.estimated_recharge ? `${resource.estimated_recharge.toFixed(2)} m³` : 'N/A';
            document.getElementById('metricRechargeRate').textContent =
                resource.recharge_rate ? `${resource.recharge_rate.toFixed(2)} mm/year` : 'N/A';
            document.getElementById('metricStorage').textContent =
                resource.current_storage ? `${resource.current_storage.toFixed(2)} m³` : 'N/A';
            document.getElementById('metricStoragePercent').textContent =
                resource.storage_percentage ? `${resource.storage_percentage.toFixed(1)}%` : 'N/A';
        }

        // Create water level chart
        createWaterLevelChart(waterLevels);

    } catch (error) {
        console.error('Error loading station details:', error);
        showError('Failed to load station details');
    } finally {
        hideLoading();
    }
}

// Create Water Level Chart
function createWaterLevelChart(waterLevels) {
    const ctx = document.getElementById('waterLevelChart');

    // Destroy existing chart if any
    if (currentCharts.waterLevel) {
        currentCharts.waterLevel.destroy();
    }

    // Sort by timestamp
    const sorted = waterLevels.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    const labels = sorted.map(wl => new Date(wl.timestamp).toLocaleDateString());
    const depths = sorted.map(wl => wl.depth);

    currentCharts.waterLevel = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Water Level Depth (m)',
                data: depths,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    reverse: true, // Reverse so depth increases downward
                    title: {
                        display: true,
                        text: 'Depth (m)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

// Populate state filter dropdown from stations
function populateStateFilter(stationsData) {
    const sel = document.getElementById('stateFilter');
    if (!sel) return;
    const states = [...new Set((stationsData || []).map(s => s.state).filter(Boolean))].sort();
    sel.innerHTML = '<option value="">All States</option>' +
        states.map(s => `<option value="${s}">${s}</option>`).join('');
}

// Load Insights (Decision Support)
async function loadInsights() {
    const container = document.getElementById('insightsContainer');
    if (!container) return;
    container.innerHTML = '<div class="loading">Loading insights...</div>';
    try {
        const res = await fetch(`${API_BASE_URL}/stations/insights/`);
        const data = await res.json();
        const insights = data.insights || [];
        if (insights.length === 0) {
            container.innerHTML = '<div class="loading">No insights yet. Add stations and water level data.</div>';
            return;
        }
        container.innerHTML = insights.map(i => `
            <div class="insight-card ${i.priority || 'info'}">
                <h4>${i.title || 'Insight'}</h4>
                <p>${i.message || ''}</p>
                <div class="action">${i.action || ''}</div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Error loading insights:', e);
        container.innerHTML = '<div class="loading">Error loading insights</div>';
    }
}

// Load Analytics
async function loadAnalytics() {
    try {
        // Load alert distribution chart
        const statsResponse = await fetch(`${API_BASE_URL}/stations/statistics/`);
        const stats = await statsResponse.json();

        createAlertChart(stats.alert_distribution);

        // Load state distribution (simplified)
        const stationsResponse = await fetch(`${API_BASE_URL}/stations/?limit=1000`);
        const stationsData = await stationsResponse.json();
        const stationsList = stationsData.results || stationsData;

        createStateChart(stationsList);
        loadInsights();

    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// Create Alert Distribution Chart
function createAlertChart(alertDistribution) {
    const ctx = document.getElementById('alertChart');

    if (currentCharts.alert) {
        currentCharts.alert.destroy();
    }

    currentCharts.alert = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'Warning', 'Normal', 'Good'],
            datasets: [{
                data: [
                    alertDistribution.critical || 0,
                    alertDistribution.warning || 0,
                    alertDistribution.normal || 0,
                    alertDistribution.good || 0,
                ],
                backgroundColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#3b82f6',
                    '#22c55e',
                ],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
}

// Create State Distribution Chart
function createStateChart(stations) {
    const ctx = document.getElementById('stateChart');

    if (currentCharts.state) {
        currentCharts.state.destroy();
    }

    // Count stations by state
    const stateCounts = {};
    stations.forEach(station => {
        const state = station.state || 'Unknown';
        stateCounts[state] = (stateCounts[state] || 0) + 1;
    });

    const sortedStates = Object.entries(stateCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10); // Top 10 states

    currentCharts.state = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedStates.map(s => s[0]),
            datasets: [{
                label: 'Number of Stations',
                data: sortedStates.map(s => s[1]),
                backgroundColor: '#2563eb',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                }
            }
        }
    });
}

// Load Alerts
async function loadAlerts() {
    const container = document.getElementById('alertsContainer');
    container.innerHTML = '<div class="loading">Loading alerts...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/resources/alerts/`);
        const alerts = await response.json();

        if (alerts.length === 0) {
            container.innerHTML = '<div class="loading">No critical alerts at this time</div>';
            return;
        }

        container.innerHTML = alerts.map(alert => `
            <div class="alert-item ${alert.alert_status}">
                <div class="alert-info">
                    <div class="alert-title">${alert.station_name} (${alert.station_code})</div>
                    <div class="alert-details">
                        Storage: ${alert.storage_percentage ? alert.storage_percentage.toFixed(1) + '%' : 'N/A'} | 
                        Trend: ${alert.trend || 'N/A'} | 
                        Status: ${alert.alert_status}
                    </div>
                </div>
                <button onclick="openStationModal('${alert.station_code}')" class="btn btn-primary">
                    View Details
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading alerts:', error);
        container.innerHTML = '<div class="loading">Error loading alerts</div>';
    }
}

// Initialize Event Listeners
function initializeEventListeners() {
    // Close modal
    document.getElementById('closeModal').addEventListener('click', () => {
        document.getElementById('stationModal').classList.remove('active');
    });

    // Close modal on outside click
    document.getElementById('stationModal').addEventListener('click', (e) => {
        if (e.target.id === 'stationModal') {
            document.getElementById('stationModal').classList.remove('active');
        }
    });

    // Refresh data
    document.getElementById('refreshData').addEventListener('click', () => {
        loadDashboardData();
    });

    // Sync station data
    document.getElementById('syncStationData').addEventListener('click', async () => {
        const stationCode = document.getElementById('modalStationCode').textContent;
        if (!stationCode) return;

        showLoading();
        try {
            const response = await fetch(`${API_BASE_URL}/stations/${stationCode}/sync_data/`, {
                method: 'POST',
            });
            const result = await response.json();

            if (result.status === 'success') {
                alert('Data synced successfully!');
                openStationModal(stationCode); // Reload modal
            } else {
                alert('Sync completed with warnings: ' + result.message);
            }
        } catch (error) {
            console.error('Error syncing data:', error);
            alert('Error syncing data');
        } finally {
            hideLoading();
        }
    });

    // Station search
    const searchInput = document.getElementById('stationSearch');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterStations(searchInput.value);
            }, 300);
        });
    }

    // Map filters
    const stateFilter = document.getElementById('stateFilter');
    const alertFilter = document.getElementById('alertFilter');

    if (stateFilter) {
        stateFilter.addEventListener('change', applyMapFilters);
    }
    if (alertFilter) {
        alertFilter.addEventListener('change', applyMapFilters);
    }
}

// Filter Stations
function filterStations(query) {
    const tbody = document.getElementById('stationsTableBody');
    const rows = tbody.querySelectorAll('tr');

    const lowerQuery = query.toLowerCase();
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(lowerQuery) ? '' : 'none';
    });
}

// Apply Map Filters
function applyMapFilters() {
    const stateFilter = document.getElementById('stateFilter').value;
    const alertFilter = document.getElementById('alertFilter').value;

    let filteredStations = stations;

    if (stateFilter) {
        filteredStations = filteredStations.filter(s => s.state === stateFilter);
    }

    if (alertFilter) {
        filteredStations = filteredStations.filter(s => s.alert_status === alertFilter);
    }

    updateMapMarkers(filteredStations);
}

// Utility Functions
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showError(message) {
    alert(message); // Simple error display - can be enhanced
}

// Make functions globally available
window.openStationModal = openStationModal;
