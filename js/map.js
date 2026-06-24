document.addEventListener('DOMContentLoaded', () => {
    const coords = window.GeoLocation.getStoredCoordinates();
    const query = window.GeoLocation.getStoredSearchQuery();

    if (!coords && !query) {
        window.location.href = '/index.html';
        return;
    }

    // Initialize Map
    const map = L.map('map').setView([15.3173, 75.7139], 7);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    if (coords) {
        L.circleMarker([coords.lat, coords.lng], {
            radius: 8,
            fillColor: '#3b82f6', // blue
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);
    }

    const loadingOverlay = document.getElementById('loading-overlay');
    const previewContainer = document.getElementById('constituency-preview');
    const previewName = document.getElementById('preview-name');
    const previewDistrict = document.getElementById('preview-district');

    async function loadConstituency(fetchDataPromise) {
        loadingOverlay.style.display = 'flex';
        previewContainer.style.display = 'none';

        try {
            const data = await fetchDataPromise;
            loadingOverlay.style.display = 'none';

            if (data.error) {
                alert(data.error);
                return;
            }

            // Draw polygon
            if (data.constituency && data.constituency.geojson) {
                const polygonLayer = L.geoJSON(data.constituency.geojson, {
                    style: {
                        fillColor: '#22c55e',
                        fillOpacity: 0.2,
                        color: '#22c55e',
                        weight: 2
                    }
                }).addTo(map);

                map.fitBounds(polygonLayer.getBounds());
            }

            // Show preview
            previewName.textContent = data.constituency.name;
            previewDistrict.textContent = data.constituency.district;
            previewContainer.style.display = 'flex'; // Match CSS layout

            // Store full data for results page
            sessionStorage.setItem('geocivic_result', JSON.stringify(data));

        } catch (error) {
            loadingOverlay.style.display = 'none';
            console.error(error);
            alert("Failed to load constituency data.");
        }
    }

    // Load data depending on the input type
    if (coords) {
        loadConstituency(window.GeoAPI.fetchByCoordinates(coords.lat, coords.lng));
    } else if (query) {
        loadConstituency(window.GeoAPI.fetchBySearch(query));
    }
});
