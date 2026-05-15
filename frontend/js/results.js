/**
 * GeoCivic Insight — Results Controller
 * Renders leader profiles, achievements, and sentiment data.
 * Vanilla JavaScript — no frameworks, no npm.
 */

(function () {
    'use strict';

    // DOM elements
    const loadingOverlay = document.getElementById('loading-overlay');
    const errorState = document.getElementById('error-state');
    const resultsContent = document.getElementById('results-content');

    /**
     * Hide loading overlay.
     */
    function hideLoading() {
        loadingOverlay.classList.add('hidden');
    }

    /**
     * Show error state and hide everything else.
     */
    function showError() {
        hideLoading();
        errorState.classList.add('visible');
        resultsContent.classList.remove('visible');
    }

    /**
     * Render all results data into the dashboard.
     * @param {Object} data - API response with constituency, mla, mp
     */
    function renderResults(data) {
        hideLoading();

        // Check for errors
        if (data.error) {
            showError();
            return;
        }

        // --- Constituency ---
        document.getElementById('constituency-name').textContent =
            data.constituency.name || 'Unknown';
        document.getElementById('constituency-district').textContent =
            data.constituency.district ? data.constituency.district + ' District' : '—';

        // --- MLA ---
        document.getElementById('mla-name').textContent =
            data.mla.name || '—';
        document.getElementById('mla-party').textContent =
            data.mla.party || '—';
        document.getElementById('mla-education').textContent =
            data.mla.education || '—';

        // Achievements
        const list = document.getElementById('mla-achievements');
        list.innerHTML = '';
        if (data.mla.summary && data.mla.summary.length > 0) {
            data.mla.summary.forEach(function (bullet) {
                const li = document.createElement('li');
                li.textContent = bullet;
                list.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No achievement data available';
            list.appendChild(li);
        }

        // Sentiment badge
        const badge = document.getElementById('sentiment-badge');
        const sentiment = data.mla.sentiment || 'Neutral';
        badge.textContent = sentiment;

        if (sentiment === 'Positive') {
            badge.style.backgroundColor = '#22c55e';
        } else if (sentiment === 'Negative') {
            badge.style.backgroundColor = '#ef4444';
        } else {
            badge.style.backgroundColor = '#6b7280';
        }

        // --- MP ---
        document.getElementById('mp-name').textContent =
            data.mp.name || '—';
        document.getElementById('mp-party').textContent =
            data.mp.party || '—';

        // Show results, hide loading
        resultsContent.classList.add('visible');
    }

    /**
     * Main initialization on page load.
     */
    document.addEventListener('DOMContentLoaded', function () {
        // Try to get cached result from map page
        const cachedData = sessionStorage.getItem('geocivic_result');

        if (cachedData) {
            try {
                const data = JSON.parse(cachedData);
                renderResults(data);
            } catch (e) {
                console.error('Failed to parse cached data:', e);
                showError();
            }
            return;
        }

        // No cached data — check for search query
        const searchQuery = GeoLocation.getStoredSearchQuery();

        if (searchQuery) {
            // Fetch data via search
            GeoAPI.fetchBySearch(searchQuery)
                .then(function (data) {
                    // Store for potential page refresh
                    sessionStorage.setItem('geocivic_result', JSON.stringify(data));
                    renderResults(data);
                })
                .catch(function (err) {
                    console.error('Failed to fetch search results:', err);
                    showError();
                });
            return;
        }

        // Check for stored coordinates
        const coords = GeoLocation.getStoredCoordinates();

        if (coords) {
            GeoAPI.fetchByCoordinates(coords.lat, coords.lng)
                .then(function (data) {
                    sessionStorage.setItem('geocivic_result', JSON.stringify(data));
                    renderResults(data);
                })
                .catch(function (err) {
                    console.error('Failed to fetch coordinate results:', err);
                    showError();
                });
            return;
        }

        // No data at all — redirect to home
        window.location.href = 'index.html';
    });
})();
