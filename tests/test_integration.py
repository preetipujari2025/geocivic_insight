"""
Integration tests for Django backend API.

Tests the full flow of API endpoints with mock data.
Compatible with current GIS-disabled Windows setup.
"""

import os
import django

# Configure Django settings before importing Django components
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geocivic.settings')
django.setup()

import json
import pytest
from django.test import Client
from django.urls import reverse


@pytest.fixture
def client():
    """Create test client for API requests."""
    return Client()


@pytest.fixture
def valid_coordinates():
    """Valid coordinates for testing."""
    return {"lat": "13.005", "lng": "77.70"}


@pytest.fixture
def invalid_coordinates():
    """Invalid coordinates for testing."""
    return {"lat": "invalid", "lng": "77.70"}


class TestLocateEndpoint:
    """Test cases for /api/locate/ endpoint."""

    def test_full_locate_flow(self, client, valid_coordinates):
        """Test complete locate endpoint flow with valid coordinates."""
        response = client.get('/api/locate/', valid_coordinates)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        
        data = response.json()
        assert 'constituency' in data
        assert 'ml_analysis' in data
        
        constituency = data['constituency']
        assert 'name' in constituency
        assert 'district' in constituency
        assert constituency['name'] == "Mahadevapura"
        assert constituency['district'] == "Bangalore Urban"

    def test_locate_returns_cors_friendly_json(self, client, valid_coordinates):
        """Test that locate endpoint returns CORS-friendly JSON response."""
        response = client.get('/api/locate/', valid_coordinates)
        
        # Check for CORS-friendly headers
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        
        # Verify JSON structure
        data = response.json()
        assert isinstance(data, dict)
        assert 'constituency' in data
        assert 'ml_analysis' in data

    def test_invalid_coordinates_return_400(self, client, invalid_coordinates):
        """Test that invalid coordinates return 400 error."""
        response = client.get('/api/locate/', invalid_coordinates)
        
        assert response.status_code == 400
        assert response['Content-Type'] == 'application/json'
        
        data = response.json()
        assert 'error' in data

    def test_missing_coordinates_return_400(self, client):
        """Test that missing coordinates return 400 error."""
        response = client.get('/api/locate/')
        
        assert response.status_code == 400
        assert response['Content-Type'] == 'application/json'
        
        data = response.json()
        assert 'error' in data

    def test_locate_with_only_lat_parameter(self, client):
        """Test locate endpoint with only latitude parameter."""
        response = client.get('/api/locate/', {'lat': '13.005'})
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data

    def test_locate_with_only_lng_parameter(self, client):
        """Test locate endpoint with only longitude parameter."""
        response = client.get('/api/locate/', {'lng': '77.70'})
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data


class TestSearchEndpoint:
    """Test cases for /api/search/ endpoint."""

    def test_full_search_flow(self, client):
        """Test complete search endpoint flow with valid query."""
        response = client.get('/api/search/', {'q': 'Mahadevapura'})
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        
        data = response.json()
        assert 'constituency' in data
        assert 'ml_analysis' in data
        
        constituency = data['constituency']
        assert 'name' in constituency
        assert 'district' in constituency

    def test_search_returns_cors_friendly_json(self, client):
        """Test that search endpoint returns CORS-friendly JSON response."""
        response = client.get('/api/search/', {'q': 'Mahadevapura'})
        
        # Check for CORS-friendly headers
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        
        # Verify JSON structure
        data = response.json()
        assert isinstance(data, dict)
        assert 'constituency' in data
        assert 'ml_analysis' in data

    def test_missing_search_query_return_400(self, client):
        """Test that missing search query returns 400 error."""
        response = client.get('/api/search/')
        
        assert response.status_code == 400
        assert response['Content-Type'] == 'application/json'
        
        data = response.json()
        assert 'error' in data

    def test_empty_search_query_return_400(self, client):
        """Test that empty search query returns 400 error."""
        response = client.get('/api/search/', {'q': ''})
        
        assert response.status_code == 400
        assert response['Content-Type'] == 'application/json'
        
        data = response.json()
        assert 'error' in data

    def test_search_not_found_return_404(self, client):
        """Test that non-existent constituency returns 404 error."""
        response = client.get('/api/search/', {'q': 'NonExistentConstituency'})
        
        assert response.status_code == 404
        assert response['Content-Type'] == 'application/json'
        
        data = response.json()
        assert 'error' in data


class TestAPIResponseStructure:
    """Test API response structure consistency."""

    def test_locate_response_structure(self, client, valid_coordinates):
        """Test locate endpoint response structure."""
        response = client.get('/api/locate/', valid_coordinates)
        data = response.json()
        
        # Check top-level structure
        assert isinstance(data, dict)
        assert 'constituency' in data
        assert 'ml_analysis' in data
        
        # Check constituency structure
        constituency = data['constituency']
        assert isinstance(constituency, dict)
        assert 'name' in constituency
        assert 'district' in constituency
        assert 'constituency_id' in constituency
        
        # Check ML analysis structure
        ml_analysis = data['ml_analysis']
        assert isinstance(ml_analysis, dict)
        assert 'summary' in ml_analysis
        assert 'achievements' in ml_analysis

    def test_search_response_structure(self, client):
        """Test search endpoint response structure."""
        response = client.get('/api/search/', {'q': 'Mahadevapura'})
        data = response.json()
        
        # Check top-level structure
        assert isinstance(data, dict)
        assert 'constituency' in data
        assert 'ml_analysis' in data
        
        # Check constituency structure
        constituency = data['constituency']
        assert isinstance(constituency, dict)
        assert 'name' in constituency
        assert 'district' in constituency
        assert 'constituency_id' in constituency
        
        # Check ML analysis structure
        ml_analysis = data['ml_analysis']
        assert isinstance(ml_analysis, dict)
        assert 'summary' in ml_analysis
        assert 'achievements' in ml_analysis


class TestAPIErrorHandling:
    """Test API error handling."""

    def test_invalid_http_method_locate(self, client):
        """Test that POST to locate endpoint returns error."""
        response = client.post('/api/locate/', {'lat': '13.005', 'lng': '77.70'})
        
        # Should return 405 Method Not Allowed or 404 depending on implementation
        assert response.status_code in [405, 404]

    def test_invalid_http_method_search(self, client):
        """Test that POST to search endpoint returns error."""
        response = client.post('/api/search/', {'q': 'Mahadevapura'})
        
        # Should return 405 Method Not Allowed or 404 depending on implementation
        assert response.status_code in [405, 404]

    def test_edge_case_coordinates(self, client):
        """Test edge case coordinates."""
        # Test with extreme valid coordinates
        edge_cases = [
            {'lat': '90.0', 'lng': '180.0'},   # North pole, international date line
            {'lat': '-90.0', 'lng': '-180.0'}, # South pole, international date line
            {'lat': '0.0', 'lng': '0.0'},      # Equator, prime meridian
        ]
        
        for coords in edge_cases:
            response = client.get('/api/locate/', coords)
            # Should return 200 (mock data) or 404 (real GIS)
            assert response.status_code in [200, 404]