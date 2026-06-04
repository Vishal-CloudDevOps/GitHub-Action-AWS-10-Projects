"""
project-02-python-ci-cd
Flask REST API demonstrating Python CI with matrix builds and artifact upload.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def index():
    """Root endpoint."""
    return jsonify(
        {
            "message": "Hello from Project 02 — Python CI/CD!",
            "status": "ok",
            "version": "1.0.0",
        }
    )


@app.route("/health")
def health():
    """Health check endpoint used by load balancers."""
    return jsonify({"status": "healthy"})


@app.route("/api/fibonacci/<int:n>")
def fibonacci(n):
    """Return the nth Fibonacci number."""
    if n < 0:
        return jsonify({"error": "n must be a non-negative integer"}), 400
    if n > 100:
        return jsonify({"error": "n must be 100 or less"}), 400

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return jsonify({"n": n, "result": a})


@app.route("/api/palindrome", methods=["POST"])
def palindrome():
    """Check whether a given word is a palindrome."""
    data = request.get_json()
    if not data or "word" not in data:
        return jsonify({"error": "'word' field is required"}), 400

    word = data["word"]
    if not isinstance(word, str):
        return jsonify({"error": "'word' must be a string"}), 400
    if not word.strip():
        return jsonify({"error": "'word' cannot be empty"}), 400

    cleaned = word.lower().replace(" ", "")
    is_palindrome = cleaned == cleaned[::-1]
    return jsonify({"word": word, "is_palindrome": is_palindrome})


@app.route("/api/stats", methods=["POST"])
def stats():
    """Return basic statistics for a list of numbers."""
    data = request.get_json()
    if not data or "numbers" not in data:
        return jsonify({"error": "'numbers' field is required"}), 400

    numbers = data["numbers"]
    if not isinstance(numbers, list):
        return jsonify({"error": "'numbers' must be a list"}), 400
    if not numbers:
        return jsonify({"error": "'numbers' cannot be empty"}), 400
    if not all(isinstance(n, (int, float)) for n in numbers):
        return jsonify({"error": "All values must be numbers"}), 400

    return jsonify(
        {
            "count": len(numbers),
            "sum": sum(numbers),
            "mean": sum(numbers) / len(numbers),
            "min": min(numbers),
            "max": max(numbers),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
