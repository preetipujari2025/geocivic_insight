/**
 * GeoCivic Insight — Map Controller
 * Handles Leaflet map initialization, constituency polygon rendering,
 * and data loading via GeoAPI.
 * Vanilla JavaScript — no frameworks, no npm.
 */

(function () {
    'use strict';

    let map = null;
    let polygonLayer = null;
    let userMarker = null;

    // DOM elements
    const loadingOverlay = document.getElementById('loading-overlay');
    const errorOverlay = document.getElementById('error-overlay');
    const errorMessage = document.getElementById('error-message');
    const constituencyPreview = document.getElementById('constituency-preview');
    const previewName = document.getElementById('preview-name');
    const previewDistrict = document.getElementById('preview-district');

    /**
     * Initialize the Leaflet map centered on Karnataka.
     */
    function initMap() {
        map = L.map('map', {
            center: [15.3173, 75.7139],
            zoom: 7,
            zoomControl: true,
        });

        // Dark-style OpenStreetMap tiles
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19,
        }).addTo(map);
    }

    /**
     * Add a circle marker for the user's GPS location.
     * @param {number} lat
     * @param {number} lng
     */
    function markUserLocation(lat, lng) {
        userMarker = L.circleMarker([lat, lng], {
            radius: 8,
            fillColor: '#3b82f6',
            fillOpacity: 0.9,
            color: '#ffffff',
            weight: 2,
        }).addTo(map);

        userMarker.bindPopup('<b>Your Location</b>').openPopup();
    }

    /**
     * Show loading overlay.
     */
    function showLoading() {
        loadingOverlay.classList.remove('hidden');
    }

    /**
     * Hide loading overlay.
     */
    function hideLoading() {
        loadingOverlay.classList.add('hidden');
    }

    /**
     * Show error message on the map.
     * @param {string} msg
     */
    function showError(msg) {
        hideLoading();
        errorMessage.textContent = msg;
        errorOverlay.classList.add('visible');
    }

    /**
     * Display constituency data on the map and preview card.
     * @param {Object} data - API response containing constituency, mla, mp
     * @param {number|null} lat - User latitude (if available)
     * @param {number|null} lng - User longitude (if available)
     */
    function displayConstituency(data, lat, lng) {
        hideLoading();

        if (data.error) {
            showError(data.error);
            return;
        }

        // Draw constituency polygon
        if (data.constituency && data.constituency.geojson) {
            polygonLayer = L.geoJSON(data.constituency.geojson, {
                style: {
                    fillColor: '#22c55e',
                    fillOpacity: 0.2,
                    color: '#22c55e',
                    weight: 2,
                },
            }).addTo(map);

            // Fit map to polygon bounds
            map.fitBounds(polygonLayer.getBounds(), { padding: [40, 40] });
        }

        // Mark user location if coordinates are available
        if (lat !== null && lng !== null) {
            markUserLocation(lat, lng);
        }

        // Show constituency preview card
        if (data.constituency) {
            previewName.textContent = data.constituency.name || 'Unknown Constituency';
            previewDistrict.textContent = data.constituency.district
                ? data.constituency.district + ' District'
                : '';
            constituencyPreview.classList.add('visible');
        }

        // Store full result data for the results page
        sessionStorage.setItem('geocivic_result', JSON.stringify(data));
    }

    /**
     * Load constituency data by GPS coordinates.
     * @param {number} lat
     * @param {number} lng
     */
    async function loadConstituencyByCoords(lat, lng) {
        showLoading();

        try {
            const data = await GeoAPI.fetchByCoordinates(lat, lng);
            displayConstituency(data, lat, lng);
        } catch (err) {
            console.error('Failed to load constituency:', err);
            showError('Failed to load constituency data. Please try again.');
        }
    }

    /**
     * Load constituency data by search query.
     * @param {string} query
     */
    async function loadConstituencyBySearch(query) {
        showLoading();

        try {
            const data = await GeoAPI.fetchBySearch(query);
            displayConstituency(data, null, null);
        } catch (err) {
            console.error('Failed to search constituency:', err);
            showError('Failed to find constituency. Please try a different search.');
        }
    }

    /**
     * Main initialization on page load.
     */
    document.addEventListener('DOMContentLoaded', function () {
        // Initialize the map
        initMap();

        // Check for stored coordinates first
        const coords = GeoLocation.getStoredCoordinates();
        const searchQuery = GeoLocation.getStoredSearchQuery();

        if (coords) {
            // GPS-based lookup
            loadConstituencyByCoords(coords.lat, coords.lng);
        } else if (searchQuery) {
            // Search-based lookup
            loadConstituencyBySearch(searchQuery);
        } else {
            // No data — redirect to home
            window.location.href = 'index.html';
        }
    });
})();
