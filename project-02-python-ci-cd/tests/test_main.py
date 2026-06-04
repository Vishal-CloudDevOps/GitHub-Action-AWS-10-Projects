"""
Comprehensive test suite for the Flask API.
Includes positive (happy path) and negative (error/edge case) tests.
"""

import pytest
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ─────────────────────────────────────────────────
# GET /
# ─────────────────────────────────────────────────
class TestIndex:
    def test_returns_200_ok(self, client):
        """✅ Root endpoint returns 200."""
        res = client.get("/")
        assert res.status_code == 200

    def test_returns_status_ok(self, client):
        """✅ Body contains status ok."""
        data = client.get("/").get_json()
        assert data["status"] == "ok"

    def test_wrong_method_returns_405(self, client):
        """❌ POST to root returns 405."""
        res = client.post("/")
        assert res.status_code == 405


# ─────────────────────────────────────────────────
# GET /health
# ─────────────────────────────────────────────────
class TestHealth:
    def test_returns_healthy(self, client):
        """✅ Health check returns healthy."""
        data = client.get("/health").get_json()
        assert data["status"] == "healthy"


# ─────────────────────────────────────────────────
# GET /api/fibonacci/<n>
# ─────────────────────────────────────────────────
class TestFibonacci:
    @pytest.mark.parametrize(
        "n,expected",
        [
            (0, 0),
            (1, 1),
            (2, 1),
            (3, 2),
            (5, 5),
            (10, 55),
            (20, 6765),
        ],
    )
    def test_correct_values(self, client, n, expected):
        """✅ Returns correct Fibonacci numbers."""
        data = client.get(f"/api/fibonacci/{n}").get_json()
        assert data["result"] == expected

    def test_returns_400_for_negative(self, client):
        """❌ Negative numbers return 400."""
        res = client.get("/api/fibonacci/-1")
        assert res.status_code == 400
        assert "non-negative" in res.get_json()["error"]

    def test_returns_400_for_too_large(self, client):
        """❌ n > 100 returns 400."""
        res = client.get("/api/fibonacci/101")
        assert res.status_code == 400

    def test_returns_400_for_string(self, client):
        """❌ String path param returns 404 (Flask type coercion)."""
        res = client.get("/api/fibonacci/abc")
        assert res.status_code == 404


# ─────────────────────────────────────────────────
# POST /api/palindrome
# ─────────────────────────────────────────────────
class TestPalindrome:
    def test_racecar_is_palindrome(self, client):
        """✅ 'racecar' is a palindrome."""
        data = client.post("/api/palindrome", json={"word": "racecar"}).get_json()
        assert data["is_palindrome"] is True

    def test_hello_is_not_palindrome(self, client):
        """✅ 'hello' is not a palindrome."""
        data = client.post("/api/palindrome", json={"word": "hello"}).get_json()
        assert data["is_palindrome"] is False

    def test_case_insensitive(self, client):
        """✅ Check is case-insensitive."""
        data = client.post("/api/palindrome", json={"word": "Racecar"}).get_json()
        assert data["is_palindrome"] is True

    def test_single_char_is_palindrome(self, client):
        """✅ Single character is always a palindrome."""
        data = client.post("/api/palindrome", json={"word": "a"}).get_json()
        assert data["is_palindrome"] is True

    def test_missing_word_returns_400(self, client):
        """❌ Missing 'word' field returns 400."""
        res = client.post("/api/palindrome", json={})
        assert res.status_code == 400

    def test_empty_word_returns_400(self, client):
        """❌ Empty word returns 400."""
        res = client.post("/api/palindrome", json={"word": "   "})
        assert res.status_code == 400

    def test_non_string_returns_400(self, client):
        """❌ Non-string word returns 400."""
        res = client.post("/api/palindrome", json={"word": 123})
        assert res.status_code == 400

    def test_empty_body_returns_400(self, client):
        """❌ No body returns 400."""
        res = client.post("/api/palindrome")
        assert res.status_code == 400


# ─────────────────────────────────────────────────
# POST /api/stats
# ─────────────────────────────────────────────────
class TestStats:
    def test_correct_stats(self, client):
        """✅ Returns correct statistical values."""
        data = client.post("/api/stats", json={"numbers": [1, 2, 3, 4, 5]}).get_json()
        assert data["count"] == 5
        assert data["sum"] == 15
        assert data["mean"] == 3.0
        assert data["min"] == 1
        assert data["max"] == 5

    def test_single_element(self, client):
        """✅ Works with a single element."""
        data = client.post("/api/stats", json={"numbers": [42]}).get_json()
        assert data["count"] == 1
        assert data["mean"] == 42

    def test_floats(self, client):
        """✅ Works with float values."""
        data = client.post("/api/stats", json={"numbers": [1.5, 2.5, 3.0]}).get_json()
        assert data["sum"] == pytest.approx(7.0)

    def test_missing_numbers_returns_400(self, client):
        """❌ Missing 'numbers' field returns 400."""
        res = client.post("/api/stats", json={})
        assert res.status_code == 400

    def test_empty_list_returns_400(self, client):
        """❌ Empty list returns 400."""
        res = client.post("/api/stats", json={"numbers": []})
        assert res.status_code == 400

    def test_non_list_returns_400(self, client):
        """❌ Non-list value returns 400."""
        res = client.post("/api/stats", json={"numbers": "not a list"})
        assert res.status_code == 400

    def test_non_numeric_elements_return_400(self, client):
        """❌ List with non-numeric elements returns 400."""
        res = client.post("/api/stats", json={"numbers": [1, "two", 3]})
        assert res.status_code == 400
