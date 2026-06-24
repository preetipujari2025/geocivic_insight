function requestLocation(onSuccess, onError, onLoading) {
    onLoading();
    if (!navigator.geolocation) {
        onError("Your browser doesn't support geolocation.");
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
                    onError("Location access denied. Please use the search bar.");
                    break;
                case error.POSITION_UNAVAILABLE:
                    onError("Location unavailable. Please use the search bar.");
                    break;
                case error.TIMEOUT:
                    onError("Location request timed out. Please try again.");
                    break;
                default:
                    onError("Unknown location error. Please use the search bar.");
                    break;
            }
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
}

function storeCoordinates(lat, lng) {
    sessionStorage.setItem('geocivic_lat', lat);
    sessionStorage.setItem('geocivic_lng', lng);
}

function getStoredCoordinates() {
    const lat = sessionStorage.getItem('geocivic_lat');
    const lng = sessionStorage.getItem('geocivic_lng');
    if (lat && lng) return { lat: parseFloat(lat), lng: parseFloat(lng) };
    return null;
}

function storeSearchQuery(query) {
    sessionStorage.setItem('geocivic_search_query', query);
}

function getStoredSearchQuery() {
    return sessionStorage.getItem('geocivic_search_query');
}

window.GeoLocation = {
    requestLocation,
    storeCoordinates,
    getStoredCoordinates,
    storeSearchQuery,
    getStoredSearchQuery
};
