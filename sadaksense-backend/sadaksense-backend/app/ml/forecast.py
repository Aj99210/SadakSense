"""Deterioration forecasting.

Rule-based fallback below; replaced by a trained gradient-boosted model with
split-conformal intervals when weights are present. Traffic forecasting
(spatio-temporal GNN) is a separate model trained from probe speeds.
"""
from dataclasses import dataclass


@dataclass
class SegmentCovariates:
    rqi: float
    age_years: float
    aadt: float            # traffic volume
    heavy_share: float
    drainage: float        # 0 poor .. 1 good
    rainfall: float        # scenario 0..1
    days_since_repair: float


def project_rqi(c: SegmentCovariates, horizon_days: int, load_multiplier: float = 1.0):
    """Return (point, lower, upper)."""
    wear = 0.0009 * horizon_days * (1 + 2.2 * c.rainfall * (1 - c.drainage)) \
        * (1 + c.heavy_share * (load_multiplier - 1) * 1.6) * (1 + 0.04 * c.age_years)
    point = max(0.0, c.rqi - wear * (10 - c.rqi * 0.4))
    half = 0.15 + 0.036 * horizon_days ** 0.5
    return round(point, 2), round(max(0, point - half), 2), round(min(10, point + half), 2)


def failure_risk(point: float, lower: float) -> float:
    """Risk in [0, 1] from the pessimistic bound."""
    return round(max(0.0, min(1.0, (5.0 - lower) / 5.0)), 3)
