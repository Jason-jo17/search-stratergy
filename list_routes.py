from app.main import app
import json

def list_routes():
    print("Listing Routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ",".join(route.methods)
            print(f"{methods} {route.path}")
        else:
            print(f"Route: {route.path}")

if __name__ == "__main__":
    list_routes()
