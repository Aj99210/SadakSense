import math

EARTH_R = 6_371_000.0


def haversine_m(lat1, lng1, lat2, lng2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_R * math.asin(math.sqrt(a))


def recency_weighted_mean(values, ages_hours, half_life_h: float = 72.0):
    """Segment RQI = recency-weighted blend of its detections (newer counts more)."""
    if not values:
        return None
    w = [0.5 ** (a / half_life_h) for a in ages_hours]
    return sum(v * x for v, x in zip(values, w)) / sum(w)
