from fastapi.routing import APIRoute

from app.main import app


def list_routes():
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({"path": route.path, "name": route.name, "methods": sorted(route.methods)})

    # Filter for enterprise routes
    enterprise_routes = [r for r in routes if "/enterprise" in r["path"]]

    print(f"Total Enterprise Routes: {len(enterprise_routes)}")
    for r in enterprise_routes:
        print(f"{r['methods']} {r['path']} -> {r['name']}")


if __name__ == "__main__":
    list_routes()
