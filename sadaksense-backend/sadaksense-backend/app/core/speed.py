"""Achievable-speed model.

Baseline: speed = limit * g(RQI). A calibrated gradient-boosted model
(trained on probe speeds from the routing API) overrides this when available.
"""

ROAD_LIMITS = {"National Highway": 80, "State Highway": 70, "Urban Arterial Road": 50,
               "Municipal Road": 40, "Colony / Internal Road": 25}


def baseline_speed(rqi: float, road_type: str = "Municipal Road") -> float:
    limit = ROAD_LIMITS.get(road_type, 50)
    factor = 0.35 + 0.65 * (rqi / 10.0) ** 1.4     # falls steeply below RQI 5
    return round(limit * factor, 1)


def congestion_level(speed_kmh: float, limit: float) -> str:
    ratio = speed_kmh / max(limit, 1)
    return "Low" if ratio > 0.8 else "Moderate" if ratio > 0.55 else "High"
