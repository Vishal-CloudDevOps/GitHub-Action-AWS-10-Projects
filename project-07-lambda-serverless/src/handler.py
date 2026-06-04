"""
project-07-lambda-serverless
AWS Lambda handler — Python REST API via API Gateway
Deployed with AWS SAM (Serverless Application Model)
"""

import json
import logging
import os

# Configure structured logging — CloudWatch picks this up automatically
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Main Lambda entry point.
    Receives API Gateway proxy events and routes them to handlers.

    Args:
        event: API Gateway proxy event dict
        context: Lambda context object (request ID, timeout, etc.)

    Returns:
        API Gateway proxy response dict
    """
    logger.info("Event received: %s", json.dumps(event))

    http_method = event.get("httpMethod", "")
    path = event.get("path", "/")

    # Route the request
    try:
        if path == "/" and http_method == "GET":
            return handle_root(event, context)
        elif path == "/health" and http_method == "GET":
            return handle_health(event, context)
        elif path == "/api/greet" and http_method == "GET":
            return handle_greet(event, context)
        elif path == "/api/calculate" and http_method == "POST":
            return handle_calculate(event, context)
        else:
            return response(404, {"error": f"Route {http_method} {path} not found"})

    except Exception as e:
        logger.error("Unhandled exception: %s", str(e), exc_info=True)
        return response(500, {"error": "Internal server error"})


def handle_root(event, context):
    """GET / — Root endpoint."""
    return response(200, {
        "message": "Project 07 — Lambda Serverless API",
        "version": os.environ.get("APP_VERSION", "1.0.0"),
        "stage": os.environ.get("STAGE", "dev"),
        "request_id": context.aws_request_id if context else "local",
    })


def handle_health(event, context):
    """GET /health — Health check for API Gateway."""
    return response(200, {"status": "healthy"})


def handle_greet(event, context):
    """GET /api/greet?name=Alice — Greet endpoint."""
    params = event.get("queryStringParameters") or {}
    name = params.get("name", "").strip()

    if not name:
        return response(400, {"error": "Query parameter 'name' is required"})
    if len(name) > 50:
        return response(400, {"error": "Name must be 50 characters or fewer"})

    return response(200, {"message": f"Hello, {name}! Welcome to serverless."})


def handle_calculate(event, context):
    """POST /api/calculate — Calculator endpoint."""
    body_str = event.get("body") or "{}"

    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        return response(400, {"error": "Invalid JSON body"})

    a = body.get("a")
    b = body.get("b")
    operation = body.get("operation", "add")

    # Validation
    if a is None or b is None:
        return response(400, {"error": "Fields 'a' and 'b' are required"})
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return response(400, {"error": "Fields 'a' and 'b' must be numbers"})
    if operation not in ("add", "subtract", "multiply", "divide"):
        return response(400, {"error": "Operation must be add, subtract, multiply, or divide"})
    if operation == "divide" and b == 0:
        return response(400, {"error": "Division by zero"})

    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b,
    }

    return response(200, {
        "a": a,
        "b": b,
        "operation": operation,
        "result": ops[operation],
    })


def response(status_code: int, body: dict) -> dict:
    """Helper: build API Gateway proxy response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
