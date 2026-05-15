"""
error_handlers.py
~~~~~~~~~~~~~~~~~
Lightweight JSON error-response helpers for the GeoCivic Insight API.

All public functions return a ``django.http.JsonResponse`` with a
consistent body shape::

    {"error": "<human-readable message>", "code": "<SCREAMING_SNAKE>"}

Usage example::

    from api.error_handlers import bad_request, not_found, server_error

    def my_view(request):
        if something_wrong:
            return bad_request("lat and lng are required")
"""

from __future__ import annotations

from django.http import JsonResponse


def error_response(message: str, code: str, status_code: int = 400) -> JsonResponse:
    """
    Build a JSON error response with a standardised body.

    Parameters
    ----------
    message : str
        A human-readable description of the error, safe to surface to clients.
    code : str
        A machine-readable error code (e.g. ``"NOT_FOUND"``).
    status_code : int, optional
        The HTTP status code to send.  Defaults to ``400``.

    Returns
    -------
    JsonResponse
        A response with ``Content-Type: application/json`` and the given status.
    """
    return JsonResponse(
        {"error": message, "code": code},
        status=status_code,
    )


# ---------------------------------------------------------------------------
# Convenience helpers — prefer these over calling error_response directly
# ---------------------------------------------------------------------------

def bad_request(message: str) -> JsonResponse:
    """Return a 400 Bad Request error response."""
    return error_response(message, "BAD_REQUEST", 400)


def not_found(message: str) -> JsonResponse:
    """Return a 404 Not Found error response."""
    return error_response(message, "NOT_FOUND", 404)


def server_error(message: str) -> JsonResponse:
    """Return a 500 Internal Server Error response."""
    return error_response(message, "SERVER_ERROR", 500)
