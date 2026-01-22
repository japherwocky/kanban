#!/usr/bin/env python
"""
Test script to verify FastAPI routes are configured correctly
"""

import sys

sys.path.insert(0, ".")

from main import app

print("=" * 60)
print("Registered FastAPI Routes:")
print("=" * 60)

for route in app.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        methods = ", ".join(sorted(route.methods))
        print(f"{methods:15} {route.path}")
    elif hasattr(route, "path"):
        print(f"{'STATIC':15} {route.path}")

print("\n" + "=" * 60)
print("Key Routes to Verify:")
print("=" * 60)

key_routes = {
    "/docs": "Frontend documentation",
    "/api/docs": "FastAPI Swagger UI",
    "/api/redoc": "FastAPI ReDoc",
    "/api/openapi.json": "FastAPI OpenAPI schema",
    "/": "Root / Landing",
    "/api/*": "API endpoints",
    "/content/*": "Markdown content files",
}

all_paths = [route.path for route in app.routes if hasattr(route, "path")]

for path, description in key_routes.items():
    if path == "/api/*":
        # Check for any /api routes
        api_routes = [p for p in all_paths if p.startswith("/api")]
        if api_routes:
            print(f"✓ {path:20} - {description}")
            print(f"  Examples: {', '.join(api_routes[:3])}...")
        else:
            print(f"✗ {path:20} - MISSING!")
    elif path == "/content/*":
        # Check for /content route
        if "/content" in all_paths:
            print(f"✓ {path:20} - {description}")
        else:
            print(f"✗ {path:20} - MISSING!")
    else:
        if path in all_paths:
            print(f"✓ {path:20} - {description}")
        else:
            print(f"✗ {path:20} - MISSING!")

print("\n" + "=" * 60)
