document.addEventListener('DOMContentLoaded', async () => {
    const overlay = document.getElementById('loading-overlay');
    const content = document.getElementById('dashboard-content');
    const loadingText = document.getElementById('loading-text');

    function renderResults(data) {
        if (data.error) {
            alert("Constituency data not found or error occurred: " + data.error);
            loadingText.textContent = "Error loading data. Please try again.";
            return;
        }

        if (!data || !data.constituency) {
            alert("Constituency data not found.");
            loadingText.textContent = "Error loading data. Please try again.";
            return;
        }

        // Constituency
        document.getElementById('constituency-name').textContent = data.constituency.name;
        document.getElementById('constituency-district').textContent = data.constituency.district;

        // MLA
        document.getElementById('mla-name').textContent = data.mla.name;
        document.getElementById('mla-party').textContent = data.mla.party;
        document.getElementById('mla-education').textContent = data.mla.education || 'Education not specified';

        // MLA Achievements
        const list = document.getElementById('mla-achievements');
        list.innerHTML = '';
        if (data.mla.summary && Array.isArray(data.mla.summary)) {
            data.mla.summary.forEach(bullet => {
                const li = document.createElement('li');
                li.textContent = bullet;
                list.appendChild(li);
            });
        }

        // Sentiment
        const badge = document.getElementById('sentiment-badge');
        const sentiment = data.mla.sentiment || 'Neutral';
        badge.textContent = sentiment;
        
        if (sentiment === 'Positive') {
            badge.style.backgroundColor = '#22c55e'; // green
        } else if (sentiment === 'Negative') {
            badge.style.backgroundColor = '#ef4444'; // red
        } else {
            badge.style.backgroundColor = '#6b7280'; // gray
        }

        // MP
        document.getElementById('mp-name').textContent = data.mp.name;
        document.getElementById('mp-party').textContent = data.mp.party;

        // Show UI
        overlay.style.display = 'none';
        content.style.display = 'flex';
    }

    // Main logic
    const storedDataStr = sessionStorage.getItem('geocivic_result');
    if (storedDataStr) {
        try {
            const data = JSON.parse(storedDataStr);
            renderResults(data);
        } catch (e) {
            console.error("Failed to parse cached data:", e);
        }
    } else {
        const query = window.GeoLocation ? window.GeoLocation.getStoredSearchQuery() : null;
        if (query) {
            overlay.style.display = 'flex';
            try {
                const data = await window.GeoAPI.fetchBySearch(query);
                // Cache it so map view can work too
                sessionStorage.setItem('geocivic_result', JSON.stringify(data));
                renderResults(data);
            } catch (err) {
                console.error(err);
                alert("Constituency data not found or error occurred.");
                loadingText.textContent = "Error loading data.";
            }
        } else {
            // No data and no query -> redirect home
            window.location.href = '/index.html';
        }
    }
});
