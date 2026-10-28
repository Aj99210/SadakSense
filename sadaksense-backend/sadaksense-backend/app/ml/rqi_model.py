"""Learned RQI (LightGBM) with SHAP drivers; falls back to the core.rqi formula."""
import os
from app.config import settings
from app.core import rqi as base

_FEATURES = ["area_D00", "area_D10", "area_D20", "area_D40", "pothole_weighted_count", "mean_confidence"]
_booster = None


def _load():
    global _booster
    if _booster is None and os.path.exists(settings.rqi_model_path):
        import lightgbm as lgb
        _booster = lgb.Booster(model_file=settings.rqi_model_path)
    return _booster


def _vec(f):
    return [[f.area_share["D00"], f.area_share["D10"], f.area_share["D20"], f.area_share["D40"],
             f.pothole_weighted_count, f.mean_confidence]]


def predict(f):
    b = _load()
    if b is None:
        return base.score(f)
    import shap
    x = _vec(f)
    rqi = float(max(0, min(10, b.predict(x)[0])))
    contrib = shap.TreeExplainer(b).shap_values(x)[0]
    drivers = sorted(({"feature": n, "contribution": round(float(c), 3)} for n, c in zip(_FEATURES, contrib)),
                     key=lambda d: d["contribution"])
    return round(rqi, 1), drivers
