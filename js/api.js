const CONFIG = {
    USE_MOCK: true, // CHANGE TO false WHEN REAL API IS READY
    API_BASE: 'http://127.0.0.1:8000/api',
    MOCK_DELAY_MS: 800, // fake network delay for realistic testing
};

const MOCK_RESPONSE = {
    "constituency": {
        "name": "Mahadevapura",
        "district": "Bangalore Urban",
        "geojson": {
            "type": "Polygon",
            "coordinates": [[[77.68, 12.99], [77.72, 12.99], [77.72, 13.02], [77.68, 13.02]]]
        }
    },
    "mla": {
        "name": "Sample MLA Name",
        "party": "Indian National Congress",
        "education": "B.E. Civil Engineering",
        "summary": [
            "Built 12 anganwadi centres across the constituency",
            "Secured Rs 45 crore for metro connectivity expansion",
            "Launched free skill training programme for 2000 youth"
        ],
        "sentiment": "Positive"
    },
    "mp": {
        "name": "Sample MP Name",
        "party": "Indian National Congress"
    }
};

async function fetchByCoordinates(lat, lng) {
    if (CONFIG.USE_MOCK) {
        await new Promise(r => setTimeout(r, CONFIG.MOCK_DELAY_MS));
        return MOCK_RESPONSE;
    } else {
        const res = await fetch(`${CONFIG.API_BASE}/locate/?lat=${lat}&lng=${lng}`);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return await res.json();
    }
}

async function fetchBySearch(query) {
    if (CONFIG.USE_MOCK) {
        await new Promise(r => setTimeout(r, CONFIG.MOCK_DELAY_MS));
        const mockCopy = JSON.parse(JSON.stringify(MOCK_RESPONSE));
        mockCopy.constituency.name = query;
        return mockCopy;
    } else {
        const res = await fetch(`${CONFIG.API_BASE}/search/?q=${encodeURIComponent(query)}`);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return await res.json();
    }
}

window.GeoAPI = { fetchByCoordinates, fetchBySearch, CONFIG };
