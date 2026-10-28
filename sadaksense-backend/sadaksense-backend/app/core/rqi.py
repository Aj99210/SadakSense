"""Road Quality Index (0-10). Pure Python so it is cheap to test.

Baseline is a transparent weighted formula; when a trained LightGBM model
is present (ml/rqi_model.py) it replaces `score()` and this module supplies the
feature vector and the condition labels.
"""
from dataclasses import dataclass

CLASS_WEIGHT = {"D00": 0.6, "D10": 0.6, "D20": 1.4, "D40": 2.2}   # potholes hurt most
AREA_PENALTY = 14.0      # RQI points lost at 100% weighted damage-area share
COUNT_PENALTY = 0.12     # per confidence-weighted pothole, on top of the area effect


@dataclass
class RQIFeatures:
    area_share: dict
    pothole_weighted_count: float
    mean_confidence: float


def _c(d):
    return d.cls.value if hasattr(d.cls, "value") else d.cls


def features_from_findings(detections, road_area_px: float) -> RQIFeatures:
    road_area_px = max(road_area_px, 1.0)
    share = {k: 0.0 for k in CLASS_WEIGHT}
    pot, confs = 0.0, []
    for d in detections:
        c = _c(d)
        share[c] += min(d.area_px / road_area_px, 1.0)
        confs.append(d.confidence)
        if c == "D40":
            pot += d.confidence
    return RQIFeatures(share, pot, sum(confs) / len(confs) if confs else 1.0)


def score(f: RQIFeatures):
    """Return (rqi, drivers). Drivers are signed contributions, SHAP-style."""
    drivers, penalty = [], 0.0
    for cls, sh in f.area_share.items():
        p = CLASS_WEIGHT[cls] * sh * AREA_PENALTY
        if p > 0:
            drivers.append({"feature": f"area_{cls}", "contribution": -round(p, 3)})
        penalty += p
    cp = COUNT_PENALTY * f.pothole_weighted_count
    if cp > 0:
        drivers.append({"feature": "pothole_count", "contribution": -round(cp, 3)})
    penalty += cp
    drivers.sort(key=lambda d: d["contribution"])
    return round(max(0.0, min(10.0, 10.0 - penalty)), 1), drivers


def condition_label(rqi: float) -> str:
    if rqi >= 7.0:
        return "Optimal (Smooth)"
    if rqi >= 3.5:
        return "Moderately Damaged"
    return "Heavily Damaged"


def segment_state(rqi) -> str:
    """Matches the heatmap legend: critical 0-3.5, moderate 3.5-7, good 7-10."""
    if rqi is None:
        return "unscanned"
    return "critical" if rqi < 3.5 else "moderate" if rqi < 7.0 else "good"


def surface_composition(detections, road_area_px: float) -> dict:
    road_area_px = max(road_area_px, 1.0)
    cracks = sum(d.area_px for d in detections if _c(d) in ("D00", "D10", "D20"))
    damaged = sum(d.area_px for d in detections if _c(d) == "D40")
    cracking = min(cracks / road_area_px, 1.0)
    dmg = min(damaged / road_area_px, 1.0)
    minor = min(0.15 * (cracking + dmg) + 0.02, 0.2)
    intact = max(0.0, 1.0 - cracking - dmg - minor)
    return {"intact": round(intact, 3), "minor_wear": round(minor, 3),
            "cracking": round(cracking, 3), "damaged": round(dmg, 3)}
