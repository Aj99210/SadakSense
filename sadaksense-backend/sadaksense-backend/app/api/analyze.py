import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core import rqi as rqi_core
from app.core.speed import ROAD_LIMITS, baseline_speed, congestion_level
from app.ml import detector, rqi_model
from app.schemas import AnalyzeResult
from app.services.privacy import anonymise

router = APIRouter(prefix="/v1", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResult)
async def analyze(file: UploadFile = File(...), lat: float | None = Form(None), lng: float | None = Form(None),
                  road_type: str = Form("Municipal Road")):
    if not detector.is_ready():
        raise HTTPException(503, "Detector weights not loaded")
    data = np.frombuffer(await file.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Unreadable image")

    img = anonymise(img)
    h, w = img.shape[:2]
    dets = detector.detect(img)
    road_area = float(h * w) * 0.55      # replaced by the SAM 3 road-mask area when the segmenter is enabled

    feats = rqi_core.features_from_findings(dets, road_area)
    score, drivers = rqi_model.predict(feats)
    speed = baseline_speed(score, road_type)

    counts = {}
    for d in dets:
        counts[d.cls.value] = counts.get(d.cls.value, 0) + 1

    return AnalyzeResult(
        rqi=score, condition=rqi_core.condition_label(score), est_speed_kmh=speed,
        congestion=congestion_level(speed, ROAD_LIMITS.get(road_type, 50)),
        damage_counts=counts, surface_composition=rqi_core.surface_composition(dets, road_area),
        drivers=drivers, lat=lat, lng=lng)
