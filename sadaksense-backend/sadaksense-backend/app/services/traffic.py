"""Traffic-aware speed intervals from the Google Routes API."""
import httpx
from app.config import settings

URL = "https://routes.googleapis.com/directions/v2:computeRoutes"


async def speed_intervals(origin, dest):
    body = {
        "origin": {"location": {"latLng": {"latitude": origin[0], "longitude": origin[1]}}},
        "destination": {"location": {"latLng": {"latitude": dest[0], "longitude": dest[1]}}},
        "travelMode": "DRIVE", "routingPreference": "TRAFFIC_AWARE",
        "extraComputations": ["TRAFFIC_ON_POLYLINE"],
    }
    headers = {"X-Goog-Api-Key": settings.routes_api_key,
               "X-Goog-FieldMask": "routes.polyline,routes.travelAdvisory.speedReadingIntervals"}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(URL, json=body, headers=headers)
        r.raise_for_status()
    route = r.json()["routes"][0]
    return route.get("travelAdvisory", {}).get("speedReadingIntervals", [])   # NORMAL | SLOW | TRAFFIC_JAM
