"""
Comprehensive tests for the Lambda handler.
Tests use mock API Gateway proxy events — no AWS needed.
"""

import json
import pytest
from unittest.mock import MagicMock
from src.handler import lambda_handler, response


# ─── Helpers ─────────────────────────────────────────────────

def make_event(method="GET", path="/", query_params=None, body=None):
    """Build a minimal API Gateway proxy event."""
    return {
        "httpMethod": method,
        "path": path,
        "queryStringParameters": query_params,
        "body": json.dumps(body) if body else None,
        "headers": {},
    }


def mock_context():
    ctx = MagicMock()
    ctx.aws_request_id = "test-request-id-123"
    return ctx


# ─── GET / ───────────────────────────────────────────────────

class TestRoot:
    def test_returns_200(self):
        """✅ Root returns 200."""
        res = lambda_handler(make_event("GET", "/"), mock_context())
        assert res["statusCode"] == 200

    def test_body_has_message(self):
        """✅ Body contains message field."""
        res = lambda_handler(make_event("GET", "/"), mock_context())
        body = json.loads(res["body"])
        assert "message" in body
        assert "Lambda" in body["message"]

    def test_wrong_method_returns_404(self):
        """❌ POST / returns 404."""
        res = lambda_handler(make_event("POST", "/"), mock_context())
        assert res["statusCode"] == 404


# ─── GET /health ─────────────────────────────────────────────

class TestHealth:
    def test_returns_healthy(self):
        """✅ Health check returns healthy."""
        res = lambda_handler(make_event("GET", "/health"), mock_context())
        assert res["statusCode"] == 200
        body = json.loads(res["body"])
        assert body["status"] == "healthy"

    def test_post_health_returns_404(self):
        """❌ POST /health returns 404."""
        res = lambda_handler(make_event("POST", "/health"), mock_context())
        assert res["statusCode"] == 404


# ─── GET /api/greet ──────────────────────────────────────────

class TestGreet:
    def test_greets_valid_name(self):
        """✅ Returns greeting for valid name."""
        res = lambda_handler(make_event("GET", "/api/greet", {"name": "Alice"}), mock_context())
        assert res["statusCode"] == 200
        body = json.loads(res["body"])
        assert "Alice" in body["message"]

    def test_trims_whitespace_name(self):
        """✅ Trims whitespace from name."""
        res = lambda_handler(make_event("GET", "/api/greet", {"name": "  Bob  "}), mock_context())
        assert res["statusCode"] == 200

    def test_missing_name_returns_400(self):
        """❌ Missing name returns 400."""
        res = lambda_handler(make_event("GET", "/api/greet", {}), mock_context())
        assert res["statusCode"] == 400
        body = json.loads(res["body"])
        assert "name" in body["error"].lower()

    def test_empty_name_returns_400(self):
        """❌ Empty name returns 400."""
        res = lambda_handler(make_event("GET", "/api/greet", {"name": "   "}), mock_context())
        assert res["statusCode"] == 400

    def test_name_too_long_returns_400(self):
        """❌ Name >50 chars returns 400."""
        res = lambda_handler(make_event("GET", "/api/greet", {"name": "A" * 51}), mock_context())
        assert res["statusCode"] == 400

    def test_no_query_params_returns_400(self):
        """❌ No query params at all returns 400."""
        res = lambda_handler(make_event("GET", "/api/greet", None), mock_context())
        assert res["statusCode"] == 400


# ─── POST /api/calculate ─────────────────────────────────────

class TestCalculate:
    @pytest.mark.parametrize("op,a,b,expected", [
        ("add", 5, 3, 8),
        ("subtract", 10, 4, 6),
        ("multiply", 3, 7, 21),
        ("divide", 15, 3, 5.0),
    ])
    def test_all_operations(self, op, a, b, expected):
        """✅ All four operations return correct results."""
        res = lambda_handler(make_event("POST", "/api/calculate", body={"a": a, "b": b, "operation": op}), mock_context())
        assert res["statusCode"] == 200
        body = json.loads(res["body"])
        assert body["result"] == expected

    def test_default_operation_is_add(self):
        """✅ Default operation is add."""
        res = lambda_handler(make_event("POST", "/api/calculate", body={"a": 2, "b": 3}), mock_context())
        assert res["statusCode"] == 200
        assert json.loads(res["body"])["result"] == 5

    def test_float_inputs(self):
        """✅ Handles float inputs."""
        res = lambda_handler(make_event("POST", "/api/calculate", body={"a": 1.5, "b": 2.5, "operation": "add"}), mock_context())
        assert res["statusCode"] == 200
        assert json.loads(res["body"])["result"] == pytest.approx(4.0)

    def test_missing_a_returns_400(self):
        """❌ Missing 'a' returns 400."""
        res = lambda_handler(make_event("POST", "/api/calculate", body={"b": 3}), mock_context())
        assert res["statusCode"] == 400

    def test_missing_b_returns_400(self):
        """❌ Missing 'b' returns 400."""
        res = lambda_handler(make_event("POST", "/api/calculate", body={"a": 3}), mock_context())
        assert res["statusCode"] == 400

    def test_string_inputs_return_400(self):
        """❌ String inputs return 400."""
        res = lambda_handler(make_event("POST", "/api/calculate", body={"a": "x", "b": 3}), mock_context())
        assert res["statusCode"] == 400

    def test_divide_by_zero_returns_400(self):
        """❌ Division by zero returns 400."""
        res = lambda_handler(make_event("POST", "/api/calculate", body={"a": 10, "b": 0, "operation": "divide"}), mock_context())
        assert res["statusCode"] == 400
        assert "zero" in json.loads(res["body"])["error"].lower()

    def test_invalid_operation_returns_400(self):
        """❌ Unknown operation returns 400."""
        res = lambda_handler(make_event("POST", "/api/calculate", body={"a": 1, "b": 2, "operation": "modulo"}), mock_context())
        assert res["statusCode"] == 400

    def test_invalid_json_body_returns_400(self):
        """❌ Invalid JSON body returns 400."""
        event = make_event("POST", "/api/calculate")
        event["body"] = "not-json"
        res = lambda_handler(event, mock_context())
        assert res["statusCode"] == 400

    def test_unknown_route_returns_404(self):
        """❌ Unknown path returns 404."""
        res = lambda_handler(make_event("GET", "/api/unknown"), mock_context())
        assert res["statusCode"] == 404


# ─── Response helper ─────────────────────────────────────────

class TestResponseHelper:
    def test_response_structure(self):
        """✅ response() returns correct structure."""
        res = response(200, {"key": "value"})
        assert res["statusCode"] == 200
        assert res["headers"]["Content-Type"] == "application/json"
        assert json.loads(res["body"]) == {"key": "value"}

    def test_cors_header_present(self):
        """✅ CORS header is present."""
        res = response(200, {})
        assert res["headers"]["Access-Control-Allow-Origin"] == "*"
