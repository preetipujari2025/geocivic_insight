/**
 * GeoCivic Insight — Geolocation Handler
 * Handles browser geolocation, coordinate storage, and search query persistence.
 * Vanilla JavaScript — no frameworks, no npm.
 */

/**
 * Request the user's current location via browser Geolocation API.
 * @param {Function} onSuccess - Called with (lat, lng, accuracy) on success
 * @param {Function} onError - Called with (errorMessage) on failure
 * @param {Function} onLoading - Called immediately to indicate loading state
 */
function requestLocation(onSuccess, onError, onLoading) {
    onLoading();

    if (!navigator.geolocation) {
        onError("Your browser doesn't support geolocation");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            const accuracy = position.coords.accuracy;
            onSuccess(lat, lng, accuracy);
        },
        (error) => {
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    onError("Location access denied. Please use the search bar instead.");
                    break;
                case error.POSITION_UNAVAILABLE:
                    onError("Location unavailable. Please use the search bar.");
                    break;
                case error.TIMEOUT:
                    onError("Location request timed out. Please try again.");
                    break;
                default:
                    onError("Unknown location error. Please use the search bar.");
            }
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
}

/**
 * Store GPS coordinates in session storage.
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 */
function storeCoordinates(lat, lng) {
    sessionStorage.setItem('geocivic_lat', lat);
    sessionStorage.setItem('geocivic_lng', lng);
}

/**
 * Retrieve stored GPS coordinates from session storage.
 * @returns {Object|null} { lat, lng } or null if not stored
 */
function getStoredCoordinates() {
    const lat = sessionStorage.getItem('geocivic_lat');
    const lng = sessionStorage.getItem('geocivic_lng');
    if (lat && lng) return { lat: parseFloat(lat), lng: parseFloat(lng) };
    return null;
}

/**
 * Store a search query in session storage.
 * @param {string} query - The search query string
 */
function storeSearchQuery(query) {
    sessionStorage.setItem('geocivic_search_query', query);
}

/**
 * Retrieve stored search query from session storage.
 * @returns {string|null} The stored query or null
 */
function getStoredSearchQuery() {
    return sessionStorage.getItem('geocivic_search_query');
}

// Export as window globals (no ES modules)
window.GeoLocation = {
    requestLocation,
    storeCoordinates,
    getStoredCoordinates,
    storeSearchQuery,
    getStoredSearchQuery
};
