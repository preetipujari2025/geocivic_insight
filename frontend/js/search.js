/**
 * GeoCivic Insight — Search Module
 * Handles search functionality with autocomplete suggestions.
 * Vanilla JavaScript — no frameworks, no npm.
 */

// Hardcoded Karnataka constituency names for autocomplete
const CONSTITUENCIES = [
    "Mahadevapura", "Shivajinagar", "Yelahanka", "Hebbal", "Rajajinagar",
    "Chickpet", "Basavanagudi", "Padmanabhanagar", "Jayanagar", "BTM Layout",
    "Vijayapura", "Hubli-Dharwad-Central", "Mysuru Rural", "Mandya", "Tumkur",
    "Belagavi", "Mangaluru", "Udupi", "Shimoga", "Davangere"
];

/**
 * Show filtered autocomplete suggestions.
 * @param {string} query - Current input text
 * @param {HTMLElement} input - The search input element
 * @param {HTMLElement} suggestionList - The suggestions container element
 */
function showSuggestions(query, input, suggestionList) {
    if (query.length < 2) {
        suggestionList.style.display = 'none';
        suggestionList.innerHTML = '';
        return;
    }

    const matches = CONSTITUENCIES.filter(function (name) {
        return name.toLowerCase().includes(query.toLowerCase());
    });

    if (matches.length === 0) {
        suggestionList.style.display = 'none';
        suggestionList.innerHTML = '';
        return;
    }

    suggestionList.innerHTML = '';

    matches.forEach(function (name) {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.textContent = name;

        item.addEventListener('click', function () {
            input.value = name;
            suggestionList.style.display = 'none';
            suggestionList.innerHTML = '';
            triggerSearch(input);
        });

        suggestionList.appendChild(item);
    });

    suggestionList.style.display = 'block';
}

/**
 * Show an error message on the input field.
 * @param {HTMLElement} inputElement - The input element to show error on
 * @param {string} message - Error message to display
 */
function showError(inputElement, message) {
    // Add red border
    inputElement.style.borderColor = '#ef4444';
    inputElement.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.2)';

    // Check if error span already exists
    let errorSpan = inputElement.parentElement.querySelector('.search-error-msg');

    if (!errorSpan) {
        errorSpan = document.createElement('span');
        errorSpan.className = 'search-error-msg';
        errorSpan.style.cssText =
            'display: block; color: #ef4444; font-size: 0.8rem; margin-top: 0.5rem; ' +
            'font-weight: 500; text-align: center;';
        inputElement.parentElement.appendChild(errorSpan);
    }

    errorSpan.textContent = message;

    // Remove after 3 seconds
    setTimeout(function () {
        inputElement.style.borderColor = '';
        inputElement.style.boxShadow = '';
        if (errorSpan && errorSpan.parentElement) {
            errorSpan.parentElement.removeChild(errorSpan);
        }
    }, 3000);
}

/**
 * Trigger the search action with the current input value.
 * @param {HTMLElement} input - The search input element
 */
function triggerSearch(input) {
    const query = input.value.trim();

    if (query.length < 3) {
        showError(input, 'Type at least 3 characters');
        return;
    }

    // Store query and clear previous data
    GeoLocation.storeSearchQuery(query);
    sessionStorage.removeItem('geocivic_lat');
    sessionStorage.removeItem('geocivic_lng');
    sessionStorage.removeItem('geocivic_result');

    window.location.href = 'map.html';
}

/**
 * Initialize search functionality on a page.
 * @param {string} inputId - ID of the search input element
 * @param {string} buttonId - ID of the search button element
 * @param {string} suggestionListId - ID of the suggestions container element
 */
function initSearch(inputId, buttonId, suggestionListId) {
    const input = document.getElementById(inputId);
    const button = document.getElementById(buttonId);
    const suggestionList = document.getElementById(suggestionListId);

    if (!input || !button) {
        console.warn('Search: input or button not found');
        return;
    }

    // Debounce timer
    let debounceTimer = null;

    // Button click handler
    button.addEventListener('click', function () {
        triggerSearch(input);
    });

    // Enter key handler
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (suggestionList) {
                suggestionList.style.display = 'none';
            }
            triggerSearch(input);
        }
    });

    // Debounced input listener for autocomplete
    if (suggestionList) {
        input.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function () {
                showSuggestions(input.value.trim(), input, suggestionList);
            }, 300);
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', function (e) {
            if (!input.contains(e.target) && !suggestionList.contains(e.target)) {
                suggestionList.style.display = 'none';
            }
        });
    }
}

// Export as window global
window.Search = { initSearch };
