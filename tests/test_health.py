import pytest


class TestHealthEndpoint:
    """Tests for the health-check endpoint."""

    def test_health_check_returns_200(self, client):
        """GET /health should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_has_status_field(self, client):
        """GET /health response body should contain a status field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data

    def test_health_check_status_is_ok(self, client):
        """GET /health should report status as ok or healthy."""
        response = client.get("/health")
        data = response.json()
        assert data.get("status", "").lower() in ("ok", "healthy", "up", "running")

    def test_health_check_content_type_is_json(self, client):
        """GET /health should return JSON content type."""
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")
