"""
serializers.py
~~~~~~~~~~~~~~
Pure Python response-shaping utilities for the GeoCivic Insight API.

No DRF / Django dependency — functions accept plain dicts and return
plain dicts, making them trivially unit-testable.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Sentinel defaults
# ---------------------------------------------------------------------------
_UNKNOWN = "Unknown"
_SENTIMENT_DEFAULT = "Neutral"
_SUMMARY_UNAVAILABLE = ["Achievement data not available"]

# Valid sentiment labels (guards against garbage from the ML pipeline)
_VALID_SENTIMENTS = {"Positive", "Neutral", "Negative"}


def build_response(
    constituency_data: dict[str, Any] | None,
    ml_result: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Shape raw data into the canonical GeoCivic Insight API response.

    Parameters
    ----------
    constituency_data : dict or None
        Record returned by ``get_constituency()``.  Expected keys:
        ``name``, ``district``, ``geojson``,
        ``mla_name``, ``mla_party``, ``mla_education``,
        ``mp_name``, ``mp_party``.
        Pass ``None`` when the constituency could not be resolved.
    ml_result : dict or None
        Output from the ML pipeline.  Expected keys:
        ``summary`` (list[str]) and ``sentiment`` (str).
        Pass ``None`` when ML results are unavailable.

    Returns
    -------
    dict
        Either a structured constituency/leader payload or an error dict:

        Success shape::

            {
                "constituency": {"name": ..., "district": ..., "geojson": ...},
                "mla": {
                    "name": ..., "party": ..., "education": ...,
                    "summary": [...], "sentiment": ...
                },
                "mp": {"name": ..., "party": ...}
            }

        Error shape::

            {"error": "Constituency not found", "code": "NOT_FOUND"}
    """
    # --- Guard: constituency not found ------------------------------------
    if constituency_data is None:
        return {"error": "Constituency not found", "code": "NOT_FOUND"}

    # --- Extract constituency fields (with safe fallbacks) ----------------
    name         = constituency_data.get("name", _UNKNOWN)
    district     = constituency_data.get("district", _UNKNOWN)
    geojson      = constituency_data.get("geojson")          # None is valid

    mla_name      = constituency_data.get("mla_name", _UNKNOWN)
    mla_party     = constituency_data.get("mla_party", _UNKNOWN)
    mla_education = constituency_data.get("mla_education", _UNKNOWN)

    mp_name  = constituency_data.get("mp_name", _UNKNOWN)
    mp_party = constituency_data.get("mp_party", _UNKNOWN)

    # --- Extract / sanitise ML results ------------------------------------
    if ml_result is not None:
        summary   = ml_result.get("summary") or _SUMMARY_UNAVAILABLE
        sentiment = ml_result.get("sentiment", _SENTIMENT_DEFAULT)

        # Reject unrecognised sentiment labels rather than leaking them
        if sentiment not in _VALID_SENTIMENTS:
            sentiment = _SENTIMENT_DEFAULT

        # Ensure summary is always a list of strings
        if not isinstance(summary, list):
            summary = [str(summary)]
    else:
        summary   = _SUMMARY_UNAVAILABLE
        sentiment = _SENTIMENT_DEFAULT

    # --- Build and return the canonical response --------------------------
    return {
        "constituency": {
            "name":    name,
            "district": district,
            "geojson": geojson,
            "constituency_id": constituency_data.get("constituency_id") if constituency_data else None,
        },
        "ml_analysis": {
            "summary": summary,
            "sentiment": sentiment,
            "achievements": ml_result.get("category", []) if ml_result else [],
        },
        "mla": {
            "name":      mla_name,
            "party":     mla_party,
            "education": mla_education,
        },
        "mp": {
            "name":  mp_name,
            "party": mp_party,
        },
    }
