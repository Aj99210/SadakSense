from types import SimpleNamespace as NS
from app.core import rqi, speed
from app.core.geo import haversine_m, recency_weighted_mean
from app.ml.forecast import SegmentCovariates, project_rqi
from app.services.complaint import grounded


def det(cls, area, conf=0.9):
    return NS(cls=cls, area_px=area, confidence=conf)


def test_clean_road_scores_high():
    assert rqi.score(rqi.features_from_findings([], 100_000))[0] == 10.0


def test_potholes_lower_rqi_more_than_cracks():
    road = 100_000
    cracks = rqi.score(rqi.features_from_findings([det("D00", 8000)], road))[0]
    pots = rqi.score(rqi.features_from_findings([det("D40", 8000)], road))[0]
    assert pots < cracks < 10


def test_segment_state_matches_heatmap_legend():
    assert rqi.segment_state(None) == "unscanned"
    assert rqi.segment_state(2.0) == "critical"
    assert rqi.segment_state(5.0) == "moderate"
    assert rqi.segment_state(8.0) == "good"


def test_speed_falls_with_rqi():
    assert speed.baseline_speed(2, "Urban Arterial Road") < speed.baseline_speed(9, "Urban Arterial Road")


def test_haversine_one_degree_latitude():
    assert abs(haversine_m(0, 0, 1, 0) - 111_195) < 300


def test_recent_detections_weigh_more():
    assert recency_weighted_mean([2.0, 8.0], [500, 1]) > 6


def test_forecast_worsens_with_rain_and_horizon():
    wet = SegmentCovariates(7.0, 8, 20000, 0.2, 0.3, 0.9, 400)
    dry = SegmentCovariates(7.0, 8, 20000, 0.2, 0.3, 0.0, 400)
    assert project_rqi(wet, 90)[0] < project_rqi(dry, 90)[0] < 7.0


def test_grounding_check_rejects_invented_numbers():
    facts = {"rqi": 3.2, "pin": "110001"}
    assert grounded("RQI is 3.2 at PIN 110001.", facts)
    assert not grounded("RQI is 3.2 and 47 potholes were found.", facts)
