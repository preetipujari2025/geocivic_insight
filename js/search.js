const CONSTITUENCIES = [
    "Mahadevapura", "Shivajinagar", "Yelahanka", "Hebbal", "Rajajinagar",
    "Chickpet", "Basavanagudi", "Padmanabhanagar", "Jayanagar", "BTM Layout",
    "Vijayapura", "Hubli-Dharwad-Central", "Mysuru Rural", "Mandya", "Tumkur", 
    "Belagavi", "Mangaluru", "Udupi", "Shimoga", "Davangere"
];

function initSearch(inputId, buttonId, suggestionListId) {
    const input = document.getElementById(inputId);
    const button = document.getElementById(buttonId);
    const suggestionList = document.getElementById(suggestionListId);

    if (!input || !button) return;

    // Debounce helper
    function debounce(func, delay) {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
            }, delay);
        };
    }

    function executeSearch() {
        const query = input.value.trim();
        if (query.length < 3) {
            showError(input, "Type at least 3 characters");
            return;
        }

        if (window.GeoLocation) {
            window.GeoLocation.storeSearchQuery(query);
        } else {
            sessionStorage.setItem('geocivic_search_query', query);
        }

        sessionStorage.removeItem('geocivic_lat');
        sessionStorage.removeItem('geocivic_lng');
        sessionStorage.removeItem('geocivic_result');

        window.location.href = '/map.html';
    }

    button.addEventListener('click', executeSearch);

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            executeSearch();
            if (suggestionList) suggestionList.style.display = 'none';
        }
    });

    if (suggestionList) {
        input.addEventListener('input', debounce((e) => {
            showSuggestions(e.target.value.trim(), input, suggestionList, executeSearch);
        }, 300));

        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target !== input && e.target !== suggestionList && !suggestionList.contains(e.target)) {
                suggestionList.style.display = 'none';
            }
        });
    }
}

function showSuggestions(query, input, suggestionList, searchCallback) {
    if (query.length < 2) {
        suggestionList.style.display = 'none';
        return;
    }

    const matches = CONSTITUENCIES.filter(name => 
        name.toLowerCase().includes(query.toLowerCase())
    );

    if (matches.length === 0) {
        suggestionList.style.display = 'none';
        return;
    }

    suggestionList.innerHTML = '';
    matches.forEach(match => {
        const div = document.createElement('div');
        div.textContent = match;
        div.style.padding = '0.5rem 1rem';
        div.style.cursor = 'pointer';
        div.style.borderBottom = '1px solid #374151';

        div.addEventListener('mouseover', () => {
            div.style.backgroundColor = '#374151';
        });
        div.addEventListener('mouseout', () => {
            div.style.backgroundColor = 'transparent';
        });

        div.addEventListener('click', () => {
            input.value = match;
            suggestionList.style.display = 'none';
            searchCallback();
        });

        suggestionList.appendChild(div);
    });

    suggestionList.style.display = 'block';
    // Position list dynamically relative to the input
    suggestionList.style.position = 'absolute';
    suggestionList.style.backgroundColor = '#1f2937';
    suggestionList.style.border = '1px solid #374151';
    suggestionList.style.borderRadius = '0.5rem';
    suggestionList.style.width = input.offsetWidth + 'px';
    suggestionList.style.maxHeight = '200px';
    suggestionList.style.overflowY = 'auto';
    suggestionList.style.zIndex = '1000';
    suggestionList.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
    
    // Slight offset
    suggestionList.style.top = (input.offsetTop + input.offsetHeight + 4) + 'px';
    suggestionList.style.left = input.offsetLeft + 'px';
}

function showError(inputElement, message) {
    const originalBorder = inputElement.style.border;
    inputElement.style.border = '1px solid #ef4444';

    let errorSpan = inputElement.nextElementSibling;
    let created = false;
    if (!errorSpan || !errorSpan.classList.contains('search-error-msg')) {
        errorSpan = document.createElement('span');
        errorSpan.classList.add('search-error-msg');
        errorSpan.style.color = '#ef4444';
        errorSpan.style.fontSize = '0.75rem';
        errorSpan.style.display = 'block';
        errorSpan.style.marginTop = '0.25rem';
        inputElement.parentNode.insertBefore(errorSpan, inputElement.nextSibling);
        created = true;
    }

    errorSpan.textContent = message;

    setTimeout(() => {
        inputElement.style.border = originalBorder;
        if (created && errorSpan.parentNode) {
            errorSpan.parentNode.removeChild(errorSpan);
        } else {
            errorSpan.textContent = '';
        }
    }, 3000);
}

window.Search = { initSearch };
