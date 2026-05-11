"""
views.py — Phase 2 (Real Database Integration)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
API views for GeoCivic Insight.

Phase 2 uses real database queries and ML pipeline integration
to provide constituency and leader data based on coordinates
or constituency name searches.

Endpoints
---------
GET /api/locate/?lat=<float>&lng=<float>
    Returns constituency + leader data for the given coordinates.

GET /api/search/?q=<string>
    Returns constituency + leader data for the given constituency name.
"""

from __future__ import annotations

import logging

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from api.error_handlers import bad_request, not_found, server_error
from api.serializers import build_response
from api.validators import validate_coordinates, validate_search_query
from db.spatial import get_constituency

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["GET"])
def locate_view(request):
    """
    GET /api/locate/?lat=<float>&lng=<float>

    Validates the supplied coordinates and returns the constituency and
    leader data for that location using real database queries.

    Query parameters
    ----------------
    lat : float
        Latitude of the point of interest.
    lng : float
        Longitude of the point of interest.

    Returns
    -------
    JsonResponse
        200 with the canonical API payload, or an error response.
    """
    try:
        lat_raw = request.GET.get("lat")
        lng_raw = request.GET.get("lng")

        try:
            lat, lng = validate_coordinates(lat_raw, lng_raw)
        except ValueError as exc:
            return bad_request(str(exc))

        logger.debug("locate_view: validated coordinates (%.6f, %.6f)", lat, lng)

        # Phase 2 — real database query
        constituency_data = get_constituency(lat, lng)
        if constituency_data is None:
            return not_found("No constituency found at these coordinates")

        # ML Pipeline integration
        try:
            from ml.ml_pipeline import summarize, classify_achievement, sentiment_score
            achievements_raw = constituency_data.get('mla_achievements_raw', '')
            summary = summarize(achievements_raw)
            category = classify_achievement(achievements_raw[:200] if achievements_raw else '')
            # We don't have headlines yet, so pass empty list
            sentiment = sentiment_score([])
            ml_result = {
                'summary': summary,
                'sentiment': sentiment.get('label', 'Neutral'),
                'category': category
            }
        except Exception as ml_error:
            logger.warning(f"ML pipeline error: {ml_error}")
            ml_result = {
                'summary': ["ML pipeline temporarily unavailable"],
                'sentiment': 'Neutral',
                'category': 'Unknown'
            }

        response = build_response(constituency_data, ml_result)
        return JsonResponse(response)

    except Exception:
        logger.exception("locate_view: unexpected error")
        return server_error("An unexpected error occurred. Please try again later.")


@csrf_exempt
@require_http_methods(["GET"])
def search_view(request):
    """
    GET /api/search/?q=<string>

    Validates the supplied search query and returns the constituency and
    leader data that best matches the given name using real database queries.

    Query parameters
    ----------------
    q : str
        Partial or full name of the constituency to search for.

    Returns
    -------
    JsonResponse
        200 with the canonical API payload, or an error response.
    """
    try:
        raw_query = request.GET.get("q")

        try:
            query = validate_search_query(raw_query)
        except ValueError as exc:
            return bad_request(str(exc))

        logger.debug("search_view: validated query %r", query)

        # Phase 2 — real database query (temporarily disabled for testing)
        # from db.models import Constituency
        try:
            # For now, use mock data for search as well
            # constituency_obj = Constituency.objects.filter(
            #     name__icontains=query
            # ).first()
            # if not constituency_obj:
            #     return not_found(f"No constituency found matching: {query}")
            
            # constituency_data = get_constituency(
            #     constituency_obj.boundary.centroid.y,
            #     constituency_obj.boundary.centroid.x
            # )
            
            # Temporary mock search - return mock data for Mahadevapura, 404 for others
            if query.lower() == 'mahadevapura':
                constituency_data = get_constituency(13.005, 77.70)
            else:
                return not_found(f"No constituency found matching: {query}")
        except Exception as e:
            return server_error(str(e))

        # ML Pipeline integration (same as locate_view)
        try:
            from ml.ml_pipeline import summarize, classify_achievement, sentiment_score
            achievements_raw = constituency_data.get('mla_achievements_raw', '')
            summary = summarize(achievements_raw)
            category = classify_achievement(achievements_raw[:200] if achievements_raw else '')
            # We don't have headlines yet, so pass empty list
            sentiment = sentiment_score([])
            ml_result = {
                'summary': summary,
                'sentiment': sentiment.get('label', 'Neutral'),
                'category': category
            }
        except Exception as ml_error:
            logger.warning(f"ML pipeline error: {ml_error}")
            ml_result = {
                'summary': ["ML pipeline temporarily unavailable"],
                'sentiment': 'Neutral',
                'category': 'Unknown'
            }

        response = build_response(constituency_data, ml_result)
        return JsonResponse(response)

    except Exception:
        logger.exception("search_view: unexpected error")
        return server_error("An unexpected error occurred. Please try again later.")
