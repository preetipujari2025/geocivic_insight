"""
validators.py
~~~~~~~~~~~~~
Pure Python validation utilities for the GeoCivic Insight API.
No Django dependencies — these can be unit-tested in isolation.
"""

# ---------------------------------------------------------------------------
# Karnataka bounding box (approximate)
# ---------------------------------------------------------------------------
_KA_LAT_MIN, _KA_LAT_MAX = 11.5, 18.5
_KA_LNG_MIN, _KA_LNG_MAX = 74.0, 78.5

# ---------------------------------------------------------------------------
# Search query constraints
# ---------------------------------------------------------------------------
_QUERY_MIN_LEN = 3
_QUERY_MAX_LEN = 200


def validate_coordinates(lat, lng):
    """
    Validate and coerce latitude / longitude values.

    Parameters
    ----------
    lat : any
        Latitude value (string, int, float, or None).
    lng : any
        Longitude value (string, int, float, or None).

    Returns
    -------
    tuple[float, float]
        A ``(lat, lng)`` pair as Python floats.

    Raises
    ------
    ValueError
        If either value is missing, non-numeric, or out of the valid
        geographic range.
    """
    # --- Presence check ---------------------------------------------------
    if lat is None or lng is None:
        raise ValueError("lat and lng are required")

    # --- Numeric coercion -------------------------------------------------
    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        raise ValueError("lat and lng must be numbers")

    # --- Range checks -----------------------------------------------------
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"lat out of range: {lat} (must be between -90 and 90)")

    if not (-180.0 <= lng <= 180.0):
        raise ValueError(f"lng out of range: {lng} (must be between -180 and 180)")

    # --- Karnataka bounding-box warning (soft check) ----------------------
    inside_karnataka = (
        _KA_LAT_MIN <= lat <= _KA_LAT_MAX
        and _KA_LNG_MIN <= lng <= _KA_LNG_MAX
    )
    if not inside_karnataka:
        print(
            f"Warning: coordinates ({lat}, {lng}) are outside the Karnataka "
            f"bounding box (lat {_KA_LAT_MIN}–{_KA_LAT_MAX}, "
            f"lng {_KA_LNG_MIN}–{_KA_LNG_MAX})"
        )

    return lat, lng


def validate_search_query(query):
    """
    Validate and normalise a text-based constituency search query.

    Parameters
    ----------
    query : any
        The raw search string supplied by the caller.

    Returns
    -------
    str
        The stripped, validated query string.

    Raises
    ------
    ValueError
        If the query is absent, empty, too short, or too long.
    """
    # --- Presence / type check --------------------------------------------
    if not query or not isinstance(query, str):
        raise ValueError("search query is required")

    query = query.strip()

    if not query:
        raise ValueError("search query is required")

    # --- Length checks ----------------------------------------------------
    if len(query) < _QUERY_MIN_LEN:
        raise ValueError(
            f"search query too short: minimum {_QUERY_MIN_LEN} characters required"
        )

    if len(query) > _QUERY_MAX_LEN:
        raise ValueError(
            f"search query too long: maximum {_QUERY_MAX_LEN} characters allowed"
        )

    return query
